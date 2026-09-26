import re

with open("backend/kartikey/api/routes/standards.py", "r") as f:
    content = f.read()

real_block = """
@router.get("/bis-sync-status")
async def bis_sync_status() -> dict:
    \"\"\"
    Returns current BIS live sync status from memory.
    \"\"\"
    from shared.sync_state import get_sync_status
    return get_sync_status()
"""

# Replace the old dummy block
dummy_pattern = re.compile(r"@router\.get\(\"/bis-sync-status\"\)\nasync def bis_sync_status\(\) -> dict:.*?(?=@router\.get\(\"/\{standard_id\}\")", re.DOTALL)
content = dummy_pattern.sub(real_block + "\n", content)

with open("backend/kartikey/api/routes/standards.py", "w") as f:
    f.write(content)

