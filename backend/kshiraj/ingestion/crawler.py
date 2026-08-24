"""
kshiraj/ingestion/crawler.py

Controlled, domain-restricted web crawler for government standards and procurement portals.
Integrates URL frontier, HTTP client, robots policy, attachment discovery, and page extractors.
"""

from __future__ import annotations

from datetime import datetime
import time
from typing import Callable, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from shared.models import EvidenceSourceType
from shared.utils import get_logger, utcnow
from kshiraj.ingestion.attachment_discovery import AttachmentDiscovery
from kshiraj.ingestion.dynamic_renderer import BasePageRenderer, HttpFallbackRenderer
from kshiraj.ingestion.frontier import UrlFrontier, classify_link, normalize_url
from kshiraj.ingestion.html_extractor import HtmlExtractor
from kshiraj.ingestion.http_client import GovtHttpClient
from kshiraj.ingestion.json_extractor import JsonExtractor
from kshiraj.ingestion.models import (
    CrawlPolicy,
    CrawlResult,
    DiscoveredLink,
    FetchedResource,
    LinkType,
    RawDocument,
)
from kshiraj.ingestion.pagination import PaginationHandler
from kshiraj.ingestion.pdf_extractor import PdfExtractor
from kshiraj.ingestion.robots import RobotsPolicy

logger = get_logger(__name__)


class GovtCrawler:
    """
    Polite and bounded web crawler designed specifically for government portals.
    """

    def __init__(
        self,
        http_client: Optional[GovtHttpClient] = None,
        renderer: Optional[BasePageRenderer] = None,
        robots_policy: Optional[RobotsPolicy] = None,
        html_extractor: Optional[HtmlExtractor] = None,
        pdf_extractor: Optional[PdfExtractor] = None,
        json_extractor: Optional[JsonExtractor] = None,
        attachment_discovery: Optional[AttachmentDiscovery] = None,
        pagination_handler: Optional[PaginationHandler] = None,
        policy_evaluator: Optional[Any] = None,
    ) -> None:
        self.http_client = http_client or GovtHttpClient()
        self.renderer = renderer or HttpFallbackRenderer(self.http_client)
        self.robots_policy = robots_policy or RobotsPolicy()
        self.html_extractor = html_extractor or HtmlExtractor()
        self.pdf_extractor = pdf_extractor or PdfExtractor()
        self.json_extractor = json_extractor or JsonExtractor()
        self.attachment_discovery = attachment_discovery or AttachmentDiscovery()
        self.pagination_handler = pagination_handler or PaginationHandler()
        
        if policy_evaluator is None:
            from kshiraj.ingestion.policy import PolicyEvaluator
            self.policy_evaluator = PolicyEvaluator()
        else:
            self.policy_evaluator = policy_evaluator

    def crawl_source(
        self,
        seed_urls: List[str],
        policy: CrawlPolicy,
        source_name: str = "Government Portal",
        source_type: EvidenceSourceType = EvidenceSourceType.OTHER_GOVERNMENT,
        on_document_acquired: Optional[Callable[[RawDocument], None]] = None,
    ) -> Tuple[CrawlResult, List[RawDocument]]:
        """
        Execute a bounded crawl starting from seed URLs according to the CrawlPolicy.
        """
        frontier = UrlFrontier(seed_urls=seed_urls, policy=policy)
        acquired_documents: List[RawDocument] = []
        errors: List[str] = []

        start_time = utcnow()
        t0 = time.perf_counter()

        result = CrawlResult(
            source_name=source_name,
            start_url=seed_urls[0] if seed_urls else "",
            start_time=start_time,
            pages_discovered=len(seed_urls),
        )

        logger.info(
            "Starting crawl for '%s' (seed=%s, max_pages=%s, max_depth=%s)",
            source_name, seed_urls, policy.max_pages, policy.max_depth
        )

        while frontier.has_next():
            item = frontier.pop_next()
            if item is None:
                break

            current_url, depth, parent_url = item
            result.pages_crawled += 1
            result.pages_fetched += 1

            # 1. Evaluate Source Policy
            if self.policy_evaluator:
                from kshiraj.ingestion.policy import ComplianceDecision
                decision = self.policy_evaluator.evaluate_url(current_url)
                if decision == ComplianceDecision.SOURCE_BLOCKED:
                    logger.info("Skipping crawl for %s: Source is flagged as WAF blocked.", current_url)
                    result.blocked_pages += 1
                    result.pages_failed += 1
                    errors.append(f"Policy blocked: {current_url}")
                    continue
                elif decision == ComplianceDecision.ACCESS_RESTRICTED:
                    logger.info("Skipping crawl for %s: Access restricted by policy.", current_url)
                    result.pages_failed += 1
                    errors.append(f"Policy restricted: {current_url}")
                    continue

            # 2. Check robots.txt compliance
            if policy.respect_robots_txt and not self.robots_policy.is_allowed(current_url, policy.user_agent):
                logger.warning("URL blocked by robots.txt: %s", current_url)
                result.robots_blocked += 1
                result.pages_failed += 1
                errors.append(f"Robots.txt disallowed: {current_url}")
                continue

            # 3. Polite crawl delay
            self.robots_policy.wait_if_needed(current_url)

            # 4. Fetch resource
            link_type, mime_hint = classify_link(current_url)

            try:
                if link_type == LinkType.DOCUMENT and mime_hint == "application/pdf":
                    fetched = self.http_client.download_document(current_url, timeout=policy.request_timeout_seconds)
                else:
                    fetched = self.http_client.fetch(current_url, timeout=policy.request_timeout_seconds)

                if fetched.status_code >= 400 or fetched.is_blocked:
                    result.pages_failed += 1
                    if fetched.is_blocked:
                        result.blocked_pages += 1
                    if fetched.requires_human_verification:
                        result.verification_required += 1

                    err = fetched.error_message or f"HTTP {fetched.status_code}"
                    if fetched.requires_human_verification:
                        err += " (CAPTCHA detected - requires human verification)"
                    errors.append(f"Failed {current_url}: {err}")
                    continue

                result.pages_succeeded += 1

                # 5. Extract document payload
                raw_doc = self._extract_raw_document(
                    fetched=fetched,
                    source_name=source_name,
                    source_type=source_type,
                )
                acquired_documents.append(raw_doc)
                result.records_extracted += 1

                if on_document_acquired:
                    on_document_acquired(raw_doc)

                # 6. If HTML page, discover pagination and outgoing links if within depth limit
                if "text/html" in fetched.content_type.lower() and depth < policy.max_depth:
                    # Discover attachments
                    attachments = self.attachment_discovery.discover_attachments(
                        html_content=fetched.text_content,
                        base_url=fetched.canonical_url,
                        depth=depth + 1,
                    )
                    result.attachments_discovered += len(attachments)
                    result.documents_discovered += len(attachments)

                    for att in attachments:
                        if frontier.add_url(
                            att.canonical_url,
                            depth=depth + 1,
                            parent_url=current_url,
                            anchor_text=att.anchor_text,
                        ):
                            result.pages_discovered += 1

                    # Discover pagination links
                    pagination_links = self.pagination_handler.extract_pagination_links(
                        html_content=fetched.text_content,
                        current_url=fetched.canonical_url,
                    )
                    for pag_url in pagination_links:
                        if frontier.add_url(pag_url, depth=depth, parent_url=current_url):
                            result.pages_discovered += 1

                    # Discover standard navigational links
                    new_links = self._extract_navigation_links(
                        html_content=fetched.text_content,
                        base_url=fetched.canonical_url,
                        frontier=frontier,
                        current_depth=depth,
                    )
                    result.pages_discovered += new_links

            except Exception as exc:
                result.pages_failed += 1
                err_str = f"Exception crawling {current_url}: {exc}"
                logger.error(err_str)
                errors.append(err_str)

        # Finalize crawl stats
        elapsed = time.perf_counter() - t0
        result.end_time = utcnow()
        result.elapsed_seconds = round(elapsed, 2)
        result.errors = errors
        result.attachments_ingested = len(acquired_documents)

        logger.info(
            "Crawl finished for '%s': %s pages (%s succeeded, %s failed) in %.2fs",
            source_name, result.pages_crawled, result.pages_succeeded, result.pages_failed, elapsed
        )
        return result, acquired_documents

    def _extract_raw_document(
        self,
        fetched: FetchedResource,
        source_name: str,
        source_type: EvidenceSourceType,
    ) -> RawDocument:
        """Parse fetched content using the appropriate content-type extractor."""
        ct = fetched.content_type.lower()

        if "application/pdf" in ct or fetched.canonical_url.lower().endswith(".pdf"):
            return self.pdf_extractor.extract_document(
                pdf_bytes=fetched.content_bytes,
                source_url=fetched.canonical_url,
                source_name=source_name,
                source_type=source_type,
            )
        elif "application/json" in ct or fetched.canonical_url.lower().endswith(".json"):
            return self.json_extractor.extract_document(
                json_data=fetched.content_bytes or fetched.text_content,
                source_url=fetched.canonical_url,
                source_name=source_name,
                source_type=source_type,
                content_hash=fetched.content_hash,
            )
        else:
            return self.html_extractor.extract_document(
                html_content=fetched.text_content,
                source_url=fetched.canonical_url,
                source_name=source_name,
                source_type=source_type,
                content_hash=fetched.content_hash,
            )

    def _extract_navigation_links(
        self,
        html_content: str,
        base_url: str,
        frontier: UrlFrontier,
        current_depth: int,
    ) -> int:
        """Extract standard HTML links and enqueue them in the frontier."""
        if not html_content:
            return 0

        enqueued = 0
        soup = BeautifulSoup(html_content, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if href and not href.startswith("#") and not href.startswith("javascript:"):
                if frontier.add_url(
                    raw_url=href,
                    depth=current_depth + 1,
                    parent_url=base_url,
                    anchor_text=a_tag.get_text(strip=True),
                ):
                    enqueued += 1
        return enqueued
