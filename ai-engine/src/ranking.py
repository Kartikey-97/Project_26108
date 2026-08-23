def rank_results(results, query_understanding):
    """
    Reranks candidate results using an evidence-based scoring formula.
    """
    for res in results:
        # FAISS returns L2 distance. Convert to a similarity score (0 to 1).
        dist = res.get('distance', 2.0)
        semantic_sim = max(0.0, 1.0 - (dist / 2.0))
        
        # Calculate sub-scores
        product_rel = 0.0
        app_rel = 0.0
        tech_rel = 0.0
        meta_conf = 0.0
        
        search_text = res.get('search_text', '').lower()
        
        # Product Relevance
        prod = query_understanding.get("product")
        if prod:
            if prod.lower() in search_text:
                product_rel = 1.0
            elif any(word in search_text for word in prod.lower().split() if len(word) > 2):
                product_rel = 0.5
                
        # Application Relevance
        app = query_understanding.get("application")
        if app:
            if app.lower() in search_text:
                app_rel = 1.0
            elif any(word in search_text for word in app.lower().split() if len(word) > 2):
                app_rel = 0.5
                
        # Technical Relevance
        techs = query_understanding.get("technical_requirements", [])
        if techs:
            matches = sum(1 for t in techs if t.lower() in search_text)
            tech_rel = matches / len(techs)
        else:
            tech_rel = 1.0 # If none specified, don't penalize
            
        # Metadata Confidence
        status_data = res.get('status', {})
        if status_data.get('verification_status') == 'verified' or status_data.get('verified') is True:
            meta_conf = 1.0
        else:
            meta_conf = 0.5
            
        final_score = (
            0.50 * semantic_sim +
            0.20 * product_rel +
            0.15 * app_rel +
            0.10 * tech_rel +
            0.05 * meta_conf
        )
        
        # Determine Reason and Evidence
        evidence = []
        reason_parts = []
        
        if product_rel > 0:
            evidence.append("title")
            evidence.append("product_categories")
            reason_parts.append(f"matches the required product '{prod}'")
            
        if app_rel > 0:
            evidence.append("scope")
            reason_parts.append(f"is suitable for the application '{app}'")
            
        if tech_rel > 0 and techs:
            evidence.append("search_text")
            reason_parts.append(f"covers technical requirements like {', '.join(techs)}")
            
        if not reason_parts:
            reason = "Recommended based on general semantic similarity to the query."
            evidence.append("search_text")
        else:
            reason = "The standard " + " and ".join(reason_parts) + "."
            
        res['semantic_score'] = round(semantic_sim, 4)
        res['final_score'] = round(final_score, 4)
        res['reason'] = reason
        res['evidence'] = list(set(evidence))
        
    # Sort descending by final score
    ranked = sorted(results, key=lambda x: x['final_score'], reverse=True)
    
    # Assign ranks
    for i, res in enumerate(ranked, 1):
        res['rank'] = i
        
    return ranked
