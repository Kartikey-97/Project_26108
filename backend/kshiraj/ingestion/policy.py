"""
kshiraj/ingestion/policy.py

Source compliance and policy management for government data acquisition.
Defines domain permissions, rate limits, storage policies (metadata vs full document),
and structured compliance evaluation outcomes without circumventing security controls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

from shared.utils import get_logger
from kshiraj.ingestion.frontier import extract_domain, normalize_url

logger = get_logger(__name__)


class ComplianceDecision(str, Enum):
    """Result of evaluating a URL or request against compliance policy."""
    ALLOWED = "allowed"
    SOURCE_BLOCKED = "source_blocked"
    ACCESS_RESTRICTED = "access_restricted"
    ROBOTS_DISALLOWED = "robots_disallowed"
    REQUIRES_HUMAN_VERIFICATION = "requires_human_verification"
    PERMISSION_REQUIRED = "permission_required"
    UNSUPPORTED_CONTENT_TYPE = "unsupported_content_type"


class StoragePermission(str, Enum):
    """Storage boundaries governing extracted government content."""
    METADATA_AND_EXCERPTS_ONLY = "metadata_and_excerpts_only"
    FULL_DOCUMENT_ALLOWED = "full_document_allowed"


@dataclass
class SourcePolicy:
    """
    Compliance and operational policy governing an authoritative government domain.
    """
    name: str
    domain: str
    allowed_domains: List[str] = field(default_factory=list)
    allowed_path_prefixes: List[str] = field(default_factory=list)
    denied_path_prefixes: List[str] = field(default_factory=list)
    permitted_content_types: List[str] = field(
        default_factory=lambda: [
            "text/html",
            "application/pdf",
            "application/json",
            "application/xml",
            "text/csv",
        ]
    )
    storage_permission: StoragePermission = StoragePermission.FULL_DOCUMENT_ALLOWED
    rate_limit_delay_seconds: float = 1.0
    max_concurrent_requests: int = 2
    max_crawl_depth: int = 3
    max_pages: int = 50
    requires_ssl_override: bool = False
    is_blocked_by_waf: bool = False
    attribution_requirement: str = "Government of India"


class PolicyEvaluator:
    """
    Evaluates target URLs and content types against configured government source policies.
    """

    def __init__(self, custom_policies: Optional[Dict[str, SourcePolicy]] = None) -> None:
        self._policies: Dict[str, SourcePolicy] = {}
        self._register_default_policies()
        if custom_policies:
            for k, p in custom_policies.items():
                self._policies[k.upper()] = p

    def register_policy(self, policy: SourcePolicy) -> None:
        """Register or update a source policy."""
        self._policies[policy.name.upper()] = policy

    def get_policy_for_url(self, url: str) -> Optional[SourcePolicy]:
        """Find matching policy based on domain."""
        domain = extract_domain(url)
        if not domain:
            return None

        for pol in self._policies.values():
            for allowed in pol.allowed_domains:
                clean_allowed = allowed.lower().strip()
                if domain == clean_allowed or domain.endswith("." + clean_allowed):
                    return pol
        return None

    def evaluate_url(self, url: str) -> ComplianceDecision:
        """
        Evaluate if a target URL is permitted for crawling and acquisition.
        """
        if not url or not url.strip():
            return ComplianceDecision.ACCESS_RESTRICTED

        policy = self.get_policy_for_url(url)
        if policy is None:
            # If domain is not in our government source registry/policy -> Restricted
            return ComplianceDecision.PERMISSION_REQUIRED

        if policy.is_blocked_by_waf:
            logger.info("URL %s matches policy '%s' which is flagged as WAF blocked.", url, policy.name)
            return ComplianceDecision.SOURCE_BLOCKED

        parsed = urlparse(url)
        path = parsed.path

        # Check denied paths
        for denied in policy.denied_path_prefixes:
            if path.startswith(denied):
                return ComplianceDecision.ACCESS_RESTRICTED

        # Check allowed paths if configured
        if policy.allowed_path_prefixes:
            if not any(path.startswith(prefix) for prefix in policy.allowed_path_prefixes):
                return ComplianceDecision.ACCESS_RESTRICTED

        return ComplianceDecision.ALLOWED

    def evaluate_content_type(self, content_type: str, policy: Optional[SourcePolicy] = None) -> bool:
        """Verify whether the HTTP Content-Type is permitted under policy."""
        if not content_type:
            return True
        clean_ct = content_type.lower().split(";")[0].strip()

        if policy:
            return any(clean_ct.startswith(p) or p.startswith(clean_ct) for p in policy.permitted_content_types)

        # Default allowed types
        return any(clean_ct.startswith(p) for p in ("text/html", "application/pdf", "application/json", "text/csv"))

    def _register_default_policies(self) -> None:
        """Pre-configure compliance policies for core Indian Government entities."""
        # 1. BIS (Bureau of Indian Standards)
        # Note: Proprietary full standards documents are not mirrored; only metadata and scope are preserved.
        self.register_policy(
            SourcePolicy(
                name="BIS",
                domain="bis.gov.in",
                allowed_domains=["bis.gov.in", "services.bis.gov.in", "standardsbis.bsbedge.com"],
                permitted_content_types=["text/html", "application/pdf", "application/json"],
                storage_permission=StoragePermission.METADATA_AND_EXCERPTS_ONLY,
                rate_limit_delay_seconds=1.0,
                max_crawl_depth=3,
                max_pages=50,
                attribution_requirement="Bureau of Indian Standards (BIS)",
            )
        )

        # 2. CPPP (Central Public Procurement Portal)
        # Note: Tender notices, corrigenda, and public bidding documents are fully open public records.
        self.register_policy(
            SourcePolicy(
                name="CPPP",
                domain="eprocure.gov.in",
                allowed_domains=["eprocure.gov.in", "cppp.gov.in"],
                permitted_content_types=["text/html", "application/pdf", "application/json", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
                storage_permission=StoragePermission.FULL_DOCUMENT_ALLOWED,
                rate_limit_delay_seconds=1.5,
                max_crawl_depth=4,
                max_pages=50,
                attribution_requirement="Central Public Procurement Portal (CPPP), NIC",
            )
        )

        # 3. DPIIT (Department for Promotion of Industry and Internal Trade)
        # Quality Control Orders are open public statutory orders. Handled gracefully when behind WAF.
        self.register_policy(
            SourcePolicy(
                name="DPIIT",
                domain="dpiit.gov.in",
                allowed_domains=["dpiit.gov.in"],
                permitted_content_types=["text/html", "application/pdf"],
                storage_permission=StoragePermission.FULL_DOCUMENT_ALLOWED,
                rate_limit_delay_seconds=1.0,
                max_crawl_depth=2,
                max_pages=30,
                is_blocked_by_waf=True,  # Observed Akamai/NIC WAF block
                attribution_requirement="DPIIT, Ministry of Commerce and Industry",
            )
        )

        # 4. eGazette (Gazette of India)
        # Public gazette notifications. Requires custom SSL verification handling for CCA certificates.
        self.register_policy(
            SourcePolicy(
                name="EGAZETTE",
                domain="egazette.gov.in",
                allowed_domains=["egazette.gov.in"],
                permitted_content_types=["text/html", "application/pdf"],
                storage_permission=StoragePermission.FULL_DOCUMENT_ALLOWED,
                rate_limit_delay_seconds=1.0,
                max_crawl_depth=3,
                max_pages=30,
                requires_ssl_override=True,  # Observed CCA India custom certificate chain
                attribution_requirement="Directorate of Printing, Gazette of India",
            )
        )
