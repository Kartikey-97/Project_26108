import sys, time
sys.path.append('ai-engine')
from src.ml.applicability_features import build_applicability_features
from src.ml.applicability_model import load_applicability_model, get_applicability_model
import pandas as pd
import joblib

load_applicability_model("../standiq_applicability_model_v2.joblib", "../standiq_applicability_model_v2_metadata.json")
model = get_applicability_model()
print(f"Model n_jobs: {model.pipeline.named_steps['classifier'].n_jobs if hasattr(model.pipeline.named_steps.get('classifier'), 'n_jobs') else 'Unknown'}")

reqs = ["Requirement " + str(i)*50 for i in range(11)]
candidates = [{"is_number": f"IS {i}", "title": "Title", "summary": "", "scope": "", "search_text": "Text"*10, "bm25_score": 0.5, "semantic_score": 0.5, "rrf_score": 0.5} for i in range(35)]

t_feat_total = 0
t_pred_total = 0
n_evals = 0

for req in reqs:
    for cand in candidates:
        n_evals += 1
        
        t0 = time.time()
        df = build_applicability_features(req, cand, candidates)
        t_feat_total += (time.time() - t0)
        
        t0 = time.time()
        model.predict(df)
        t_pred_total += (time.time() - t0)

print(f"Evals: {n_evals}")
print(f"Total Feature Time: {t_feat_total:.4f}s")
print(f"Total Predict Time: {t_pred_total:.4f}s")
