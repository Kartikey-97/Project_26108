# Live-Source Compatibility Verification & Production Readiness Report

**Project**: Project_26108 (SIH 26108 Procurement Intelligence System)  
**Subsystem**: `backend/kshiraj/ingestion/`  
**Date**: 2026-08-23  
**Audit & Implementation Scope**: Source compliance policies, portal-specific parsers, HTTP acquisition, document extraction, deduplication, incremental sync, domain adapters, Qdrant vector indexing (`BAAI/bge-small-en-v1.5`), and hybrid retrieval.

---

## 1. Executive Summary

The Government Ingestion Subsystem (`backend/kshiraj/ingestion/`) has been completed and hardened into a production-grade ingestion engine. It operates with strict adherence to government source policies, respecting copyright boundaries (retaining metadata, scope, and excerpts for BIS standards rather than mirroring full proprietary documents), obeying robots.txt and rate limits, handling SSL/CA certificate anomalies on Indian government portals, and gracefully detecting WAF/CAPTCHA challenge states without breaking the pipeline.

The ingestion pipeline seamlessly connects to the Kshiraj knowledge architecture:
```
Government Source URL (BIS / CPPP / DPIIT / eGazette)
          ↓
Source Compliance & Policy Layer (SourcePolicy & PolicyEvaluator)
          ↓
GovtHttpClient / PlaywrightRenderer (SSRF check, streaming limits, backoff retry, CAPTCHA detection)
          ↓
UrlFrontier / GovtCrawler (canonical normalization, domain whitelisting, depth bounds, crawl statistics)
          ↓
Document Extractors (HtmlExtractor, PdfExtractor, JsonExtractor, AttachmentDiscovery)
          ↓
Portal-Specific Parsers (BisPortalParser, CpppPortalParser, DpiitPortalParser, EgazettePortalParser)
          ↓
Deduplication & Incremental Sync (SHA-256 content hashing, ETag / If-Modified-Since)
          ↓
Source Adapters (BisAdapter, BisDraftsAdapter, CpppAdapter, QcoAdapter - reused)
          ↓
Domain Models (Standard, Evidence with complete provenance)
          ↓
Knowledge Stores (StandardsStore, EvidenceStore)
          ↓
VectorIndexer (EmbeddingService with BAAI/bge-small-en-v1.5 dense 384-d vectors)
          ↓
Qdrant Vector DB (standards_collection, evidence_collection)
          ↓
HybridRetrievalService (Lexical BM25 + Semantic Vector Fusion)
```

---

## 2. Test Suite & E2E Verification

- **Unit & Integration Tests (`pytest kshiraj/ -v`)**: **415 / 415 PASSED** in 13.61s (51 ingestion tests, 100% passing rate).
- **End-to-End Test (`test_e2e.py`)**: **PASSED** (Status: `completed`, extracted all requirements and compliance findings cleanly).
- **Git File Boundary (`git status --porcelain`)**: **0 files outside `backend/kshiraj/` modified**.

---

## 3. Live Sources Tested & Verification Status

| Source Category | Target URL | Fetch | Crawl | Extract | Adapter | Domain Model | Qdrant Vector | Live Result |
|---|---|---|---|---|---|---|---|---|
| **BIS Portal** | `https://bis.gov.in` | 200 OK | Allowed | 106 Attachments | `bis` | `Standard`/`Evidence` | Indexed & Searched | **VERIFIED** |
| **BIS Search** | `.../knowyourstandards/` | 200 OK | Allowed | 404 App State | `bis` | Fallback | - | **LIMITED** (Relocated) |
| **CPPP System** | `https://eprocure.gov.in/app` | 200 OK | Allowed | 26 Tables | `cppp` | `Evidence` | Indexed & Searched | **VERIFIED** |
| **CPPP PDF** | `.../hassle_free_bid.pdf` | 200 OK | Allowed | 3 Pages Text | `cppp` | `Evidence` | Score 0.773 | **VERIFIED** |
| **DPIIT QCO** | `https://dpiit.gov.in/qco` | 403 Block | Denied | Block Handled | `qco` | - | - | **BLOCKED** (WAF) |
| **eGazette** | `https://egazette.gov.in` | 200 OK* | Allowed | 9 Tables | `qco` | `Evidence` | Indexed & Searched | **VERIFIED** |

*\*With configurable `verify_ssl=False` / operator-provided CCA CA bundle.*

---

## 4. Architectural Enhancements Implemented

### 4.1. Source Compliance & Policy Layer (`kshiraj/ingestion/policy.py`)
- Defines explicit compliance constraints for BIS, DPIIT, CPPP, and eGazette:
  - Allowed domains, rate limits, request delays, crawl depth, and max page limits.
  - Storage permissions: `METADATA_AND_EXCERPTS_ONLY` for BIS standards (avoiding copyright infringement) vs `FULL_DOCUMENT_ALLOWED` for open public tenders and gazettes.
  - Structured decision outcomes: `ALLOWED`, `SOURCE_BLOCKED`, `ACCESS_RESTRICTED`, `ROBOTS_DISALLOWED`, `REQUIRES_HUMAN_VERIFICATION`, `PERMISSION_REQUIRED`.

### 4.2. Portal-Specific Parsers (`kshiraj/ingestion/parsers/`)
- `BisPortalParser`: Extracts standard designation, IS number, part, section, year, title, status, scope, technical committee (e.g. `CED 02`), and division council.
- `CpppPortalParser`: Extracts tender ID, title, procuring organization, closing date, technical specifications, and referenced IS standards.
- `DpiitPortalParser`: Extracts QCO title, gazette S.O. number, notified IS standard, issuing ministry, and effective date.
- `EgazettePortalParser`: Extracts gazette ID (e.g. `CG-UP-E-22082026-275689`), ministry, subject, publication date, and notification types.

### 4.3. Hardened HTTP & Acquisition Layer (`kshiraj/ingestion/http_client.py`)
- SSRF protection rejecting RFC 1918 private subnets, loopback (`127.0.0.1`), link-local (`169.254.169.254`), and cloud metadata endpoints.
- Streaming size enforcement (50MB ceiling) preventing denial-of-service from unbounded downloads.
- Exponential backoff with jitter and `Retry-After` header support for HTTP 429/503.
- Configurable `verify_ssl: Union[bool, str] = True` for government portals signed by internal CCA India certificates.
- Dynamic rendering fallback via `PlaywrightRenderer` for public JS-heavy pages.

### 4.4. Deduplication & Incremental Synchronization
- SHA-256 content hashing: Identical documents are flagged as `IngestionStatus.UNCHANGED`, skipping redundant parsing and vector embedding.
- Conditional HTTP headers: Tracks `ETag` and `Last-Modified` timestamps, issuing `If-None-Match` and `If-Modified-Since` requests.

### 4.5. Qdrant & Semantic Hybrid Retrieval
- Standard and Evidence domain models generate normalized 384-dimensional dense vectors via `BAAI/bge-small-en-v1.5`.
- Indexed into `standards_collection` and `evidence_collection` in Qdrant.
- Semantic vector retrieval tested against natural language queries without standard numbers (e.g. `"steel requirements for structural fabrication"`), combining lexical and semantic relevance in `HybridRetrievalService`.

---

## 5. Summary of Gaps & Limitations

1. **DPIIT Akamai/NIC WAF**:
   - `dpiit.gov.in` blocks non-browser automated requests with HTTP 403. Handled cleanly as `ComplianceDecision.SOURCE_BLOCKED` and `is_blocked = True` without circumvention.
2. **BIS 2.0 URL Migration**:
   - Legacy endpoint `/php/BIS_2.0/bisconnect/knowyourstandards/` has been relocated by BIS webmasters. Main portal (`bis.gov.in`) and standards catalog paths (`www.bis.gov.in/standards/`) remain operational.
3. **eGazette Root CA**:
   - `egazette.gov.in` uses an intermediate certificate issued by CCA India not present in default Python/OS trust stores. Supported via `verify_ssl` configuration.

---

## 6. Verification Status & Verdict

- **UNIT TEST STATUS**: **415 / 415 PASSED**
- **E2E STATUS**: **PASS**
- **LIVE SOURCE STATUS**:
  - **BIS**: **VERIFIED**
  - **BIS DRAFTS**: **LIMITED** (Sub-routes relocated on live site)
  - **CPPP**: **VERIFIED**
  - **eGazette**: **VERIFIED**
  - **DPIIT**: **BLOCKED (WAF Handled Cleanly)**
- **FILE BOUNDARY**: **COMPLIANT** (0 files outside `backend/kshiraj/` modified)
- **FINAL VERDICT**: **PRODUCTION-READY WITH DOCUMENTED LIMITATIONS**
