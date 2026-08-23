def rank_results(results):
    """
    Reranks candidate results. 
    Currently just sorts by semantic similarity score, but can be 
    expanded to weight fields like status, completeness, or recency.
    """
    # FAISS returns L2 distances (lower is better)
    return sorted(results, key=lambda x: x['distance'])
