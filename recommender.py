"""
End-to-end procurement recommendation flow.

Combines:
1. Requirement-level analysis
2. Existing MiniLM embedding
3. Existing FAISS retrieval
4. Proper relevance/ranking
5. Evidence/provenance mapping
6. Issue detection
7. Confidence/uncertainty
8. Structured final result

This does not change the core retrieval approach.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from src.embedding import generate_embeddings
from src.search import VectorStore
from src.ranking import rank_results
from src.gap_detector import detect_gaps
from src.requirement_analysis import analyze_requirement_text
from src.evidence import build_evidence_map, evidence_summary
from src.issue_detector import detect_issues
from src.confidence import classify_confidence


class Recommender:
    def __init__(
        self,
        data_path: str = "data/bis_50_knowledge_base.json",
    ):
        self.data_path = data_path
        self.standards: List[Dict[str, Any]] = []
        self.vector_store = None
        self._load_and_index()

    def _load_and_index(self) -> None:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"Dataset not found at {self.data_path}"
            )

        with open(
            self.data_path,
            "r",
            encoding="utf-8",
        ) as f:
            self.standards = json.load(f)

        if not self.standards:
            raise ValueError("Knowledge base is empty.")

        search_texts = [
            std.get("search_text", "")
            for std in self.standards
        ]

        embeddings = generate_embeddings(search_texts)

        self.vector_store = VectorStore(
            dimension=embeddings.shape[1]
        )
        self.vector_store.add_embeddings(
            embeddings
        )

    def _recommend_for_requirement(
        self,
        requirement: Dict[str, Any],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        query = requirement["value"]

        query_emb = generate_embeddings(query)

        distances, indices = self.vector_store.search(
            query_emb,
            top_k=min(top_k, len(self.standards)),
        )

        raw_results = []

        for dist, idx in zip(distances, indices):
            if idx == -1:
                continue

            standard = self.standards[idx]

            result = {
                "is_number": standard.get("is_number"),
                "title": standard.get("title"),
                "distance": float(dist),
                "_standard": standard,
            }

            raw_results.append(result)

        ranked = rank_results(
            raw_results,
            query=query,
        )

        final_results = []

        for result in ranked:
            standard = result.pop("_standard")

            evidence = build_evidence_map(
                standard,
                requirement_text=query,
            )

            issues = detect_issues(
                requirement=requirement,
                standard=standard,
                evidence=evidence,
            )

            gaps = detect_gaps(standard)

            # Convert existing gap output into explicit issues too.
            for gap in gaps:
                issues.append({
                    "type": "KNOWLEDGE_BASE_GAP",
                    "severity": "MEDIUM",
                    "message": gap,
                    "requires_human_review": True,
                })

            confidence = classify_confidence(
                relevance_score=result["relevance_score"],
                evidence=evidence,
                issues=issues,
            )

            evidence_info = evidence_summary(evidence)

            status_data = standard.get("status") or {}
            version_data = standard.get("version") or {}

            final_results.append({
                "is_number": standard.get("is_number"),
                "title": standard.get("title"),
                "relevance_score": result["relevance_score"],
                "ranking": result["ranking"],
                "distance": result["distance"],

                "reason_for_recommendation": (
                    "Candidate retrieved by semantic similarity and "
                    "reranked using available procurement/standard metadata. "
                    "This is a retrieval recommendation, not by itself "
                    "proof of legal or regulatory applicability."
                ),

                "evidence": evidence,
                "evidence_summary": evidence_info,

                "related_standards": standard.get(
                    "related_standards", []
                ),
                "normative_references": standard.get(
                    "normative_references", []
                ),
                "test_methods": standard.get(
                    "test_methods", []
                ),

                "version": version_data,
                "status": status_data,

                "missing_information_gaps": gaps,
                "issues": issues,
                "confidence": confidence,

                "source": standard.get("source"),
                "data_quality": standard.get(
                    "data_quality"
                ),
            })

        return final_results

    def recommend(
        self,
        query: str,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        requirement_analysis = analyze_requirement_text(
            query
        )

        requirements = requirement_analysis["requirements"]

        # If the text contains no detectable requirement structure,
        # still perform one query-level retrieval rather than returning
        # nothing.
        if not requirements:
            requirements = [{
                "requirement_id": "REQ-001",
                "name": "Procurement query",
                "value": query,
                "unit": None,
                "specifications": [],
                "context": {
                    "source_type": "supplied_text",
                },
                "source_location": {
                    "text": query,
                },
                "explicit_standard_references": [],
                "signals": {},
                "confidence": "LOW",
            }]

        analyses = []

        for requirement in requirements:
            recommendations = self._recommend_for_requirement(
                requirement,
                top_k=top_k,
            )

            analyses.append({
                "requirement": requirement,
                "recommendations": recommendations,
            })

        all_issues = [
            issue
            for analysis in analyses
            for recommendation in analysis["recommendations"]
            for issue in recommendation["issues"]
        ]

        human_review = any(
            issue.get("requires_human_review")
            for issue in all_issues
        )

        return {
            "query": query,
            "requirements": [
                analysis["requirement"]
                for analysis in analyses
            ],
            "analyses": analyses,
            "alerts": all_issues,
            "requires_human_review": human_review,
            "summary": {
                "requirement_count": len(analyses),
                "recommendation_count": sum(
                    len(a["recommendations"])
                    for a in analyses
                ),
                "issue_count": len(all_issues),
                "human_review_required": human_review,
            },
        }
