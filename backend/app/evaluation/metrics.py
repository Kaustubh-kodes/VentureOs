"""
Mathematical definitions for evaluation metrics.
All metrics are based strictly on measurable inputs and deterministic criteria.
"""
from typing import List, Set, Any


def calculate_precision_at_k(retrieved: List[str], expected: List[str], k: int = 5) -> float:
    """
    Precision@K = (Relevant retrieved items in top K) / K
    Measures the purity of the top-K retrieved results.
    """
    if k <= 0:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    expected_set: Set[str] = {e.lower().strip() for e in expected if e}
    if not expected_set:
        return 0.0
    
    hits = sum(1 for item in top_k if any(exp in item.lower().strip() or item.lower().strip() in exp for exp in expected_set))
    return round(hits / float(k), 4)


def calculate_recall_at_k(retrieved: List[str], expected: List[str], k: int = 5) -> float:
    """
    Recall@K = (Relevant retrieved items in top K) / (Total expected relevant items)
    Measures the coverage of expected knowledge chunks retrieved.
    """
    expected_set: Set[str] = {e.lower().strip() for e in expected if e}
    if not expected_set:
        return 1.0  # vacuously satisfied if no expected constraints specified
    top_k = retrieved[:k]
    if not top_k:
        return 0.0

    matched_expected = 0
    for exp in expected_set:
        if any(exp in item.lower().strip() or item.lower().strip() in exp for item in top_k):
            matched_expected += 1

    return round(matched_expected / float(len(expected_set)), 4)


def calculate_hit_rate_at_k(retrieved: List[str], expected: List[str], k: int = 5) -> float:
    """
    Hit Rate@K = 1.0 if at least one relevant result appears in top K, else 0.0.
    """
    expected_set: Set[str] = {e.lower().strip() for e in expected if e}
    if not expected_set:
        return 1.0
    top_k = retrieved[:k]
    for item in top_k:
        if any(exp in item.lower().strip() or item.lower().strip() in exp for exp in expected_set):
            return 1.0
    return 0.0


def calculate_mrr(retrieved: List[str], expected: List[str]) -> float:
    """
    Mean Reciprocal Rank (MRR) = 1 / rank_of_first_relevant_item
    Evaluates where the first relevant knowledge source appears in the ranking.
    """
    expected_set: Set[str] = {e.lower().strip() for e in expected if e}
    if not expected_set:
        return 1.0

    for rank_idx, item in enumerate(retrieved, start=1):
        if any(exp in item.lower().strip() or item.lower().strip() in exp for exp in expected_set):
            return round(1.0 / rank_idx, 4)
    return 0.0


def calculate_f1_score(precision: float, recall: float) -> float:
    """Harmonic mean of precision and recall."""
    if (precision + recall) == 0.0:
        return 0.0
    return round(2 * (precision * recall) / (precision + recall), 4)
