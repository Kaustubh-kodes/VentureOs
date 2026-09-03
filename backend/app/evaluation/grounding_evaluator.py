import logging
from typing import Dict, Any, List, Set

logger = logging.getLogger("ventureos.evaluation.grounding")


class GroundingEvaluator:
    """
    Evaluates evidence attribution, grounding integrity, and unsupported claims.
    Verifies that claims labeled as FOUNDER EVIDENCE actually correspond to retrieved documents.
    """

    def evaluate_grounding(
        self,
        agent_outputs: Dict[str, Dict[str, Any]],
        retrieved_sources: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validates that sources claimed in agent deliverables genuinely exist
        within the retrieved RAG knowledge chunks for that session.
        """
        valid_retrieved_docs: Set[str] = set()
        for src in retrieved_sources:
            name = src.get("document_name") or src.get("document") or ""
            if name:
                valid_retrieved_docs.add(name.lower().strip())

        valid_evidence_count = 0
        invalid_evidence_count = 0
        unsupported_references: List[Dict[str, Any]] = []
        assumptions_identified = 0
        classification_issues: List[str] = []

        for agent_name, out in agent_outputs.items():
            if not isinstance(out, dict):
                continue

            sources_used = out.get("sources_used", [])
            for s in sources_used:
                doc_name = s.get("document_name") if isinstance(s, dict) else str(s)
                doc_clean = doc_name.lower().strip()

                if valid_retrieved_docs and doc_clean not in valid_retrieved_docs:
                    # Claimed source was not in retrieved context
                    invalid_evidence_count += 1
                    unsupported_references.append({
                        "agent": agent_name,
                        "claimed_source": doc_name,
                        "reason": "Source document was not retrieved or passed into agent context",
                    })
                else:
                    valid_evidence_count += 1

            # Check assumption classification
            for key in ["key_risks", "major_risks", "critical_assumptions", "market_risks", "financial_risks"]:
                val = out.get(key)
                if isinstance(val, list):
                    assumptions_identified += len(val)

            # Detect potential misclassifications (e.g. bold claims without source backing)
            if agent_name in ("market", "finance") and not sources_used:
                thesis = str(out.get("tam_sam_som", "") or out.get("unit_economics", ""))
                if "billion" in thesis.lower() or "trillion" in thesis.lower():
                    classification_issues.append(
                        f"[{agent_name.upper()}] Large market/financial claims without cited founder evidence."
                    )

        total_evidence_refs = valid_evidence_count + invalid_evidence_count
        grounding_rate = (
            round(valid_evidence_count / float(total_evidence_refs), 4)
            if total_evidence_refs > 0
            else 1.0
        )

        return {
            "valid_evidence_count": valid_evidence_count,
            "invalid_evidence_count": invalid_evidence_count,
            "grounding_rate": grounding_rate,
            "unsupported_source_references": unsupported_references,
            "assumptions_identified": assumptions_identified,
            "classification_issues": classification_issues,
            "is_grounding_valid": invalid_evidence_count == 0,
            "summary": (
                f"Verified {valid_evidence_count} evidence references ({invalid_evidence_count} invalid). "
                f"Identified {assumptions_identified} assumptions across agents."
            ),
        }


grounding_evaluator = GroundingEvaluator()
