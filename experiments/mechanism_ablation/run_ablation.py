"""
Master Runner for Experiment A: Mechanism Ablation.
Evaluates A1 through A9, Search Budget Sweep, Verification Sweep, and RESOLVE Sweep.
Categorizes failures according to the 11-category failure taxonomy.
"""

import os
import sys
import json
import time
from typing import Dict, List, Any

# Ensure project root is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
proj_root = os.path.dirname(curr_dir)
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

from decisive_paartha.config.models import get_model_config
from decisive_paartha.systems.llm_client import FrontierLLMClient
from decisive_paartha.benchmark.task_corpus import get_benchmark_corpus, BenchmarkTask
from decisive_paartha.evaluation.evaluator import BlindedEvaluator
from decisive_paartha.evaluation.metrics import aggregate_system_metrics

from mechanism_ablation.systems_ablation import (
    create_ablation_system, ModularAblationAgent
)

TAXONOMY_CATEGORIES = [
    "REPRESENTATION", "UNDERSTANDING", "TOOL_SELECTION", "PARAMETER_BINDING",
    "CONTRACT_VIOLATION", "EXECUTION", "VERIFICATION", "SEARCH", "RECOVERY",
    "GENERATION", "MODEL_LIMITATION"
]

def classify_failure_mode(task: BenchmarkTask, result: Dict[str, Any], eval_res: Dict[str, Any]) -> str:
    """Classifies task failure into the 11-category taxonomy."""
    sys_name = result.get("system", "")
    trace = result.get("trace", [])
    inv_calls = result.get("invalid_tool_calls", 0)

    if "A1" in sys_name:
        return "MODEL_LIMITATION"

    # Check trace errors
    errors = [str(step.get("error", "")) for step in trace if not step.get("success", True)]
    
    if any("Constraint" in e or "Binding" in e or "col" in e.lower() for e in errors):
        return "PARAMETER_BINDING"
    if any("ContractViolation" in e or "Precondition" in e for e in errors):
        return "CONTRACT_VIOLATION"
    if any("Verification" in e or "Invariant" in e for e in errors):
        return "VERIFICATION"
    if any("Unknown tool" in e for e in errors):
        return "TOOL_SELECTION"
    if any("Crash" in e or "Execution" in e for e in errors):
        return "EXECUTION"
    if result.get("search_expansions", 0) > 6:
        return "SEARCH"
    if inv_calls > 0:
        return "PARAMETER_BINDING"
    if eval_res.get("partial_score", 0.0) < 0.5:
        return "UNDERSTANDING"
    return "MODEL_LIMITATION"


def run_mechanism_ablation():
    print("=" * 80)
    print("PAARTHA EXPERIMENT A: CONTROLLED MECHANISM ABLATION")
    print("Isolating Contracts, RESOLVE, Invariant Verification, and SET-CR Search")
    print("=" * 80)

    model_config = get_model_config()
    print(f"[Model Provider] {model_config.provider} | Model: {model_config.model_name}")
    print(f"[API Endpoint] {model_config.api_base_url}")
    print(f"[API Key Configured] {'YES' if model_config.api_key else 'NO (Simulated)'}")

    client = FrontierLLMClient(model_config)
    evaluator = BlindedEvaluator()
    corpus = get_benchmark_corpus()
    eval_tasks = corpus["level2"] + corpus["level3_transfer"]
    print(f"[Corpus] Evaluating {len(eval_tasks)} tasks across ablation systems ({len(corpus['level2'])} Level 2, {len(corpus['level3_transfer'])} Level 3).")

    results_dir = os.path.join(curr_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # 1. PRIMARY MATRIX: A1 THROUGH A9
    # --------------------------------------------------------------------------
    system_ids = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"]
    matrix_results: Dict[str, Any] = {}
    failure_distribution: Dict[str, Dict[str, int]] = {sid: {cat: 0 for cat in TAXONOMY_CATEGORIES} for sid in system_ids}

    print("\n" + "-" * 80)
    print("[MATRIX] Running Systems A1 through A9...")
    print("-" * 80)

    for sid in system_ids:
        sys_obj = create_ablation_system(sid, client)
        print(f"--> Running System {sid}: {sys_obj.name}")
        records = []

        for task in eval_tasks:
            res = sys_obj.solve_task(task.description, task.initial_state)
            eval_res = evaluator.evaluate_result(task, res)

            # Classify failure if not exact match
            if not eval_res.get("exact_match", False):
                cat = classify_failure_mode(task, res, eval_res)
                eval_res["failure_attribution"] = cat
                failure_distribution[sid][cat] += 1
            else:
                eval_res["failure_attribution"] = "NONE"

            records.append(eval_res)
            time.sleep(0.3)  # API pacing

        agg = aggregate_system_metrics(records)
        matrix_results[sid] = {
            "name": sys_obj.name,
            "metrics": agg,
            "failures": failure_distribution[sid],
            "details": records
        }
        print(f"    Success: {agg['success_rate']*100:.1f}% | Avg F1: {agg['avg_partial_score']:.3f} | Invalid Calls: {agg['total_invalid_tool_calls']} | Latency: {agg['avg_latency_ms']:.1f}ms | Tokens: {agg['total_tokens']}")

    # --------------------------------------------------------------------------
    # 2. SEARCH BUDGET SWEEP: k in [0, 1, 2, 4, 8, 16]
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[SUB-ABLATION 1] Search Budget Sweep (k in [0, 1, 2, 4, 8, 16])...")
    print("-" * 80)
    search_sweep_results: Dict[int, Any] = {}

    for k in [0, 1, 2, 4, 8, 16]:
        agent = ModularAblationAgent(
            f"Search_Budget_k_{k}", client,
            use_contracts=True, use_resolve=True, use_verification=True,
            use_search=(k > 0), search_budget=k
        )
        records = []
        for task in eval_tasks[:4]:  # Standardized 4-task subset for depth sweep
            res = agent.solve_task(task.description, task.initial_state)
            eval_res = evaluator.evaluate_result(task, res)
            records.append(eval_res)
            time.sleep(0.2)
        agg = aggregate_system_metrics(records)
        search_sweep_results[k] = agg
        print(f"  k = {k:2d}: Success = {agg['success_rate']*100:.1f}% | Expansions = {agg['total_search_expansions']} | Latency = {agg['avg_latency_ms']:.1f}ms")

    # --------------------------------------------------------------------------
    # 3. VERIFICATION ISOLATION SWEEP: [None, Invariant Check, Invariant + Rollback]
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[SUB-ABLATION 2] Verification Isolation Sweep...")
    print("-" * 80)
    verification_sweep_results: Dict[str, Any] = {}

    v_configs = [
        ("None", False, False),
        ("Invariant_Check_Only", True, False),
        ("Invariant_Plus_Rollback", True, True)
    ]
    for v_name, use_v, use_s in v_configs:
        agent = ModularAblationAgent(
            f"Verification_{v_name}", client,
            use_contracts=True, use_resolve=True,
            use_verification=use_v, use_search=use_s, search_budget=4
        )
        records = []
        for task in eval_tasks[:4]:
            res = agent.solve_task(task.description, task.initial_state)
            eval_res = evaluator.evaluate_result(task, res)
            records.append(eval_res)
            time.sleep(0.2)
        agg = aggregate_system_metrics(records)
        verification_sweep_results[v_name] = agg
        print(f"  Verification Mode '{v_name}': Success = {agg['success_rate']*100:.1f}% | Avg F1 = {agg['avg_partial_score']:.3f} | Invalid Calls = {agg['total_invalid_tool_calls']}")

    # --------------------------------------------------------------------------
    # 4. RESOLVE ISOLATION SWEEP: [Direct, Contracts, RESOLVE, RESOLVE + Verify]
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[SUB-ABLATION 3] RESOLVE Isolation Sweep...")
    print("-" * 80)
    resolve_sweep_results: Dict[str, Any] = {}

    r_configs = [
        ("Direct_LLM", False, False, False),
        ("LLM_Plus_Contracts", True, False, False),
        ("LLM_Plus_RESOLVE", False, True, False),
        ("RESOLVE_Plus_Verification", True, True, True)
    ]
    for r_name, u_con, u_res, u_ver in r_configs:
        agent = ModularAblationAgent(
            f"RESOLVE_Sweep_{r_name}", client,
            use_contracts=u_con, use_resolve=u_res,
            use_verification=u_ver, use_search=False
        )
        records = []
        for task in eval_tasks[:4]:
            res = agent.solve_task(task.description, task.initial_state)
            eval_res = evaluator.evaluate_result(task, res)
            records.append(eval_res)
            time.sleep(0.2)
        agg = aggregate_system_metrics(records)
        resolve_sweep_results[r_name] = agg
        print(f"  Level '{r_name}': Success = {agg['success_rate']*100:.1f}% | Invalid Calls = {agg['total_invalid_tool_calls']} | F1 = {agg['avg_partial_score']:.3f}")

    # --------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------
    full_payload = {
        "metadata": {
            "experiment": "PAARTHA_MECHANISM_ABLATION",
            "provider": model_config.provider,
            "model_name": model_config.model_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "primary_matrix_a1_a9": matrix_results,
        "search_budget_sweep": {str(k): v for k, v in search_sweep_results.items()},
        "verification_sweep": verification_sweep_results,
        "resolve_sweep": resolve_sweep_results
    }

    out_file = os.path.join(results_dir, "ablation_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, indent=2)

    print("\n" + "=" * 80)
    print(f"EXPERIMENT A COMPLETED. Results serialized to:\n{out_file}")
    print("=" * 80)

if __name__ == "__main__":
    run_mechanism_ablation()
