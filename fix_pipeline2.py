with open('backend/kartikey/orchestration/pipeline.py', 'r') as f:
    content = f.read()

old_block = """
            if existing:
                # Add new standard if not already there
                if not any(s.id == new_standard.id for s in existing.applicable_standards):
                    existing.applicable_standards.append(new_standard)
                    modified = True
"""

new_block = """
            if existing:
                # Add new standard if not already there
                if not any(s.id == new_standard.id for s in existing.applicable_standards):
                    # Inherit relevance_score from the standard it supersedes
                    old_std = next((s for s in existing.applicable_standards if getattr(s, 'relevance_score', None) is not None), None)
                    if old_std:
                        new_standard.relevance_score = old_std.relevance_score
                    else:
                        new_standard.relevance_score = 0.99
                    
                    existing.applicable_standards.append(new_standard)
                    modified = True
"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('backend/kartikey/orchestration/pipeline.py', 'w') as f:
        f.write(content)
    print("Fixed pipeline.py")
else:
    print("Could not find block in pipeline.py")
