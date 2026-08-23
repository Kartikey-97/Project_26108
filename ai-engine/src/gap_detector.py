def detect_gaps(standard_record):
    """
    Detect missing or unverified fields in a BIS standard record.
    """
    gaps = []
    
    if not standard_record.get("scope"):
        gaps.append("Official scope is missing.")
        
    norm_refs = standard_record.get("normative_references", [])
    if not norm_refs:
        gaps.append("No normative references are explicitly mapped.")
        
    test_methods = standard_record.get("test_methods", [])
    if not test_methods:
        gaps.append("No test methods are mapped.")
        
    cert = standard_record.get("certification", {})
    if not cert.get("verified"):
        gaps.append("Certification requirements (e.g., QCO mandatory status) need manual verification.")
        
    status = standard_record.get("status", {})
    if not status.get("verified"):
        gaps.append("Standard validity/status needs manual verification.")
        
    return gaps
