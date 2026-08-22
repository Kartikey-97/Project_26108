# Backend — SIH 26108

AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications.

---

## Developer Split

| Area | Owner |
|---|---|
| `kartikey/` | Kartikey — API, orchestration, document processing, buyer-side analysis |
| `kshiraj/` | Kshiraj — source adapters, knowledge/retrieval, AI/ML client, enrichment |
| `database/` | **Shared** — both touch this; agree on schema before building stores |
| `shared/` | **Shared** — models, contracts, utils; agree before building anything |

---

## Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL + pgvector
- **ORM:** SQLAlchemy + Alembic (migrations)
- **Background tasks:** FastAPI `BackgroundTasks` (no Celery for MVP)
- **AI/ML integration:** Python module initially (HTTP service if ML team deploys separately — TBD)
- **Auth:** None for MVP

---

## Data Flow

```
EXTERNAL SOURCES              USER PDF/TEXT
       │                            │
  KSHIRAJ                      KARTIKEY
source_adapters          document_processing
  (fetch raw)             (extract + normalize)
       │                            │
       └────────────┬───────────────┘
                    ↓
             SHARED MODELS
                    │
                    ↓
                DATABASE
           (PostgreSQL + pgvector)
                    │
                    ↓
          KSHIRAJ RETRIEVAL
       (knowledge/retrieval_service)
                    │
            relevant standards
                    │
                    ↓
          KARTIKEY ORCHESTRATION
           (pipeline + task_runner)
                    │
                    ↓
             AI/ML MODULE
          (kshiraj/aiml_client)
                    │
           structured findings
                    ↓
          KSHIRAJ ENRICHMENT
      (version_checker + crossref)
                    │
           enriched knowledge
                    ↓
          KARTIKEY ANALYSIS
      (compliance + findings assembly)
                    │
           final Finding objects
                    ↓
          KARTIKEY API RESPONSE
                    │
                    ↓
                FRONTEND
```

---

## Analysis Status Lifecycle

```
queued → extracting → retrieving → analyzing → enriching → completed
                                                          ↘ partially_completed
                                                          ↘ failed
```

---

## API Shape (agree with frontend before deep build)

```
POST   /api/v1/analyses              create analysis (text or document_id)
GET    /api/v1/analyses/{id}         poll status + get results
POST   /api/v1/documents/upload      upload tender document
GET    /api/v1/standards/{id}        get a specific standard
GET    /api/v1/standards/search      search standards by query
GET    /api/v1/analyses/{id}/report  export report
GET    /health                        health check
```

---

## AI/ML Contract (agree with ML team before deep build)

**Backend → AI/ML:**
```json
{
  "analysis_id": "...",
  "extracted_text": "...",
  "requirements": [{ "id", "text", "category" }],
  "retrieved_standards": [{ "id", "title", "text_excerpt", "version", "source" }]
}
```

**AI/ML → Backend:**
```json
{
  "analysis_id": "...",
  "findings": [{
    "finding_id": "...",
    "requirement_id": "...",
    "verdict": "justified|outdated|incorrect_scope|ambiguous|...",
    "reason": "...",
    "evidence_ids": ["..."],
    "applicable_standard_ids": ["..."],
    "confidence": 0.87,
    "recommended_action": "..."
  }]
}
```

---

## Local Dev Setup

```bash
# Create virtualenv
python -m venv .venv
source .venv/bin/activate

# Install dependencies (once requirements.txt exists)
pip install -r requirements.txt

# Run
uvicorn kartikey.api.main:app --reload
```

---

## MVP Target

**LED street lighting tender → full pipeline → structured response to frontend.**

Once this vertical slice works end-to-end, expand to additional procurement categories.
