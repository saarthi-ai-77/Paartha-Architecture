"""
EXP-024: Sustained Autonomous System Integration & Emergent Behavior Trial Suite
(Chief Systems Engineer Directive -- Phase IV)

Runs 5 random seeds of the 300-episode continuous multi-session trial scenario in runtime/sip002/.
Collects system telemetry, anomaly classifications, emergent retention curves, and failure boundaries.
"""

import os
import sys
import json
import numpy as np

SIP002_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "runtime", "sip002")
sys.path.insert(0, SIP002_DIR)

from run_sustained_trial import main_trial

def main():
    seeds = [0, 1, 2, 3, 4]
    seed_summaries = []

    for seed in seeds:
        print(f"\n--- Running EXP-024 Seed {seed} ---")
        log_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"episodes_seed_{seed}.jsonl")
        summary = main_trial(seed=seed, log_path=log_p)
        seed_summaries.append(summary)

    # Aggregate metrics
    s1_accs = [s["s1_fact_recall_after_eviction"] for s in seed_summaries]
    s3_accs = [s["s3_recent_fact_recall"] for s in seed_summaries]
    scan_accs = [s["scan_compose_accuracy"] for s in seed_summaries]

    aggregated = {
        "exp_id": "EXP-024",
        "n_seeds": len(seeds),
        "episodes_per_trial": seed_summaries[0]["n_total_episodes"],
        "metrics": {
            "s1_historical_fact_recall_mean": float(np.mean(s1_accs)),
            "s1_historical_fact_recall_std": float(np.std(s1_accs)),
            "s3_recent_fact_recall_mean": float(np.mean(s3_accs)),
            "s3_recent_fact_recall_std": float(np.std(s3_accs)),
            "scan_compose_accuracy_mean": float(np.mean(scan_accs)),
            "scan_compose_accuracy_std": float(np.std(scan_accs))
        },
        "per_seed_summaries": seed_summaries
    }

    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(res_path, "w") as f:
        json.dump(aggregated, f, indent=2)

    print("\n=================== EXP-024 RESULTS SUMMARY ===================")
    print(json.dumps(aggregated, indent=2))
    print(f"\nSaved full EXP-024 results to {res_path}")

if __name__ == "__main__":
    main()
