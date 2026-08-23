"""
kshiraj/ingestion/tests/test_policy.py

Unit tests for source compliance and policy evaluation.
"""

from __future__ import annotations

import pytest

from kshiraj.ingestion.policy import (
    ComplianceDecision,
    PolicyEvaluator,
    SourcePolicy,
    StoragePermission,
)


class TestPolicyEvaluator:

    def test_default_policies_registered(self):
        evaluator = PolicyEvaluator()
        bis_pol = evaluator.get_policy_for_url("https://services.bis.gov.in/standards")
        assert bis_pol is not None
        assert bis_pol.name == "BIS"
        assert bis_pol.storage_permission == StoragePermission.METADATA_AND_EXCERPTS_ONLY

        cppp_pol = evaluator.get_policy_for_url("https://eprocure.gov.in/eprocure/app")
        assert cppp_pol is not None
        assert cppp_pol.name == "CPPP"
        assert cppp_pol.storage_permission == StoragePermission.FULL_DOCUMENT_ALLOWED

    def test_evaluate_url_allowed_vs_restricted(self):
        evaluator = PolicyEvaluator()

        # Permitted government portal
        assert evaluator.evaluate_url("https://bis.gov.in/standards/list") == ComplianceDecision.ALLOWED
        assert evaluator.evaluate_url("https://eprocure.gov.in/tenders/view") == ComplianceDecision.ALLOWED

        # WAF blocked source
        assert evaluator.evaluate_url("https://dpiit.gov.in/quality-control-orders") == ComplianceDecision.SOURCE_BLOCKED

        # Non-registered / non-gov domain requires permission
        assert evaluator.evaluate_url("https://commercial-scraper-target.com/data") == ComplianceDecision.PERMISSION_REQUIRED

    def test_content_type_evaluation(self):
        evaluator = PolicyEvaluator()
        bis_pol = evaluator.get_policy_for_url("https://bis.gov.in")

        assert evaluator.evaluate_content_type("text/html; charset=utf-8", bis_pol) is True
        assert evaluator.evaluate_content_type("application/pdf", bis_pol) is True
        assert evaluator.evaluate_content_type("video/mp4", bis_pol) is False

    def test_custom_policy_registration(self):
        evaluator = PolicyEvaluator()
        custom = SourcePolicy(
            name="GE_M",
            domain="gem.gov.in",
            allowed_domains=["gem.gov.in"],
            storage_permission=StoragePermission.FULL_DOCUMENT_ALLOWED,
        )
        evaluator.register_policy(custom)

        assert evaluator.evaluate_url("https://gem.gov.in/catalogue") == ComplianceDecision.ALLOWED
