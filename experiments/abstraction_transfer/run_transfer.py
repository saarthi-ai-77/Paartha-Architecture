"""
Master Runner for Experiments B & C: Genuine Abstraction Transfer.
Evaluates cross-domain structural transfer from Domain A (Logistics)
to Domain B (Spectroscopy) and Domain C (Financial Market Microstructure).
"""

import os
import sys
import json
import time
from typing import Dict, List, Any

curr_dir = os.path.dirname(os.path.abspath(__file__))
proj_root = os.path.dirname(curr_dir)
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

from decisive_paartha.config.models import get_model_config
from decisive_paartha.systems.llm_client import FrontierLLMClient
from decisive_paartha.tools.primitive_tools import initialize_primitive_tools, State
from decisive_paartha.evaluation.evaluator import BlindedEvaluator
from decisive_paartha.evaluation.metrics import aggregate_system_metrics

from abstraction_transfer.corpus_multidomain import get_multidomain_corpus, BenchmarkTask
from abstraction_transfer.leakage_audit import run_multidomain_leakage_audit
from abstraction_transfer.transfer_engine import (
    CleanAntiUnifier, create_clean_tool_schema, diagnose_b2_failure
)
from decisive_paartha.systems.paartha_discovery import MotifMiner, MDLCompressionEngine
from decisive_paartha.systems.paartha_runtime import PaarthaRuntime
from decisive_paartha.systems.llm_tools import SystemBLlmTools


def run_abstraction_transfer_experiment():
    print("=" * 80)
    print("PAARTHA EXPERIMENTS B & C: GENUINE ABSTRACTION TRANSFER")
    print("Domain A (Logistics) -> Domain B (Spectroscopy) -> Domain C (Finance)")
    print("=" * 80)

    model_config = get_model_config()
    print(f"[Model Provider] {model_config.provider} | Model: {model_config.model_name}")
    print(f"[API Endpoint] {model_config.api_base_url}")
    print(f"[API Key Configured] {'YES' if model_config.api_key else 'NO (Simulated)'}")

    # 1. LEAKAGE AUDIT
    print("\n" + "-" * 80)
    print("[PHASE 0] Multi-Domain Leakage Audit...")
    print("-" * 80)
    audit_res = run_multidomain_leakage_audit(curr_dir)
    print(f"  Leakage Audit Status: {audit_res['verdict']} (Scanned {audit_res['files_scanned']} files, {audit_res['total_leakages']} leaks)")
    if audit_res["verdict"] != "PASSED_CLEAN":
        raise RuntimeError("Leakage audit failed! Check details in audit report.")

    client = FrontierLLMClient(model_config)
    evaluator = BlindedEvaluator()
    corpus = get_multidomain_corpus()

    results_dir = os.path.join(curr_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    # 2. DOMAIN A DISCOVERY
    print("\n" + "-" * 80)
    print("[PHASE 1] Experience & Abstraction Discovery in Domain A...")
    print("-" * 80)
    exp_tasks = corpus["domain_a_experience"]
    traces = [t.ideal_steps for t in exp_tasks]
    print(f"  Captured {len(traces)} verified execution traces from Domain A tasks.")

    miner = MotifMiner(min_length=2, max_length=3, min_support=2)
    motifs = miner.mine(traces)
    print(f"  Mined {len(motifs)} recurring motifs.")

    anti_unifier = CleanAntiUnifier()
    mdl_engine = MDLCompressionEngine()
    accepted_abstractions = {}

    for m in motifs:
        cand = anti_unifier.anti_unify(m, traces)
        if cand:
            gain = mdl_engine.evaluate_gain(cand, traces)
            print(f"  Candidate: {cand.name} | Sub-primitives: {cand.sub_primitives} | MDL Gain: {gain} bits")
            if gain > 0:
                accepted_abstractions[cand.name] = cand
                print(f"    -> ACCEPTED into Capability Library (+{gain} bits compression)")

    print(f"\n[PHASE 2] Freezing Discovered Library: {list(accepted_abstractions.keys())}")
    print("Zero weight updates (Delta Theta = 0). Frozen for cross-domain evaluation.")

    # 3. EVALUATION ACROSS DOMAINS B & C
    transfer_results = {}
    b2_diagnostics = {}

    for domain_key, domain_name in [("domain_b_spectroscopy", "Domain B: Spectroscopy"), ("domain_c_finance", "Domain C: Finance")]:
        print("\n" + "=" * 80)
        print(f"[EVALUATION] Testing Transfer on {domain_name}")
        print("=" * 80)

        tasks = corpus[domain_key]
        domain_records = {
            "System_B1_LLM_Primitives": [],
            "System_B2_LLM_Primitives_CleanAbstractions": [],
            "System_C_Paartha_Runtime_Primitives": [],
            "System_D_Paartha_Runtime_Abstractions": []
        }

        # Initialize Systems for this domain
        # B1: LLM + Primitives
        sys_b1 = SystemBLlmTools(client, tool_registry=initialize_primitive_tools(), is_b2=False)

        # B2: LLM + Primitives + Clean Abstractions (with fair interface!)
        b2_tools = initialize_primitive_tools()
        b2_tools.update(accepted_abstractions)
        sys_b2 = SystemBLlmTools(client, tool_registry=b2_tools, is_b2=True)

        # System C: Paartha Runtime with primitives only
        sys_c = PaarthaRuntime(client, capabilities=initialize_primitive_tools())

        # System D: Paartha Runtime with primitives + abstractions
        d_tools = initialize_primitive_tools()
        d_tools.update(accepted_abstractions)
        sys_d = PaarthaRuntime(client, capabilities=d_tools)

        # Run tasks
        b2_domain_diag = []
        for task in tasks:
            print(f"\n---> Task: {task.task_id} ({task.description})")

            # B1
            res_b1 = sys_b1.solve_task(task.description, task.initial_state)
            eval_b1 = evaluator.evaluate_result(task, res_b1)
            domain_records["System_B1_LLM_Primitives"].append(eval_b1)
            time.sleep(0.3)

            # B2
            res_b2 = sys_b2.solve_task(task.description, task.initial_state)
            eval_b2 = evaluator.evaluate_result(task, res_b2)
            domain_records["System_B2_LLM_Primitives_CleanAbstractions"].append(eval_b2)
            time.sleep(0.3)

            # Diagnose B2 if failed
            if not eval_b2.get("exact_match", False):
                diag = diagnose_b2_failure(task, res_b2.get("trace", []), task.initial_state)
                b2_domain_diag.append({"task_id": task.task_id, "diagnosis": diag})
                print(f"      [B2 Failure Diagnosis] {diag}")
            else:
                b2_domain_diag.append({"task_id": task.task_id, "diagnosis": "NONE_SUCCESS"})

            # System C
            res_c = sys_c.solve_task(task.description, task.initial_state)
            eval_c = evaluator.evaluate_result(task, res_c)
            domain_records["System_C_Paartha_Runtime_Primitives"].append(eval_c)
            time.sleep(0.3)

            # System D
            res_d = sys_d.solve_task(task.description, task.initial_state)
            eval_d = evaluator.evaluate_result(task, res_d)
            domain_records["System_D_Paartha_Runtime_Abstractions"].append(eval_d)
            time.sleep(0.3)

        # Aggregate domain metrics
        domain_metrics = {}
        for sname, recs in domain_records.items():
            agg = aggregate_system_metrics(recs)
            domain_metrics[sname] = agg
            print(f"  -> {sname:45s}: Success = {agg['success_rate']*100:.1f}% | Avg F1 = {agg['avg_partial_score']:.3f} | Latency = {agg['avg_latency_ms']:.1f}ms | Tokens = {agg['total_tokens']}")

        # Transfer Ratio D / B1
        tr = domain_metrics["System_D_Paartha_Runtime_Abstractions"]["success_rate"] / max(0.01, domain_metrics["System_B1_LLM_Primitives"]["success_rate"])
        print(f"  --> Cross-Domain Transfer Ratio (D / B1) on {domain_name}: {tr:.2f}x")

        transfer_results[domain_key] = {
            "name": domain_name,
            "metrics": domain_metrics,
            "transfer_ratio_d_over_b1": round(tr, 2),
            "details": domain_records
        }
        b2_diagnostics[domain_key] = b2_domain_diag

    # Serialize complete benchmark results
    full_payload = {
        "metadata": {
            "experiment": "PAARTHA_GENUINE_ABSTRACTION_TRANSFER",
            "provider": model_config.provider,
            "model_name": model_config.model_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "leakage_audit": audit_res,
        "domain_a_discovery": {
            "traces_captured": len(traces),
            "motifs_mined": len(motifs),
            "abstractions_accepted": list(accepted_abstractions.keys())
        },
        "cross_domain_evaluations": transfer_results,
        "system_b2_diagnostics": b2_diagnostics
    }

    out_file = os.path.join(results_dir, "transfer_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, indent=2)

    print("\n" + "=" * 80)
    print(f"EXPERIMENTS B & C COMPLETED. Results serialized to:\n{out_file}")
    print("=" * 80)

if __name__ == "__main__":
    run_abstraction_transfer_experiment()
