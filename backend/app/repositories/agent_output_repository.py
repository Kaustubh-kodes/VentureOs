import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from app.services.supabase_service import supabase_service
from app.schemas.agent_output import AgentOutputCreate, AgentOutputUpdate

logger = logging.getLogger("ventureos.agent_output_repository")


class AgentOutputRepository:
    def __init__(self):
        self.table_name = "agent_outputs"

    def _client(self):
        return supabase_service.get_client()

    def create_agent_output(self, output_in: AgentOutputCreate) -> Dict[str, Any]:
        """Create a new agent output record in the database."""
        client = self._client()
        payload = output_in.model_dump()
        try:
            logger.info("Creating agent output for agent '%s' in session %s", output_in.agent_name, output_in.session_id)
            response = client.table(self.table_name).insert(payload).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Database returned no record on agent output insert.")
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error creating agent output in Supabase: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database error creating agent output: {str(e)}")

    def update_agent_output(self, output_id: str, update_in: AgentOutputUpdate) -> Dict[str, Any]:
        """Update an existing agent output record by its ID."""
        client = self._client()
        payload = {k: v for k, v in update_in.model_dump().items() if v is not None}
        try:
            response = client.table(self.table_name).update(payload).eq("id", output_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail=f"Agent output record {output_id} not found for update.")
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error updating agent output %s in Supabase: %s", output_id, str(e))
            raise HTTPException(status_code=500, detail=f"Database error updating agent output: {str(e)}")

    def update_by_session_and_agent(
        self,
        session_id: str,
        agent_name: str,
        status: str,
        output_json: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update agent output by session_id and agent_name with duration and timestamp tracking."""
        client = self._client()
        payload: Dict[str, Any] = {"status": status}
        if output_json is not None:
            if duration_ms is not None or started_at is not None or completed_at is not None:
                meta = output_json.setdefault("_meta", {})
                if duration_ms is not None:
                    meta["duration_ms"] = duration_ms
                if started_at is not None:
                    meta["started_at"] = started_at
                if completed_at is not None:
                    meta["completed_at"] = completed_at
            payload["output_json"] = output_json
        if error_message is not None:
            payload["error_message"] = error_message
        if duration_ms is not None:
            payload["duration_ms"] = duration_ms
        if started_at is not None:
            payload["started_at"] = started_at
        if completed_at is not None:
            payload["completed_at"] = completed_at

        try:
            logger.info("Updating agent output for '%s' in session %s to status '%s'", agent_name, session_id, status)
            response = (
                client.table(self.table_name)
                .update(payload)
                .eq("session_id", session_id)
                .eq("agent_name", agent_name)
                .execute()
            )
            if not response.data:
                logger.warning("No existing record found for agent '%s' in session %s, creating fallback", agent_name, session_id)
                new_record = AgentOutputCreate(
                    session_id=session_id,
                    agent_name=agent_name,
                    status=status,
                    output_json=output_json,
                    error_message=error_message,
                )
                return self.create_agent_output(new_record)
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            # If duration_ms column not yet migrated in Supabase, strip and retry cleanly
            if any(k in payload for k in ("duration_ms", "started_at", "completed_at")):
                clean_payload = {k: v for k, v in payload.items() if k not in ("duration_ms", "started_at", "completed_at")}
                try:
                    res = (
                        client.table(self.table_name)
                        .update(clean_payload)
                        .eq("session_id", session_id)
                        .eq("agent_name", agent_name)
                        .execute()
                    )
                    if res.data:
                        return res.data[0]
                except Exception:
                    pass
            logger.error("Error updating agent output by session and agent: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database error updating agent output: {str(e)}")

    def get_session_agent_outputs(self, session_id: str) -> List[Dict[str, Any]]:
        """Fetch all agent outputs for a session ordered by created_at."""
        client = self._client()
        try:
            response = (
                client.table(self.table_name)
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .execute()
            )
            return response.data or []
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error fetching agent outputs for session %s: %s", session_id, str(e))
            raise HTTPException(status_code=500, detail=f"Database error fetching agent outputs: {str(e)}")


agent_output_repository = AgentOutputRepository()
