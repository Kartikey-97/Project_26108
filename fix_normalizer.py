with open('backend/kshiraj/bis_live_ingestion/normalizer.py', 'r') as f:
    content = f.read()

old_block = """
def normalize_standard(
    detail: dict[str, Any],
    amendments: list[dict[str, Any]] | None = None,
    *,
    source_url: str = PORTAL_URL,
) -> tuple[Standard, list[Evidence]]:
    designation = normalize_designation(str(detail.get("standardNumber") or ""))
    is_number, part, section, year = parse_designation(designation)
"""

new_block = """
def normalize_standard(
    detail: dict[str, Any],
    amendments: list[dict[str, Any]] | None = None,
    *,
    source_url: str = PORTAL_URL,
) -> tuple[Standard, list[Evidence]]:
    raw_designation = str(detail.get("standardNumber") or "")
    designation = normalize_designation(raw_designation)
    is_number, part, section, _ = parse_designation(designation)
    
    # Extract year safely before it gets stripped
    year = None
    import re
    year_match = re.search(r":\s*(\d{4})", raw_designation)
    if year_match:
        year = int(year_match.group(1))
"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('backend/kshiraj/bis_live_ingestion/normalizer.py', 'w') as f:
        f.write(content)
    print("Fixed normalizer.py")
else:
    print("Could not find block in normalizer.py")
