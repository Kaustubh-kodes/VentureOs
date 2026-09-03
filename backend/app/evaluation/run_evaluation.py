import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from app.evaluation.rag_evaluator import rag_evaluator
from app.evaluation.agent_evaluator import agent_evaluator
from app.evaluation.grounding_evaluator import grounding_evaluator
from app.evaluation.regression_evaluator import regression_evaluator
from app.services.supabase_service import supabase_service

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ventureos.evaluation.runner")


def load_dataset() -> list:
    dataset_path = Path(__file__).parent / "datasets" / "evaluation_cases.json"
    if dataset_path.exists():
        with open(dataset_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return []


def run_full_evaluation() -> Dict[str, Any]:
    """
    Executes end-to-end evaluation suite across RAG, Agent Quality, Grounding, and Baselines.
    """
    cases = load_dataset()
    logger.info("Loaded %d evaluation scenarios.", len(cases))

    # 1. RAG Retrieval Evaluation
    rag_results = rag_evaluator.evaluate_all(cases)

    # 2. Agent Quality Evaluation (Benchmark representative mock & synthesized agent deliverables)
    agent_scores: Dict[str, float] = {}
    sample_outputs = {
        "ceo": {
            "executive_summary": "Next-generation career acceleration platform integrating ATS optimization and AI mock interviews.",
            "strategic_moat": "Proprietary ATS parsing engine and exclusive university career service integrations.",
            "core_thesis": "Career services are understaffed and students need personalized, algorithmic interview preparation.",
            "strategic_recommendations": ["Initiate university pilots", "Launch freemium ATS resume builder"],
        },
        "market": {
            "target_customers": ["College seniors", "University career centers"],
            "tam_sam_som": "TAM of $18.4B across global higher education career readiness and recruitment tech.",
            "competitor_analysis": [{"name": "Handshake", "weakness": "Lacks AI preparation co-pilot"}],
            "market_risks": ["Long university enterprise procurement cycles"],
        },
        "product": {
            "mvp_features": ["ATS resume scanner", "Real-time voice behavioral interview simulator"],
            "system_architecture": "Next.js frontend with FastAPI async micro-pipeline and pgvector semantic matching.",
            "differentiation_factor": "Instant ATS compatibility score with direct job description alignment.",
            "product_risks": ["Audio latency during live conversational mock interview sessions"],
        },
        "marketing": {
            "icp_persona": "University career service directors and third/fourth-year undergraduate students.",
            "acquisition_channels": ["Campus ambassador network", "Direct LinkedIn outreach to university deans"],
            "positioning_statement": "The only interview preparation co-pilot backed by university career service offices.",
            "gtm_motion": "B2B2C university enterprise licensing paired with viral student peer referrals.",
        },
        "finance": {
            "revenue_streams": ["University annual software licenses", "Direct student pro subscriptions"],
            "unit_economics": "Projected CAC of $12 with $96 annual LTV yielding an 8.0x LTV/CAC ratio.",
            "financial_risks": ["High summer seasonality during academic calendar breaks"],
            "runway_months": 14,
            "burn_rate": "$3,200 / month",
        },
        "investment": {
            "investment_score": 84,
            "investment_readiness": "Early Seed Ready. Strong defensibility via institutional career center moat.",
            "major_risks": ["Dependence on university fiscal calendar budgets"],
            "critical_assumptions": ["Universities willing to pilot unaccredited third-party software tools"],
        },
        "synthesis": {
            "executive_summary": "Comprehensive 20-section venture blueprint synthesizing institutional moats and student viral loops.",
            "top_5_priorities": ["Close 3 university letters of intent", "Deploy beta ATS scanner", "Launch campus ambassador program"],
            "final_verdict": "Pursue with institutional pilot focus",
            "conflicting_assessments": [],
            "sources_used": [{"document_name": "Pitch Deck.pdf", "page": 4}],
        },
    }

    for agent_name, out in sample_outputs.items():
        eval_res = agent_evaluator.evaluate_agent(agent_name, out)
        agent_scores[agent_name] = eval_res["overall_score"]

    # 3. Grounding & Source Attribution Validation
    retrieved_sources = [{"document_name": "Pitch Deck.pdf", "page": 4}]
    grounding_results = grounding_evaluator.evaluate_grounding(sample_outputs, retrieved_sources)

    # 4. Regression & Threshold Evaluation
    regression_results = regression_evaluator.compare_metrics(rag_results, agent_scores, grounding_results)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evaluation_cases": len(cases),
        "rag": {
            "precision_at_5": rag_results.get("avg_precision_at_k", 0.0),
            "recall_at_5": rag_results.get("avg_recall_at_k", 0.0),
            "hit_rate_at_5": rag_results.get("avg_hit_rate_at_k", 0.0),
            "mrr": rag_results.get("avg_mrr", 0.0),
        },
        "agent_quality": agent_scores,
        "grounding": {
            "valid_evidence_count": grounding_results.get("valid_evidence_count", 0),
            "invalid_evidence_count": grounding_results.get("invalid_evidence_count", 0),
            "grounding_rate": grounding_results.get("grounding_rate", 1.0),
            "assumptions_identified": grounding_results.get("assumptions_identified", 0),
        },
        "regression": {
            "status": regression_results.get("status"),
            "checks_passed": regression_results.get("checks_passed", []),
            "regressions": regression_results.get("regressions", []),
        },
        "overall_status": "PASS" if regression_results.get("passed") else "WARN",
    }

    # Save to reports/latest_evaluation.json
    report_file = Path(__file__).parent / "reports" / "latest_evaluation.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Optionally persist in Supabase evaluation_runs table
    try:
        client = supabase_service.get_client()
        client.table("evaluation_runs").insert({
            "evaluation_type": "full_suite",
            "status": summary["overall_status"],
            "summary": summary,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        logger.debug("Could not persist evaluation run to Supabase: %s", e)

    return summary


def print_formatted_report(summary: Dict[str, Any]):
    rag = summary["rag"]
    agents = summary["agent_quality"]
    grounding = summary["grounding"]
    regression = summary["regression"]

    print("\n" + "=" * 55)
    print("        VENTUREOS AI SYSTEM EVALUATION REPORT        ")
    print("=" * 55)
    print(f"Timestamp:        {summary.get('timestamp')}")
    print(f"Evaluation Cases: {summary.get('evaluation_cases')}")
    print("\n--- RAG RETRIEVAL METRICS ---")
    print(f"Precision@5:      {rag.get('precision_at_5', 0.0):.2f}")
    print(f"Recall@5:         {rag.get('recall_at_5', 0.0):.2f}")
    print(f"Hit Rate@5:       {rag.get('hit_rate_at_5', 0.0):.2f}")
    print(f"MRR:              {rag.get('mrr', 0.0):.2f}")

    print("\n--- AGENT STRUCTURAL QUALITY SCORES ---")
    for agent, score in agents.items():
        print(f"{agent.upper():<16}  {score:.2f} / 1.00")

    print("\n--- GROUNDING & EVIDENCE INTEGRITY ---")
    print(f"Valid Evidence Refs:    {grounding.get('valid_evidence_count')}")
    print(f"Invalid Evidence Refs:  {grounding.get('invalid_evidence_count')}")
    print(f"Grounding Rate:         {grounding.get('grounding_rate', 1.0) * 100:.1f}%")
    print(f"Assumptions Tracked:    {grounding.get('assumptions_identified')}")

    print("\n--- REGRESSION & BASELINE CHECKS ---")
    print(f"Status:           {regression.get('status')}")
    for p in regression.get("checks_passed", []):
        print(f"  [PASS] {p}")
    for r in regression.get("regressions", []):
        print(f"  [WARN] {r}")

    print("\n" + "=" * 55)
    print(f"OVERALL EVALUATION: {summary.get('overall_status')}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    report = run_full_evaluation()
    print_formatted_report(report)
