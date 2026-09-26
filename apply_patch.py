import json

with open('/Users/kartikeygupta/.gemini/antigravity/brain/d763f1ea-b854-42e1-9c3d-e8bd8a439b7a/.user_uploaded/media_1789826536912.json') as f:
    patch = json.load(f)

with open('backend/shared/bis_catalogue_reconciled.json') as f:
    catalogue = json.load(f)

apply_updates = patch['apply']
updated_count = 0

for item in catalogue:
    # Handle the specific name fixes requested in the previous session
    if item['is_number'] == 'IS/IEC 60669 : Part 2 : Sec 2':
        item['is_number'] = 'IS/IEC 60669 : Part 2 : Sec 1'
        item['normalized_is_number'] = 'IS/IEC 60669 : Part 2 : Sec 1'
    if item['is_number'] == 'IS 15885 : Part 2 : Sec 13':
        item['title'] = 'Safety of Lamp Controlgear Part 2 Particular Requirements Section 13 d.c. or a.c. Supplied Electronic Controlgear for LED Modules'
        
    base = item['is_number']
    if base in apply_updates:
        item['certification'] = apply_updates[base]
        updated_count += 1

with open('backend/shared/bis_catalogue_reconciled.json', 'w') as f:
    json.dump(catalogue, f, indent=2)

print(f"Updated {updated_count} records.")
