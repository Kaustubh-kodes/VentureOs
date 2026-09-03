import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from app.repositories.session_repository import session_repository
from app.repositories.agent_output_repository import agent_output_repository
from app.repositories.execution_log_repository import execution_log_repository
from app.services.rag_service import rag_service

# Agent imports
from app.agents.ceo_agent import ceo_agent
from app.agents.market_agent import market_agent
from app.agents.product_agent import product_agent
from app.agents.marketing_agent import marketing_agent
from app.agents.finance_agent import finance_agent
from app.agents.investment_agent import investment_agent
from app.agents.synthesis_agent import synthesis_agent

# Schemas
from app.schemas.analysis import StartupAnalysisRequest
from app.schemas.multi_agent import (
    MultiAgentStatusResponse,
    AgentStatusInfo,
    SourceReference,
)

logger = logging.getLogger("ventureos.agent_orchestrator")

AGENT_DISPLAY_NAMES = {
    "ceo": "CEO / Strategy",
    "market": "Market Research",
    "product": "Product",
    "marketing": "Marketing / GTM",
    "finance": "Finance",
    "investment": "Investment / Risk",
    "synthesis": "Final Synthesis",
}


class AgentOrchestrator:
    AGENTS_SEQUENCE = ["ceo", "market", "product", "marketing", "finance", "investment", "synthesis"]

    async def run_full_pipeline(self, session_id: str) -> None:
        """
        Executes the 7-agent sequential intelligence pipeline:
        CEO -> Market -> Product -> Marketing -> Finance -> Investment -> Synthesis
        """
        session = session_repository.get_session(session_id)
        if not session:
            logger.error("Cannot run orchestrator: Session %s not found.", session_id)
            return

        session_repository.update_session_status(session_id, "processing")
        execution_log_repository.log_event(
            session_id,
            "system",
            "analysis_started",
            "Multi-agent venture intelligence workflow started.",
            {"started_at": datetime.now(timezone.utc).isoformat()}
        )

        startup_context = {
            "startup_idea": session.get("startup_idea", ""),
            "target_audience": session.get("target_audience", ""),
            "industry": session.get("industry", ""),
            "budget": session.get("budget", ""),
            "timeline": session.get("timeline", ""),
            "notes": session.get("notes") or "",
        }

        agent_results: Dict[str, Any] = {}
        all_sources: List[Dict[str, Any]] = []
        any_failure = False

        # --- 1. CEO Agent ---
        ceo_output = await self._run_agent_step(
            agent_name="ceo",
            agent_instance=None,
            session_id=session_id,
            startup_context=startup_context,
            all_sources=all_sources,
        )
        if ceo_output:
            agent_results["ceo"] = ceo_output
        else:
            any_failure = True

        # --- 2. Market Research Agent ---
        market_context = self._format_predecessor_summary("CEO & Strategy", agent_results.get("ceo"))
        market_output = await self._run_agent_step(
            agent_name="market",
            agent_instance=market_agent,
            session_id=session_id,
            startup_context=startup_context,
            predecessor_context=market_context,
            all_sources=all_sources,
        )
        if market_output:
            agent_results["market"] = market_output
        else:
            any_failure = True

        # --- 3. Product Agent ---
        product_context = self._format_predecessor_summary("CEO & Strategy", agent_results.get("ceo"))
        product_output = await self._run_agent_step(
            agent_name="product",
            agent_instance=product_agent,
            session_id=session_id,
            startup_context=startup_context,
            predecessor_context=product_context,
            all_sources=all_sources,
        )
        if product_output:
            agent_results["product"] = product_output
        else:
            any_failure = True

        # --- 4. Marketing Agent ---
        mkt_predecessors = "\n".join(filter(None, [
            self._format_predecessor_summary("CEO & Strategy", agent_results.get("ceo")),
            self._format_predecessor_summary("Market Research", agent_results.get("market")),
        ]))
        marketing_output = await self._run_agent_step(
            agent_name="marketing",
            agent_instance=marketing_agent,
            session_id=session_id,
            startup_context=startup_context,
            predecessor_context=mkt_predecessors,
            all_sources=all_sources,
        )
        if marketing_output:
            agent_results["marketing"] = marketing_output
        else:
            any_failure = True

        # --- 5. Finance Agent ---
        fin_predecessors = "\n".join(filter(None, [
            self._format_predecessor_summary("CEO & Strategy", agent_results.get("ceo")),
            self._format_predecessor_summary("Market Research", agent_results.get("market")),
            self._format_predecessor_summary("Product Strategy", agent_results.get("product")),
        ]))
        finance_output = await self._run_agent_step(
            agent_name="finance",
            agent_instance=finance_agent,
            session_id=session_id,
            startup_context=startup_context,
            predecessor_context=fin_predecessors,
            all_sources=all_sources,
        )
        if finance_output:
            agent_results["finance"] = finance_output
        else:
            any_failure = True

        # --- 6. Investment Agent (Actively challenges all findings) ---
        inv_predecessors = "\n".join(filter(None, [
            self._format_predecessor_summary("CEO Strategy", agent_results.get("ceo")),
            self._format_predecessor_summary("Market Analysis", agent_results.get("market")),
            self._format_predecessor_summary("Product Roadmap", agent_results.get("product")),
            self._format_predecessor_summary("Marketing GTM", agent_results.get("marketing")),
            self._format_predecessor_summary("Financial Model", agent_results.get("finance")),
        ]))
        investment_output = await self._run_agent_step(
            agent_name="investment",
            agent_instance=investment_agent,
            session_id=session_id,
            startup_context=startup_context,
            predecessor_context=inv_predecessors,
            all_sources=all_sources,
        )
        if investment_output:
            agent_results["investment"] = investment_output
        else:
            any_failure = True

        # --- 7. Final Synthesis Agent ---
        synthesis_predecessors = "\n".join(filter(None, [
            self._format_full_output("CEO Strategy", agent_results.get("ceo")),
            self._format_full_output("Market Analysis", agent_results.get("market")),
            self._format_full_output("Product Strategy", agent_results.get("product")),
            self._format_full_output("Marketing & GTM", agent_results.get("marketing")),
            self._format_full_output("Financial Model", agent_results.get("finance")),
            self._format_full_output("Investment Evaluation", agent_results.get("investment")),
        ]))
        synthesis_output = await self._run_agent_step(
            agent_name="synthesis",
            agent_instance=synthesis_agent,
            session_id=session_id,
            startup_context=startup_context,
            predecessor_context=synthesis_predecessors,
            all_sources=all_sources,
        )

        # Finalize Session Status
        final_status = "completed" if not any_failure and synthesis_output else "partially_completed"
        if not synthesis_output and len(agent_results) == 0:
            final_status = "failed"

        session_repository.update_session_status(session_id, final_status)
        execution_log_repository.log_event(
            session_id,
            "system",
            "analysis_completed",
            f"Multi-agent analysis finished with status '{final_status}'.",
            {"status": final_status, "completed_agents": list(agent_results.keys())},
        )
        logger.info("Session %s multi-agent pipeline completed with status: %s", session_id, final_status)

    async def _run_agent_step(
        self,
        agent_name: str,
        agent_instance: Any,
        session_id: str,
        startup_context: Dict[str, Any],
        all_sources: List[Dict[str, Any]],
        predecessor_context: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Executes a single agent step with timing, logging, RAG, retry, and persistence."""
        t0 = time.time()
        started_at = datetime.now(timezone.utc).isoformat()
        display_name = AGENT_DISPLAY_NAMES.get(agent_name, agent_name.capitalize())

        execution_log_repository.log_event(
            session_id, agent_name, "agent_started", f"{display_name} started execution.",
            {"started_at": started_at}
        )
        agent_output_repository.update_by_session_and_agent(
            session_id=session_id,
            agent_name=agent_name,
            status="processing",
            started_at=started_at,
        )

        try:
            # 1. Agent-specific RAG retrieval
            if agent_instance:
                query = agent_instance.build_retrieval_query(startup_context)
            else:
                query = f"{startup_context.get('startup_idea')} {startup_context.get('industry')} business model vision"

            execution_log_repository.log_event(
                session_id, agent_name, "retrieval_started", f"Searching knowledge base: '{query[:65]}...'"
            )

            chunks = rag_service.retrieve_context(query=query, top_k=5)
            rag_context, sources = rag_service.build_rag_context(chunks)

            source_refs = []
            for s in sources:
                ref = {
                    "document_name": s.get("document", "Document"),
                    "page": s.get("page"),
                }
                source_refs.append(ref)
                if not any(x.get("document_name") == ref["document_name"] and x.get("page") == ref["page"] for x in all_sources):
                    all_sources.append(ref)

            execution_log_repository.log_event(
                session_id,
                agent_name,
                "retrieval_completed",
                f"Retrieved {len(chunks)} relevant chunks ({len(sources)} source files).",
                {"chunks_retrieved": len(chunks), "sources_count": len(sources)},
            )

            # 2. LLM Reasoning Call
            execution_log_repository.log_event(
                session_id, agent_name, "llm_started", f"Generating structured analysis for {display_name}..."
            )

            if agent_instance:
                result_model = await agent_instance.execute(
                    startup_context=startup_context,
                    rag_context=rag_context,
                    predecessor_context=predecessor_context,
                )
                output_dict = result_model.model_dump()
            else:
                req = StartupAnalysisRequest(
                    startup_idea=startup_context["startup_idea"],
                    target_audience=startup_context["target_audience"],
                    industry=startup_context["industry"],
                    budget=startup_context["budget"],
                    timeline=startup_context["timeline"],
                    notes=startup_context.get("notes"),
                )
                ceo_res = await ceo_agent.analyse(req, rag_context=rag_context)
                output_dict = ceo_res.model_dump()

            if source_refs:
                output_dict["sources_used"] = source_refs

            execution_log_repository.log_event(
                session_id, agent_name, "validation_passed", f"Validated {display_name} structured deliverables."
            )

            # 3. Complete & Record Execution Duration
            t1 = time.time()
            duration_ms = int((t1 - t0) * 1000)
            completed_at = datetime.now(timezone.utc).isoformat()

            agent_output_repository.update_by_session_and_agent(
                session_id=session_id,
                agent_name=agent_name,
                status="completed",
                output_json=output_dict,
                duration_ms=duration_ms,
                started_at=started_at,
                completed_at=completed_at,
            )

            execution_log_repository.log_event(
                session_id,
                agent_name,
                "agent_completed",
                f"{display_name} completed in {duration_ms / 1000:.1f}s.",
                {"duration_ms": duration_ms, "completed_at": completed_at}
            )
            return output_dict

        except Exception as e:
            t1 = time.time()
            duration_ms = int((t1 - t0) * 1000)
            error_msg = str(e)
            logger.error("Agent %s failed for session %s: %s", agent_name, session_id, error_msg)
            execution_log_repository.log_event(
                session_id, agent_name, "agent_failed", f"{display_name} encountered an error: {error_msg[:100]}",
                {"duration_ms": duration_ms}
            )
            agent_output_repository.update_by_session_and_agent(
                session_id=session_id,
                agent_name=agent_name,
                status="failed",
                error_message=error_msg[:500],
                duration_ms=duration_ms,
                started_at=started_at,
            )
            return None

    def _format_predecessor_summary(self, role: str, output: Optional[Dict[str, Any]]) -> str:
        if not output:
            return ""
        summary = output.get("summary") or output.get("market_summary") or output.get("product_summary") or output.get("financial_summary") or output.get("investment_summary") or output.get("vision_statement") or ""
        return f"[{role} Key Findings]: {summary[:300]}"

    def _format_full_output(self, role: str, output: Optional[Dict[str, Any]]) -> str:
        if not output:
            return f"[{role} Findings]: (Analysis failed or unavailable)"
        import json
        clean_dump = {k: v for k, v in output.items() if not k.startswith("_") and k != "sources_used"}
        return f"[{role} Full Structured Findings]:\n{json.dumps(clean_dump, default=str)}"

    def get_analysis_status(self, session_id: str) -> MultiAgentStatusResponse:
        """Calculates live progress metrics, agent durations, and agent status array for a session."""
        session = session_repository.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

        agent_records = agent_output_repository.get_session_agent_outputs(session_id)

        agents_list: List[AgentStatusInfo] = []
        agents_map: Dict[str, AgentStatusInfo] = {}
        completed_count = 0
        current_agent = None
        has_synthesis = False

        for name in self.AGENTS_SEQUENCE:
            record = next((r for r in agent_records if r.get("agent_name") == name), None)
            st = record.get("status", "pending") if record else "pending"
            out = (record.get("output_json") or {}) if record else {}
            meta = out.get("_meta", {})
            sources_count = len(out.get("sources_used", []))

            # Duration and timestamps from columns or _meta fallback
            dur = record.get("duration_ms") if record and record.get("duration_ms") is not None else meta.get("duration_ms")
            s_at = record.get("started_at") if record and record.get("started_at") else meta.get("started_at")
            c_at = record.get("completed_at") if record and record.get("completed_at") else meta.get("completed_at")
            if not c_at and st == "completed" and record:
                c_at = str(record.get("updated_at"))

            info = AgentStatusInfo(
                name=name,
                display_name=AGENT_DISPLAY_NAMES.get(name, name.capitalize()),
                status=st,
                sources_count=sources_count,
                started_at=str(s_at) if s_at else None,
                completed_at=str(c_at) if c_at else None,
                duration_ms=dur,
                error_message=record.get("error_message") if record else None,
            )
            agents_list.append(info)
            agents_map[name] = info

            if st == "completed":
                completed_count += 1
                if name == "synthesis":
                    has_synthesis = True
            elif st == "processing":
                current_agent = name

        progress = int((completed_count / len(self.AGENTS_SEQUENCE)) * 100)
        events = execution_log_repository.get_events(session_id, limit=200)

        session_st = session.get("status", "created")

        return MultiAgentStatusResponse(
            success=True,
            session_id=session_id,
            overall_status=session_st,
            session_status=session_st,
            progress_percentage=progress,
            overall_progress=progress,
            current_agent=current_agent,
            started_at=session.get("created_at"),
            updated_at=session.get("updated_at"),
            agents=agents_list,
            agents_map=agents_map,
            has_final_report=has_synthesis,
            events_count=len(events),
            logs_count=len(events),
        )

    async def retry_agent(self, session_id: str, agent_name: str) -> Dict[str, Any]:
        """Reruns a single failed agent."""
        if agent_name not in self.AGENTS_SEQUENCE:
            raise HTTPException(status_code=400, detail=f"Unknown agent '{agent_name}'.")

        session = session_repository.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

        agent_instances = {
            "market": market_agent,
            "product": product_agent,
            "marketing": marketing_agent,
            "finance": finance_agent,
            "investment": investment_agent,
            "synthesis": synthesis_agent,
        }

        startup_context = {
            "startup_idea": session.get("startup_idea", ""),
            "target_audience": session.get("target_audience", ""),
            "industry": session.get("industry", ""),
            "budget": session.get("budget", ""),
            "timeline": session.get("timeline", ""),
            "notes": session.get("notes") or "",
        }

        output = await self._run_agent_step(
            agent_name=agent_name,
            agent_instance=agent_instances.get(agent_name),
            session_id=session_id,
            startup_context=startup_context,
            all_sources=[],
        )

        return {"success": bool(output is not None), "agent": agent_name, "output": output}


agent_orchestrator = AgentOrchestrator()
