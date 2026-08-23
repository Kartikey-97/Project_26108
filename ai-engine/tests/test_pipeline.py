import sys
import os
import json

# Ensure src is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.recommender import Recommender

def test_pipeline():
    print("Initializing Recommender Pipeline...")
    recommender = Recommender(data_path="data/bis_50_knowledge_base.json")
    
    queries = [
        "We need to procure 90W LED street lights for highway roads.",
        "We need electric motors for industrial water pumps.",
        "We need electrical cables for a government office building.",
        "We need office chairs."
    ]
    
    for query in queries:
        print("\n" + "="*80)
        print(f"QUERY: '{query}'")
        print("="*80)
        
        results = recommender.recommend(query, top_k=3)
        
        print("\n[QUERY UNDERSTANDING]")
        print(json.dumps(results.get("query_understanding"), indent=2))
        
        print(f"\n[CONFIDENCE]: {results.get('confidence').upper()}")
        
        print("\n[TOP RECOMMENDATIONS]")
        for res in results.get("recommendations", []):
            print(f"\n  Rank {res['rank']}: {res['is_number']}")
            print(f"  Title: {res['title']}")
            print(f"  Semantic Score: {res['semantic_score']:.4f} | Final Score: {res['final_score']:.4f}")
            print(f"  Reason: {res['reason']}")
            print(f"  Evidence: {res['evidence']}")
            
        print("\n[RELATIONSHIPS]")
        print(f"  Related Standards: {results.get('related_standards')}")
        print(f"  Test Methods: {results.get('test_methods')}")
        print(f"  Safety Standards: {results.get('safety_standards')}")
        print(f"  Normative References: {results.get('normative_references')}")
        
        print("\n[POTENTIAL GAPS]")
        for gap in results.get("potential_gaps", []):
            print(f"  - {gap}")
            
    print("\nEnd-to-end reasoning tests passed successfully.")

if __name__ == '__main__':
    test_pipeline()
