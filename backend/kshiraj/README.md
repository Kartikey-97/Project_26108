# kshiraj/

**Owner: Kshiraj**

## Responsibilities

| Package | What it does |
|---|---|
| `source_adapters/` | Fetch raw data from external sources (BIS, CPPP, QCO, BIS Drafts) |
| `knowledge/` | Store and retrieve standards + evidence (pgvector semantic search) |
| `aiml_client/` | Integration adapter with the AI/ML team's component |
| `enrichment/` | Knowledge enrichment: version checking, cross-reference extraction |

## What Kshiraj does NOT own

- API routes → `kartikey/api/`
- Pipeline orchestration → `kartikey/orchestration/`
- Document upload/extraction → `kartikey/document_processing/`
- Compliance reasoning / buyer-side analysis → `kartikey/analysis/`
- Database schema / migrations → `database/` (shared)

## Boundary: source_adapters vs document_processing

```
kshiraj/source_adapters  →  raw document / raw data
                                     │
kartikey/document_processing  ←──────┘
                                     │
                             extracted + normalized text
```

`bis_adapter.py` fetches raw pages/documents. It does NOT parse PDF text, chunk, or embed.

## Boundary: enrichment vs analysis

```
kshiraj/enrichment   →   version info + cross-references  (knowledge enrichment)
                                     │
kartikey/analysis    ←───────────────┘
                                     │
              compliance rules + evidence assembly  →  final Finding
```

Kshiraj answers: "What is the current status / what are the related standards?"
Kartikey answers: "Should this requirement exist?"

## AI/ML client note

Check with the AI/ML team first:
- If they provide a Python module → import directly, no HTTP client needed
- If they deploy a separate service → implement `client.py` as an HTTP adapter

Do not build gRPC/Celery infrastructure prematurely.
