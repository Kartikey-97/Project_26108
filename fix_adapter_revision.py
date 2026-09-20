with open('frontend/src/services/adapter.ts', 'r') as f:
    content = f.read()

import re
old_rev = r"revision: raw.status \? String\(raw.status\).replace\(/_/g, ' '\) : 'Current',"
new_rev = r"revision: raw.status ? (String(raw.status) === 'unknown' ? 'Active' : String(raw.status).replace(/_/g, ' ')) : 'Current',"

if re.search(old_rev, content):
    content = re.sub(old_rev, new_rev, content)
    with open('frontend/src/services/adapter.ts', 'w') as f:
        f.write(content)
    print("Fixed revision unknown text")
else:
    print("Could not find revision string")
