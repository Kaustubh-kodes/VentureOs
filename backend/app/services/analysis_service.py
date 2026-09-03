import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.schemas.analysis import StartupAnalysisRequest, CEOAnalysis
from app.schemas.session import SessionCreate, SessionResponse, SessionSummary, SessionListResponse
from app.schemas.agent_output import AgentOutputCreate, AgentOutputResponse, SessionDetailsResponse
from app.agents.ceo_agent import ceo_agent
from app.repositories.session_repository import session_repository
from app.repositories.agent_output_repository import agent_output_repository

logger = logging.getLogger("ventureos.analysis_service")


class AnalysisService:
    async def run_ceo_analysis(self, request: StartupAnalysisRequest) -> Dict[str, Any]:
        """
        Coordinates full CEO analysis workflow:
        1. Creates Startup Session with status 'created' -> 'processing'
        2. Creates CEO Agent Output record with status 'processing'
        3. Executes CEO Agent (Gemini API with Pydantic validation)
        4. Saves validated CEO output as JSONB, sets status 'completed'
        5. Updates Session status to 'completed'
        6. On failure: updates Agent Output and Session to 'failed' with safe error message
        """
        # Step 1: Create Startup Session
        logger.info("Starting persistent CEO analysis session for industry: %s", request.industry)
        session_in = SessionCreate(
            startup_idea=request.startup_idea,
            target_audience=request.target_audience,
            industry=request.industry,
            budget=request.budget,
            timeline=request.timeline,
            notes=request.notes,
            status="processing",
        )
        session_record = session_repository.create_session(session_in)
        session_id = str(session_record.get("id"))
        logger.info("Created session ID: %s", session_id)

        # Step 2: Create CEO Agent Output record
        agent_output_in = AgentOutputCreate(
            session_id=session_id,
            agent_name="ceo",
            status="processing",
        )
        agent_output_repository.create_agent_output(agent_output_in)

        # Step 3: Retrieve Grounded Context from Knowledge Base (RAG)
        rag_context = ""
        sources_used = []
        try:
            from app.services.rag_service import rag_service
            retrieval_query = rag_service.build_retrieval_query(
                startup_idea=request.startup_idea,
                industry=request.industry,
                target_audience=request.target_audience,
                budget=request.budget,
                timeline=request.timeline,
            )
            chunks = rag_service.retrieve_context(query=retrieval_query)
            if chunks:
                rag_context, sources_used = rag_service.build_rag_context(chunks)
                logger.info("Injected %d knowledge chunks into CEO Agent prompt (%d sources)", len(chunks), len(sources_used))
            else:
                logger.info("No knowledge base chunks retrieved. Proceeding with standard CEO reasoning.")
        except Exception as rag_err:
            logger.warning("RAG retrieval encountered non-fatal error: %s. Falling back to standard reasoning.", str(rag_err))

        # Step 4: Execute CEO Agent
        try:
            logger.info("Executing CEO Agent reasoning for session %s...", session_id)
            ceo_result: CEOAnalysis = await ceo_agent.analyse(request, rag_context=rag_context)
            logger.info("CEO Agent successfully generated validated analysis for session %s", session_id)

            # Step 5: Save JSONB output and mark agent as completed
            output_dict = ceo_result.model_dump()
            if sources_used:
                output_dict["_sources_used"] = sources_used

            agent_output_repository.update_by_session_and_agent(
                session_id=session_id,
                agent_name="ceo",
                status="completed",
                output_json=output_dict,
            )

            # Step 6: Mark session as completed
            session_repository.update_session_status(session_id=session_id, status="completed")

            return {
                "success": True,
                "session_id": session_id,
                "status": "completed",
                "sources_used": sources_used,
                "data": ceo_result,
            }

        except HTTPException as http_exc:
            logger.error("HTTP error during CEO analysis for session %s: %s", session_id, http_exc.detail)
            safe_msg = str(http_exc.detail)
            self._handle_failure(session_id, safe_msg)
            raise http_exc
        except Exception as e:
            logger.error("Unexpected error during CEO analysis for session %s: %s", session_id, str(e))
            safe_msg = "An error occurred while generating the CEO strategy report."
            self._handle_failure(session_id, safe_msg)
            raise HTTPException(status_code=500, detail=safe_msg)

    def _handle_failure(self, session_id: str, error_message: str):
        """Record failure state across session and agent outputs."""
        try:
            agent_output_repository.update_by_session_and_agent(
                session_id=session_id,
                agent_name="ceo",
                status="failed",
                error_message=error_message,
            )
            session_repository.update_session_status(session_id=session_id, status="failed")
            logger.info("Marked session %s and CEO output as failed.", session_id)
        except Exception as db_err:
            logger.error("Failed to record failure state for session %s: %s", session_id, str(db_err))

    def get_session_details(self, session_id: str) -> SessionDetailsResponse:
        """Fetch session and all related agent outputs."""
        session_data = session_repository.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Startup session '{session_id}' not found.")

        agent_records = agent_output_repository.get_session_agent_outputs(session_id)
        agent_outputs = [
            AgentOutputResponse(
                id=str(r.get("id")),
                session_id=str(r.get("session_id")),
                agent_name=r.get("agent_name"),
                status=r.get("status"),
                output_json=r.get("output_json"),
                error_message=r.get("error_message"),
                created_at=str(r.get("created_at")) if r.get("created_at") else None,
                updated_at=str(r.get("updated_at")) if r.get("updated_at") else None,
            )
            for r in agent_records
        ]

        session_model = SessionResponse(
            id=str(session_data.get("id")),
            startup_idea=session_data.get("startup_idea"),
            target_audience=session_data.get("target_audience"),
            industry=session_data.get("industry"),
            budget=session_data.get("budget"),
            timeline=session_data.get("timeline"),
            notes=session_data.get("notes"),
            status=session_data.get("status"),
            created_at=str(session_data.get("created_at")) if session_data.get("created_at") else None,
            updated_at=str(session_data.get("updated_at")) if session_data.get("updated_at") else None,
        )

        return SessionDetailsResponse(
            success=True,
            session=session_model,
            agent_outputs=agent_outputs,
        )

    def list_sessions(self, limit: int = 20, offset: int = 0) -> SessionListResponse:
        """Fetch list of recent sessions with pagination."""
        capped_limit = min(max(1, limit), 100)
        capped_offset = max(0, offset)

        records, total = session_repository.list_sessions(limit=capped_limit, offset=capped_offset)
        summaries = [
            SessionSummary(
                id=str(r.get("id")),
                startup_idea=r.get("startup_idea"),
                target_audience=r.get("target_audience"),
                industry=r.get("industry"),
                budget=r.get("budget"),
                timeline=r.get("timeline"),
                status=r.get("status"),
                created_at=str(r.get("created_at")) if r.get("created_at") else None,
            )
            for r in records
        ]

        return SessionListResponse(
            success=True,
            total=total,
            limit=capped_limit,
            offset=capped_offset,
            sessions=summaries,
        )


analysis_service = AnalysisService()
