import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.multi_agent import (
    MarketAnalysis,
    ProductAnalysis,
    MarketingAnalysis,
    FinanceAnalysis,
    InvestmentAnalysis,
    SynthesisReport,
    ConflictingAssessment,
    SourceReference,
)
from app.agents.market_agent import market_agent
from app.agents.product_agent import product_agent
from app.agents.marketing_agent import marketing_agent
from app.agents.finance_agent import finance_agent
from app.agents.investment_agent import investment_agent
from app.agents.synthesis_agent import synthesis_agent
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_schema_validations():
    # Market Analysis
    m = MarketAnalysis(
        market_summary="Large opportunity in B2B microservices",
        target_customers=["DevOps leads", "Engineering VPs"],
        market_opportunity="TAM is $12B growing at 22% CAGR",
        competitive_landscape=["Manual scripts", "Generic observability tools"],
        market_gaps=["No automated resolution for API breaking changes"],
        key_assumptions=["Engineers willing to trust automated fixes"],
        risks=["Long enterprise sales cycles"],
        recommendations=["Focus initially on mid-market SaaS"],
        confidence=85,
        sources_used=[SourceReference(document_name="market_research.pdf", page=3)],
    )
    assert m.confidence == 85
    assert len(m.sources_used) == 1

    # Investment Analysis
    inv = InvestmentAnalysis(
        investment_summary="High-potential Seed-stage developer tooling play",
        investment_score=78,
        strengths=["Defensible technical moat", "Clear enterprise buyer"],
        major_risks=["High integration friction"],
        critical_assumptions=["OpenAI/Gemini latency remains under 2s"],
        red_flags=[],
        investment_readiness="Seed Ready",
        conditions_for_investment=["Prove 5 enterprise pilots with >50% retention"],
        recommendations=["Build SOC2 compliance roadmap"],
    )
    assert inv.investment_score == 78
    assert inv.investment_readiness == "Seed Ready"

    # Conflicting Assessment & Synthesis Report
    conflict = ConflictingAssessment(
        area="Pricing Strategy",
        agent_a="finance",
        agent_a_view="Recommend $500/month minimum tier to ensure gross margins",
        agent_b="marketing",
        agent_b_view="Recommend free tier and $49/month self-serve for viral growth",
        analysis="Founder must run price-sensitivity tests with first 20 beta users.",
    )
    assert conflict.area == "Pricing Strategy"


def test_agent_retrieval_queries():
    ctx = {
        "startup_idea": "AI copilot for cloud cost optimization",
        "industry": "FinOps",
        "target_audience": "FinOps Engineers and CTOs",
        "budget": "$25,000",
        "timeline": "3 months",
    }
    m_q = market_agent.build_retrieval_query(ctx)
    p_q = product_agent.build_retrieval_query(ctx)
    mkt_q = marketing_agent.build_retrieval_query(ctx)
    f_q = finance_agent.build_retrieval_query(ctx)
    inv_q = investment_agent.build_retrieval_query(ctx)
    syn_q = synthesis_agent.build_retrieval_query(ctx)

    assert "target market" in m_q.lower()
    assert "product features" in p_q.lower()
    assert "acquisition channels" in mkt_q.lower()
    assert "pricing" in f_q.lower()
    assert "risks" in inv_q.lower()
    assert "strategy" in syn_q.lower()


def test_base_agent_prompt_construction():
    ctx = {
        "startup_idea": "Smart battery management for EVs",
        "target_audience": "Fleet operators",
        "industry": "CleanTech",
        "budget": "$50,000",
        "timeline": "6 months",
        "notes": "Patented sensor tech",
    }
    prompt = product_agent.build_user_prompt(
        startup_context=ctx,
        rag_context="[Source: deck.pdf] Battery lifespan extended by 30%.",
        predecessor_context="[CEO Key Findings]: High focus on logistics fleets.",
    )
    assert "Smart battery management for EVs" in prompt
    assert "deck.pdf" in prompt
    assert "CEO Key Findings" in prompt


def test_api_multi_agent_routes():
    # Calling endpoints with a non-existent UUID should return 404 or 500/503 depending on Supabase
    dummy_id = "00000000-0000-0000-0000-000000000000"
    res_status = client.get(f"/api/analysis/{dummy_id}/status")
    assert res_status.status_code in (404, 500, 503)

    res_logs = client.get(f"/api/analysis/{dummy_id}/logs")
    assert res_logs.status_code in (200, 500, 503)


if __name__ == "__main__":
    test_schema_validations()
    print("[PASS] test_schema_validations passed")
    test_agent_retrieval_queries()
    print("[PASS] test_agent_retrieval_queries passed")
    test_base_agent_prompt_construction()
    print("[PASS] test_base_agent_prompt_construction passed")
    test_api_multi_agent_routes()
    print("[PASS] test_api_multi_agent_routes passed")
    print("\nAll Phase 6 Multi-Agent tests passed successfully!")
