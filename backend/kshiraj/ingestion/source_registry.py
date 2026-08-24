"""
kshiraj/ingestion/source_registry.py

Registry and configuration repository for authoritative Indian government sources.
Maps source endpoints to domain policies, crawl boundaries, and source adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from shared.models import EvidenceSourceType
from shared.utils import get_logger
from kshiraj.ingestion.models import CrawlPolicy

logger = get_logger(__name__)


@dataclass
class GovernmentSourceConfig:
    """
    Configuration for an authoritative government data source.
    """
    name: str
    source_type: EvidenceSourceType
    base_urls: List[str]
    allowed_domains: List[str]
    adapter_name: str                      # 'bis', 'bis_drafts', 'cppp', 'qco', etc.
    description: str = ""
    allowed_path_prefixes: List[str] = field(default_factory=list)
    denied_path_prefixes: List[str] = field(default_factory=list)
    crawl_policy: Optional[CrawlPolicy] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    parser_strategy: str = "auto"          # 'auto', 'html_table', 'json_api', 'pdf_attachment'


class SourceRegistry:
    """
    Central catalog of registered government data sources.
    """

    def __init__(self) -> None:
        self._sources: Dict[str, GovernmentSourceConfig] = {}
        self._register_default_sources()

    def register_source(self, config: GovernmentSourceConfig) -> None:
        """Register or update a government source configuration."""
        key = config.name.strip().upper()
        self._sources[key] = config
        logger.debug("Registered government source '%s'", key)

    def get_source(self, name: str) -> Optional[GovernmentSourceConfig]:
        """Lookup a source configuration by name."""
        return self._sources.get(name.strip().upper())

    def list_sources(self) -> List[GovernmentSourceConfig]:
        """Return all registered source configurations."""
        return list(self._sources.values())

    def match_source_by_url(self, url: str) -> Optional[GovernmentSourceConfig]:
        """Find the matching source configuration for a given URL based on domain."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not domain:
                return None

            for source in self._sources.values():
                for allowed in source.allowed_domains:
                    allowed_clean = allowed.lower().strip()
                    if domain == allowed_clean or domain.endswith("." + allowed_clean):
                        return source
            return None
        except Exception:
            return None

    def _register_default_sources(self) -> None:
        """Populate initial canonical Indian Government data sources."""
        # 1. BIS Catalog (Bureau of Indian Standards)
        self.register_source(
            GovernmentSourceConfig(
                name="BIS_CATALOG",
                source_type=EvidenceSourceType.BIS_STANDARD,
                base_urls=[
                    "https://www.bis.gov.in/standards/",
                    "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/knowyourstandards/",
                ],
                allowed_domains=["services.bis.gov.in", "bis.gov.in"],
                adapter_name="bis",
                description="Bureau of Indian Standards official catalog and standards database.",
                crawl_policy=CrawlPolicy(
                    allowed_domains=["services.bis.gov.in", "bis.gov.in"],
                    max_depth=3,
                    max_pages=50,
                    crawl_delay_seconds=1.0,
                ),
            )
        )

        # 2. BIS Wide Circulation Drafts
        self.register_source(
            GovernmentSourceConfig(
                name="BIS_DRAFTS",
                source_type=EvidenceSourceType.BIS_WIDE_CIRCULATION_DRAFT,
                base_urls=[
                    "https://www.bis.gov.in/standards/technical-department/wc-drafts/",
                    "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/wc_drafts/",
                ],
                allowed_domains=["services.bis.gov.in", "bis.gov.in"],
                adapter_name="bis_drafts",
                description="BIS Wide Circulation Draft standards undergoing committee review.",
                crawl_policy=CrawlPolicy(
                    allowed_domains=["services.bis.gov.in", "bis.gov.in"],
                    max_depth=2,
                    max_pages=30,
                    crawl_delay_seconds=1.0,
                ),
            )
        )

        # 3. CPPP / eProcure Tenders
        self.register_source(
            GovernmentSourceConfig(
                name="CPPP_TENDERS",
                source_type=EvidenceSourceType.CPPP_TENDER,
                base_urls=["https://eprocure.gov.in/eprocure/app"],
                allowed_domains=["eprocure.gov.in", "cppp.gov.in"],
                adapter_name="cppp",
                description="Central Public Procurement Portal tender specifications and corrigenda.",
                crawl_policy=CrawlPolicy(
                    allowed_domains=["eprocure.gov.in", "cppp.gov.in"],
                    max_depth=4,
                    max_pages=50,
                    crawl_delay_seconds=1.5,
                ),
            )
        )

        # 4. QCO Gazette Notifications (DPIIT / MeitY / Ministries)
        self.register_source(
            GovernmentSourceConfig(
                name="QCO_NOTIFICATIONS",
                source_type=EvidenceSourceType.QCO_NOTIFICATION,
                base_urls=["https://dpiit.gov.in/quality-control-orders", "https://egazette.gov.in/"],
                allowed_domains=["dpiit.gov.in", "egazette.gov.in", "meity.gov.in"],
                adapter_name="qco",
                description="Quality Control Orders and Gazette notifications mandating BIS compliance.",
                crawl_policy=CrawlPolicy(
                    allowed_domains=["dpiit.gov.in", "egazette.gov.in", "meity.gov.in"],
                    max_depth=3,
                    max_pages=30,
                    crawl_delay_seconds=1.0,
                ),
            )
        )
