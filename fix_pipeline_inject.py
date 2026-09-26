with open('backend/kartikey/orchestration/pipeline.py', 'r') as f:
    content = f.read()

import re

old_block = r"""    try:
        analysis = await repository\.get\(analysis_id\)
        if not analysis or not analysis\.requirements:
            return

        extracted_text = analysis\.raw_text or ""
        if analysis\.input_type == InputType\.DOCUMENT and analysis\.document_id:
            extracted_text = get_extracted_text\(analysis\.document_id\) or ""

        request = AimlRequest\(
            analysis_id=analysis\.id,
            extracted_text=extracted_text,
            requirements=analysis\.requirements,
            retrieved_standards=\[new_standard\],
        \)

        client = AimlClient\(timeout=settings\.aiml_timeout_seconds\)
        response = await client\.run_analysis\(request\)

        # Merge findings
        modified = False
        for new_finding in response\.findings:
            if not new_finding\.applicable_standard_ids:
                continue
            
            # Find existing finding for this requirement
            existing = next\(\(f for f in analysis\.findings if f\.requirement_id == new_finding\.requirement_id\), None\)
            if existing:
                # Add new standard if not already there
                if not any\(s\.id == new_standard\.id for s in existing\.applicable_standards\):
                    # Inherit relevance_score from the standard it supersedes
                    old_std = next\(\(s for s in existing\.applicable_standards if getattr\(s, 'relevance_score', None\) is not None\), None\)
                    if old_std:
                        new_standard\.relevance_score = old_std\.relevance_score
                    else:
                        new_standard\.relevance_score = 0\.99
                    
                    existing\.applicable_standards\.append\(new_standard\)
                    modified = True

        if modified:
            await repository\.save\(analysis\)
            logger\.info\("rescore_and_merge: Successfully injected %s into findings for analysis %s", new_standard\.is_number, analysis_id\)

    except Exception as e:"""

new_block = """    try:
        analysis = await repository.get(analysis_id)
        if not analysis:
            return

        modified = False
        new_is_norm = new_standard.designation.replace(" ", "").lower() if hasattr(new_standard, "designation") else new_standard.is_number.replace(" ", "").lower()
        
        for finding in analysis.findings:
            if not hasattr(finding, 'applicable_standards'):
                continue
                
            for old_std in finding.applicable_standards:
                if old_std.superseded_by:
                    old_sup_norm = old_std.superseded_by.replace(" ", "").lower()
                    if old_sup_norm == new_is_norm or old_sup_norm == new_standard.is_number.replace(" ", "").lower():
                        if not any(ns.id == new_standard.id for ns in finding.applicable_standards):
                            new_standard.relevance_score = getattr(old_std, 'relevance_score', 0.99)
                            finding.applicable_standards.append(new_standard)
                            modified = True
                        break # Move to next finding

        if modified:
            await repository.save(analysis)
            logger.info("rescore_and_merge: Successfully injected %s into findings for analysis %s", new_standard.is_number, analysis_id)
        else:
            logger.info("rescore_and_merge: %s did not supersede any existing standards in findings", new_standard.is_number)

    except Exception as e:"""

if re.search(old_block, content):
    content = re.sub(old_block, new_block, content)
    with open('backend/kartikey/orchestration/pipeline.py', 'w') as f:
        f.write(content)
    print("Fixed pipeline.py direct injection")
else:
    print("Could not find block in pipeline.py")
