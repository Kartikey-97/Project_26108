import sys
import time
import cProfile
import pstats
from concurrent.futures import ThreadPoolExecutor

sys.path.append('ai-engine')
from src.ml.applicability_features import build_applicability_features
from src.ml.applicability_model import load_applicability_model, get_applicability_model

def run_test():
    load_applicability_model("../standiq_applicability_model_v2.joblib", "../standiq_applicability_model_v2_metadata.json")
    model = get_applicability_model()
    print("Model loaded")

    reqs = ["TECHNICAL SPECIFICATION FOR 90W-120W LED STREET LIGHTING LUMINAIRES " + str(i) * 50 for i in range(11)]
    candidates = []
    for i in range(35):
        candidates.append({
            "is_number": f"IS {i}",
            "title": "Title mock " + str(i)*10,
            "summary": "Summary mock " + str(i)*20,
            "scope": "Scope mock " + str(i)*20,
            "search_text": "Search text mock " + str(i)*50,
            "bm25_score": 0.5,
            "semantic_score": 0.5,
            "rrf_score": 0.5
        })


    def process_req(req_text):
        for cand in candidates:
            # 1. build features
            df = build_applicability_features(req_text, cand, candidates)
            # 2. predict
            pred = model.predict(df)

    t_start = time.time()
    for req in reqs:
        process_req(req) # sequential to measure easily
    t_end = time.time()
    
    print(f"Total time (sequential): {t_end - t_start:.2f}s")

cProfile.run('run_test()', 'ml_stats')
p = pstats.Stats('ml_stats')
p.sort_stats('cumtime').print_stats(30)
