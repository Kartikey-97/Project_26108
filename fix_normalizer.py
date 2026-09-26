import re

with open('backend/kshiraj/bis_live_ingestion/normalizer.py', 'r') as f:
    content = f.read()

def replacer(match):
    return match.group(1)

old_func = """def normalize_designation(value: str) -> str:
    value = re.sub(r"\\s+", " ", value.strip())"""
new_func = """def normalize_designation(value: str) -> str:
    value = value.strip().upper()
    value = re.sub(r"^(IS(?:/[A-Z]+)?)\s*(\d+)", r"\g<1> \g<2>", value)
    value = re.sub(r"\s+", " ", value)"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('backend/kshiraj/bis_live_ingestion/normalizer.py', 'w') as f:
        f.write(content)
    print("Fixed")
else:
    print("Not found")
