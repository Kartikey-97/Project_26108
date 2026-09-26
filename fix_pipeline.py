with open('backend/kartikey/orchestration/pipeline.py', 'r') as f:
    content = f.read()

# Replace the injected function with one that has correct imports
old_func = """async def rescore_and_merge(analysis_id: str, new_standard: Standard) -> None:
    \"\"\"
    Called after BIS Sync discovers a superseding standard.
    Evaluates the new standard against the analysis requirements and injects it
    into the existing findings if it is highly applicable.
    \"\"\"
    from shared.config import settings
    from kshiraj.aiml_client.client import AimlClient
    from shared.contracts import AimlRequest
    from kartikey.api.main import repository
    from kartikey.document_processing.storage import get_extracted_text

    try:
        analysis = await repository.get(analysis_id)
        if not analysis or not analysis.requirements:
            return

        extracted_text = analysis.raw_text or ""
        if analysis.input_type == InputType.DOCUMENT and analysis.document_id:
            extracted_text = get_extracted_text(analysis.document_id) or ""

        request = AimlRequest(
            analysis_id=analysis.id,
            extracted_text=extracted_text,
            requirements=analysis.requirements,
            retrieved_standards=[new_standard],
        )

        client = AimlClient(timeout=settings.aiml_timeout_seconds)
        response = await client.run_analysis(request)

        # Merge findings
        modified = False
        for new_finding in response.findings:
            if new_finding.verdict == Verdict.JUSTIFIED:
                continue
            
            # Find existing finding for this requirement
            existing = next((f for f in analysis.findings if f.requirement_id == new_finding.requirement_id), None)
            if existing:
                # Add new standard if not already there
                if not any(s.id == new_standard.id for s in existing.applicable_standards):
                    existing.applicable_standards.append(new_standard)
                    modified = True

        if modified:
            await repository.save(analysis)
            logger.info("rescore_and_merge: Successfully injected %s into findings for analysis %s", new_standard.is_number, analysis_id)

    except Exception as e:
        logger.error("rescore_and_merge failed for analysis %s: %s", analysis_id, e)"""

new_func = """async def rescore_and_merge(analysis_id: str, new_standard: 'Standard') -> None:
    \"\"\"
    Called after BIS Sync discovers a superseding standard.
    Evaluates the new standard against the analysis requirements and injects it
    into the existing findings if it is highly applicable.
    \"\"\"
    from shared.config import settings
    from kshiraj.aiml_client.client import AimlClient
    from shared.contracts import AimlRequest
    from kartikey.api.main import repository
    from kartikey.document_processing.storage import get_extracted_text
    from shared.models import Standard, InputType, Verdict

    try:
        analysis = await repository.get(analysis_id)
        if not analysis or not analysis.requirements:
            return

        extracted_text = analysis.raw_text or ""
        if analysis.input_type == InputType.DOCUMENT and analysis.document_id:
            extracted_text = get_extracted_text(analysis.document_id) or ""

        request = AimlRequest(
            analysis_id=analysis.id,
            extracted_text=extracted_text,
            requirements=analysis.requirements,
            retrieved_standards=[new_standard],
        )

        client = AimlClient(timeout=settings.aiml_timeout_seconds)
        response = await client.run_analysis(request)

        # Merge findings
        modified = False
        for new_finding in response.findings:
            if new_finding.verdict == Verdict.JUSTIFIED:
                continue
            
            # Find existing finding for this requirement
            existing = next((f for f in analysis.findings if f.requirement_id == new_finding.requirement_id), None)
            if existing:
                # Add new standard if not already there
                if not any(s.id == new_standard.id for s in existing.applicable_standards):
                    existing.applicable_standards.append(new_standard)
                    modified = True

        if modified:
            await repository.save(analysis)
            logger.info("rescore_and_merge: Successfully injected %s into findings for analysis %s", new_standard.is_number, analysis_id)

    except Exception as e:
        logger.error("rescore_and_merge failed for analysis %s: %s", analysis_id, e)"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('backend/kartikey/orchestration/pipeline.py', 'w') as f:
        f.write(content)
    print("Replaced successfully.")
else:
    print("Old function not found!")
