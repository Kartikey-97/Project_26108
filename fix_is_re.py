with open('backend/kshiraj/bis_live_ingestion/normalizer.py', 'r') as f:
    content = f.read()

import re

old_block = r"""_IS_RE = re.compile(
    r"^\s*(IS\s*\d+)\s*(?:\((Part\s*\d+(?:\s+and\s+\d+)?)(?:\s*/\s*(Sec\s*\d+))?\))?\s*(?::\s*(\d{4}))?\s*$",
    re.IGNORECASE,
)"""

new_block = r"""_IS_RE = re.compile(
    r"^\s*(IS(?:/[A-Z]+)?\s*\d+)\s*(?:\((Part\s*\d+(?:\s+and\s+\d+)?)(?:\s*/\s*(Sec\s*\d+))?\))?\s*(?::\s*(\d{4}))?\s*$",
    re.IGNORECASE,
)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('backend/kshiraj/bis_live_ingestion/normalizer.py', 'w') as f:
        f.write(content)
    print("Fixed _IS_RE")
else:
    print("Could not find _IS_RE")
