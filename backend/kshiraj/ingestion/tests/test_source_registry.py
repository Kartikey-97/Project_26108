"""
kshiraj/ingestion/tests/test_source_registry.py

Unit tests for SourceRegistry and GovernmentSourceConfig.
"""

from __future__ import annotations

import pytest

from shared.models import EvidenceSourceType
from kshiraj.ingestion.source_registry import GovernmentSourceConfig, SourceRegistry


class TestSourceRegistry:

    def test_default_sources_registered(self):
        registry = SourceRegistry()
        sources = registry.list_sources()

        assert len(sources) >= 4
        source_names = {s.name for s in sources}
        assert "BIS_CATALOG" in source_names
        assert "BIS_DRAFTS" in source_names
        assert "CPPP_TENDERS" in source_names
        assert "QCO_NOTIFICATIONS" in source_names

    def test_match_source_by_url(self):
        registry = SourceRegistry()

        bis_source = registry.match_source_by_url("https://services.bis.gov.in/php/standards")
        assert bis_source is not None
        assert bis_source.adapter_name == "bis"
        assert bis_source.source_type == EvidenceSourceType.BIS_STANDARD

        cppp_source = registry.match_source_by_url("https://eprocure.gov.in/eprocure/app?page=tender")
        assert cppp_source is not None
        assert cppp_source.adapter_name == "cppp"
        assert cppp_source.source_type == EvidenceSourceType.CPPP_TENDER

        unknown = registry.match_source_by_url("https://example.com/other")
        assert unknown is None

    def test_register_custom_source(self):
        registry = SourceRegistry()
        custom = GovernmentSourceConfig(
            name="GE_M_PORTAL",
            source_type=EvidenceSourceType.GEM_CATALOG,
            base_urls=["https://gem.gov.in/"],
            allowed_domains=["gem.gov.in"],
            adapter_name="gem",
        )
        registry.register_source(custom)

        assert registry.get_source("GE_M_PORTAL") == custom
        assert registry.match_source_by_url("https://gem.gov.in/catalog/item1") == custom
