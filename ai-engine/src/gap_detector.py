def detect_gaps(standard_record, query_understanding=None):
    """
    Detect missing or unverified fields in a BIS standard record.
    """
    gaps = []
    
    if not standard_record.get("scope"):
        gaps.append("Official scope is potentially unspecified.")
        
    norm_refs = standard_record.get("normative_references", [])
    if not norm_refs:
        gaps.append("Normative references are potentially unspecified.")
        
    test_methods = standard_record.get("test_methods", [])
    if not test_methods:
        gaps.append("Test methods are potentially unspecified (consider specifying testing requirements).")
        
    cert = standard_record.get("certification", {})
    if not cert.get("verified"):
        gaps.append("Certification requirements need verification (consider specifying QCO status).")
        
    status = standard_record.get("status", {})
    if status.get("verification_status") != "verified" and not status.get("verified"):
        gaps.append("Standard validity/status needs manual verification.")
        
    if query_understanding:
        techs = query_understanding.get("technical_requirements", [])
        if techs:
            gaps.append(f"Consider explicitly verifying if the standard covers: {', '.join(techs)}")
            
    return gaps
