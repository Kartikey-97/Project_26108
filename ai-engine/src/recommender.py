"""
ai-engine/src/recommender.py

Orchestrates the full recommendation pipeline:
  1. parse_query    — LLM-powered structured query understanding
  2. HybridRetriever — BM25 + FAISS cosine (Reciprocal Rank Fusion)
  3. rank_results   — multi-signal reranking with proper evidence objects
  4. check_currentness — deterministic version/supersession check
  5. detect_gaps    — real requirement vs standard coverage gaps
"""

import json
import logging
import os

from src.embedding import generate_embeddings
from src.search import HybridRetriever
from src.ranking import rank_results
from src.gap_detector import detect_gaps
from src.query_understanding import parse_query
from src.currentness import check_currentness, check_explicit_reference

logger = logging.getLogger(__name__)


class Recommender:
    def __init__(self, data_path: str = "data/bis_full_knowledge_base.json"):
        self.data_path = data_path
        self.standards: list = []
        self.retriever = None
        self._load_and_index()

    def _load_and_index(self) -> None:
        if not os.path.exists(self.data_path):
            # Graceful fallback to the 50-record knowledge base if full one not present
            fallback = "data/bis_50_knowledge_base.json"
            if os.path.exists(fallback):
                logger.warning(
                    "Full knowledge base not found at '%s', falling back to '%s'.",
                    self.data_path, fallback
                )
                self.data_path = fallback
            else:
                logger.error("No knowledge base found — Recommender will not function.")
                return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.standards = json.load(f)
        except Exception as exc:
            logger.error("Failed to load knowledge base: %s", exc)
            return

        if not self.standards:
            logger.error("Knowledge base at '%s' is empty.", self.data_path)
            return

        logger.info("Generating embeddings for %d standards…", len(self.standards))
        try:
            search_texts = [std.get("search_text", "") for std in self.standards]
            embeddings = generate_embeddings(search_texts)

            logger.info("Building HybridRetriever (BM25 + FAISS cosine) over %d standards…", len(self.standards))
            self.retriever = HybridRetriever().fit(self.standards, embeddings)
            logger.info("Recommender ready — %d standards indexed.", len(self.standards))
        except Exception as exc:
            logger.error("Failed to build retrieval index: %s", exc)
            self.retriever = None

    def recommend(self, query: str, top_k: int = 5) -> dict:
        if self.retriever is None:
            return {"error": "Recommender not initialized — dataset missing or empty."}

        if not query or not query.strip():
            return {"error": "Query cannot be empty."}

        try:
            # ----------------------------------------------------------------
            # 1. Structured query understanding
            # ----------------------------------------------------------------
            query_understanding = parse_query(query)
            logger.info(
                "Query understood: product=%s domain=%s tech_reqs=%d",
                query_understanding.get("product"),
                query_understanding.get("domain"),
                len(query_understanding.get("technical_requirements") or []),
            )

            # ----------------------------------------------------------------
            # 2. Hybrid retrieval — BM25 + FAISS via Reciprocal Rank Fusion
            # ----------------------------------------------------------------
            query_emb = generate_embeddings(query)
            candidates = self.retriever.search(query, query_emb, top_k=20)

            # ----------------------------------------------------------------
            # 3. Reranking with structured evidence
            # ----------------------------------------------------------------
            ranked_results = rank_results(candidates, query_understanding)
            final_recommendations = ranked_results[:top_k]

            if not final_recommendations:
                return {
                    "query": query,
                    "query_understanding": query_understanding,
                    "recommendations": [],
                    "potential_gaps": [],
                    "currentness": {},
                    "confidence": "low",
                }

            # ----------------------------------------------------------------
            # 4. Currentness check on top result
            # ----------------------------------------------------------------
            primary_std = final_recommendations[0]
            currentness_verdict = check_currentness(primary_std)

            explicit_refs = query_understanding.get("explicit_standard_refs") or []
            additional_currentness = {}
            for ref in explicit_refs[:3]:
                verdict = check_explicit_reference(ref, cited_year=None, standards=self.standards)
                if verdict:
                    additional_currentness[ref] = verdict

            # ----------------------------------------------------------------
            # 5. Gap detection against top standard
            # ----------------------------------------------------------------
            gaps = detect_gaps(primary_std, query_understanding)

            # ----------------------------------------------------------------
            # 6. Overall confidence from top result
            # ----------------------------------------------------------------
            top_confidence = primary_std.get("confidence", "low")

            # ----------------------------------------------------------------
            # 7. Aggregate related metadata across all top recommendations
            # ----------------------------------------------------------------
            related_stds = set()
            test_methods = set()
            norm_refs = set()
            safety_stds = set()
            output_recs = []

            for rec in final_recommendations:
                for r in (rec.get("related_standards") or []):
                    related_stds.add(r)
                for t in (rec.get("test_methods") or []):
                    test_methods.add(t)
                for n in (rec.get("normative_references") or []):
                    norm_refs.add(n)
                if "safety" in (rec.get("title") or "").lower():
                    safety_stds.add(rec.get("is_number"))

                output_recs.append({
                    "rank":             rec.get("rank"),
                    "is_number":        rec.get("is_number"),
                    "title":            rec.get("title"),
                    "semantic_score":   rec.get("semantic_score"),
                    "bm25_score":       rec.get("bm25_score"),
                    "relevance_score":  rec.get("relevance_score"),
                    "final_score":      rec.get("final_score"),
                    "confidence":       rec.get("confidence"),
                    "confidence_reasons": rec.get("confidence_reasons", []),
                    "reason":           rec.get("reason"),
                    "evidence":         rec.get("evidence", []),
                    "retrieval_source": rec.get("retrieval_source", "semantic"),
                    "version":          rec.get("version") or {},
                    "status":           rec.get("status") or {},
                })

            return {
                "query":                 query,
                "query_understanding":   query_understanding,
                "recommendations":       output_recs,
                "related_standards":     sorted(related_stds),
                "test_methods":          sorted(test_methods),
                "safety_standards":      sorted(s for s in safety_stds if s),
                "normative_references":  sorted(norm_refs),
                "potential_gaps":        gaps,
                "currentness":           currentness_verdict,
                "additional_currentness": additional_currentness,
                "confidence":            top_confidence,
            }

        except Exception as exc:
            logger.error("Recommendation pipeline failed for query '%s': %s", query[:80], exc)
            return {
                "error": f"Recommendation failed: {str(exc)}",
                "query": query,
            }
