import logging
import math
from typing import Dict, Any, Optional, List
from app.services.supabase_service import supabase_service

logger = logging.getLogger("ventureos.history_repository")


class HistoryRepository:
    def __init__(self):
        self.sessions_table = "startup_sessions"
        self.outputs_table = "agent_outputs"

    def _client(self):
        return supabase_service.get_client()

    def get_paginated_history(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves paginated venture analysis history with investment scores and readiness stages.
        Ordered newest first.
        """
        client = self._client()
        offset = (page - 1) * page_size

        try:
            # 1. Base query for sessions
            query = client.table(self.sessions_table).select("*", count="exact")
            if status and status.strip() and status != "all":
                query = query.eq("status", status.strip().lower())

            res = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
            sessions = res.data or []
            total = res.count if res.count is not None else len(sessions)
            total_pages = math.ceil(total / page_size) if total > 0 else 1

            if not sessions:
                return {
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 1,
                    "items": [],
                }

            # 2. Batch fetch relevant agent outputs for these sessions to extract scores
            session_ids = [s["id"] for s in sessions]
            outputs_res = (
                client.table(self.outputs_table)
                .select("session_id, agent_name, output_json, status")
                .in_("session_id", session_ids)
                .in_("agent_name", ["synthesis", "investment", "ceo"])
                .execute()
            )
            outputs_by_session: Dict[str, Dict[str, Any]] = {}
            for out in (outputs_res.data or []):
                sid = out.get("session_id")
                if sid not in outputs_by_session:
                    outputs_by_session[sid] = {}
                outputs_by_session[sid][out.get("agent_name")] = out.get("output_json") or {}

            # 3. Assemble history items
            items: List[Dict[str, Any]] = []
            for s in sessions:
                sid = s.get("id")
                sess_outs = outputs_by_session.get(sid, {})
                synth_out = sess_outs.get("synthesis", {})
                inv_out = sess_outs.get("investment", {})

                # Extract score and readiness
                score = synth_out.get("investment_score") or inv_out.get("investment_score")
                readiness = synth_out.get("investment_readiness") or inv_out.get("investment_readiness")
                sources = synth_out.get("sources_used") or inv_out.get("sources_used") or []

                items.append({
                    "id": sid,
                    "startup_idea": s.get("startup_idea", ""),
                    "industry": s.get("industry", ""),
                    "target_audience": s.get("target_audience", ""),
                    "budget": s.get("budget", ""),
                    "timeline": s.get("timeline", ""),
                    "status": s.get("status", "created"),
                    "investment_score": score,
                    "investment_readiness": readiness,
                    "sources_count": len(sources) if isinstance(sources, list) else 0,
                    "created_at": s.get("created_at"),
                })

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "items": items,
            }

        except Exception as e:
            logger.error("Error retrieving analysis history: %s", str(e))
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 1,
                "items": [],
            }


history_repository = HistoryRepository()
