import logging
from typing import Optional, List, Tuple, Dict, Any
from fastapi import HTTPException
from app.services.supabase_service import supabase_service
from app.schemas.session import SessionCreate, SessionResponse, SessionSummary

logger = logging.getLogger("ventureos.session_repository")


class SessionRepository:
    def __init__(self):
        self.table_name = "startup_sessions"

    def _client(self):
        return supabase_service.get_client()

    def create_session(self, session_in: SessionCreate) -> Dict[str, Any]:
        """Insert a new startup session and return the created record."""
        client = self._client()
        payload = session_in.model_dump()
        try:
            logger.info("Creating startup session in database for industry: %s", session_in.industry)
            response = client.table(self.table_name).insert(payload).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Database returned no record on session insert.")
            created = response.data[0]
            logger.info("Session created successfully with ID: %s", created.get("id"))
            return created
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error creating session in Supabase: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database error creating session: {str(e)}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by UUID."""
        client = self._client()
        try:
            response = client.table(self.table_name).select("*").eq("id", session_id).execute()
            if not response.data or len(response.data) == 0:
                return None
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error fetching session %s from Supabase: %s", session_id, str(e))
            raise HTTPException(status_code=500, detail=f"Database error fetching session: {str(e)}")

    def update_session_status(self, session_id: str, status: str) -> Dict[str, Any]:
        """Update session lifecycle status."""
        client = self._client()
        try:
            logger.info("Updating session %s status to: %s", session_id, status)
            response = client.table(self.table_name).update({"status": status}).eq("id", session_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found for update.")
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error updating session %s status in Supabase: %s", session_id, str(e))
            raise HTTPException(status_code=500, detail=f"Database error updating session status: {str(e)}")

    def list_sessions(self, limit: int = 20, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """List sessions with pagination ordered by created_at DESC."""
        client = self._client()
        try:
            # Postgrest range is inclusive
            response = (
                client.table(self.table_name)
                .select("id, startup_idea, target_audience, industry, budget, timeline, status, created_at", count="exact")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            data = response.data or []
            total = response.count if response.count is not None else len(data)
            return data, total
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error listing sessions from Supabase: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database error listing sessions: {str(e)}")


session_repository = SessionRepository()
