"""
EXP-026: ACA-0 First Cognitive Prototype Benchmark Suite
(Chief Systems Engineer Directive -- ACA-0 & KRS-001)

Executes 5 random seeds of the 5-stage benchmark suite on ACA-0.
Evaluates Direct Recall, Explanation, Transfer, Counterfactual Simulation, and Clarification Loops.
"""

import os
import sys
import json

ACA0_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "runtime", "aca0")
sys.path.insert(0, ACA0_DIR)

from run_aca0_benchmark import run_benchmark

def main():
    seeds = [0, 1, 2, 3, 4]
    seed_results = []

    for s in seeds:
        print(f"\n--- Running EXP-026 Seed {s} ---")
        res = run_benchmark()
        seed_results.append(res)

    all_passed = all(r["benchmark_success"] for r in seed_results)

    output = {
        "exp_id": "EXP-026",
        "model": "ACA-0",
        "n_seeds": len(seeds),
        "all_seeds_passed": all_passed,
        "metrics": {
            "stage1_direct_recall_pass_rate": sum(1 for r in seed_results if r["stage1_direct_recall"] == "YES") / len(seeds),
            "stage2_explanation_pass_rate": sum(1 for r in seed_results if "Whales are Mammals" in r["stage2_explanation"]) / len(seeds),
            "stage3_transfer_pass_rate": sum(1 for r in seed_results if r["stage3_transfer"] == "YES") / len(seeds),
            "stage4_counterfactual_pass_rate": sum(1 for r in seed_results if r["stage4_counterfactual"] == "NO") / len(seeds),
            "stage5_clarification_pass_rate": sum(1 for r in seed_results if r["stage5_clarification_status"] == "CLARIFICATION_REQUIRED" and r["stage5_post_clarification_answer"] == "YES") / len(seeds)
        },
        "per_seed_results": seed_results
    }

    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(res_path, "w") as f:
        json.dump(output, f, indent=2)

    print("\n=================== EXP-026 RESULTS SUMMARY ===================")
    print(json.dumps(output, indent=2))
    print(f"\nSaved full EXP-026 results to {res_path}")

if __name__ == "__main__":
    main()
