import json

patch_file = '/Users/kartikeygupta/.gemini/antigravity/brain/d763f1ea-b854-42e1-9c3d-e8bd8a439b7a/.user_uploaded/media_1789826536912.json'
cat_file = 'backend/shared/bis_catalogue_reconciled.json'

with open(patch_file, 'r') as f:
    patch = json.load(f)

with open(cat_file, 'r') as f:
    cat = json.load(f)

cat_is_numbers = {record['is_number'] for record in cat}

print("=== Verifying APPLY ===")
for is_num in patch['apply']:
    if is_num not in cat_is_numbers:
        print(f"NOT FOUND IN CATALOGUE: {is_num}")
    else:
        print(f"Found: {is_num}")

print("\n=== Verifying HOLD ===")
for item in patch['hold']:
    is_num = item['is_number']
    if is_num not in cat_is_numbers:
        print(f"NOT FOUND IN CATALOGUE: {is_num}")
    else:
        print(f"Found: {is_num}")

