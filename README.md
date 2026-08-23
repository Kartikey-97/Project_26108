# Six immediate intelligence features

These files implement the six capabilities requested without changing
the core MiniLM + FAISS approach:

1. Proper relevance/ranking -> ranking.py
2. Evidence/provenance -> evidence.py
5. Requirement-level analysis -> requirement_analysis.py
6. Issue detection -> issue_detector.py
7. Confidence/uncertainty -> confidence.py
10. End-to-end evidence-grounded result -> recommender.py

Place these files under the project's `src/` package, replacing the
same-named modules where applicable.

Important:
- The existing `embedding.py` and `search.py` remain the retrieval foundation.
- No fine-tuning is required for these changes.
- No standards are invented.
- Unverified knowledge-base fields remain unverified.
- Evidence is only emitted from fields actually present in the record.
- High-severity or unverified findings are flagged for human review.

The `recommender.py` now returns a structured result containing:
requirements, analyses, recommendations, ranking, evidence, issues,
confidence, alerts, and a human-review flag.
