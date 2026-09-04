import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from app.schemas.analysis import StartupAnalysisRequest, CEOAnalysisResponse
from app.schemas.session import SessionListResponse
from app.schemas.agent_output import SessionDetailsResponse
from app.schemas.multi_agent import (
    MultiAgentStatusResponse,
    MultiAgentRunResponse,
    AgentExecutionLog,
    AnalysisEventsResponse,
    AnalysisEventItem,
    PaginatedAnalysisHistoryResponse,
)
from app.services.analysis_service import analysis_service
from app.services.agent_orchestrator import agent_orchestrator
from app.repositories.agent_output_repository import agent_output_repository
from app.repositories.session_repository import session_repository
from app.repositories.execution_log_repository import execution_log_repository
from app.repositories.history_repository import history_repository

logger = logging.getLogger("ventureos.api.analysis")

router = APIRouter(tags=["Analysis & Sessions"])


# ---------------------------------------------------------------------------
# Phase 3 & 4 Endpoints (Preserved for backwards compatibility)
# ---------------------------------------------------------------------------

@router.post("/api/analyse/ceo", response_model=CEOAnalysisResponse)
@router.post("/analyse/ceo", response_model=CEOAnalysisResponse)
async def analyse_ceo(request: StartupAnalysisRequest):
    """
    Single-agent CEO analysis with persistence.
    """
    logger.info("Received CEO analysis request for industry: %s", request.industry)
    result = await analysis_service.run_ceo_analysis(request)
    return CEOAnalysisResponse(
        success=result["success"],
        session_id=result.get("session_id"),
        status=result.get("status", "completed"),
        sources_used=result.get("sources_used", []),
        data=result["data"],
    )


@router.get("/api/sessions/{session_id}", response_model=SessionDetailsResponse)
@router.get("/sessions/{session_id}", response_model=SessionDetailsResponse)
async def get_session(session_id: str):
    """
    Retrieve full session details and all associated agent outputs.
    """
    return analysis_service.get_session_details(session_id)


@router.get("/api/sessions", response_model=SessionListResponse)
@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(default=20, ge=1, le=100, description="Max number of sessions to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
):
    """
    List recent startup analysis sessions with pagination.
    """
    return analysis_service.list_sessions(limit=limit, offset=offset)


# ---------------------------------------------------------------------------
# Phase 6: Multi-Agent Intelligence Pipeline Endpoints
# ---------------------------------------------------------------------------

@router.post("/api/analysis/start", response_model=MultiAgentRunResponse)
@router.post("/analysis/start", response_model=MultiAgentRunResponse)
async def start_multi_agent_pipeline(request: StartupAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Creates a new startup session and immediately starts the full 7-agent intelligence pipeline:
    CEO -> Market -> Product -> Marketing -> Finance -> Investment -> Final Synthesis.
    """
    logger.info("Starting new multi-agent session for industry: %s", request.industry)
    session = session_repository.create_session(request)
    agent_orchestrator.initialize_pipeline_records(session["id"])
    background_tasks.add_task(agent_orchestrator.run_full_pipeline, session["id"])
    return MultiAgentRunResponse(
        success=True,
        session_id=session["id"],
        message="Multi-agent intelligence analysis initiated successfully.",
    )


@router.post("/api/analysis/{session_id}/run", response_model=MultiAgentRunResponse)
@router.post("/analysis/{session_id}/run", response_model=MultiAgentRunResponse)
async def run_multi_agent_analysis(session_id: str, background_tasks: BackgroundTasks):
    """
    Starts the sequential multi-agent intelligence pipeline in the background:
    CEO -> Market -> Product -> Marketing -> Finance -> Investment -> Final Synthesis.
    Includes concurrency lock to prevent duplicate execution on an actively processing session.
    """
    session = session_repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session.get("status") == "processing":
        logger.info("Session %s is already processing. Ignoring duplicate launch request.", session_id)
        return MultiAgentRunResponse(
            success=True,
            session_id=session_id,
            message="Analysis is already actively running.",
        )

    logger.info("Starting multi-agent run for session: %s", session_id)
    background_tasks.add_task(agent_orchestrator.run_full_pipeline, session_id)
    return MultiAgentRunResponse(
        success=True,
        session_id=session_id,
        message="Multi-agent intelligence analysis initiated successfully.",
    )


@router.get("/api/analysis/{session_id}/status", response_model=MultiAgentStatusResponse)
@router.get("/analysis/{session_id}/status", response_model=MultiAgentStatusResponse)
async def get_analysis_status(session_id: str):
    """
    Poll live progress, agent states (pending, processing, completed, failed), and progress %.
    """
    return agent_orchestrator.get_analysis_status(session_id)


@router.get("/api/analysis/{session_id}/logs", response_model=List[AgentExecutionLog])
@router.get("/analysis/{session_id}/logs", response_model=List[AgentExecutionLog])
async def get_execution_logs(session_id: str, limit: int = Query(default=100, ge=1, le=500)):
    """
    Fetch chronological execution events for the live terminal timeline.
    """
    records = execution_log_repository.get_session_logs(session_id, limit=limit)
    return [
        AgentExecutionLog(
            id=str(r.get("id")),
            session_id=str(r.get("session_id")),
            agent_name=r.get("agent_name"),
            event_type=r.get("event_type"),
            message=r.get("message"),
            metadata=r.get("metadata") or {},
            created_at=str(r.get("created_at")) if r.get("created_at") else None,
        )
        for r in records
    ]


@router.get("/api/analysis/history", response_model=PaginatedAnalysisHistoryResponse)
@router.get("/analysis/history", response_model=PaginatedAnalysisHistoryResponse)
async def get_analysis_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(default=None, description="Optional filter by status"),
):
    """
    Paginated venture analysis history with investment scores and readiness stages, newest first.
    """
    return history_repository.get_paginated_history(page=page, page_size=page_size, status=status)


@router.get("/api/analysis/{session_id}/events", response_model=AnalysisEventsResponse)
@router.get("/analysis/{session_id}/events", response_model=AnalysisEventsResponse)
async def get_analysis_events(session_id: str, limit: int = Query(default=150, ge=1, le=500)):
    """
    Fetch chronological execution events for real-time observability.
    """
    records = execution_log_repository.get_events(session_id, limit=limit)
    events = [
        AnalysisEventItem(
            id=str(r.get("id")),
            timestamp=str(r.get("created_at")) if r.get("created_at") else "",
            agent_name=r.get("agent_name", "system"),
            event_type=r.get("event_type", "info"),
            message=r.get("message", ""),
            metadata=r.get("metadata") or {},
        )
        for r in records
    ]
    return AnalysisEventsResponse(success=True, session_id=session_id, events=events)


@router.get("/api/analysis/{session_id}/agents")
@router.get("/analysis/{session_id}/agents")
async def get_all_agents_output(session_id: str):
    """
    Returns structured outputs of all completed agents for the session.
    """
    records = agent_output_repository.get_session_agent_outputs(session_id)
    results = {}
    for r in records:
        results[r.get("agent_name")] = {
            "status": r.get("status"),
            "output": r.get("output_json"),
            "error_message": r.get("error_message"),
            "updated_at": r.get("updated_at"),
        }
    return {"success": True, "session_id": session_id, "agents": results}


@router.get("/api/analysis/{session_id}/agents/{agent_name}")
@router.get("/analysis/{session_id}/agents/{agent_name}")
async def get_single_agent_output(session_id: str, agent_name: str):
    """
    Returns structured output for a specific agent.
    """
    records = agent_output_repository.get_session_agent_outputs(session_id)
    target = next((r for r in records if r.get("agent_name") == agent_name), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"No output found for agent '{agent_name}'.")

    return {
        "success": True,
        "session_id": session_id,
        "agent_name": agent_name,
        "status": target.get("status"),
        "output": target.get("output_json"),
        "error_message": target.get("error_message"),
        "updated_at": target.get("updated_at"),
    }


@router.get("/api/analysis/{session_id}/report")
@router.get("/analysis/{session_id}/report")
async def get_final_report(session_id: str):
    """
    Returns the final synthesized 20-section Investor-Grade Report.
    """
    records = agent_output_repository.get_session_agent_outputs(session_id)
    synthesis = next((r for r in records if r.get("agent_name") == "synthesis"), None)
    if not synthesis or synthesis.get("status") != "completed":
        raise HTTPException(status_code=404, detail="Final synthesis report has not been completed yet.")

    return {
        "success": True,
        "session_id": session_id,
        "status": "completed",
        "report": synthesis.get("output_json"),
    }


@router.post("/api/analysis/{session_id}/agents/{agent_name}/retry")
@router.post("/analysis/{session_id}/agents/{agent_name}/retry")
async def retry_agent(session_id: str, agent_name: str):
    """
    Retry an individual failed agent.
    Rejects retry if agent is currently actively processing.
    """
    records = agent_output_repository.get_session_agent_outputs(session_id)
    current = next((r for r in records if r.get("agent_name") == agent_name), None)
    if current and current.get("status") == "processing":
        raise HTTPException(status_code=400, detail=f"Agent '{agent_name}' is already actively executing.")

    return await agent_orchestrator.retry_agent(session_id, agent_name)


@router.get("/api/analysis/{session_id}/metrics")
@router.get("/analysis/{session_id}/metrics")
async def get_session_metrics(session_id: str):
    """
    Returns real execution, duration, RAG chunk, and cost metrics for an analysis session.
    """
    from app.services.session_metrics_service import session_metrics_service
    return {
        "success": True,
        "metrics": session_metrics_service.get_session_metrics(session_id),
    }
