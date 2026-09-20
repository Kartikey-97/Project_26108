import sys, time
sys.path.append('ai-engine')
from src.ml.applicability_features import build_applicability_features
from src.ml.applicability_model import load_applicability_model, get_applicability_model
import pandas as pd

load_applicability_model("../standiq_applicability_model_v2.joblib", "../standiq_applicability_model_v2_metadata.json")
model = get_applicability_model()

reqs = ["Requirement " + str(i)*50 for i in range(11)]
candidates = [{"is_number": f"IS {i}", "title": "Title", "summary": "", "scope": "", "search_text": "Text"*10, "bm25_score": 0.5, "semantic_score": 0.5, "rrf_score": 0.5} for i in range(35)]

t0 = time.time()
dfs = []
for req in reqs:
    for cand in candidates:
        dfs.append(build_applicability_features(req, cand, candidates))
t_feat = time.time() - t0

t0 = time.time()
full_df = pd.concat(dfs, ignore_index=True)
preds = model.predict(full_df)
t_pred = time.time() - t0

print(f"Total Feature Time: {t_feat:.4f}s")
print(f"Total Predict Time (Batch 385): {t_pred:.4f}s")
