import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ventureos.evaluation.regression")


class RegressionEvaluator:
    def __init__(self, baseline_path: Optional[str] = None):
        if baseline_path:
            self.baseline_path = Path(baseline_path)
        else:
            self.baseline_path = Path(__file__).parent / "baselines" / "baseline_metrics.json"
        self._baseline_data = self._load_baselines()

    def _load_baselines(self) -> Dict[str, Any]:
        try:
            if self.baseline_path.exists():
                with open(self.baseline_path, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning("Could not load baseline metrics from %s: %s", self.baseline_path, e)
        return {}

    def compare_metrics(
        self,
        rag_metrics: Dict[str, Any],
        agent_scores: Dict[str, float],
        grounding_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compares evaluation metrics against defined baseline thresholds.
        Detects measurable quality degradation rather than text variation.
        """
        baselines = self._baseline_data
        regressions: List[str] = []
        checks_passed: List[str] = []

        # 1. RAG Thresholds
        rag_base = baselines.get("rag", {})
        min_p = rag_base.get("minimum_precision_at_5", 0.40)
        min_hr = rag_base.get("minimum_hit_rate_at_5", 0.70)
        min_mrr = rag_base.get("minimum_mrr", 0.50)

        curr_p = rag_metrics.get("avg_precision_at_k", 0.0)
        curr_hr = rag_metrics.get("avg_hit_rate_at_k", 0.0)
        curr_mrr = rag_metrics.get("avg_mrr", 0.0)

        if curr_p < min_p:
            regressions.append(f"RAG Precision@5 degraded: {curr_p:.2f} < threshold {min_p:.2f}")
        else:
            checks_passed.append(f"RAG Precision@5 ({curr_p:.2f} >= {min_p:.2f})")

        if curr_hr < min_hr:
            regressions.append(f"RAG HitRate@5 degraded: {curr_hr:.2f} < threshold {min_hr:.2f}")
        else:
            checks_passed.append(f"RAG HitRate@5 ({curr_hr:.2f} >= {min_hr:.2f})")

        if curr_mrr < min_mrr:
            regressions.append(f"RAG MRR degraded: {curr_mrr:.2f} < threshold {min_mrr:.2f}")
        else:
            checks_passed.append(f"RAG MRR ({curr_mrr:.2f} >= {min_mrr:.2f})")

        # 2. Agent Quality Thresholds
        agent_base = baselines.get("agents", {})
        min_avg_score = agent_base.get("minimum_average_quality_score", 0.80)
        min_single_score = agent_base.get("minimum_single_agent_score", 0.70)

        if agent_scores:
            avg_score = sum(agent_scores.values()) / len(agent_scores)
            if avg_score < min_avg_score:
                regressions.append(f"Average Agent Quality degraded: {avg_score:.2f} < threshold {min_avg_score:.2f}")
            else:
                checks_passed.append(f"Average Agent Quality ({avg_score:.2f} >= {min_avg_score:.2f})")

            for agent_name, score in agent_scores.items():
                if score < min_single_score:
                    regressions.append(f"Agent '{agent_name}' score degraded: {score:.2f} < {min_single_score:.2f}")
                else:
                    checks_passed.append(f"Agent '{agent_name}' ({score:.2f} >= {min_single_score:.2f})")

        # 3. Grounding Thresholds
        unsupported_count = len(grounding_metrics.get("unsupported_source_references", []))
        if unsupported_count > 0:
            regressions.append(f"Found {unsupported_count} unsupported source references in deliverables.")
        else:
            checks_passed.append("Zero unsupported source references (Grounding 100%)")

        status = "PASSED" if not regressions else "REGRESSION_DETECTED"

        return {
            "status": status,
            "passed": len(regressions) == 0,
            "regressions_count": len(regressions),
            "regressions": regressions,
            "checks_passed": checks_passed,
            "thresholds_used": baselines,
        }


regression_evaluator = RegressionEvaluator()
