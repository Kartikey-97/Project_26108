import re
import glob
import os

files_to_check = [
    "backend/kartikey/orchestration/knowledge_registry.py",
    "backend/shared/seed_data.py"
]

for filepath in files_to_check:
    if not os.path.exists(filepath):
        continue
    with open(filepath, "r") as f:
        content = f.read()
    
    new_content = content.replace("standardsbis.gov.in", "standards.bis.gov.in")
    
    with open(filepath, "w") as f:
        f.write(new_content)

