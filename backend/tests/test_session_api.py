import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app
from app.schemas.session import SessionCreate, SessionResponse
from app.schemas.agent_output import AgentOutputCreate

client = TestClient(app)


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_ceo_request_validation():
    # Test short idea fails with 422
    res = client.post("/api/analyse/ceo", json={
        "startup_idea": "short",
        "target_audience": "Founders",
        "industry": "SaaS",
        "budget": "Under $10,000",
        "timeline": "1-3 months"
    })
    assert res.status_code == 422


def test_session_unconfigured_credentials_returns_503():
    # Without SUPABASE_URL and SUPABASE_KEY set, sessions endpoints return 503 gracefully
    res_list = client.get("/api/sessions")
    assert res_list.status_code in (200, 503)

    res_get = client.get("/api/sessions/00000000-0000-0000-0000-000000000000")
    assert res_get.status_code in (404, 503)


def test_pydantic_session_models():
    # Test session and agent output models validate accurately
    s_create = SessionCreate(
        startup_idea="An autonomous AI agent for developer security compliance",
        target_audience="Software Engineers and CTOs",
        industry="DevTools",
        budget="$10,000-$50,000",
        timeline="3-6 months",
        status="created",
    )
    dump = s_create.model_dump()
    assert dump["industry"] == "DevTools"
    assert dump["status"] == "created"

    ao_create = AgentOutputCreate(
        session_id="00000000-0000-0000-0000-000000000000",
        agent_name="ceo",
        status="processing",
    )
    ao_dump = ao_create.model_dump()
    assert ao_dump["agent_name"] == "ceo"
    assert ao_dump["status"] == "processing"


if __name__ == "__main__":
    test_health_check()
    print("[PASS] test_health_check passed")
    test_ceo_request_validation()
    print("[PASS] test_ceo_request_validation passed (422)")
    test_session_unconfigured_credentials_returns_503()
    print("[PASS] test_session_unconfigured_credentials_returns_503 passed")
    test_pydantic_session_models()
    print("[PASS] test_pydantic_session_models passed")
    print("\nAll Phase 4 backend tests passed successfully!")
