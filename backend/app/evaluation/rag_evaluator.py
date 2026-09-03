import logging
from typing import Dict, Any, List, Optional
from app.services.rag_service import rag_service
from app.evaluation.metrics import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_hit_rate_at_k,
    calculate_mrr,
)

logger = logging.getLogger("ventureos.evaluation.rag")


class RAGEvaluator:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def evaluate_query(
        self,
        query: str,
        expected_sources: List[str],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates RAG retrieval for a single query against expected source identifiers.
        Uses real retrieval via rag_service.retrieve_context.
        """
        chunks = rag_service.retrieve_context(query=query, top_k=self.top_k, session_id=session_id)
        retrieved_identifiers = []
        for c in chunks:
            doc_name = c.get("document_name") or c.get("metadata", {}).get("document_name") or ""
            content_snippet = c.get("content", "")[:120]
            retrieved_identifiers.append(f"{doc_name} {content_snippet}")

        p_at_k = calculate_precision_at_k(retrieved_identifiers, expected_sources, k=self.top_k)
        r_at_k = calculate_recall_at_k(retrieved_identifiers, expected_sources, k=self.top_k)
        hit_rate = calculate_hit_rate_at_k(retrieved_identifiers, expected_sources, k=self.top_k)
        mrr = calculate_mrr(retrieved_identifiers, expected_sources)

        return {
            "query": query,
            "top_k": self.top_k,
            "chunks_retrieved": len(chunks),
            "precision_at_k": p_at_k,
            "recall_at_k": r_at_k,
            "hit_rate_at_k": hit_rate,
            "mrr": mrr,
            "expected_sources": expected_sources,
            "retrieved_sample": [c.get("content", "")[:80] for c in chunks[:3]],
        }

    def evaluate_all(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs RAG retrieval evaluation across a dataset of test cases.
        Calculates macro-averaged metrics.
        """
        results: List[Dict[str, Any]] = []
        for case in test_cases:
            queries = case.get("retrieval_queries", [])
            for q_obj in queries:
                q = q_obj.get("query", "")
                exp = q_obj.get("expected_source_identifiers", [])
                if q:
                    eval_res = self.evaluate_query(query=q, expected_sources=exp)
                    eval_res["case_id"] = case.get("id")
                    results.append(eval_res)

        if not results:
            return {
                "total_queries": 0,
                "avg_precision_at_k": 0.0,
                "avg_recall_at_k": 0.0,
                "avg_hit_rate_at_k": 0.0,
                "avg_mrr": 0.0,
                "evaluations": [],
            }

        avg_p = sum(r["precision_at_k"] for r in results) / len(results)
        avg_r = sum(r["recall_at_k"] for r in results) / len(results)
        avg_hr = sum(r["hit_rate_at_k"] for r in results) / len(results)
        avg_mrr = sum(r["mrr"] for r in results) / len(results)

        return {
            "total_queries": len(results),
            "top_k": self.top_k,
            "avg_precision_at_k": round(avg_p, 4),
            "avg_recall_at_k": round(avg_r, 4),
            "avg_hit_rate_at_k": round(avg_hr, 4),
            "avg_mrr": round(avg_mrr, 4),
            "evaluations": results,
        }


rag_evaluator = RAGEvaluator()
