with open('backend/kartikey/api/routes/analyses.py', 'r') as f:
    content = f.read()

old_block = """
            for i, standard in enumerate(stds):
                # Always return the freshest state from in-memory store in case it was synced
                fresh_std = store.get_by_id(standard.id)
                if fresh_std:
                    stds[i] = fresh_std
                    standard = fresh_std
"""

new_block = """
            for i, standard in enumerate(stds):
                # Always return the freshest state from in-memory store in case it was synced
                fresh_std = store.get_by_id(standard.id)
                if fresh_std:
                    # Preserve transient ML scores attached to the document finding
                    fresh_std.relevance_score = getattr(standard, 'relevance_score', None)
                    fresh_std.semantic_score = getattr(standard, 'semantic_score', None)
                    fresh_std.text_excerpt = getattr(standard, 'text_excerpt', None)
                    
                    stds[i] = fresh_std
                    standard = fresh_std
"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('backend/kartikey/api/routes/analyses.py', 'w') as f:
        f.write(content)
    print("Fixed get_analysis standard overriding")
else:
    print("Could not find block in get_analysis")
