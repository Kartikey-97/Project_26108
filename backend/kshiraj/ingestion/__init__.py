"""
kshiraj/ingestion/__init__.py

Public interface for the Kshiraj Government Ingestion Subsystem.
Provides robust HTTP acquisition, bounded crawling, attachment extraction,
document deduplication, source compliance policies, and integration with
the Kshiraj knowledge & vector pipeline.
"""

from kshiraj.ingestion.attachment_discovery import AttachmentDiscovery
from kshiraj.ingestion.crawler import GovtCrawler
from kshiraj.ingestion.deduplication import DocumentDeduplicator, DocumentState
from kshiraj.ingestion.dynamic_renderer import BasePageRenderer, HttpFallbackRenderer, PlaywrightRenderer
from kshiraj.ingestion.frontier import UrlFrontier, classify_link, extract_domain, normalize_url
from kshiraj.ingestion.html_extractor import HtmlExtractor
from kshiraj.ingestion.http_client import GovtHttpClient, GovtHttpClientError
from kshiraj.ingestion.incremental import IncrementalIngestionTracker, UrlSyncState
from kshiraj.ingestion.ingestion_pipeline import IngestionPipeline
from kshiraj.ingestion.json_extractor import JsonExtractor
from kshiraj.ingestion.models import (
    CrawlPolicy,
    CrawlResult,
    DiscoveredLink,
    ExtractionStatus,
    FetchedResource,
    IngestionResult,
    IngestionStatus,
    LinkType,
    PageMetadata,
    RawDocument,
)
from kshiraj.ingestion.pagination import PaginationHandler
from kshiraj.ingestion.parsers import (
    BasePortalParser,
    BisPortalParser,
    CpppPortalParser,
    DpiitPortalParser,
    EgazettePortalParser,
)
from kshiraj.ingestion.pdf_extractor import PdfExtractor
from kshiraj.ingestion.policy import (
    ComplianceDecision,
    PolicyEvaluator,
    SourcePolicy,
    StoragePermission,
)
from kshiraj.ingestion.robots import RobotsPolicy
from kshiraj.ingestion.source_registry import GovernmentSourceConfig, SourceRegistry

__all__ = [
    "AttachmentDiscovery",
    "BasePageRenderer",
    "BasePortalParser",
    "BisPortalParser",
    "ComplianceDecision",
    "CpppPortalParser",
    "CrawlPolicy",
    "CrawlResult",
    "DiscoveredLink",
    "DocumentDeduplicator",
    "DocumentState",
    "DpiitPortalParser",
    "EgazettePortalParser",
    "ExtractionStatus",
    "FetchedResource",
    "GovernmentSourceConfig",
    "GovtCrawler",
    "GovtHttpClient",
    "GovtHttpClientError",
    "HtmlExtractor",
    "HttpFallbackRenderer",
    "IncrementalIngestionTracker",
    "IngestionPipeline",
    "IngestionResult",
    "IngestionStatus",
    "JsonExtractor",
    "LinkType",
    "PageMetadata",
    "PaginationHandler",
    "PdfExtractor",
    "PlaywrightRenderer",
    "PolicyEvaluator",
    "RawDocument",
    "RobotsPolicy",
    "SourcePolicy",
    "SourceRegistry",
    "StoragePermission",
    "UrlFrontier",
    "UrlSyncState",
    "classify_link",
    "extract_domain",
    "normalize_url",
]
