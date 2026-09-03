import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.evaluation.metrics import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_hit_rate_at_k,
    calculate_mrr,
    calculate_f1_score,
)
from app.evaluation.agent_evaluator import agent_evaluator
from app.evaluation.grounding_evaluator import grounding_evaluator
from app.evaluation.regression_evaluator import regression_evaluator


def test_rag_metrics_calculations():
    retrieved = ["doc_pitch_deck", "doc_financials", "doc_competitors", "doc_team", "doc_random"]
    expected = ["pitch_deck", "financials"]

    p_5 = calculate_precision_at_k(retrieved, expected, k=5)
    r_5 = calculate_recall_at_k(retrieved, expected, k=5)
    hr_5 = calculate_hit_rate_at_k(retrieved, expected, k=5)
    mrr = calculate_mrr(retrieved, expected)

    assert p_5 == 0.4, f"Expected 0.4, got {p_5}"
    assert r_5 == 1.0, f"Expected 1.0, got {r_5}"
    assert hr_5 == 1.0, f"Expected 1.0, got {hr_5}"
    assert mrr == 1.0, f"Expected 1.0, got {mrr}"
    print("[PASS] test_rag_metrics_calculations")


def test_mrr_first_relevant_at_rank_2():
    retrieved = ["doc_irrelevant", "doc_pitch_deck", "doc_random"]
    expected = ["pitch_deck"]

    mrr = calculate_mrr(retrieved, expected)
    assert mrr == 0.5, f"Expected 0.5 (rank 2), got {mrr}"
    print("[PASS] test_mrr_first_relevant_at_rank_2")


def test_agent_evaluator_all_agents():
    sample_outputs = {
        "ceo": {
            "executive_summary": "Comprehensive venture strategy for automated healthcare operations.",
            "strategic_moat": "High switching cost EHR integrations and proprietary clinical models.",
            "core_thesis": "Clinics waste 30% of administrative hours on manual insurance pre-authorization.",
            "strategic_recommendations": ["Focus on tier 2 outpatient clinics", "Build direct EHR connector"],
        },
        "investment": {
            "investment_score": 82,
            "investment_readiness": "Seed ready with verified hospital demand.",
            "major_risks": ["EHR API vendor lock-in"],
            "critical_assumptions": ["Clinics willing to route HIPAA data through cloud proxy"],
        },
    }

    ceo_res = agent_evaluator.evaluate_ceo_output(sample_outputs["ceo"])
    assert ceo_res["passed"] is True
    assert ceo_res["overall_score"] == 1.0

    inv_res = agent_evaluator.evaluate_investment_output(sample_outputs["investment"])
    assert inv_res["passed"] is True
    assert inv_res["overall_score"] == 1.0
    print("[PASS] test_agent_evaluator_all_agents")


def test_grounding_evaluator_detects_unsupported_reference():
    agent_outputs = {
        "market": {
            "tam_sam_som": "TAM is $50 billion globally.",
            "sources_used": [{"document_name": "Fabricated_Report.pdf"}],
            "market_risks": ["Procurement delays"],
        }
    }
    retrieved_sources = [{"document_name": "Actual_Founder_Deck.pdf"}]

    res = grounding_evaluator.evaluate_grounding(agent_outputs, retrieved_sources)
    assert res["is_grounding_valid"] is False
    assert res["invalid_evidence_count"] == 1
    assert len(res["unsupported_source_references"]) == 1
    assert res["unsupported_source_references"][0]["claimed_source"] == "Fabricated_Report.pdf"
    print("[PASS] test_grounding_evaluator_detects_unsupported_reference")


def test_regression_evaluator_baseline_comparison():
    rag_metrics = {
        "avg_precision_at_k": 0.60,
        "avg_hit_rate_at_k": 0.85,
        "avg_mrr": 0.75,
    }
    agent_scores = {
        "ceo": 0.90,
        "market": 0.85,
        "product": 0.90,
    }
    grounding_metrics = {
        "unsupported_source_references": [],
    }

    result = regression_evaluator.compare_metrics(rag_metrics, agent_scores, grounding_metrics)
    assert result["passed"] is True
    assert result["status"] == "PASSED"
    assert len(result["regressions"]) == 0
    print("[PASS] test_regression_evaluator_baseline_comparison")


if __name__ == "__main__":
    test_rag_metrics_calculations()
    test_mrr_first_relevant_at_rank_2()
    test_agent_evaluator_all_agents()
    test_grounding_evaluator_detects_unsupported_reference()
    test_regression_evaluator_baseline_comparison()
    print("\nAll Evaluation Tests Passed Successfully!")
