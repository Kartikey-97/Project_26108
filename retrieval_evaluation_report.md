# StandIQ AI Engine: Live Evaluation Report

This report validates the accuracy of the deployed StandIQ AI Engine (`/recommend` endpoint) across a dataset of 30 realistic procurement queries. The engine uses a Hybrid Retrieval architecture (BM25 + Semantic FAISS + RRF) coupled with an LLM-based query understanding layer.

## 📊 Summary Metrics

| Metric | Score |
|---|---|
| **Total Queries** | 30 |
| **Recall@1** | 0.0% |
| **Recall@3** | 0.0% |
| **Recall@5** | 0.0% |
| **MRR (Mean Reciprocal Rank)** | 0.000 |
| **Avg. Pipeline Latency** | 5.081s |

## 🔍 Detailed Results

| Status | Procurement Query | Expected Standard | Top-10 Rank |
|:---:|---|---|---|
