"""
SIP-002 / EXP-024: Sustained System Integration & Emergent Behavior Trial Suite
300 continuous interactive episodes across 5 sessions.
"""

import os
import sys
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runtime import ACASustainedRuntime

SCAN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "experiments", "exp_mvp001_scan_compositional")

def load_scan_pairs(filename, limit=None):
    path = os.path.join(SCAN_DIR, filename)
    pairs = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            in_part, out_part = line[len("IN: "):].split(" OUT: ")
            pairs.append((in_part.split(" "), out_part.split(" ")))
            if limit and len(pairs) >= limit: break
    return pairs

def main_trial(seed=0, log_path=None):
    random.seed(seed)
    if log_path is None:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "episodes_sip002.jsonl")
    if os.path.exists(log_path):
        os.remove(log_path)

    rt = ACASustainedRuntime(episode_log_path=log_path, capacity=30, micro_replay_steps=5)

    print("=== Training compose pathway on SCAN ===")
    train_pairs = load_scan_pairs("tasks_train_addprim_jump.txt")
    rt.train_compose_on(train_pairs, steps=300, batch_size=32)

    cities = [f"City_{i}" for i in range(15)]

    # --- Session 1: Single-Exposure Factual Teaching (50 facts) ---
    print("=== Session 1: Single-Exposure Teaching (50 facts) ===")
    s1_facts = [(f"S1_Name_{i}", random.choice(cities)) for i in range(50)]
    for name, city in s1_facts:
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})

    # --- Session 2: Interleaved Operational Workload ---
    print("=== Session 2: Interleaved Workload (Context, Query, SCAN) ===")
    s2_scan = load_scan_pairs("tasks_test_addprim_jump.txt", limit=30)
    for i in range(30):
        rt.handle_request({"kind": "context_update", "slot": "topic", "value": f"topic_{i}"})
        rt.handle_request({"kind": "context_query", "slot": "topic"})
        # Query random S1 fact
        q_name, true_city = random.choice(s1_facts)
        rt.handle_request({"kind": "query_fact", "name": q_name})
        # SCAN command
        toks, _ = s2_scan[i]
        rt.handle_request({"kind": "scan_command", "tokens": toks})

    # --- Session 3: Capacity Stress & Eviction Overload ---
    print("=== Session 3: Capacity Stress Overload (100 new facts) ===")
    s3_facts = [(f"S3_Name_{i}", random.choice(cities)) for i in range(100)]
    for name, city in s3_facts:
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})

    # Query a name never taught to log "unknown"
    rt.handle_request({"kind": "query_fact", "name": "Never_Taught_Name_S3"})

    # --- Session 4: Offline Mentor Cycle ---
    print("=== Session 4: Offline Mentor Cycle & Knowledge Promotion ===")
    mentor_outcome = rt.run_offline_mentor_cycle()

    # --- Session 5: System Re-Evaluation ---
    print("=== Session 5: System Re-Evaluation ===")

    # 1. Recall on S1 facts (evicted from memory, test backbone absorption)
    s1_correct = 0
    for name, true_city in s1_facts:
        ep = rt.handle_request({"kind": "query_fact", "name": name})
        if ep.response == true_city: s1_correct += 1
    s1_acc = s1_correct / len(s1_facts)

    # 2. Recall on S3 facts (currently in memory)
    s3_correct = 0
    for name, true_city in s3_facts[-30:]:
        ep = rt.handle_request({"kind": "query_fact", "name": name})
        if ep.response == true_city: s3_correct += 1
    s3_acc = s3_correct / len(s3_facts[-30:])

    # 3. SCAN compose accuracy
    scan_test = load_scan_pairs("tasks_test_addprim_jump.txt", limit=50)
    scan_correct = 0
    for toks, true_act in scan_test:
        ep = rt.handle_request({"kind": "scan_command", "tokens": toks})
        pred_act = ep.response.split(" ") if ep.response else []
        if pred_act == true_act: scan_correct += 1
    scan_acc = scan_correct / len(scan_test)

    # Telemetry summary
    all_episodes = rt.episode_log.read_all()
    anomalies = {}
    for ep_dict in all_episodes:
        for a in ep_dict.get("anomalies", []):
            cl = a["classification"]
            anomalies[cl] = anomalies.get(cl, 0) + 1

    summary = {
        "n_total_episodes": len(all_episodes),
        "session1_facts_count": len(s1_facts),
        "session3_facts_count": len(s3_facts),
        "memory_final_size": len(rt.memory.store),
        "memory_capacity": rt.memory.capacity,
        "s1_fact_recall_after_eviction": s1_acc,
        "s3_recent_fact_recall": s3_acc,
        "scan_compose_accuracy": scan_acc,
        "mentor_cycle_outcome": mentor_outcome,
        "anomaly_classification_counts": anomalies
    }

    print("\n========== SIP-002 TRIAL SUMMARY ==========")
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    main_trial(seed=0)
