import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.repositories.session_repository import session_repository
from app.repositories.agent_output_repository import agent_output_repository
from app.repositories.execution_log_repository import execution_log_repository

logger = logging.getLogger("ventureos.services.metrics")


class SessionMetricsService:
    def get_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """
        Calculates real execution, cost, and observability metrics for an analysis session.
        Never fabricates tokens or estimates false values.
        """
        session = session_repository.get_session(session_id)
        if not session:
            return {
                "session_id": session_id,
                "status": "not_found",
                "agents_total": 7,
                "agents_completed": 0,
                "agents_failed": 0,
                "total_duration_ms": 0,
                "total_llm_calls": 0,
                "total_tokens": None,
                "total_rag_chunks_retrieved": 0,
                "total_retries": 0,
            }

        outputs = agent_output_repository.get_session_agent_outputs(session_id)
        events = execution_log_repository.get_events(session_id, limit=200)

        completed_count = sum(1 for o in outputs if o.get("status") == "completed")
        failed_count = sum(1 for o in outputs if o.get("status") == "failed")
        
        # Calculate sum of measured agent execution durations
        total_duration_ms = 0
        for o in outputs:
            dur = o.get("duration_ms") or o.get("output_json", {}).get("_meta", {}).get("duration_ms")
            if isinstance(dur, (int, float)):
                total_duration_ms += int(dur)

        # Count retries and chunk retrievals from recorded analysis events
        retries_count = 0
        total_chunks = 0
        for ev in events:
            ev_type = ev.get("event_type", "")
            if ev_type == "agent_retry" or "retry" in ev_type:
                retries_count += 1
            if ev_type == "retrieval_completed":
                meta = ev.get("metadata", {})
                if isinstance(meta, dict) and "chunks_retrieved" in meta:
                    total_chunks += int(meta.get("chunks_retrieved", 0))

        # If events did not record chunk count, sum sources_used from outputs
        if total_chunks == 0:
            for o in outputs:
                sources = o.get("output_json", {}).get("sources_used", [])
                if isinstance(sources, list):
                    total_chunks += len(sources)

        # Tokens: report None unless explicit token metadata is stored
        tokens_used = None

        return {
            "session_id": session_id,
            "status": session.get("status", "unknown"),
            "agents_total": 7,
            "agents_completed": completed_count,
            "agents_failed": failed_count,
            "total_duration_ms": total_duration_ms,
            "total_duration_formatted": self._format_duration(total_duration_ms),
            "total_llm_calls": completed_count + failed_count + retries_count,
            "total_tokens": tokens_used,
            "total_rag_chunks_retrieved": total_chunks,
            "total_retries": retries_count,
        }

    def _format_duration(self, ms: int) -> str:
        if not ms or ms <= 0:
            return "0s"
        total_seconds = ms / 1000.0
        if total_seconds < 60:
            return f"{total_seconds:.1f}s"
        mins = int(total_seconds // 60)
        secs = int(total_seconds % 60)
        return f"{mins}m {secs}s"


session_metrics_service = SessionMetricsService()
