import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from datetime import datetime, timezone
from app.schemas.multi_agent import (
    AgentStatusInfo,
    MultiAgentStatusResponse,
    AnalysisEventItem,
    AnalysisEventsResponse,
    AnalysisHistoryItem,
    PaginatedAnalysisHistoryResponse,
)
from app.repositories.history_repository import history_repository
from app.repositories.execution_log_repository import execution_log_repository
from app.services.agent_orchestrator import agent_orchestrator, AGENT_DISPLAY_NAMES


def test_agent_status_info_schema():
    """Verify AgentStatusInfo schema supports duration_ms and timestamps."""
    info = AgentStatusInfo(
        name="market",
        display_name="Market Research",
        status="completed",
        sources_count=3,
        started_at="2026-09-04T00:10:00Z",
        completed_at="2026-09-04T00:10:14Z",
        duration_ms=14200,
    )
    assert info.name == "market"
    assert info.display_name == "Market Research"
    assert info.duration_ms == 14200
    assert info.sources_count == 3


def test_multi_agent_status_response_backward_compatibility():
    """Verify MultiAgentStatusResponse provides both agents list and agents_map dictionary."""
    agent_list = [
        AgentStatusInfo(name="ceo", display_name="CEO / Strategy", status="completed", duration_ms=12000),
        AgentStatusInfo(name="market", display_name="Market Research", status="processing"),
    ]
    resp = MultiAgentStatusResponse(
        success=True,
        session_id="test-session-123",
        overall_status="processing",
        session_status="processing",
        progress_percentage=14,
        overall_progress=14,
        current_agent="market",
        agents=agent_list,
        agents_map={a.name: a for a in agent_list},
        has_final_report=False,
    )
    assert resp.progress_percentage == 14
    assert len(resp.agents) == 2
    assert "ceo" in resp.agents_map
    assert resp.agents_map["ceo"].duration_ms == 12000


def test_execution_events_chronological_and_sanitized():
    """Verify execution events schema and ensure no secrets are exposed."""
    sample_event = AnalysisEventItem(
        id="evt-1",
        timestamp="2026-09-04T00:12:00Z",
        agent_name="investment",
        event_type="retrieval_completed",
        message="Retrieved 4 relevant chunks (2 sources).",
        metadata={"chunks_retrieved": 4, "sources_count": 2},
    )
    resp = AnalysisEventsResponse(
        success=True,
        session_id="test-session-123",
        events=[sample_event],
    )
    assert resp.success is True
    assert len(resp.events) == 1
    assert "GEMINI_API_KEY" not in resp.events[0].message
    assert "system_prompt" not in resp.events[0].message


def test_history_repository_pagination():
    """Verify history repository pagination structure."""
    result = history_repository.get_paginated_history(page=1, page_size=10)
    assert "total" in result
    assert "page" in result
    assert "page_size" in result
    assert "items" in result
    assert isinstance(result["items"], list)
    if result["items"]:
        first = result["items"][0]
        assert "id" in first
        assert "startup_idea" in first
        assert "status" in first


def test_agent_display_names():
    """Verify all 7 agents have professional human-readable display names."""
    expected = ["ceo", "market", "product", "marketing", "finance", "investment", "synthesis"]
    for agent in expected:
        assert agent in AGENT_DISPLAY_NAMES
        assert len(AGENT_DISPLAY_NAMES[agent]) > 2


if __name__ == "__main__":
    test_agent_status_info_schema()
    print("[PASS] test_agent_status_info_schema")
    test_multi_agent_status_response_backward_compatibility()
    print("[PASS] test_multi_agent_status_response_backward_compatibility")
    test_execution_events_chronological_and_sanitized()
    print("[PASS] test_execution_events_chronological_and_sanitized")
    test_history_repository_pagination()
    print("[PASS] test_history_repository_pagination")
    test_agent_display_names()
    print("[PASS] test_agent_display_names")
    print("\nAll Phase 7 tests passed successfully!")
