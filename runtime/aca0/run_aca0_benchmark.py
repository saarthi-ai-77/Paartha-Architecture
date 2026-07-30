"""
ACA-0 5-Stage Benchmark Suite Execution Script

Evaluates ACA-0 on the canonical first lesson:
"All mammals breathe air.
 Whales are mammals.
 Therefore whales breathe air."

Executes Stages 1-5:
1. Stage 1: Direct Recall ("Do whales breathe air?")
2. Stage 2: Explanation ("Why do whales breathe air?")
3. Stage 3: Transfer ("If dolphins are mammals, do dolphins breathe air?")
4. Stage 4: Counterfactual ("If whales were fish instead of mammals, would the previous conclusion still hold?")
5. Stage 5: Clarification & Interactive Knowledge Update ("Do platypuses produce milk?" -> CLARIFICATION_REQUIRED -> Mentor Clarifies -> Knowledge Updated -> Verified)
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runtime import ACA0CognitiveRuntime

def run_benchmark():
    rt = ACA0CognitiveRuntime()

    print("=================== ACA-0 BENCHMARK EXECUTION ===================")

    # --- Lesson Ingress ---
    lesson_lines = [
        "All mammals breathe air.",
        "Whales are mammals.",
        "Therefore whales breathe air."
    ]
    print("\n--- Lesson Ingress ---")
    for l in lesson_lines: print(f"  Mentor: {l}")
    lesson_res = rt.teach_lesson(lesson_lines)
    print(f"  ACA-0 Understanding Outcome: {lesson_res['status']} (Constructed: {lesson_res['constructed_elements']})")

    # --- Stage 1: Direct Recall ---
    print("\n--- Stage 1: Direct Recall ---")
    print("  Question: Do whales breathe air?")
    s1_res = rt.ask_question(1, {"kind": "direct_recall", "subject": "Whale", "predicate": "breathes", "object": "Air"})
    print(f"  ACA-0 Answer: {s1_res['answer']}")
    print(f"  Proof Trace: {s1_res['proof_trace']}")

    # --- Stage 2: Explanation ---
    print("\n--- Stage 2: Explanation ---")
    print("  Question: Why do whales breathe air?")
    s2_res = rt.ask_question(2, {"kind": "explanation", "subject": "Whale", "predicate": "breathes", "object": "Air"})
    print(f"  ACA-0 Explanation: {s2_res['explanation']}")

    # --- Stage 3: Transfer ---
    print("\n--- Stage 3: Transfer ---")
    print("  Question: If dolphins are mammals, do dolphins breathe air?")
    s3_res = rt.ask_question(3, {"kind": "transfer", "subject": "Dolphin", "category": "Mammal", "predicate": "breathes", "object": "Air"})
    print(f"  ACA-0 Answer: {s3_res['answer']}")
    print(f"  ACA-0 Transfer Explanation: {s3_res['explanation']}")

    # --- Stage 4: Counterfactual ---
    print("\n--- Stage 4: Counterfactual ---")
    print("  Question: If whales were fish instead of mammals, would the previous conclusion still hold?")
    s4_res = rt.ask_question(4, {"kind": "counterfactual", "subject": "Whale", "old_category": "Mammal", "new_category": "Fish", "predicate": "breathes", "object": "Air"})
    print(f"  ACA-0 Answer: {s4_res['answer']}")
    print(f"  ACA-0 Counterfactual Explanation: {s4_res['explanation']}")

    # --- Stage 5: Clarification & Interactive Knowledge Update ---
    print("\n--- Stage 5: Clarification Loop ---")
    print("  Question: Do platypuses breathe air?")
    s5_init = rt.ask_question(5, {"kind": "clarification", "subject": "Platypus", "predicate": "breathes"})
    print(f"  ACA-0 Status: {s5_init['status']}")
    print(f"  ACA-0 Clarification Request: {s5_init['query_text']}")

    # Mentor Clarification
    clarification_lines = ["Platypuses are mammals."]
    print(f"\n  Mentor Clarification: '{clarification_lines[0]}'")
    rt.clarify_knowledge(clarification_lines)

    # Re-evaluate Stage 5 after clarification
    s5_re_eval = rt.ask_question(1, {"kind": "direct_recall", "subject": "Platypus", "predicate": "breathes", "object": "Air"})
    print(f"  ACA-0 Re-Evaluation Answer: {s5_re_eval['answer']}")
    print(f"  Updated Proof Trace: {s5_re_eval['proof_trace']}")

    # Verification summary
    success = (
        s1_res["answer"] == "YES" and
        "Whales are Mammals" in s2_res["explanation"] and
        s3_res["answer"] == "YES" and
        s4_res["answer"] == "NO" and
        s5_init["status"] == "CLARIFICATION_REQUIRED" and
        s5_re_eval["answer"] == "YES"
    )

    summary = {
        "benchmark_success": success,
        "stage1_direct_recall": s1_res["answer"],
        "stage2_explanation": s2_res["explanation"],
        "stage3_transfer": s3_res["answer"],
        "stage4_counterfactual": s4_res["answer"],
        "stage5_clarification_status": s5_init["status"],
        "stage5_post_clarification_answer": s5_re_eval["answer"]
    }

    print("\n=================== BENCHMARK SUMMARY ===================")
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    run_benchmark()
