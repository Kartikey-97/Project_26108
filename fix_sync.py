with open('backend/kshiraj/bis_live_ingestion/sync.py', 'r') as f:
    content = f.read()

old_block = """
            existing = next(
                (
                    s for s in self.standards_store.list_all()
                    if normalize_designation(s.base_designation) == requested
                ),
                None,
            )
"""

new_block = """
            existing = next(
                (
                    s for s in self.standards_store.list_all()
                    if normalize_designation(s.base_designation) == requested 
                    and (
                        not std.is_number or not s.is_number 
                        or s.is_number.replace(" ", "").lower() == std.is_number.replace(" ", "").lower()
                    )
                ),
                None,
            )
"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('backend/kshiraj/bis_live_ingestion/sync.py', 'w') as f:
        f.write(content)
    print("Fixed sync.py")
else:
    print("Could not find block in sync.py")
