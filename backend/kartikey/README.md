# kartikey/

**Owner: Kartikey**

## Responsibilities

| Package | What it does |
|---|---|
| `api/` | FastAPI app: all routes, middleware, request/response shaping |
| `orchestration/` | Analysis pipeline state machine + async task dispatch |
| `document_processing/` | Validate, store, and extract text from uploaded PDFs/DOCX |
| `analysis/` | Buyer-side reasoning: compliance rules, evidence assembly, final Finding |

## What Kartikey does NOT own

- External source fetching → `kshiraj/source_adapters/`
- Standards/evidence retrieval → `kshiraj/knowledge/`
- AI/ML integration → `kshiraj/aiml_client/`
- Version checking / cross-ref extraction → `kshiraj/enrichment/`
- Database schema / migrations → `database/` (shared)

## Boundary: document_processing vs source_adapters

```
kshiraj/source_adapters   →   raw document / raw data
                                       │
kartikey/document_processing   ←───────┘
                                       │
                               extracted + normalized Document
                                       │
                               shared models → database
```

`extractor.py` must NOT reach out to external sources.
`bis_adapter.py` must NOT do PDF extraction or embeddings.

## Boundary: analysis vs enrichment

```
kshiraj/enrichment     →   version info + cross-references (knowledge enrichment)
                                       │
kartikey/analysis      ←───────────────┘
                                       │
           compliance rules + evidence assembly → final Finding
```

Kartikey's `analysis/` answers: "Should this requirement exist?"
Kshiraj's `enrichment/` answers: "What is the current version / what are the cross-references?"
