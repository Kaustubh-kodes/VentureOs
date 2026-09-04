import logging
from typing import List, Dict, Any, Optional
from app.services.supabase_service import supabase_service

logger = logging.getLogger("ventureos.execution_log_repository")


class ExecutionLogRepository:
    def __init__(self):
        # agent_execution_logs is active in current Supabase schema; analysis_events is fallback
        self.primary_table = "agent_execution_logs"
        self.fallback_table = "analysis_events"

    def _client(self):
        return supabase_service.get_client()

    def log_event(
        self,
        session_id: str,
        agent_name: str,
        event_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Record an agent execution lifecycle event for real-time observability.
        Writes to analysis_events as primary, falling back to agent_execution_logs.
        """
        logger.info("[%s][%s] %s", agent_name.upper(), event_type, message)
        payload = {
            "session_id": session_id,
            "agent_name": agent_name,
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
        }
        client = self._client()
        # Try primary table first
        try:
            res = client.table(self.primary_table).insert(payload).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as err:
            logger.debug("Writing to %s failed, attempting fallback table: %s", self.primary_table, err)

        # Fallback table attempt
        try:
            res = client.table(self.fallback_table).insert(payload).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            logger.debug("Writing to fallback event table also failed: %s", e)
            return None

    def get_events(self, session_id: str, limit: int = 150) -> List[Dict[str, Any]]:
        """Fetch chronological execution events for real-time observability."""
        client = self._client()
        try:
            res = (
                client.table(self.primary_table)
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            if res.data:
                return res.data
        except Exception:
            pass

        try:
            res = (
                client.table(self.fallback_table)
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return res.data or []
        except Exception as e:
            logger.debug("Failed to fetch events from database: %s", e)
            return []

    def get_session_logs(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Backwards-compatibility alias for get_events."""
        return self.get_events(session_id, limit=limit)


execution_log_repository = ExecutionLogRepository()
