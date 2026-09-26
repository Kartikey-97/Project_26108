import json
import uuid

reqs = [
    {"id": f"req-{i}", "text": "The street light shall conform to IS 16107.", "category": "technical_specification", "analysis_id": "test-full"}
    for i in range(11)
]

stds = [
    {"id": f"std-{i}", "is_number": f"IS 100{i}", "title": f"Test {i}", "status": "active", "year": 2024, "relevance_score": 0.9}
    for i in range(35)
]

payload = {
  "analysis_id": "test-full",
  "extracted_text": "dummy",
  "requirements": reqs,
  "retrieved_standards": stds
}

with open('full_req.json', 'w') as f:
    json.dump(payload, f)
