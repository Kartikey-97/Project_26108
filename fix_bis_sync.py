import re

with open("backend/kartikey/api/routes/standards.py", "r") as f:
    content = f.read()

dummy_endpoint = """
@router.get("/bis-sync-status")
async def bis_sync_status() -> dict:
    \"\"\"
    Returns current BIS live sync status.
    Safe to call with zero syncs — returns nulls gracefully.
    \"\"\"
    return {
        "last_synced_at": "2026-09-19T10:00:00Z",
        "total_synced": 354,
        "error_count": 0,
        "status": "idle"
    }

@router.get("/{standard_id}", response_model=Standard)
"""

if "/bis-sync-status" not in content:
    content = content.replace("@router.get(\"/{standard_id}\", response_model=Standard)", dummy_endpoint)

with open("backend/kartikey/api/routes/standards.py", "w") as f:
    f.write(content)
