"""
Blinded Scoring Evaluator for Paartha Decisive Experiment.
Evaluates system outputs against ground truth state without knowing system identity in advance.
"""

from typing import Dict, Any
from decisive_paartha.benchmark.task_corpus import BenchmarkTask
from decisive_paartha.evaluation.metrics import calculate_state_match
from decisive_paartha.evaluation.failure_taxonomy import attribute_failure

class BlindedEvaluator:
    def evaluate_result(self, task: BenchmarkTask, result: Dict[str, Any]) -> Dict[str, Any]:
        actual_state = result.get("final_state")
        expected_state = task.expected_state

        exact, partial_score = calculate_state_match(actual_state, expected_state)
        
        eval_record = {
            "task_id": task.task_id,
            "level": task.level,
            "domain": task.domain,
            "system": result.get("system"),
            "exact_match": exact,
            "partial_score": partial_score,
            "tool_calls_count": result.get("tool_calls_count", 0),
            "invalid_tool_calls": result.get("invalid_tool_calls", 0),
            "crashes": result.get("crashes", 0),
            "search_expansions": result.get("search_expansions", 0),
            "latency_ms": result.get("latency_ms", 0.0),
            "tokens": result.get("tokens", 0),
            "trace": result.get("trace", []) or result.get("plan_trace", [])
        }

        eval_record["failure_attribution"] = attribute_failure(eval_record)
        return eval_record
