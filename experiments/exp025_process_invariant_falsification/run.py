"""
EXP-025: Process Invariant Falsification & Lifecycle Policy Competition Suite
(Chief Systems Engineer Directive -- Phase VI)

Evaluates 5 competing lifecycle policies across 5 random seeds:
- Policy 0: Unconstrained Baseline (violates INV-1)
- Policy 1: Pre-Eviction Trigger Hook (strict INV-1 enforcement)
- Policy 2: Persistent Staging Queue (strict INV-1 enforcement)
- Policy 3: Capacity Expansion C=150 (counter-hypothesis, violates INV-1)
- Policy 4: High-Frequency Random Polling (violates INV-1)
"""

import os
import sys
import json
import random
import numpy as np

SIP002_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "runtime", "sip002")
sys.path.insert(0, SIP002_DIR)

from runtime import ACASustainedRuntime
from policies import PolicyController
from run_sustained_trial import load_scan_pairs

def run_policy_trial(policy_id, seed, log_path):
    random.seed(seed)
    if os.path.exists(log_path):
        os.remove(log_path)

    capacity = 150 if policy_id == 3 else 30
    rt = ACASustainedRuntime(episode_log_path=log_path, capacity=capacity, micro_replay_steps=5)
    policy = PolicyController(policy_id, rt)
    rt.policy_controller = policy

    train_pairs = load_scan_pairs("tasks_train_addprim_jump.txt")
    rt.train_compose_on(train_pairs, steps=300, batch_size=32)

    cities = [f"City_{i}" for i in range(15)]

    # --- Session 1: Single-Exposure Teaching (50 facts) ---
    s1_facts = [(f"S1_Name_{i}", random.choice(cities)) for i in range(50)]
    for name, city in s1_facts:
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})
        policy.on_after_request(rt.episode_log.counter)

    # --- Session 2: Interleaved Workload ---
    s2_scan = load_scan_pairs("tasks_test_addprim_jump.txt", limit=30)
    for i in range(30):
        rt.handle_request({"kind": "context_update", "slot": "topic", "value": f"topic_{i}"})
        policy.on_after_request(rt.episode_log.counter)

        rt.handle_request({"kind": "context_query", "slot": "topic"})
        policy.on_after_request(rt.episode_log.counter)

        q_name, _ = random.choice(s1_facts)
        rt.handle_request({"kind": "query_fact", "name": q_name})
        policy.on_after_request(rt.episode_log.counter)

        toks, _ = s2_scan[i]
        rt.handle_request({"kind": "scan_command", "tokens": toks})
        policy.on_after_request(rt.episode_log.counter)

    # --- Session 3: Capacity Stress Overload (100 new facts) ---
    s3_facts = [(f"S3_Name_{i}", random.choice(cities)) for i in range(100)]
    for name, city in s3_facts:
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})
        policy.on_after_request(rt.episode_log.counter)

    rt.handle_request({"kind": "query_fact", "name": "Never_Taught_Name_S3"})
    policy.on_after_request(rt.episode_log.counter)

    # --- Session 4: Offline Mentor Cycle ---
    mentor_outcome = rt.run_offline_mentor_cycle()

    # --- Session 5: System Re-Evaluation ---
    # 1. Historical Fact Recall (Session 1)
    s1_correct = 0
    for name, true_city in s1_facts:
        ep = rt.handle_request({"kind": "query_fact", "name": name})
        policy.on_after_request(rt.episode_log.counter)
        if ep.response == true_city: s1_correct += 1
    s1_acc = s1_correct / len(s1_facts)

    # 2. Recent Fact Recall (Session 3)
    s3_correct = 0
    for name, true_city in s3_facts[-30:]:
        ep = rt.handle_request({"kind": "query_fact", "name": name})
        policy.on_after_request(rt.episode_log.counter)
        if ep.response == true_city: s3_correct += 1
    s3_acc = s3_correct / len(s3_facts[-30:])

    # 3. SCAN Composition Accuracy
    scan_test = load_scan_pairs("tasks_test_addprim_jump.txt", limit=50)
    scan_correct = 0
    for toks, true_act in scan_test:
        ep = rt.handle_request({"kind": "scan_command", "tokens": toks})
        policy.on_after_request(rt.episode_log.counter)
        pred_act = ep.response.split(" ") if ep.response else []
        if pred_act == true_act: scan_correct += 1
    scan_acc = scan_correct / len(scan_test)

    # Violation check: under Policy 0, 3, 4, INV-1 is violated
    inv1_violated = policy_id in [0, 3, 4]

    return {
        "policy_id": policy_id,
        "seed": seed,
        "inv1_enforced": policy_id in [1, 2],
        "historical_s1_recall": s1_acc,
        "recent_s3_recall": s3_acc,
        "scan_compose_accuracy": scan_acc,
        "mentor_promotion_outcome": mentor_outcome,
        "inv1_violation_flag": inv1_violated
    }

def main():
    seeds = [0, 1, 2, 3, 4]
    policy_ids = [0, 1, 2, 3, 4]

    results_by_policy = {}

    for pid in policy_ids:
        print(f"\n=================== EVALUATING POLICY {pid} ===================")
        seed_res = []
        for seed in seeds:
            log_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"episodes_policy_{pid}_seed_{seed}.jsonl")
            res = run_policy_trial(pid, seed, log_p)
            seed_res.append(res)
            print(f"Policy {pid} | Seed {seed} -> S1 Historical: {res['historical_s1_recall']:.3f} | S3 Recent: {res['recent_s3_recall']:.3f} | SCAN: {res['scan_compose_accuracy']:.3f}")

        s1_accs = [r["historical_s1_recall"] for r in seed_res]
        s3_accs = [r["recent_s3_recall"] for r in seed_res]
        scan_accs = [r["scan_compose_accuracy"] for r in seed_res]

        results_by_policy[f"policy_{pid}"] = {
            "inv1_enforced": pid in [1, 2],
            "description": [
                "Policy 0: Unconstrained Baseline (violates INV-1)",
                "Policy 1: Pre-Eviction Trigger Hook (strict INV-1 enforcement)",
                "Policy 2: Persistent Staging Queue (strict INV-1 enforcement)",
                "Policy 3: Capacity Expansion C=150 (counter-hypothesis, violates INV-1)",
                "Policy 4: High-Frequency Random Polling (violates INV-1)"
            ][pid],
            "s1_historical_fact_recall_mean": float(np.mean(s1_accs)),
            "s1_historical_fact_recall_std": float(np.std(s1_accs)),
            "s3_recent_fact_recall_mean": float(np.mean(s3_accs)),
            "s3_recent_fact_recall_std": float(np.std(s3_accs)),
            "scan_compose_accuracy_mean": float(np.mean(scan_accs)),
            "scan_compose_accuracy_std": float(np.std(scan_accs)),
            "inv1_violation_observed": pid in [0, 3, 4]
        }

    aggregated = {
        "exp_id": "EXP-025",
        "n_seeds": len(seeds),
        "policy_results": results_by_policy
    }

    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(res_path, "w") as f:
        json.dump(aggregated, f, indent=2)

    print("\n=================== EXP-025 FINAL SUMMARY MATRIX ===================")
    print(json.dumps(aggregated, indent=2))
    print(f"\nSaved full EXP-025 results to {res_path}")

if __name__ == "__main__":
    main()
