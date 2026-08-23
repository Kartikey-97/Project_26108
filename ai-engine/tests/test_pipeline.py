import sys
import os

# Ensure src is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.recommender import Recommender
from src.embedding import _model
import json

def test_pipeline():
    print("Initializing Recommender Pipeline...")
    recommender = Recommender(data_path="data/bis_50_knowledge_base.json")
    print(f"Number of records loaded: {len(recommender.standards)}")
    print(f"Embedding model used: {_model}")
    
    query = "We need to procure 90W LED street lights for highway roads."
    print(f"\nRunning end-to-end test with query: '{query}'")
    
    results = recommender.recommend(query, top_k=5)
    
    print("\n" + "="*50)
    print("RECOMMENDATION RESULTS")
    print("="*50)
    
    for i, res in enumerate(results, 1):
        print(f"\nRank {i}: {res['is_number']}")
        print(f"Title: {res['title']}")
        print(f"L2 Distance Score (Similarity): {res['distance']:.4f}")
        print(f"Relevance Score (Ranking): {res['relevance_score']:.4f}")
        print(f"Reason: {res['reason_for_recommendation']}")
        print(f"Related Standards: {res['related_standards']}")
        print(f"Test Methods: {res['test_methods']}")
        
        status = res.get('status', {})
        print(f"Status: {status.get('value')} (Verified: {status.get('verified')})")
        
        version = res.get('version') or {}
        if version:
            print("Version Information:")
            for k, v in version.items():
                print(f"  {k}: {v}")
        else:
            print(f"Edition Year: {res.get('edition_year')}")
        
        print("\nGap detection results / Missing Information:")
        for gap in res.get('missing_information_gaps', []):
            print(f" - {gap}")
            
    assert len(results) > 0, "No recommendations returned."
    print("\nEnd-to-end test passed successfully.")

if __name__ == '__main__':
    test_pipeline()
