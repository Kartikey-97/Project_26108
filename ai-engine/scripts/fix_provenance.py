import json
import os

kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bis_full_knowledge_base.json')

with open(kb_path, 'r', encoding='utf-8') as f:
    records = json.load(f)

for r in records:
    # 1. Strip raw embeddings if any script accidentally adds them
    if 'embedding' in r:
        del r['embedding']

    # 2. Convert scope to a provenance object
    scope_val = r.get('scope')
    
    # If it's already a dict, skip or normalize
    if isinstance(scope_val, dict):
        pass
    else:
        if scope_val:  # It has an official/curated string
            source_t = "curated" if "Curated" in str(r.get('source', {})) else "official"
            r['scope'] = {
                "value": scope_val,
                "source_type": source_t,
                "verified": True
            }
        else: # It's null, we use the synthesized summary
            r['scope'] = {
                "value": r.get('scope_summary', ''),
                "source_type": "synthetic",
                "verified": False
            }

    # 3. Clean up the old scope_summary field to prevent confusion
    if 'scope_summary' in r:
        del r['scope_summary']

    # 4. Standardise certification provenance
    cert = r.get('certification')
    if cert and isinstance(cert, dict):
        if 'source_type' not in cert:
            cert['source_type'] = "curated" if "Curated" in str(r.get('source', {})) else "official"
            if cert.get('mandatory') is None:
                cert['verified'] = False
                cert['source_type'] = "unverified"

with open(kb_path, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Fixed provenance for {len(records)} records.")
