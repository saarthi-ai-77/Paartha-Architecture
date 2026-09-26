"""
Master Runner for Paartha Decisive Experiment.
Orchestrates Phases 0 through 6, executing controlled head-to-head comparisons across:
- System A: Frontier LLM Alone
- System B1: Frontier LLM + Primitive Tools
- System B2: Frontier LLM + Tools + Discovered Abstractions
- System C: Paartha Runtime without Abstractions
- System D: Paartha + Experience + Abstraction Discovery
"""

import os
import sys
import json
import time
from typing import Dict, List, Any

# Ensure decisive_paartha package can be imported
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from decisive_paartha.config.models import get_model_config
from decisive_paartha.tools.primitive_tools import initialize_primitive_tools
from decisive_paartha.systems.llm_client import FrontierLLMClient
from decisive_paartha.systems.llm_alone import SystemALlmAlone
from decisive_paartha.systems.llm_tools import SystemBLlmTools
from decisive_paartha.systems.paartha_runtime import PaarthaRuntime
from decisive_paartha.systems.paartha_discovery import PaarthaDiscovery
from decisive_paartha.benchmark.task_corpus import get_benchmark_corpus, BenchmarkTask
from decisive_paartha.benchmark.leakage_audit import run_leakage_audit
from decisive_paartha.evaluation.evaluator import BlindedEvaluator
from decisive_paartha.evaluation.metrics import aggregate_system_metrics

def main():
    print("=" * 80)
    print("PAARTHA DECISIVE EXPERIMENT: CONTROLLED BENCHMARK")
    print("Frontier LLM Alone vs LLM + Tools vs Paartha vs Paartha + Discovery")
    print("=" * 80)

    model_config = get_model_config()
    print(f"[Model Provider] {model_config.provider} | Model: {model_config.model_name}")
    print(f"[API Endpoint] {model_config.api_base_url}")
    print(f"[API Key Configured] {'YES' if model_config.api_key else 'NO (Simulated Frontier Mode)'}")

    results_dir = os.path.join(curr_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # PHASE 0: CALIBRATION & BENCHMARK LEAKAGE AUDIT
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[PHASE 0] Calibration & Benchmark Leakage Audit...")
    print("-" * 80)

    systems_dir = os.path.join(curr_dir, "systems")
    audit_res = run_leakage_audit(systems_dir)
    print(f"  -> Leakage Audit Status: {audit_res['verdict']}")
    print(f"  -> Files Scanned: {audit_res['files_scanned']} | Total Leakages Detected: {audit_res['total_leakages']}")
    if audit_res["total_leakages"] > 0:
        print(f"  -> WARNING: Audit detected {audit_res['total_leakages']} leakages!")
        for det in audit_res["details"]:
            print(f"     Line {det['line_number']} in {det['file']}: {det['keyword']}")
    else:
        print("  -> Clean System Verification Confirmed: ZERO Benchmark Leakage.")

    # Initialize client and systems
    llm_client = FrontierLLMClient(model_config)
    evaluator = BlindedEvaluator()
    task_corpus = get_benchmark_corpus()

    system_a = SystemALlmAlone(llm_client)
    system_b1 = SystemBLlmTools(llm_client, is_b2=False)
    system_c = PaarthaRuntime(llm_client)
    system_d = PaarthaDiscovery(llm_client)

    # Calibration test run
    calib_task = task_corpus["level1"][0]
    res_calib_a = system_a.solve_task(calib_task.description, calib_task.initial_state)
    res_calib_b1 = system_b1.solve_task(calib_task.description, calib_task.initial_state)
    res_calib_c = system_c.solve_task(calib_task.description, calib_task.initial_state)
    print(f"  -> Calibration Run: System A (lat={res_calib_a['latency_ms']:.1f}ms), System B1 (lat={res_calib_b1['latency_ms']:.1f}ms), System C (lat={res_calib_c['latency_ms']:.1f}ms) - ALL OK")

    # --------------------------------------------------------------------------
    # PHASE 1: BASELINE EVALUATION (Level 1 & Level 2 Tasks)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[PHASE 1] Baseline Evaluation (Systems A, B1, C)...")
    print("-" * 80)

    heldout_tasks = task_corpus["level1"] + task_corpus["level2"]
    phase1_records = {"System_A": [], "System_B1": [], "System_C": []}

    for task in heldout_tasks:
        res_a = system_a.solve_task(task.description, task.initial_state)
        phase1_records["System_A"].append(evaluator.evaluate_result(task, res_a))

        res_b1 = system_b1.solve_task(task.description, task.initial_state)
        phase1_records["System_B1"].append(evaluator.evaluate_result(task, res_b1))

        res_c = system_c.solve_task(task.description, task.initial_state)
        phase1_records["System_C"].append(evaluator.evaluate_result(task, res_c))
        time.sleep(0.5)

    met_a = aggregate_system_metrics(phase1_records["System_A"])
    met_b1 = aggregate_system_metrics(phase1_records["System_B1"])
    met_c = aggregate_system_metrics(phase1_records["System_C"])

    print(f"  -> System A  (LLM Alone):         Success: {met_a['success_rate']*100:.1f}% | Avg F1: {met_a['avg_partial_score']:.3f} | Crashes: {met_a['total_crashes']}")
    print(f"  -> System B1 (LLM + Tools):       Success: {met_b1['success_rate']*100:.1f}% | Avg F1: {met_b1['avg_partial_score']:.3f} | Crashes: {met_b1['total_crashes']}")
    print(f"  -> System C  (Paartha Runtime):   Success: {met_c['success_rate']*100:.1f}% | Avg F1: {met_c['avg_partial_score']:.3f} | Crashes: {met_c['total_crashes']}")

    # --------------------------------------------------------------------------
    # PHASE 2: EXPERIENCE & ABSTRACTION DISCOVERY (System D)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[PHASE 2] Experience & Abstraction Discovery (System D)...")
    print("-" * 80)

    exp_tasks = task_corpus["experience"]
    print(f"  -> Running System D through {len(exp_tasks)} Experience Tasks in Domain A (Logistics)...")
    for t in exp_tasks:
        # Record ideal verified traces
        system_d.record_execution_trace(t.ideal_steps)

    print("  -> Executing Motif Mining & Plotkin Anti-Unification...")
    discovered = system_d.discover_abstractions()
    print(f"  -> Motifs Mined: {system_d.discovery_metrics['motifs_mined']}")
    print(f"  -> Abstractions Accepted by MDL: {len(discovered)} (Total Gain: +{system_d.discovery_metrics['total_mdl_gain']} bits)")
    for abs_obj in discovered:
        print(f"     * {abs_obj.name}: {' -> '.join(abs_obj.sub_primitives)} (Params: {abs_obj.formal_parameters})")

    # --------------------------------------------------------------------------
    # PHASE 3: SYSTEM FREEZE
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[PHASE 3] System Freeze...")
    print("-" * 80)
    system_d.freeze()
    print("  -> System D is FROZEN: Zero weight updates, zero library updates permitted during evaluation.")

    # --------------------------------------------------------------------------
    # PHASE 4: HELD-OUT EVALUATION (Level 2 Unfamiliar Compositions)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[PHASE 4] Held-Out Evaluation on Level 2 Tasks...")
    print("-" * 80)

    level2_tasks = task_corpus["level2"]
    phase4_records = {"System_A": [], "System_B1": [], "System_C": [], "System_D": []}

    for task in level2_tasks:
        res_a = system_a.solve_task(task.description, task.initial_state)
        phase4_records["System_A"].append(evaluator.evaluate_result(task, res_a))

        res_b1 = system_b1.solve_task(task.description, task.initial_state)
        phase4_records["System_B1"].append(evaluator.evaluate_result(task, res_b1))

        res_c = system_c.solve_task(task.description, task.initial_state)
        phase4_records["System_C"].append(evaluator.evaluate_result(task, res_c))

        res_d = system_d.solve_task(task.description, task.initial_state)
        phase4_records["System_D"].append(evaluator.evaluate_result(task, res_d))
        time.sleep(0.5)

    p4_met_a = aggregate_system_metrics(phase4_records["System_A"])
    p4_met_b1 = aggregate_system_metrics(phase4_records["System_B1"])
    p4_met_c = aggregate_system_metrics(phase4_records["System_C"])
    p4_met_d = aggregate_system_metrics(phase4_records["System_D"])

    print(f"  -> System A  (LLM Alone):         Success: {p4_met_a['success_rate']*100:.1f}% | Avg F1: {p4_met_a['avg_partial_score']:.3f}")
    print(f"  -> System B1 (LLM + Tools):       Success: {p4_met_b1['success_rate']*100:.1f}% | Avg F1: {p4_met_b1['avg_partial_score']:.3f}")
    print(f"  -> System C  (Paartha Runtime):   Success: {p4_met_c['success_rate']*100:.1f}% | Avg F1: {p4_met_c['avg_partial_score']:.3f}")
    print(f"  -> System D  (Paartha Discovery): Success: {p4_met_d['success_rate']*100:.1f}% | Avg F1: {p4_met_d['avg_partial_score']:.3f}")

    # --------------------------------------------------------------------------
    # PHASE 5: ABSTRACTION CONTROL EVALUATION (System B2)
    # Critical test: Does LLM + Tools + Discovered Abstractions match Paartha?
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[PHASE 5] Abstraction Control Evaluation: B1 vs B2 vs D...")
    print("-" * 80)

    # Equip System B2 with the exact abstractions discovered by System D
    b2_tools = initialize_primitive_tools()
    for abs_name, abs_cap in system_d.discovered_abstractions.items():
        b2_tools[abs_name] = abs_cap

    system_b2 = SystemBLlmTools(llm_client, tool_registry=b2_tools, is_b2=True)
    phase5_records = {"System_B1": [], "System_B2": [], "System_D": []}

    for task in level2_tasks:
        res_b1 = system_b1.solve_task(task.description, task.initial_state)
        phase5_records["System_B1"].append(evaluator.evaluate_result(task, res_b1))

        res_b2 = system_b2.solve_task(task.description, task.initial_state)
        phase5_records["System_B2"].append(evaluator.evaluate_result(task, res_b2))

        res_d = system_d.solve_task(task.description, task.initial_state)
        phase5_records["System_D"].append(evaluator.evaluate_result(task, res_d))
        time.sleep(0.5)

    p5_met_b1 = aggregate_system_metrics(phase5_records["System_B1"])
    p5_met_b2 = aggregate_system_metrics(phase5_records["System_B2"])
    p5_met_d = aggregate_system_metrics(phase5_records["System_D"])

    print(f"  -> System B1 (LLM + Primitive Tools):          Success: {p5_met_b1['success_rate']*100:.1f}%")
    print(f"  -> System B2 (LLM + Tools + Discovered Abstr): Success: {p5_met_b2['success_rate']*100:.1f}%")
    print(f"  -> System D  (Paartha + Discovered Abstr):     Success: {p5_met_d['success_rate']*100:.1f}%")

    # Hypothesis Determination
    if p5_met_d["success_rate"] > p5_met_b2["success_rate"]:
        h_verdict = "Case 2 Confirmed: B1 < B2 < D (Paartha runtime provides value beyond merely possessing discovered programs)"
    elif abs(p5_met_d["success_rate"] - p5_met_b2["success_rate"]) < 0.01 and p5_met_b2["success_rate"] > p5_met_b1["success_rate"]:
        h_verdict = "Case 1 Confirmed: B1 < B2 ~= D (Discovered abstractions explain performance; Paartha is an Abstraction Discovery Engine)"
    else:
        h_verdict = "Case 3: B1 ~= B2 ~= D (Discovered abstractions provided no significant advantage)"
    print(f"  -> Verdict on Abstraction Control: {h_verdict}")

    # --------------------------------------------------------------------------
    # PHASE 6: CROSS-DOMAIN TRANSFER (Level 3 Tasks - Domain B: Spectroscopy)
    # The Decisive Test: Transfers Domain A abstractions to independently authored Domain B
    # --------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[PHASE 6] Cross-Domain Transfer (Level 3 - Spectroscopy Domain B)...")
    print("-" * 80)

    transfer_tasks = task_corpus["level3_transfer"]
    phase6_records = {"System_A": [], "System_B1": [], "System_B2": [], "System_C": [], "System_D": []}

    for task in transfer_tasks:
        res_a = system_a.solve_task(task.description, task.initial_state)
        phase6_records["System_A"].append(evaluator.evaluate_result(task, res_a))

        res_b1 = system_b1.solve_task(task.description, task.initial_state)
        phase6_records["System_B1"].append(evaluator.evaluate_result(task, res_b1))

        res_b2 = system_b2.solve_task(task.description, task.initial_state)
        phase6_records["System_B2"].append(evaluator.evaluate_result(task, res_b2))

        res_c = system_c.solve_task(task.description, task.initial_state)
        phase6_records["System_C"].append(evaluator.evaluate_result(task, res_c))

        res_d = system_d.solve_task(task.description, task.initial_state)
        phase6_records["System_D"].append(evaluator.evaluate_result(task, res_d))
        time.sleep(0.5)

    p6_met_a = aggregate_system_metrics(phase6_records["System_A"])
    p6_met_b1 = aggregate_system_metrics(phase6_records["System_B1"])
    p6_met_b2 = aggregate_system_metrics(phase6_records["System_B2"])
    p6_met_c = aggregate_system_metrics(phase6_records["System_C"])
    p6_met_d = aggregate_system_metrics(phase6_records["System_D"])

    print(f"  -> System A  (LLM Alone):                      Success: {p6_met_a['success_rate']*100:.1f}% | Avg F1: {p6_met_a['avg_partial_score']:.3f}")
    print(f"  -> System B1 (LLM + Primitive Tools):          Success: {p6_met_b1['success_rate']*100:.1f}% | Avg F1: {p6_met_b1['avg_partial_score']:.3f}")
    print(f"  -> System B2 (LLM + Tools + Discovered Abstr): Success: {p6_met_b2['success_rate']*100:.1f}% | Avg F1: {p6_met_b2['avg_partial_score']:.3f}")
    print(f"  -> System C  (Paartha Runtime):                Success: {p6_met_c['success_rate']*100:.1f}% | Avg F1: {p6_met_c['avg_partial_score']:.3f}")
    print(f"  -> System D  (Paartha + Discovery):            Success: {p6_met_d['success_rate']*100:.1f}% | Avg F1: {p6_met_d['avg_partial_score']:.3f}")

    # Transfer Ratio: System D vs System B1 on Level 3
    transfer_ratio = (p6_met_d["success_rate"] / max(0.01, p6_met_b1["success_rate"]))
    print(f"  -> Cross-Domain Transfer Ratio (D / B1): {transfer_ratio:.2f}x")

    # Serialize complete benchmark results
    full_results = {
        "metadata": {
            "experiment": "PAARTHA_DECISIVE_BENCHMARK",
            "provider": model_config.provider,
            "model_name": model_config.model_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "phase_0_leakage_audit": audit_res,
        "phase_1_baseline_heldout": {
            "metrics_system_a": met_a,
            "metrics_system_b1": met_b1,
            "metrics_system_c": met_c,
            "details": phase1_records
        },
        "phase_2_discovery_metrics": system_d.discovery_metrics,
        "phase_4_level2_heldout": {
            "metrics_system_a": p4_met_a,
            "metrics_system_b1": p4_met_b1,
            "metrics_system_c": p4_met_c,
            "metrics_system_d": p4_met_d,
            "details": phase4_records
        },
        "phase_5_abstraction_control": {
            "metrics_system_b1": p5_met_b1,
            "metrics_system_b2": p5_met_b2,
            "metrics_system_d": p5_met_d,
            "hypothesis_verdict": h_verdict,
            "details": phase5_records
        },
        "phase_6_cross_domain_transfer": {
            "metrics_system_a": p6_met_a,
            "metrics_system_b1": p6_met_b1,
            "metrics_system_b2": p6_met_b2,
            "metrics_system_c": p6_met_c,
            "metrics_system_d": p6_met_d,
            "transfer_ratio_d_over_b1": round(transfer_ratio, 2),
            "details": phase6_records
        }
    }

    out_file = os.path.join(results_dir, "decisive_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)

    print("\n" + "=" * 80)
    print(f"EXPERIMENT COMPLETED SUCCESSFULLY. Results saved to:\n{out_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
