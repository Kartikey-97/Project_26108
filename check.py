import json
with open("backend/shared/bis_catalogue_reconciled.json", "r") as f:
    cat = json.load(f)

for item in cat:
    if item["is_number"] in ["IS 9537 : Part 2", "IS/IEC 60669 : Part 2 : Sec 2", "IS 15885 : Part 2 : Sec 13"]:
        print(f"--- {item['is_number']} ---")
        print(f"Title: {item['title']}")
        print(f"Certification: {item['certification']}")
