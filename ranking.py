"""
Relevance ranking for procurement -> Indian Standard retrieval.

Keeps the existing MiniLM + FAISS approach and adds deterministic
metadata signals on top of the FAISS semantic distance.

No legal applicability is inferred here. The score is a ranking signal.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "on",
    "with", "from", "by", "as", "is", "are", "be", "must", "shall",
    "required", "requirement", "product", "material", "supply",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _semantic_score(distance: float) -> float:
    # Existing FAISS uses IndexFlatL2. This converts lower-is-better
    # L2 distance into a bounded higher-is-better ranking signal.
    return 1.0 / (1.0 + max(float(distance), 0.0))


def _keyword_overlap(query: str, standard: Dict[str, Any]) -> float:
    query_tokens = _tokens(query)
    if not query_tokens:
        return 0.0

    searchable = " ".join(
        [
            str(standard.get("title") or ""),
            str(standard.get("scope") or ""),
            str(standard.get("scope_summary") or ""),
            " ".join(map(str, standard.get("keywords") or [])),
            " ".join(map(str, standard.get("product_categories") or [])),
        ]
    )

    standard_tokens = _tokens(searchable)
    if not standard_tokens:
        return 0.0

    return len(query_tokens & standard_tokens) / len(query_tokens)


def _category_signal(query: str, standard: Dict[str, Any]) -> float:
    q = (query or "").lower()
    categories = [
        str(x).lower()
        for x in (standard.get("product_categories") or [])
    ]
    keywords = [
        str(x).lower()
        for x in (standard.get("keywords") or [])
    ]

    if any(term and term in q for term in categories + keywords):
        return 1.0

    # Small domain hints for the MVP; this is not a legal rule.
    lighting_terms = {"led", "luminaire", "street", "road", "lighting", "lamp"}
    q_tokens = _tokens(query)
    if q_tokens & lighting_terms:
        text = " ".join(categories + keywords + [
            str(standard.get("title") or ""),
            str(standard.get("scope_summary") or ""),
        ])
        if any(term in text for term in lighting_terms):
            return 0.8

    return 0.0


def _completeness_signal(standard: Dict[str, Any]) -> float:
    checks = [
        bool(standard.get("scope")),
        bool(standard.get("normative_references")),
        bool(standard.get("related_standards")),
        bool(standard.get("test_methods")),
        bool(standard.get("version")),
        bool(standard.get("source")),
    ]
    return sum(checks) / len(checks)


def score_result(query: str, result: Dict[str, Any]) -> Dict[str, Any]:
    standard = result.get("_standard", result)

    semantic = _semantic_score(result.get("distance", 0.0))
    keyword = _keyword_overlap(query, standard)
    category = _category_signal(query, standard)
    completeness = _completeness_signal(standard)

    # Semantic retrieval remains the dominant signal.
    final_score = (
        0.65 * semantic
        + 0.15 * keyword
        + 0.10 * category
        + 0.10 * completeness
    )

    result["ranking"] = {
        "semantic_score": round(semantic, 6),
        "keyword_overlap": round(keyword, 6),
        "category_signal": round(category, 6),
        "metadata_completeness": round(completeness, 6),
        "final_relevance_score": round(final_score, 6),
    }
    result["relevance_score"] = round(final_score, 6)

    return result


def rank_results(
    results: List[Dict[str, Any]],
    query: str = "",
) -> List[Dict[str, Any]]:
    scored = [score_result(query, r) for r in results]
    return sorted(
        scored,
        key=lambda x: x.get("relevance_score", 0.0),
        reverse=True,
    )
