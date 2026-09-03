import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "VentureOS API"

def test_ceo_validation_error_short_idea():
    res = client.post("/api/analyse/ceo", json={
        "startup_idea": "short",
        "target_audience": "Students",
        "industry": "EdTech",
        "budget": "Under $10,000",
        "timeline": "1-3 months"
    })
    assert res.status_code == 422

def test_ceo_validation_error_missing_fields():
    res = client.post("/api/analyse/ceo", json={
        "startup_idea": "Valid startup idea with plenty of characters"
    })
    assert res.status_code == 422

def test_ceo_missing_api_key_returns_503():
    res = client.post("/api/analyse/ceo", json={
        "startup_idea": "A comprehensive AI powered platform for early stage founder advisory.",
        "target_audience": "Early stage founders and solopreneurs",
        "industry": "SaaS",
        "budget": "Under $10,000",
        "timeline": "1-3 months"
    })
    assert res.status_code == 503
    assert "GEMINI_API_KEY" in res.json()["detail"]

if __name__ == "__main__":
    test_health_endpoint()
    print("[PASS] test_health_endpoint passed")
    test_ceo_validation_error_short_idea()
    print("[PASS] test_ceo_validation_error_short_idea passed (422)")
    test_ceo_validation_error_missing_fields()
    print("[PASS] test_ceo_validation_error_missing_fields passed (422)")
    test_ceo_missing_api_key_returns_503()
    print("[PASS] test_ceo_missing_api_key_returns_503 passed (503)")
    print("\nAll automated backend tests passed successfully!")
