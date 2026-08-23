"""
kshiraj/ingestion/frontier.py

URL Frontier and canonical URL normalization for bounded, domain-restricted crawling.
Implements:
  - Canonical URL normalization (query sorting, scheme/host lowercasing, fragment stripping)
  - Strict domain restriction and allowlist validation
  - Depth-bounded queue management (FIFO with depth tracking)
  - Visited set deduplication
  - Path prefix and file extension filtering
"""

from __future__ import annotations

from collections import deque
import re
from typing import Deque, Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from shared.utils import get_logger
from kshiraj.ingestion.models import CrawlPolicy, DiscoveredLink, LinkType

logger = get_logger(__name__)

# Non-document asset extensions that should not be crawled as web pages
_IGNORED_ASSET_EXTENSIONS = {
    ".css", ".js", ".mjs", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".ico", ".webp", ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3",
    ".avi", ".mov", ".wmv", ".zip", ".tar", ".gz", ".7z", ".rar", ".exe",
}

# Document extensions
_DOCUMENT_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv",
    ".json": "application/json",
    ".xml": "application/xml",
}


def normalize_url(raw_url: str, base_url: Optional[str] = None) -> str:
    """
    Produce a canonical, normalized string representation of a URL.

    - Resolves relative links against `base_url`
    - Lowercases scheme and netloc
    - Removes default ports (80 for http, 443 for https)
    - Strips fragment identifiers (`#...`)
    - Collapses redundant slashes in path
    - Sorts query parameters for deterministic hashing
    - Removes tracking params (utm_*, gclid, etc.)
    """
    if not raw_url or not raw_url.strip():
        return ""

    cleaned = raw_url.strip()
    if base_url:
        cleaned = urljoin(base_url, cleaned)

    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https"):
        return ""

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Remove default port
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    # Normalize path
    path = parsed.path or "/"
    path = re.sub(r"/+", "/", path)  # Collapse multiple slashes

    # Normalize and filter query parameters
    query_params = parse_qsl(parsed.query, keep_blank_values=False)
    filtered_params = []
    for k, v in query_params:
        lower_k = k.lower()
        if lower_k.startswith("utm_") or lower_k in ("gclid", "fbclid", "ref", "source"):
            continue
        filtered_params.append((k, v))

    # Sort query parameters for determinism
    filtered_params.sort(key=lambda item: (item[0], item[1]))
    normalized_query = urlencode(filtered_params)

    # Reconstruct without fragment
    return urlunparse((scheme, netloc, path, "", normalized_query, ""))


def extract_domain(url: str) -> str:
    """Extract domain / hostname from a URL."""
    try:
        parsed = urlparse(url)
        return parsed.hostname.lower() if parsed.hostname else ""
    except Exception:
        return ""


def classify_link(url: str) -> Tuple[LinkType, Optional[str]]:
    """Classify a target URL into document, pagination, navigation, or asset."""
    parsed = urlparse(url)
    path_lower = parsed.path.lower()

    for ext, mime in _DOCUMENT_EXTENSIONS.items():
        if path_lower.endswith(ext):
            return LinkType.DOCUMENT, mime

    # Check for pagination signals in path or query
    query_lower = parsed.query.lower()
    if any(p in query_lower for p in ("page=", "pageno=", "p=", "offset=", "start=")) or "page/" in path_lower:
        return LinkType.PAGINATION, None

    return LinkType.NAVIGATION, None


class UrlFrontier:
    """
    Manages the queue of discovered URLs to visit during a crawling session.
    Enforces depth limits, domain restrictions, visited deduplication, and max page bounds.
    """

    def __init__(
        self,
        seed_urls: Optional[List[str]] = None,
        policy: Optional[CrawlPolicy] = None,
    ) -> None:
        self.policy = policy or CrawlPolicy()
        self._queue: Deque[Tuple[str, int, str]] = deque()  # (canonical_url, depth, parent_url)
        self._visited: Set[str] = set()
        self._queued: Set[str] = set()
        self._discovered_documents: List[DiscoveredLink] = []

        if seed_urls:
            for seed in seed_urls:
                self.add_url(seed, depth=0, parent_url="")

    def __len__(self) -> int:
        return len(self._queue)

    @property
    def visited_count(self) -> int:
        return len(self._visited)

    @property
    def discovered_documents(self) -> List[DiscoveredLink]:
        return list(self._discovered_documents)

    def is_domain_allowed(self, url: str) -> bool:
        """Check if the URL belongs to an allowed domain."""
        domain = extract_domain(url)
        if not domain:
            return False

        if not self.policy.allowed_domains:
            return True

        for allowed in self.policy.allowed_domains:
            allowed_clean = allowed.lower().strip()
            if domain == allowed_clean or domain.endswith("." + allowed_clean):
                return True
        return False

    def is_path_allowed(self, url: str) -> bool:
        """Check if URL path satisfies prefix allow/deny rules."""
        parsed = urlparse(url)
        path = parsed.path

        # Check denied prefixes first
        for denied in self.policy.denied_path_prefixes:
            if path.startswith(denied):
                return False

        # Check ignored asset extensions
        for ext in _IGNORED_ASSET_EXTENSIONS:
            if path.lower().endswith(ext):
                return False

        # If allowed prefixes are specified, URL must match at least one
        if self.policy.allowed_path_prefixes:
            return any(path.startswith(prefix) for prefix in self.policy.allowed_path_prefixes)

        return True

    def is_url_crawlable(self, url: str, depth: int) -> bool:
        """Evaluate whether a URL is valid for enqueueing."""
        if not url:
            return False

        if depth > self.policy.max_depth:
            return False

        if not self.is_domain_allowed(url):
            return False

        if not self.is_path_allowed(url):
            return False

        if url in self._visited or url in self._queued:
            return False

        return True

    def add_url(
        self,
        raw_url: str,
        depth: int = 0,
        parent_url: str = "",
        anchor_text: str = "",
    ) -> bool:
        """
        Normalize and enqueue a URL if it satisfies crawling policies.
        Returns True if enqueued, False otherwise.
        """
        canonical = normalize_url(raw_url, base_url=parent_url)
        if not canonical:
            return False

        link_type, mime_hint = classify_link(canonical)

        # If it's a downloadable document, register in discovered documents
        if link_type == LinkType.DOCUMENT:
            doc_link = DiscoveredLink(
                url=raw_url,
                canonical_url=canonical,
                anchor_text=anchor_text,
                link_type=LinkType.DOCUMENT,
                parent_url=parent_url,
                depth=depth,
                mime_type_hint=mime_hint,
            )
            if not any(d.canonical_url == canonical for d in self._discovered_documents):
                self._discovered_documents.append(doc_link)

        # Evaluate if we should queue this page for crawling
        if not self.is_url_crawlable(canonical, depth):
            return False

        self._queue.append((canonical, depth, parent_url))
        self._queued.add(canonical)
        return True

    def pop_next(self) -> Optional[Tuple[str, int, str]]:
        """
        Retrieve the next URL to fetch from the queue.
        Marks URL as visited.
        """
        if not self._queue:
            return None

        canonical, depth, parent_url = self._queue.popleft()
        self._visited.add(canonical)
        return canonical, depth, parent_url

    def has_next(self) -> bool:
        """Check if there are pending URLs and visited count has not exceeded max_pages."""
        if len(self._visited) >= self.policy.max_pages:
            return False
        return len(self._queue) > 0

    def mark_visited(self, url: str) -> None:
        """Manually mark a URL as visited."""
        canonical = normalize_url(url)
        if canonical:
            self._visited.add(canonical)

    def is_visited(self, url: str) -> bool:
        """Check if a URL has already been visited."""
        canonical = normalize_url(url)
        return canonical in self._visited
