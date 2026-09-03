import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("ventureos.evaluation.agent")


class AgentEvaluator:
    """
    Automated structural and requirement quality checks for specialized venture agents.
    Evaluates semantic and structural presence rather than exact string equality.
    """

    def evaluate_ceo_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Tuple[str, bool]] = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("executive_summary_present", bool(output.get("executive_summary") and len(str(output.get("executive_summary"))) > 30)),
            ("strategic_moat_present", bool(output.get("strategic_moat") and len(str(output.get("strategic_moat"))) > 15)),
            ("core_thesis_present", bool(output.get("core_thesis") and len(str(output.get("core_thesis"))) > 15)),
            ("strategic_recommendations_actionable", bool(output.get("strategic_recommendations") and len(output.get("strategic_recommendations", [])) >= 2)),
        ]
        return self._build_result("ceo", checks)

    def evaluate_market_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Tuple[str, bool]] = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("target_customers_identified", bool(output.get("target_customers") and len(output.get("target_customers", [])) >= 1)),
            ("tam_sam_som_evaluated", bool(output.get("tam_sam_som") and len(str(output.get("tam_sam_som"))) > 20)),
            ("competitors_identified", bool(output.get("competitor_analysis") and len(output.get("competitor_analysis", [])) >= 1)),
            ("market_risks_included", bool(output.get("market_risks") and len(output.get("market_risks", [])) >= 1)),
        ]
        return self._build_result("market", checks)

    def evaluate_product_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Tuple[str, bool]] = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("mvp_features_specified", bool(output.get("mvp_features") and len(output.get("mvp_features", [])) >= 2)),
            ("system_architecture_defined", bool(output.get("system_architecture") and len(str(output.get("system_architecture"))) > 20)),
            ("differentiation_factor_present", bool(output.get("differentiation_factor") and len(str(output.get("differentiation_factor"))) > 15)),
            ("product_risks_present", bool(output.get("product_risks") and len(output.get("product_risks", [])) >= 1)),
        ]
        return self._build_result("product", checks)

    def evaluate_marketing_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Tuple[str, bool]] = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("icp_persona_defined", bool(output.get("icp_persona") and len(str(output.get("icp_persona"))) > 20)),
            ("acquisition_channels_specified", bool(output.get("acquisition_channels") and len(output.get("acquisition_channels", [])) >= 2)),
            ("positioning_statement_present", bool(output.get("positioning_statement") and len(str(output.get("positioning_statement"))) > 15)),
            ("gtm_motion_defined", bool(output.get("gtm_motion") and len(str(output.get("gtm_motion"))) > 15)),
        ]
        return self._build_result("marketing", checks)

    def evaluate_finance_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Tuple[str, bool]] = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("revenue_streams_identified", bool(output.get("revenue_streams") and len(output.get("revenue_streams", [])) >= 1)),
            ("unit_economics_defined", bool(output.get("unit_economics") and len(str(output.get("unit_economics"))) > 20)),
            ("financial_risks_included", bool(output.get("financial_risks") and len(output.get("financial_risks", [])) >= 1)),
            ("runway_analysis_present", bool(output.get("runway_months") or output.get("burn_rate"))),
        ]
        return self._build_result("finance", checks)

    def evaluate_investment_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        score = output.get("investment_score")
        valid_score = isinstance(score, (int, float)) and 0 <= score <= 100
        checks: List[Tuple[str, bool]] = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("investment_score_bounded_0_100", valid_score),
            ("investment_readiness_stated", bool(output.get("investment_readiness") and len(str(output.get("investment_readiness"))) > 10)),
            ("major_risks_identified", bool(output.get("major_risks") and len(output.get("major_risks", [])) >= 1)),
            ("critical_assumptions_stated", bool(output.get("critical_assumptions") and len(output.get("critical_assumptions", [])) >= 1)),
        ]
        return self._build_result("investment", checks)

    def evaluate_synthesis_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Tuple[str, bool]] = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("executive_summary_present", bool(output.get("executive_summary") and len(str(output.get("executive_summary"))) > 30)),
            ("top_5_priorities_present", bool(output.get("top_5_priorities") and len(output.get("top_5_priorities", [])) >= 3)),
            ("final_verdict_present", bool(output.get("final_verdict") and len(str(output.get("final_verdict"))) > 2)),
            ("conflicting_assessments_handled", "conflicting_assessments" in output),
        ]
        return self._build_result("synthesis", checks)

    def evaluate_agent(self, agent_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
        method = getattr(self, f"evaluate_{agent_name}_output", None)
        if callable(method):
            return method(output)
        # Fallback generic check
        checks = [
            ("schema_non_empty", bool(output and isinstance(output, dict))),
            ("has_keys", len(output.keys()) >= 2 if isinstance(output, dict) else False),
        ]
        return self._build_result(agent_name, checks)

    def _build_result(self, agent_name: str, checks: List[Tuple[str, bool]]) -> Dict[str, Any]:
        passed_count = sum(1 for _, passed in checks if passed)
        total_count = len(checks)
        score = round(passed_count / float(total_count), 4) if total_count > 0 else 0.0
        return {
            "agent": agent_name,
            "overall_score": score,
            "passed_count": passed_count,
            "total_count": total_count,
            "passed": score >= 0.80,
            "checks": [{"name": name, "passed": passed} for name, passed in checks],
        }


agent_evaluator = AgentEvaluator()
