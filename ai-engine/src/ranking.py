"""
ai-engine/src/ranking.py

Reranks hybrid retrieval candidates using a multi-signal scoring formula.

Key improvements:
  - semantic_score is now a proper cosine similarity (after embedding.py fix)
  - relevance_score and confidence are separate concepts
  - evidence is a list of structured dicts, not field-name strings
  - IS number exact-match bonus: if tender cites IS XXXX, that standard gets boosted
  - Weights: 45% semantic + 20% BM25 (if available) + 20% product + 10% tech + 5% meta
"""

import logging

logger = logging.getLogger(__name__)


def rank_results(results: list[dict], query_understanding: dict) -> list[dict]:
    """
    Rerank a list of candidate standard dicts from the HybridRetriever.

    Each result dict is enriched with:
      - relevance_score    : float [0, 1]
      - semantic_score     : float [0, 1] — cosine similarity (now correct)
      - confidence         : str  — 'high' | 'medium' | 'low'
      - confidence_reasons : list[str]
      - reason             : str  — human-readable explanation
      - evidence           : list[dict] — structured evidence objects
      - rank               : int

    Parameters
    ----------
    results : list[dict]
        Candidate standards from HybridRetriever.search() or plain VectorStore.search().
    query_understanding : dict
        Parsed procurement requirements from query_understanding.parse_query().
    """
    product = query_understanding.get("product") or ""
    application = query_understanding.get("application") or ""
    domain = query_understanding.get("domain") or ""
    tech_reqs = query_understanding.get("technical_requirements") or []
    explicit_refs = query_understanding.get("explicit_standard_refs") or []
    cert_reqs = query_understanding.get("certification_requirements") or []

    for res in results:
        search_text = res.get("search_text", "").lower()
        title = res.get("title", "").lower()
        is_number = res.get("is_number", "")
        keywords = " ".join(res.get("keywords") or []).lower()
        combined = search_text + " " + title + " " + keywords

        # -------------------------------------------------------------------
        # Semantic similarity — now a real cosine score [0, 1]
        # (was broken `1 - dist/2` before the embedding fix)
        # -------------------------------------------------------------------
        semantic_score = float(res.get("semantic_score", 0.0))

        # BM25 lexical score — normalise to [0, 1] using a generous cap of 20
        bm25_raw = float(res.get("bm25_score", 0.0))
        bm25_score = min(bm25_raw / 20.0, 1.0) if bm25_raw > 0 else 0.0

        # -------------------------------------------------------------------
        # Product relevance [0, 1]
        # -------------------------------------------------------------------
        product_rel = 0.0
        product_evidence = None
        if product:
            if product.lower() in combined:
                product_rel = 1.0
                product_evidence = {
                    "source": "BIS catalog",
                    "document": is_number,
                    "field": "title/keywords",
                    "excerpt": title[:120],
                    "matched_term": product,
                }
            elif any(w in combined for w in product.lower().split() if len(w) > 3):
                product_rel = 0.6
                product_evidence = {
                    "source": "BIS catalog",
                    "document": is_number,
                    "field": "search_text",
                    "excerpt": title[:120],
                    "matched_term": f"partial match for '{product}'",
                }

        # -------------------------------------------------------------------
        # Application/domain relevance [0, 1]
        # -------------------------------------------------------------------
        app_rel = 0.0
        if application and application.lower() in combined:
            app_rel = 1.0
        elif domain and domain.lower() in combined:
            app_rel = 0.7

        # -------------------------------------------------------------------
        # Technical requirement coverage [0, 1]
        # -------------------------------------------------------------------
        tech_rel = 1.0  # don't penalise if none specified
        tech_evidence = []
        if tech_reqs:
            matched = 0
            for req in tech_reqs:
                param = req.get("parameter", "")
                value = req.get("value", "")
                # Check both parameter name and value in the standard text
                if param.lower() in combined or value.lower() in combined:
                    matched += 1
                    tech_evidence.append({
                        "source": "BIS catalog",
                        "document": is_number,
                        "field": "scope/search_text",
                        "excerpt": f"Standard text contains reference to '{param}'",
                        "matched_term": f"{param}={value}",
                    })
            tech_rel = matched / len(tech_reqs)

        # -------------------------------------------------------------------
        # Explicit IS reference match — strong signal [0 or 1]
        # -------------------------------------------------------------------
        ref_boost = 0.0
        ref_evidence = None
        is_norm = is_number.lower().replace(" ", "").replace(":", "")
        for ref in explicit_refs:
            ref_norm = ref.lower().replace(" ", "").replace(":", "")
            if ref_norm in is_norm or is_norm in ref_norm:
                ref_boost = 1.0
                ref_evidence = {
                    "source": "Tender specification",
                    "document": is_number,
                    "field": "explicit_citation",
                    "excerpt": f"Tender explicitly cites '{ref}'",
                    "matched_term": ref,
                }
                break

        # -------------------------------------------------------------------
        # Metadata confidence [0.5 or 1.0]
        # -------------------------------------------------------------------
        status_data = res.get("status") or {}
        version_data = res.get("version") or {}
        verified = (
            status_data.get("verified") is True
            or version_data.get("verification_status") == "verified"
        )
        meta_conf = 1.0 if verified else 0.5

        # -------------------------------------------------------------------
        # Final relevance score
        # If explicit IS ref matched → give it a 0.3 boost (capped at 1.0)
        # -------------------------------------------------------------------
        base_score = (
            0.40 * semantic_score
            + 0.15 * bm25_score
            + 0.20 * product_rel
            + 0.10 * app_rel
            + 0.10 * tech_rel
            + 0.05 * meta_conf
        )
        relevance_score = min(1.0, base_score + (0.3 * ref_boost))

        # -------------------------------------------------------------------
        # Confidence (separate from relevance — based on verifiability)
        # -------------------------------------------------------------------
        confidence_reasons = []
        if semantic_score > 0.7:
            confidence_reasons.append("strong semantic match")
        if bm25_score > 0.4:
            confidence_reasons.append("lexical keyword match")
        if product_rel == 1.0:
            confidence_reasons.append("product category matched exactly")
        if ref_boost == 1.0:
            confidence_reasons.append("standard explicitly cited in tender")
        if tech_rel > 0.5:
            confidence_reasons.append(f"{int(tech_rel*100)}% of technical parameters matched")
        if not verified:
            confidence_reasons.append("standard metadata not verified (manual check recommended)")

        if relevance_score > 0.72:
            confidence = "high"
        elif relevance_score > 0.45:
            confidence = "medium"
        else:
            confidence = "low"

        # -------------------------------------------------------------------
        # Human-readable reason
        # -------------------------------------------------------------------
        reason_parts = []
        if product_rel > 0:
            reason_parts.append(f"matches the required product category '{product or domain}'")
        if app_rel > 0:
            reason_parts.append(f"is applicable to '{application or domain}'")
        if tech_rel > 0 and tech_reqs:
            n = sum(1 for r in tech_reqs if r.get("parameter", "").lower() in combined or r.get("value", "").lower() in combined)
            reason_parts.append(f"covers {n}/{len(tech_reqs)} specified technical parameters")
        if ref_boost > 0:
            reason_parts.append("is explicitly cited in the tender specification")

        if not reason_parts:
            reason = "Recommended based on semantic similarity to the procurement requirement."
        else:
            reason = "The standard " + "; ".join(reason_parts) + "."

        # -------------------------------------------------------------------
        # Structured evidence objects
        # -------------------------------------------------------------------
        evidence = []
        if product_evidence:
            evidence.append(product_evidence)
        if ref_evidence:
            evidence.append(ref_evidence)
        evidence.extend(tech_evidence[:3])  # cap at 3 tech evidence items

        # Fallback if nothing matched
        if not evidence:
            evidence.append({
                "source": "BIS catalog",
                "document": is_number,
                "field": "semantic_similarity",
                "excerpt": title[:120],
                "matched_term": "vector similarity",
            })

        # Write back enriched fields
        res["semantic_score"] = round(semantic_score, 4)
        res["bm25_score"] = round(bm25_score, 4)
        res["relevance_score"] = round(relevance_score, 4)
        res["final_score"] = round(relevance_score, 4)  # backward compat alias
        res["confidence"] = confidence
        res["confidence_reasons"] = confidence_reasons
        res["reason"] = reason
        res["evidence"] = evidence

    # Sort descending by relevance score
    ranked = sorted(results, key=lambda x: x["relevance_score"], reverse=True)
    for i, r in enumerate(ranked, 1):
        r["rank"] = i

    return ranked
