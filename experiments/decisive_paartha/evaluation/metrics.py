"""
Metrics Engine for Paartha Decisive Experiment.
Calculates Capability, Reliability, Efficiency, Learning, and Search metrics.
"""

from typing import Dict, List, Any, Optional, Tuple
from decisive_paartha.tools.primitive_tools import State

def calculate_state_match(actual: State, expected: State) -> Tuple[bool, float]:
    """
    Evaluates whether actual State matches expected State.
    Returns (exact_match_boolean, partial_f1_score).
    """
    exact = actual.equals(expected)
    if exact:
        return True, 1.0
    
    act_rows = actual.to_dict_list()
    exp_rows = expected.to_dict_list()
    
    if not act_rows or not exp_rows:
        return False, 0.0

    act_cols = actual.columns()
    exp_cols = expected.columns()
    col_jaccard = len(act_cols.intersection(exp_cols)) / max(1, len(act_cols.union(exp_cols)))
    row_count_ratio = min(len(act_rows), len(exp_rows)) / max(len(act_rows), len(exp_rows))
    
    # Check value alignment on available rows
    val_matches = 0
    total_checked = 0
    for r_idx in range(min(len(act_rows), len(exp_rows))):
        for c in act_cols.intersection(exp_cols):
            total_checked += 1
            if str(act_rows[r_idx].get(c)) == str(exp_rows[r_idx].get(c)):
                val_matches += 1
    
    val_accuracy = (val_matches / max(1, total_checked))
    f1 = 0.3 * col_jaccard + 0.3 * row_count_ratio + 0.4 * val_accuracy
    return False, round(f1, 4)


def aggregate_system_metrics(run_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates individual task evaluations into comprehensive system metrics."""
    if not run_records:
        return {}

    total = len(run_records)
    exact_successes = sum(1 for r in run_records if r.get("exact_match", False))
    avg_f1 = sum(r.get("partial_score", 0.0) for r in run_records) / total
    total_crashes = sum(r.get("crashes", 0) for r in run_records)
    total_invalid_calls = sum(r.get("invalid_tool_calls", 0) for r in run_records)
    total_tool_calls = sum(r.get("tool_calls_count", 0) for r in run_records)
    total_search_expansions = sum(r.get("search_expansions", 0) for r in run_records)
    avg_latency = sum(r.get("latency_ms", 0.0) for r in run_records) / total
    total_tokens = sum(r.get("tokens", 0) for r in run_records)

    return {
        "tasks_evaluated": total,
        "exact_success_count": exact_successes,
        "success_rate": round(exact_successes / total, 4),
        "avg_partial_score": round(avg_f1, 4),
        "total_crashes": total_crashes,
        "crash_rate": round(total_crashes / total, 4),
        "total_invalid_tool_calls": total_invalid_calls,
        "invalid_tool_call_rate": round(total_invalid_calls / max(1, total_tool_calls), 4),
        "total_tool_calls": total_tool_calls,
        "total_search_expansions": total_search_expansions,
        "avg_latency_ms": round(avg_latency, 2),
        "total_tokens": total_tokens
    }
