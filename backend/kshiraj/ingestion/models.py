"""
kshiraj/ingestion/models.py

Data contracts and type definitions for the Government Ingestion Subsystem.
Defines structured representations for fetched resources, raw documents,
discovered links, crawl configurations, and pipeline results with full provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid

from shared.models import DocumentType as BISDocumentType, EvidenceSourceType
from shared.utils import utcnow


def _new_uuid() -> str:
    return str(uuid.uuid4())


class IngestionStatus(str, Enum):
    """Lifecycle status of a document or URL ingestion job."""
    NEW = "new"
    UNCHANGED = "unchanged"
    MODIFIED = "modified"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    REQUIRES_HUMAN_VERIFICATION = "requires_human_verification"


class ExtractionStatus(str, Enum):
    """Status of content/text extraction from a downloaded document."""
    SUCCESS = "success"
    EMPTY = "empty"
    OCR_REQUIRED = "ocr_required"
    MALFORMED = "malformed"
    UNSUPPORTED_TYPE = "unsupported_type"
    FAILED = "failed"


class LinkType(str, Enum):
    """Classification of a link discovered during crawling."""
    DOCUMENT = "document"          # PDF, DOCX, XLS, CSV, XML
    PAGINATION = "pagination"      # Next page, page number link
    NAVIGATION = "navigation"      # Detail page, category link
    ATTACHMENT = "attachment"      # Download button / embedded file
    EXTERNAL = "external"          # Link to non-target domain


@dataclass
class FetchedResource:
    """
    Result of fetching a single HTTP resource (HTML, JSON, PDF, etc.).
    Preserves HTTP headers, timestamps, hash, and redirection provenance.
    """
    url: str
    canonical_url: str
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    content_bytes: bytes = b""
    text_content: str = ""
    content_type: str = "text/html"
    content_length: int = 0
    content_hash: str = ""                     # SHA-256
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    retrieved_at: datetime = field(default_factory=utcnow)
    redirected_urls: List[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    is_blocked: bool = False
    requires_human_verification: bool = False  # e.g. CAPTCHA detected
    error_message: Optional[str] = None


@dataclass
class DiscoveredLink:
    """A link extracted from an HTML or structured page."""
    url: str
    canonical_url: str
    anchor_text: str = ""
    link_type: LinkType = LinkType.NAVIGATION
    parent_url: str = ""
    depth: int = 0
    mime_type_hint: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class PageMetadata:
    """Extracted HTML/PDF metadata."""
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    author: Optional[str] = None
    published_date: Optional[str] = None
    headings: Dict[str, List[str]] = field(default_factory=dict)  # h1, h2, h3
    tables: List[List[Dict[str, Any]]] = field(default_factory=list)
    json_ld: List[Dict[str, Any]] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RawDocument:
    """
    A standardized internal representation of an acquired government document.
    Carries raw text, page-by-page breakdown, content hash, and source metadata.
    """
    id: str = field(default_factory=_new_uuid)
    source_url: str = ""
    canonical_url: str = ""
    source_name: str = ""
    source_type: EvidenceSourceType = EvidenceSourceType.OTHER_GOVERNMENT
    mime_type: str = "text/html"
    content_hash: str = ""                     # SHA-256
    content_length: int = 0
    text_content: str = ""
    page_texts: Dict[int, str] = field(default_factory=dict)  # page_number -> text
    page_count: int = 1
    metadata: PageMetadata = field(default_factory=PageMetadata)
    extraction_status: ExtractionStatus = ExtractionStatus.SUCCESS
    retrieved_at: datetime = field(default_factory=utcnow)
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None  # for structured API / JSON endpoints


@dataclass
class CrawlPolicy:
    """Configuration governing crawl bounds, rate limits, and allowed scopes."""
    allowed_domains: List[str] = field(default_factory=list)
    allowed_path_prefixes: List[str] = field(default_factory=list)
    denied_path_prefixes: List[str] = field(default_factory=list)
    max_depth: int = 3
    max_pages: int = 100
    crawl_delay_seconds: float = 0.5
    respect_robots_txt: bool = True
    user_agent: str = "Project26108-GovtIngestionBot/1.0 (+https://github.com/Kartikey-97/ThreatLens)"
    max_response_size_bytes: int = 50 * 1024 * 1024  # 50 MB
    request_timeout_seconds: float = 30.0
    max_retries: int = 3
    follow_redirects: bool = True
    same_domain_only: bool = True


@dataclass
class IngestionResult:
    """Outcome of ingesting a single document or URL through the pipeline."""
    id: str = field(default_factory=_new_uuid)
    source_url: str = ""
    status: IngestionStatus = IngestionStatus.SUCCESS
    content_hash: str = ""
    standards_created: int = 0
    standards_updated: int = 0
    evidence_created: int = 0
    standard_ids: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    indexed_vector_count: int = 0
    error_message: Optional[str] = None
    elapsed_seconds: float = 0.0
    retrieved_at: datetime = field(default_factory=utcnow)


@dataclass
class CrawlResult:
    """Aggregate statistics for a multi-page crawl and ingestion run."""
    source_name: str
    start_url: str
    pages_discovered: int = 0
    pages_fetched: int = 0
    pages_crawled: int = 0
    pages_succeeded: int = 0
    pages_failed: int = 0
    documents_discovered: int = 0
    attachments_discovered: int = 0
    attachments_ingested: int = 0
    duplicates_skipped: int = 0
    blocked_pages: int = 0
    robots_blocked: int = 0
    verification_required: int = 0
    records_extracted: int = 0
    standards_ingested: int = 0
    evidence_ingested: int = 0
    vectors_indexed: int = 0
    ingestion_results: List[IngestionResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=utcnow)
    end_time: Optional[datetime] = None
    elapsed_seconds: float = 0.0
