import json
import os
from src.embedding import generate_embeddings
from src.search import VectorStore
from src.ranking import rank_results
from src.gap_detector import detect_gaps
from src.query_understanding import parse_query

class Recommender:
    def __init__(self, data_path="data/bis_50_knowledge_base.json"):
        self.data_path = data_path
        self.standards = []
        self.vector_store = None
        self._load_and_index()
        
    def _load_and_index(self):
        if not os.path.exists(self.data_path):
            print(f"Dataset not found at {self.data_path}")
            return
            
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.standards = json.load(f)
            
        if not self.standards:
            return
            
        search_texts = [std.get("search_text", "") for std in self.standards]
        embeddings = generate_embeddings(search_texts)
        
        self.vector_store = VectorStore(dimension=embeddings.shape[1])
        self.vector_store.add_embeddings(embeddings)

    def recommend(self, query, top_k=5):
        if not self.vector_store:
            return {"error": "Vector store not initialized"}
            
        query_understanding = parse_query(query)
            
        query_emb = generate_embeddings(query)
        # Retrieve 20 candidates for reasoning/reranking
        distances, indices = self.vector_store.search(query_emb, top_k=20)
        
        candidates = []
        for dist, idx in zip(distances, indices):
            if idx == -1:
                continue
            std = self.standards[idx].copy()
            std['distance'] = float(dist)
            candidates.append(std)
            
        # Rerank
        ranked_results = rank_results(candidates, query_understanding)
        
        # Take top K
        final_recommendations = ranked_results[:top_k]
        
        # Format the output items
        output_recs = []
        related_stds = set()
        test_methods = set()
        safety_stds = set()
        norm_refs = set()
        
        if final_recommendations:
            # Generate gaps based on the top primary standard
            primary_std = final_recommendations[0]
            gaps = detect_gaps(primary_std, query_understanding)
            
            # Confidence based on final score of top candidate
            top_score = primary_std.get('final_score', 0)
            if top_score > 0.7:
                confidence = "high"
            elif top_score > 0.4:
                confidence = "medium"
            else:
                confidence = "low"
        else:
            gaps = []
            confidence = "low"
            
        for rec in final_recommendations:
            status_data = rec.get("status", {}) or {}
            version_data = rec.get("version") or {}
            if "latest_known_edition" in status_data:
                version_data = {
                    "latest_known_edition": status_data.get("latest_known_edition"),
                    "latest_known_year": status_data.get("latest_known_year"),
                    "supersedes": status_data.get("supersedes"),
                    "verification_status": status_data.get("verification_status")
                }
                
            output_rec = {
                "rank": rec.get("rank"),
                "is_number": rec.get("is_number"),
                "title": rec.get("title"),
                "semantic_score": rec.get("semantic_score"),
                "final_score": rec.get("final_score"),
                "reason": rec.get("reason"),
                "evidence": rec.get("evidence", []),
                "version": version_data,
                "status": status_data
            }
            output_recs.append(output_rec)
            
            # Aggregate relationships from all top recommendations to enrich the response
            for r in rec.get("related_standards", []):
                related_stds.add(r)
            for t in rec.get("test_methods", []):
                test_methods.add(t)
            for n in rec.get("normative_references", []):
                norm_refs.add(n)
                
            if "safety" in rec.get("title", "").lower() or "safety" in rec.get("standard_type", "").lower():
                safety_stds.add(rec.get("is_number"))

        response = {
            "query": query,
            "query_understanding": query_understanding,
            "recommendations": output_recs,
            "related_standards": list(related_stds),
            "test_methods": list(test_methods),
            "safety_standards": list(safety_stds),
            "normative_references": list(norm_refs),
            "potential_gaps": gaps,
            "confidence": confidence
        }
        
        return response
