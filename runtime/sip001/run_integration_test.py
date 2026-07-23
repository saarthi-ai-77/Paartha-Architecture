"""
SIP-001 Section 12: Integration Test Suite. One scripted scenario, not a
unit-test grid -- the object under test is integration behavior itself.
Exercises: facts taught under real capacity pressure (capacity=30 < 40
facts taught, forcing real eviction, mirroring EXP-018), a genuinely novel
query (triggering the Learning Lifecycle), SCAN commands through the
compose pathway, context updates, and Knowledge Promotion -- while writing
every request's episode into the SAME shared memory as facts (a third
schema, testing whether EXP-019's write-starvation mechanism recurs for
episode content, which no prior experiment tested).

Per SIP-001 Section 9/18: anomalies are classified, not fixed, during this
run. This script only observes and reports.
"""

import os
import sys
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runtime import ACARuntime

SCAN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                        "experiments", "exp_mvp001_scan_compositional")


def load_scan_pairs(filename, limit=None):
    path = os.path.join(SCAN_DIR, filename)
    pairs = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            in_part, out_part = line[len("IN: "):].split(" OUT: ")
            pairs.append((in_part.split(" "), out_part.split(" ")))
            if limit and len(pairs) >= limit:
                break
    return pairs


def main():
    random.seed(0)
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "episodes.jsonl")
    if os.path.exists(log_path):
        os.remove(log_path)  # fresh run

    rt = ACARuntime(episode_log_path=log_path)

    print("=== Training compose pathway on real SCAN data (offline, matching EXP-020) ===")
    train_pairs = load_scan_pairs("tasks_train_addprim_jump.txt")
    rt.train_compose_on(train_pairs, steps=300, batch_size=32)

    print("=== Teaching 40 facts under capacity=30 (deliberate over-subscription, mirrors EXP-018) ===")
    cities = [f"City_{i}" for i in range(15)]
    names = [f"Name_{i}" for i in range(40)]
    taught = []
    for i, name in enumerate(names):
        city = random.choice(cities)
        taught.append((name, city))
        rt.handle_request({"kind": "teach_fact", "name": name, "city": city})
        if i % 10 == 0:
            rt.handle_request({"kind": "context_update", "slot": "topic", "value": f"batch_{i // 10}"})

    print("=== Querying early-taught (Name_0..4) and late-taught (Name_35..39) facts ===")
    early_results, late_results = [], []
    for name, true_city in taught[:5]:
        ep = rt.handle_request({"kind": "query_fact", "name": name})
        early_results.append((name, true_city, ep.response))
    for name, true_city in taught[-5:]:
        ep = rt.handle_request({"kind": "query_fact", "name": name})
        late_results.append((name, true_city, ep.response))

    print("=== Querying a name never taught (expect 'I do not know' + learning opportunity) ===")
    novel_ep = rt.handle_request({"kind": "query_fact", "name": "Never_Taught_Name"})

    print("=== Running SCAN commands through the compose pathway ===")
    test_pairs = load_scan_pairs("tasks_test_addprim_jump.txt")
    scan_sample = random.sample(test_pairs, 20)
    scan_results = []
    for tokens, true_actions in scan_sample:
        ep = rt.handle_request({"kind": "scan_command", "tokens": tokens})
        predicted = ep.response.split(" ") if ep.response else []
        scan_results.append({"tokens": tokens, "true": true_actions, "predicted": predicted,
                              "correct": predicted == true_actions})

    print("=== Invoking Knowledge Promotion (EXP-010's mechanism, already known-limited) ===")
    promo_outcome = rt.run_knowledge_promotion()

    print("=== Re-querying early facts after promotion, to see if anything changed ===")
    post_promo_early = []
    for name, true_city in taught[:5]:
        ep = rt.handle_request({"kind": "query_fact", "name": name})
        post_promo_early.append((name, true_city, ep.response))

    # -- Summarize --------------------------------------------------
    all_episodes = rt.episode_log.read_all()
    anomaly_counts = {}
    for ep_dict in all_episodes:
        for a in ep_dict["anomalies"]:
            anomaly_counts[a["classification"]] = anomaly_counts.get(a["classification"], 0) + 1

    scan_acc = sum(r["correct"] for r in scan_results) / len(scan_results)

    summary = {
        "n_episodes": len(all_episodes),
        "anomaly_counts_by_classification": anomaly_counts,
        "early_fact_recall_pre_promotion": early_results,
        "late_fact_recall": late_results,
        "novel_query_response": novel_ep.response,
        "scan_accuracy_sample": scan_acc,
        "scan_results_sample": scan_results,
        "knowledge_promotion_outcome": promo_outcome,
        "early_fact_recall_post_promotion": post_promo_early,
        "memory_final_size": len(rt.memory.store),
        "memory_capacity": rt.memory.capacity,
    }

    # -- Control: repeated-exposure teaching (mirrors Benchmark A's actual
    # regime -- many gradient steps per fact -- to isolate whether one-shot
    # teaching, not a runtime bug, explains the universal "I do not know"
    # above. Fresh runtime instance, not sharing state with the main run. --
    print("=== CONTROL: repeated-exposure teaching (fresh runtime, mirrors Benchmark A's regime) ===")
    rt2 = ACARuntime(episode_log_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "episodes_control.jsonl"))
    if os.path.exists(rt2.episode_log.path):
        os.remove(rt2.episode_log.path)
    control_names = [f"CtrlName_{i}" for i in range(10)]
    control_cities = [f"City_{i}" for i in range(15)]
    control_facts = [(n, random.choice(control_cities)) for n in control_names]
    for _ in range(30):  # 30 repeated exposures per fact, vs. 1 in the main scenario
        for name, city in control_facts:
            rt2.handle_request({"kind": "teach_fact", "name": name, "city": city})
    control_results = []
    for name, true_city in control_facts:
        ep = rt2.handle_request({"kind": "query_fact", "name": name})
        control_results.append({"name": name, "true_city": true_city, "response": ep.response,
                                 "correct": ep.response == true_city})
    control_acc = sum(r["correct"] for r in control_results) / len(control_results)
    summary["control_repeated_exposure"] = {
        "accuracy": control_acc,
        "results": control_results,
        "memory_coverage": rt2.memory.coverage("fact", control_names),
    }

    print("\n========== INTEGRATION TEST SUMMARY ==========")
    print(json.dumps(summary, indent=2))

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "integration_test_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
