"""
kshiraj/aiml_client/test_client.py

Comprehensive unit tests for the Kshiraj AI/ML client boundary.

Tests cover:
  - adapter: zero candidates, one candidate, duplicate standards, deterministic ordering, text_excerpt handling
  - mock execution: valid response, analysis_id preservation, requirement_id preservation
  - error handling: malformed request, HTTP errors, timeouts, invalid payload
  - HTTP execution: HTTP 200 success, HTTP 500 error, connection error, timeout
  - configuration: mock vs HTTP selection
  - async concurrency
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from shared.config import Settings, settings
from shared.contracts import AimlFinding, AimlRequest, AimlResponse
from shared.models import Evidence, EvidenceSourceType, Requirement, Standard, StandardStatus
from kshiraj.aiml_client.client import AimlClient, adapt_retrieved_standards
from kshiraj.aiml_client.schemas import (
    AimlClientError,
    AimlResponseError,
    AimlTimeoutError,
)
from kshiraj.knowledge.retrieval_service import (
    CandidateStandard,
    RetrievalQuery,
    RetrievalResult,
)


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def sample_standard_1() -> Standard:
    return Standard(
        id="std-101",
        is_number="IS 10322",
        title="Luminaires - General Requirements",
        scope="Covers safety and specification requirements for luminaires.",
        status=StandardStatus.ACTIVE,
        relevance_score=9.5,
    )


@pytest.fixture
def sample_standard_2() -> Standard:
    return Standard(
        id="std-102",
        is_number="IS 694",
        title="Polyvinyl Chloride Insulated Cables",
        scope="Covers PVC insulated cables for working voltages up to 1100V.",
        status=StandardStatus.ACTIVE,
        relevance_score=8.0,
    )


@pytest.fixture
def sample_evidence() -> Evidence:
    return Evidence(
        id="ev-201",
        source_type=EvidenceSourceType.BIS_STANDARD,
        source_name="IS 10322 Clause 4.1",
        excerpt="Luminaires shall be constructed so that they withstand normal use.",
    )


@pytest.fixture
def sample_requirement_1() -> Requirement:
    return Requirement(
        id="req-1",
        analysis_id="analysis-100",
        text="Luminaires shall comply with IS 10322.",
        is_reference="IS 10322",
    )


@pytest.fixture
def sample_requirement_2() -> Requirement:
    return Requirement(
        id="req-2",
        analysis_id="analysis-100",
        text="Cables shall be copper conductor PVC insulated.",
        is_reference="IS 694",
    )


@pytest.fixture
def sample_aiml_request(sample_requirement_1, sample_requirement_2, sample_standard_1, sample_standard_2) -> AimlRequest:
    return AimlRequest(
        analysis_id="analysis-100",
        extracted_text="Sample procurement text for LED luminaires and cabling.",
        requirements=[sample_requirement_1, sample_requirement_2],
        retrieved_standards=[sample_standard_1, sample_standard_2],
    )


# ===========================================================================
# 1. Adapter tests
# ===========================================================================

class TestAdapter:
    """Tests for adapt_retrieved_standards."""

    def test_adapter_zero_candidates_none(self):
        result = adapt_retrieved_standards(None)
        assert result == []

    def test_adapter_zero_candidates_empty_list(self):
        result = adapt_retrieved_standards([])
        assert result == []

    def test_adapter_zero_candidates_empty_result(self):
        query = RetrievalQuery(query_text="nonexistent")
        ret_result = RetrievalResult(query=query, candidates=[], total_candidates=0)
        result = adapt_retrieved_standards(ret_result)
        assert result == []

    def test_adapter_one_candidate(self, sample_standard_1):
        cand = CandidateStandard(standard=sample_standard_1, score=9.5)
        result = adapt_retrieved_standards([cand])
        assert len(result) == 1
        assert result[0].id == "std-101"
        assert result[0].is_number == "IS 10322"
        assert result[0].relevance_score == 9.5
        assert result[0].text_excerpt == "Covers safety and specification requirements for luminaires."

    def test_adapter_duplicate_standards(self, sample_standard_1):
        cand1 = CandidateStandard(standard=sample_standard_1, score=9.5)
        cand2 = CandidateStandard(standard=sample_standard_1, score=9.5)
        result = adapt_retrieved_standards([cand1, cand2])
        assert len(result) == 1
        assert result[0].id == "std-101"

    def test_adapter_deterministic_ordering(self, sample_standard_1, sample_standard_2):
        cand1 = CandidateStandard(standard=sample_standard_1, score=9.5)
        cand2 = CandidateStandard(standard=sample_standard_2, score=8.0)

        # Test order 1
        res1 = adapt_retrieved_standards([cand1, cand2])
        assert [s.id for s in res1] == ["std-101", "std-102"]

        # Test order 2
        res2 = adapt_retrieved_standards([cand2, cand1])
        assert [s.id for s in res2] == ["std-102", "std-101"]

    def test_adapter_text_excerpt_handling_existing_excerpt(self):
        std = Standard(
            id="std-3",
            is_number="IS 1000",
            title="Title",
            text_excerpt="Pre-existing explicit text excerpt",
            scope="Scope text",
        )
        cand = CandidateStandard(standard=std, score=5.0)
        res = adapt_retrieved_standards([cand])
        assert res[0].text_excerpt == "Pre-existing explicit text excerpt"

    def test_adapter_text_excerpt_handling_from_evidence(self, sample_evidence):
        std = Standard(
            id="std-4",
            is_number="IS 2000",
            title="Title without explicit excerpt",
            scope="Scope text",
        )
        cand = CandidateStandard(standard=std, score=5.0, evidence=[sample_evidence])
        res = adapt_retrieved_standards([cand])
        assert res[0].text_excerpt == "Luminaires shall be constructed so that they withstand normal use."

    def test_adapter_text_excerpt_handling_from_scope(self):
        std = Standard(
            id="std-5",
            is_number="IS 3000",
            title="Title",
            scope="Scope text used as fallback excerpt",
        )
        cand = CandidateStandard(standard=std, score=5.0)
        res = adapt_retrieved_standards([cand])
        assert res[0].text_excerpt == "Scope text used as fallback excerpt"

    def test_adapter_text_excerpt_handling_none(self):
        std = Standard(
            id="std-6",
            is_number="IS 4000",
            title="Title",
            scope=None,
        )
        cand = CandidateStandard(standard=std, score=5.0)
        res = adapt_retrieved_standards([cand])
        assert res[0].text_excerpt is None


# ===========================================================================
# 2. Mock Execution tests
# ===========================================================================

class TestMockExecution:
    """Tests for AimlClient mock mode execution."""

    @pytest.mark.asyncio
    async def test_valid_mock_response(self, sample_aiml_request):
        client = AimlClient(force_mock=True)
        assert client.is_mock is True

        response = await client.run_analysis(sample_aiml_request)
        assert isinstance(response, AimlResponse)
        assert response.analysis_id == "analysis-100"
        assert len(response.findings) == 2
        assert response.extraction_metadata["execution_mode"] == "mock"

    @pytest.mark.asyncio
    async def test_mock_preserves_analysis_id(self, sample_aiml_request):
        client = AimlClient(force_mock=True)
        response = await client.run_analysis(sample_aiml_request)
        assert response.analysis_id == sample_aiml_request.analysis_id

    @pytest.mark.asyncio
    async def test_mock_preserves_requirement_ids(self, sample_aiml_request):
        client = AimlClient(force_mock=True)
        response = await client.run_analysis(sample_aiml_request)
        req_ids = [f.requirement_id for f in response.findings]
        assert req_ids == ["req-1", "req-2"]

    @pytest.mark.asyncio
    async def test_mock_finding_fields(self, sample_aiml_request):
        client = AimlClient(force_mock=True)
        response = await client.run_analysis(sample_aiml_request)
        f1 = response.findings[0]
        assert f1.finding_id.startswith("mock-finding-")
        assert f1.requirement_id == "req-1"
        assert f1.applicable_standard_ids == ["std-101"]
        assert f1.verdict == "justified"
        assert f1.confidence == 0.90


# ===========================================================================
# 3. Client configuration & validation tests
# ===========================================================================

class TestClientConfigAndValidation:
    """Tests for configuration selection and request validation."""

    def test_client_config_defaults_to_settings(self):
        client = AimlClient()
        if settings.aiml_service_url:
            assert client.is_mock is False
        else:
            assert client.is_mock is True

    def test_client_config_explicit_url(self):
        client = AimlClient(service_url="http://localhost:9000/analyze")
        assert client.is_mock is False
        assert client.service_url == "http://localhost:9000/analyze"

    def test_client_config_force_mock(self):
        client = AimlClient(service_url="http://localhost:9000/analyze", force_mock=True)
        assert client.is_mock is True

    @pytest.mark.asyncio
    async def test_malformed_request_raises_client_error(self):
        client = AimlClient(force_mock=True)
        with pytest.raises(AimlClientError) as exc_info:
            await client.run_analysis("not_an_aiml_request")  # type: ignore[arg-type]
        assert exc_info.value.code == "INVALID_REQUEST"


# ===========================================================================
# 4. HTTP Execution tests
# ===========================================================================

class TestHttpExecution:
    """Tests for AimlClient HTTP mode execution using mocked httpx transport."""

    @pytest.mark.asyncio
    async def test_http_success(self, sample_aiml_request):
        url = "http://aiml-service.internal/api/v1/analyze"
        mock_response_payload = {
            "analysis_id": "analysis-100",
            "findings": [
                {
                    "finding_id": "find-1",
                    "requirement_id": "req-1",
                    "verdict": "justified",
                    "reason": "Specification matches IS 10322.",
                    "applicable_standard_ids": ["std-101"],
                    "confidence": 0.95,
                }
            ],
            "extraction_metadata": {"model": "gemini-1.5-pro"},
        }

        mock_httpx_response = httpx.Response(
            status_code=200,
            json=mock_response_payload,
            request=httpx.Request("POST", url),
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response

            client = AimlClient(service_url=url)
            assert client.is_mock is False

            response = await client.run_analysis(sample_aiml_request)
            assert isinstance(response, AimlResponse)
            assert response.analysis_id == "analysis-100"
            assert len(response.findings) == 1
            assert response.findings[0].verdict == "justified"
            assert response.extraction_metadata["model"] == "gemini-1.5-pro"

    @pytest.mark.asyncio
    async def test_http_error_500(self, sample_aiml_request):
        url = "http://aiml-service.internal/api/v1/analyze"
        mock_httpx_response = httpx.Response(
            status_code=500,
            text="Internal Server Error in ML Model execution",
            request=httpx.Request("POST", url),
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response

            client = AimlClient(service_url=url)
            with pytest.raises(AimlResponseError) as exc_info:
                await client.run_analysis(sample_aiml_request)

            assert exc_info.value.code == "HTTP_500"
            assert "500" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_http_timeout(self, sample_aiml_request):
        url = "http://aiml-service.internal/api/v1/analyze"
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Read timed out")

            client = AimlClient(service_url=url, timeout=5.0)
            with pytest.raises(AimlTimeoutError) as exc_info:
                await client.run_analysis(sample_aiml_request)

            assert exc_info.value.code == "AIML_TIMEOUT"

    @pytest.mark.asyncio
    async def test_http_connection_error(self, sample_aiml_request):
        url = "http://aiml-service.internal/api/v1/analyze"
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection refused")

            client = AimlClient(service_url=url)
            with pytest.raises(AimlResponseError) as exc_info:
                await client.run_analysis(sample_aiml_request)

            assert exc_info.value.code == "CONNECTION_ERROR"

    @pytest.mark.asyncio
    async def test_http_invalid_payload(self, sample_aiml_request):
        url = "http://aiml-service.internal/api/v1/analyze"
        # Missing required fields like 'findings'
        invalid_payload = {
            "analysis_id": "analysis-100",
            "invalid_field": True,
        }
        mock_httpx_response = httpx.Response(
            status_code=200,
            json=invalid_payload,
            request=httpx.Request("POST", url),
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_httpx_response

            client = AimlClient(service_url=url)
            with pytest.raises(AimlResponseError) as exc_info:
                await client.run_analysis(sample_aiml_request)

            assert exc_info.value.code == "INVALID_RESPONSE_PAYLOAD"


# ===========================================================================
# 5. Async Concurrency tests
# ===========================================================================

class TestAsyncConcurrency:
    """Test concurrent async analysis requests."""

    @pytest.mark.asyncio
    async def test_concurrent_mock_calls(self, sample_aiml_request):
        client = AimlClient(force_mock=True)

        req1 = sample_aiml_request.model_copy(update={"analysis_id": "job-1"})
        req2 = sample_aiml_request.model_copy(update={"analysis_id": "job-2"})
        req3 = sample_aiml_request.model_copy(update={"analysis_id": "job-3"})

        results = await asyncio.gather(
            client.run_analysis(req1),
            client.run_analysis(req2),
            client.run_analysis(req3),
        )

        assert len(results) == 3
        assert [r.analysis_id for r in results] == ["job-1", "job-2", "job-3"]
