import json
import os
from src.embedding import generate_embeddings
from src.search import VectorStore
from src.ranking import rank_results
from src.gap_detector import detect_gaps

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

    def recommend(self, query, top_k=3):
        if not self.vector_store:
            return []
            
        query_emb = generate_embeddings(query)
        distances, indices = self.vector_store.search(query_emb, top_k=top_k)
        
        results = []
        for dist, idx in zip(distances, indices):
            if idx == -1:
                continue
            std = self.standards[idx]
            gaps = detect_gaps(std)
            
            status_data = std.get("status", {}) or {}
            version_data = std.get("version") or {}
            if "latest_known_edition" in status_data:
                version_data = {
                    "latest_known_edition": status_data.get("latest_known_edition"),
                    "latest_known_year": status_data.get("latest_known_year"),
                    "supersedes": status_data.get("supersedes"),
                    "verification_status": status_data.get("verification_status")
                }
                
            result = {
                "is_number": std.get("is_number"),
                "title": std.get("title"),
                "distance": float(dist),
                "relevance_score": float(dist), # Placeholder for derived score
                "reason_for_recommendation": "High semantic similarity between the procurement requirement and the standard's indexed description.",
                "related_standards": std.get("related_standards", []),
                "test_methods": std.get("test_methods", []),
                "version": version_data,
                "status": status_data,
                "missing_information_gaps": gaps
            }
            results.append(result)
            
        ranked_results = rank_results(results)
        return ranked_results
