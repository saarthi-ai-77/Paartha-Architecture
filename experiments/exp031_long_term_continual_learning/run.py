"""
EXP-031: Domain 5 -- Long-Term Continual Learning Falsification Trial (1,000 Lessons)
(Chief Systems Engineer Directive -- Phase VII Execution)

Evaluates runtime/sip002/ under 1,000 sequential lessons (N=1,000 > C=30 capacity)
across 5 random seeds (0-4) with CPA-001 INV-1 enforced via Policy 1 (Pre-Eviction Trigger Hook).

Evaluates:
- Session 1 (Lessons 1-200): Early Batch Teaching
- Session 2 (Lessons 201-600): Middle Batch Teaching & Interleaved Workloads
- Session 3 (Lessons 601-1,000): Late Batch Teaching & Capacity Saturation
- Session 4: Offline Mentor Consolidation Cycle
- Session 5: Historical Recall Evaluation across Early (1-200), Middle (201-600), and Late (601-1,000) Batches
"""

import os
import sys
import json
import random

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SIP002_DIR = os.path.join(ROOT_DIR, "runtime", "sip002")

if "compose" in sys.modules:
    del sys.modules["compose"]

if SIP002_DIR not in sys.path:
    sys.path.insert(0, SIP002_DIR)

from runtime import ACASustainedRuntime
from policies import PolicyController

cities = ["Tokyo", "Paris", "London", "Berlin", "Sydney", "Cairo", "Toronto", "Seoul", "Madrid", "Rome"]

def run_exp031_seed(seed):
    random.seed(seed)
    capacity = 30
    n_lessons = 1000

    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"episode_log_seed_{seed}.jsonl")
    rt = ACASustainedRuntime(episode_log_path=log_path, capacity=capacity)
    policy = PolicyController(policy_id=1, runtime=rt)
    rt.policy_controller = policy

    # Generate 1,000 sequential factual lessons using 100 entities across 10 properties/cities
    n_entities = 100
    lessons = [(f"Person_{i % n_entities}", random.choice(cities)) for i in range(n_lessons)]

    # --- Batch 1: Lessons 1-200 ---
    for name, city in lessons[0:200]:
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})
        rt.memory.unconditional_write("fact", name, city, entropy=0.1, policy_controller=policy)

    # Periodic Offline Mentor Cycle 1
    rt.run_offline_mentor_cycle()

    # --- Batch 2: Lessons 201-600 ---
    for name, city in lessons[200:600]:
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})
        rt.memory.unconditional_write("fact", name, city, entropy=0.1, policy_controller=policy)

    # Periodic Offline Mentor Cycle 2
    rt.run_offline_mentor_cycle()

    # --- Batch 3: Lessons 601-1,000 ---
    for name, city in lessons[600:1000]:
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})
        rt.memory.unconditional_write("fact", name, city, entropy=0.1, policy_controller=policy)

    # Final Offline Mentor Cycle
    rt.run_offline_mentor_cycle()

    # --- Final Evaluation Across Early, Middle, and Late Batches ---
    def eval_batch_recall(batch):
        correct = 0
        for name, true_city in batch:
            val = rt.memory.get("fact", name)
            if val == true_city:
                correct += 1
            else:
                # Query recall_model (consolidated semantic store)
                ep = rt.handle_request({"kind": "query_fact", "name": name})
                if ep.response == true_city:
                    correct += 1
        return correct / len(batch) if batch else 1.0

    early_acc = eval_batch_recall(lessons[0:200])
    middle_acc = eval_batch_recall(lessons[200:600])
    late_acc = eval_batch_recall(lessons[600:1000])
    overall_acc = eval_batch_recall(lessons)

    passed = (overall_acc >= 0.95)

    return {
        "seed": seed,
        "early_batch_recall": early_acc,
        "middle_batch_recall": middle_acc,
        "late_batch_recall": late_acc,
        "overall_recall": overall_acc,
        "seed_passed": passed
    }

def main():
    seeds = [0, 1, 2, 3, 4]
    results = []

    print("=================== EXP-031 DOMAIN 5 LONG-TERM CONTINUAL LEARNING TRIAL (1,000 LESSONS) ===================")
    for s in seeds:
        res = run_exp031_seed(s)
        results.append(res)
        print(f"Seed {s}: Early={res['early_batch_recall']:.3f}, Middle={res['middle_batch_recall']:.3f}, Late={res['late_batch_recall']:.3f}, Overall={res['overall_recall']:.3f}, Passed={res['seed_passed']}")

    all_passed = all(r["seed_passed"] for r in results)
    avg_early = sum(r["early_batch_recall"] for r in results) / len(seeds)
    avg_middle = sum(r["middle_batch_recall"] for r in results) / len(seeds)
    avg_late = sum(r["late_batch_recall"] for r in results) / len(seeds)
    avg_overall = sum(r["overall_recall"] for r in results) / len(seeds)

    summary = {
        "exp_id": "EXP-031",
        "domain": "Domain 5 -- Long-Term Continual Learning (1,000 Lessons)",
        "model": "runtime/sip002 (CPA-001 INV-1 Policy 1)",
        "capacity": 30,
        "total_lessons": 1000,
        "n_seeds": len(seeds),
        "all_seeds_passed": all_passed,
        "metrics": {
            "avg_early_batch_recall": avg_early,
            "avg_middle_batch_recall": avg_middle,
            "avg_late_batch_recall": avg_late,
            "avg_overall_recall": avg_overall,
            "pass_rate": sum(1 for r in results if r["seed_passed"]) / len(seeds)
        },
        "per_seed_results": results
    }

    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(res_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=================== EXP-031 SUMMARY ===================")
    print(json.dumps(summary, indent=2))
    print(f"Saved EXP-031 results to {res_path}")

if __name__ == "__main__":
    main()
