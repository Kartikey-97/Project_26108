with open('backend/kartikey/orchestration/pipeline.py', 'r') as f:
    content = f.read()

old_block = """
        # Merge findings
        modified = False
        for new_finding in response.findings:
            if new_finding.verdict == Verdict.JUSTIFIED:
                continue
"""

new_block = """
        # Merge findings
        modified = False
        for new_finding in response.findings:
            if not new_finding.applicable_standard_ids:
                continue
"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('backend/kartikey/orchestration/pipeline.py', 'w') as f:
        f.write(content)
    print("Fixed pipeline.py verdict check")
else:
    print("Could not find block in pipeline.py")
