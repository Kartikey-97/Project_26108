from fastapi.testclient import TestClient
import uuid
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.main import app

client = TestClient(app)

def test_valid_request():
    payload = {
        "analysis_id": str(uuid.uuid4()),
        "extracted_text": "Sample",
        "requirements": [
            {
                "id": str(uuid.uuid4()),
                "analysis_id": str(uuid.uuid4()),
                "text": "The luminaire shall have an IP65 rating.",
                "category": "other"
            }
        ],
        "retrieved_standards": [
            {
                "id": str(uuid.uuid4()),
                "is_number": "IS 10322",
                "title": "Luminaires",
                "status": "Active"
            }
        ]
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "findings" in data
    assert len(data["findings"]) == 1
    # Check ML classifier worked
    assert data["findings"][0]["verdict"] in ["justified", "outdated_reference", "requires_human_verification"]

def test_outdated_standard_case():
    payload = {
        "analysis_id": str(uuid.uuid4()),
        "extracted_text": "Sample",
        "requirements": [
            {
                "id": str(uuid.uuid4()),
                "analysis_id": str(uuid.uuid4()),
                "text": "The luminaire shall have an IP65 rating.",
                "category": "other"
            }
        ],
        "retrieved_standards": [
            {
                "id": str(uuid.uuid4()),
                "is_number": "IS 10322",
                "title": "Luminaires",
                "status": "Superseded"
            }
        ]
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["findings"][0]["verdict"] == "outdated_reference"
    
def test_invalid_request():
    payload = {"invalid_field": "data"}
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422 # Pydantic validation error

if __name__ == "__main__":
    test_valid_request()
    test_outdated_standard_case()
    test_invalid_request()
    print("API Tests passed.")
