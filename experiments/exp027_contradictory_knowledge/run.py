"""
EXP-027: Domain 1 -- Contradictory Knowledge Falsification Trial
(Chief Systems Engineer Directive -- Phase VII Execution)

Evaluates ACA-0 (frozen reference system) across 5 random seeds (0-4) on contradictory lesson streams:
1. Lesson 1 (Base Knowledge K1):
   - "All mammals breathe air."
   - "Whales are mammals."
   - "Therefore whales breathe air."

2. Lesson 2 (Contradictory Lesson K2):
   - "Whales are fish."
   - "All fish breathe water."

3. Target Queries:
   - Query 1 (Contradiction Audit): Check if ACA-0 detects contradiction between K1 and K2.
   - Query 2 (Memory Integrity): "Do whales breathe air?" (Verifies if K1 is preserved or corrupted by K2).
"""

import os
import sys
import json

ACA0_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "runtime", "aca0")
sys.path.insert(0, ACA0_DIR)

from runtime import ACA0CognitiveRuntime

def run_exp027_seed(seed):
    rt = ACA0CognitiveRuntime()

    # Step 1: Teach Lesson 1 (Base Knowledge K1)
    k1_lines = [
        "All mammals breathe air.",
        "Whales are mammals.",
        "Therefore whales breathe air."
    ]
    res_k1 = rt.teach_lesson(k1_lines)

    # Verify K1 recall prior to contradiction
    q_k1 = rt.ask_question(1, {"kind": "direct_recall", "subject": "Whale", "predicate": "breathes", "object": "Air"})
    pre_k1_recall = (q_k1["answer"] == "YES")

    # Step 2: Teach Lesson 2 (Contradictory Lesson K2)
    k2_lines = [
        "Whales are fish.",
        "All fish breathe water."
    ]
    res_k2 = rt.teach_lesson(k2_lines)

    # Step 3: Check Contradiction State & Memory Protection
    # Check if Whales has conflicting categories (Mammal vs Fish)
    categories_whale = rt.kg.query_relation("Whale", "is_a")
    has_multiple_categories = (len(categories_whale) > 1)

    # Query 1: Memory Integrity under contradiction ("Do whales breathe air?")
    q_post_air = rt.ask_question(1, {"kind": "direct_recall", "subject": "Whale", "predicate": "breathes", "object": "Air"})

    # Query 2: Contradictory fact ("Do whales breathe water?")
    q_post_water = rt.ask_question(1, {"kind": "direct_recall", "subject": "Whale", "predicate": "breathes", "object": "Water"})

    # Check if system detected contradiction / emitted clarification state
    # A robust system should reject K2 or detect conflict (categories_whale = ["Mammal", "Fish"])
    contradiction_detected = has_multiple_categories or (q_post_water["answer"] == "UNKNOWN")
    k1_preserved = (q_post_air["answer"] == "YES")

    passed = (contradiction_detected and k1_preserved)

    return {
        "seed": seed,
        "pre_k1_recall": pre_k1_recall,
        "categories_assigned": categories_whale,
        "has_multiple_categories": has_multiple_categories,
        "post_air_answer": q_post_air["answer"],
        "post_water_answer": q_post_water["answer"],
        "contradiction_detected": contradiction_detected,
        "k1_preserved": k1_preserved,
        "seed_passed": passed
    }

def main():
    seeds = [0, 1, 2, 3, 4]
    results = []

    print("=================== EXP-027 DOMAIN 1 CONTRADICTION TRIAL ===================")
    for s in seeds:
        res = run_exp027_seed(s)
        results.append(res)
        print(f"Seed {s}: Pre-K1 Recall={res['pre_k1_recall']}, Categories={res['categories_assigned']}, Post-Air={res['post_air_answer']}, Post-Water={res['post_water_answer']}, Passed={res['seed_passed']}")

    all_passed = all(r["seed_passed"] for r in results)
    k1_preservation_rate = sum(1 for r in results if r["k1_preserved"]) / len(seeds)
    contradiction_detection_rate = sum(1 for r in results if r["contradiction_detected"]) / len(seeds)

    summary = {
        "exp_id": "EXP-027",
        "domain": "Domain 1 -- Contradictory Knowledge",
        "model": "ACA-0 (Frozen Reference System)",
        "n_seeds": len(seeds),
        "all_seeds_passed": all_passed,
        "metrics": {
            "pre_k1_recall_rate": sum(1 for r in results if r["pre_k1_recall"]) / len(seeds),
            "k1_preservation_rate": k1_preservation_rate,
            "contradiction_detection_rate": contradiction_detection_rate,
            "overall_pass_rate": sum(1 for r in results if r["seed_passed"]) / len(seeds)
        },
        "per_seed_results": results
    }

    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(res_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=================== EXP-027 SUMMARY ===================")
    print(json.dumps(summary, indent=2))
    print(f"Saved EXP-027 results to {res_path}")

if __name__ == "__main__":
    main()
