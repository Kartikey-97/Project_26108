with open('backend/kartikey/api/routes/analyses.py', 'r') as f:
    content = f.read()

def clean(s):
    return s.replace(" ", "").lower() if s else ""

# 1. Fix get_analysis dynamic injection
# Replace the bad normalize_designation match
old_match_1 = "superseding = next((s for s in store.list_all() if (s.is_number and normalize_designation(s.is_number) == norm_target) or (hasattr(s, 'designation') and normalize_designation(s.designation) == norm_target)), None)"
new_match_1 = "superseding = next((s for s in store.list_all() if (s.is_number and s.is_number.replace(' ', '').lower() == standard.superseded_by.replace(' ', '').lower()) or (hasattr(s, 'designation') and s.designation.replace(' ', '').lower() == standard.superseded_by.replace(' ', '').lower())), None)"

if old_match_1 in content:
    content = content.replace(old_match_1, new_match_1)
    print("Fixed get_analysis")
else:
    print("Could not find get_analysis match")

# 2. Fix trigger_manual_bis_sync background task
old_match_2 = """
            for sup_is in new_superseded_ids:
                norm_sup = normalize_designation(sup_is)
                # Find it in the store
                new_std = next((s for s in store.list_all() if (s.is_number and normalize_designation(s.is_number) == norm_sup) or (hasattr(s, 'designation') and normalize_designation(s.designation) == norm_sup)), None)
"""
new_match_2 = """
            for sup_is in new_superseded_ids:
                # Find it in the store EXACTLY matching the returned supersedes string (ignoring whitespace/case)
                new_std = next((s for s in store.list_all() if (s.is_number and s.is_number.replace(' ', '').lower() == sup_is.replace(' ', '').lower()) or (hasattr(s, 'designation') and s.designation.replace(' ', '').lower() == sup_is.replace(' ', '').lower())), None)
"""

if old_match_2 in content:
    content = content.replace(old_match_2, new_match_2)
    print("Fixed trigger_manual_bis_sync")
else:
    print("Could not find trigger_manual_bis_sync match")

with open('backend/kartikey/api/routes/analyses.py', 'w') as f:
    f.write(content)
