"""
EXP-022: Dedicated Falsification & Architecture Accommodation of Single-Exposure Teaching
(DEC-006 Steps 3 & 4)

This experiment isolates the single-exposure factual teaching limitation identified during
SIP-001 integration testing. It systematically tests 4 batteries across 5 seeds:
- Battery A: Implementation Bug Falsification (loss reduction, gradient norm, seq alignment, mask)
- Battery B: Optimization / Hyperparameter Artifact Falsification (LR sweep, step count sweep k=1..30, optimizer dynamics)
- Battery C: Algorithmic Mechanism Limitation Falsification (ME-03 running median vs unconditional write vs absolute threshold vs novel-key write)
- Battery D: DEC-006 Step 4 Architecture Accommodation Analysis (SOS-001 unconditional episodic write policy vs dynamic confidence boundary vs micro-replay)
"""

import os
import sys
import json
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Ensure runtime modules can be imported
SIP001_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "runtime", "sip001")
sys.path.insert(0, SIP001_DIR)

from recall_model import CausalTransformerLM
from runtime import VOCAB_SIZE, SEQ_LEN
from memory import EpisodicMemory
from evaluate import evaluate_local, knowledge_boundary
from context_state import WorkingStateStore

WAS, BORN, IN, DOT = 0, 1, 2, 3
N_SPECIAL = 4
MAX_NAMES, MAX_CITIES = 50, 20
NAME_BASE, CITY_BASE = N_SPECIAL, N_SPECIAL + MAX_NAMES
CITY_POS = 4
CONFIDENCE_THRESHOLD_NATS = 1.5

def fact_sequence(name_id, city_id):
    return [name_id, WAS, BORN, IN, city_id, DOT]

def run_battery_a(device, seed):
    """Battery A: Implementation Bug Falsification"""
    torch.manual_seed(seed)
    model = CausalTransformerLM(VOCAB_SIZE, SEQ_LEN).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=3e-4)

    name_id = NAME_BASE + 0
    city_id = CITY_BASE + 0
    seq = torch.tensor([fact_sequence(name_id, city_id)], dtype=torch.long, device=device)

    # Initial forward
    logits_before = model(seq)
    loss_before = F.cross_entropy(logits_before[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1)).item()
    ent_before = evaluate_local(logits_before, CITY_POS - 1)[0].item()
    target_logit_before = logits_before[0, CITY_POS - 1, city_id].item()

    # Step
    opt.zero_grad()
    loss = F.cross_entropy(logits_before[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1))
    loss.backward()

    # Measure gradient norms
    total_grad_norm = torch.sqrt(sum(p.grad.norm()**2 for p in model.parameters() if p.grad is not None)).item()

    opt.step()

    # After step forward
    with torch.no_grad():
        logits_after = model(seq)
        loss_after = F.cross_entropy(logits_after[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1)).item()
        ent_after = evaluate_local(logits_after, CITY_POS - 1)[0].item()
        target_logit_after = logits_after[0, CITY_POS - 1, city_id].item()

    # Check causal mask isolation: position 3 logits ("IN") predicting position 4 ("City")
    seq_mod = torch.tensor([[name_id, WAS, BORN, IN, CITY_BASE + 5, DOT]], dtype=torch.long, device=device)
    with torch.no_grad():
        logits_mod = model(seq_mod)
        ent_mod = evaluate_local(logits_mod, CITY_POS - 1)[0].item()

    causal_mask_correct = abs(ent_after - ent_mod) < 1e-6

    return {
        "loss_before": loss_before,
        "loss_after": loss_after,
        "loss_delta": loss_before - loss_after,
        "ent_before": ent_before,
        "ent_after": ent_after,
        "ent_delta": ent_before - ent_after,
        "target_logit_before": target_logit_before,
        "target_logit_after": target_logit_after,
        "target_logit_delta": target_logit_after - target_logit_before,
        "total_grad_norm": total_grad_norm,
        "causal_mask_correct": causal_mask_correct,
        "bug_detected": not causal_mask_correct or (loss_before - loss_after <= 0)
    }

def run_battery_b(device, seed):
    """Battery B: Optimization / Hyperparameter Artifact Falsification"""
    lr_results = {}
    lrs = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]

    for lr in lrs:
        torch.manual_seed(seed)
        model = CausalTransformerLM(VOCAB_SIZE, SEQ_LEN).to(device)
        opt = torch.optim.Adam(model.parameters(), lr=lr)

        name_id = NAME_BASE + 1
        city_id = CITY_BASE + 1
        seq = torch.tensor([fact_sequence(name_id, city_id)], dtype=torch.long, device=device)

        with torch.no_grad():
            ent_0 = evaluate_local(model(seq), CITY_POS - 1)[0].item()

        logits = model(seq)
        loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1))
        opt.zero_grad(); loss.backward(); opt.step()

        with torch.no_grad():
            logits_1 = model(seq)
            ent_1 = evaluate_local(logits_1, CITY_POS - 1)[0].item()
            pred = logits_1[0, CITY_POS - 1, :].argmax(dim=-1).item()

        lr_results[str(lr)] = {
            "ent_0": ent_0,
            "ent_1": ent_1,
            "ent_drop": ent_0 - ent_1,
            "correct": pred == city_id,
            "confident": ent_1 < CONFIDENCE_THRESHOLD_NATS
        }

    # Step count trajectory sweep k=1..30 at standard lr=3e-4 and high lr=1e-2
    step_trajectories = {}
    for lr in [3e-4, 1e-2]:
        torch.manual_seed(seed)
        model = CausalTransformerLM(VOCAB_SIZE, SEQ_LEN).to(device)
        opt = torch.optim.Adam(model.parameters(), lr=lr)

        name_id = NAME_BASE + 2
        city_id = CITY_BASE + 2
        seq = torch.tensor([fact_sequence(name_id, city_id)], dtype=torch.long, device=device)

        traj = []
        for k in range(1, 31):
            logits = model(seq)
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

            with torch.no_grad():
                logits_eval = model(seq)
                ent_k = evaluate_local(logits_eval, CITY_POS - 1)[0].item()
                pred_k = logits_eval[0, CITY_POS - 1, :].argmax(dim=-1).item()
                loss_k = F.cross_entropy(logits_eval[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1)).item()

            traj.append({
                "step": k,
                "loss": loss_k,
                "entropy": ent_k,
                "pred": pred_k,
                "correct": pred_k == city_id,
                "confident": ent_k < CONFIDENCE_THRESHOLD_NATS
            })
        step_trajectories[str(lr)] = traj

    return {
        "lr_sweep": lr_results,
        "step_trajectories": step_trajectories
    }

def run_battery_c(device, seed):
    """Battery C: Algorithmic Mechanism Limitation Falsification (ME-03 Gating)"""
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)

    cities = [f"City_{i}" for i in range(15)]
    names = [f"Name_{i}" for i in range(40)]
    facts = [(n, rng.choice(cities)) for n in names]

    policies = ["gated_write", "unconditional_write", "absolute_threshold", "novel_key_write"]
    policy_results = {}

    for policy in policies:
        torch.manual_seed(seed)
        model = CausalTransformerLM(VOCAB_SIZE, SEQ_LEN).to(device)
        opt = torch.optim.Adam(model.parameters(), lr=3e-4)
        mem = EpisodicMemory(capacity=30)

        name_map = {}
        city_map = {}

        def get_name_id(name):
            if name not in name_map: name_map[name] = NAME_BASE + len(name_map)
            return name_map[name]

        def get_city_id(city):
            if city not in city_map: city_map[city] = CITY_BASE + len(city_map)
            return city_map[city]

        write_outcomes = []
        recorded_entropies = []

        # Teaching phase (1 exposure per fact)
        for name, city in facts:
            nid, cid = get_name_id(name), get_city_id(city)
            seq = torch.tensor([fact_sequence(nid, cid)], dtype=torch.long, device=device)

            logits = model(seq)
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

            with torch.no_grad():
                ent = evaluate_local(logits, CITY_POS - 1)[0].item()
            recorded_entropies.append(ent)

            if policy == "gated_write":
                out = mem.gated_write("fact", name, city, ent)
            elif policy == "unconditional_write":
                out = mem.unconditional_write("fact", name, city, ent)
            elif policy == "absolute_threshold":
                out = mem.gated_write("fact", name, city, ent) if ent > 2.0 else "skipped_below_abs_threshold"
            elif policy == "novel_key_write":
                key = mem.namespace("fact", name)
                if key in mem.store:
                    out = "skipped_already_present"
                else:
                    if len(mem.store) >= mem.capacity:
                        worst_k = min(mem.store.keys(), key=lambda k: mem.store[k][1])
                        del mem.store[worst_k]
                    mem.store[key] = (city, ent)
                    out = "written_novel_key"

            write_outcomes.append(out)

        # Query phase
        queries_correct_backbone = 0
        queries_correct_memory = 0
        queries_correct_pipeline = 0

        for name, true_city in facts:
            nid = get_name_id(name)
            seq = torch.tensor([[nid, WAS, BORN, IN, DOT, DOT]], dtype=torch.long, device=device)
            with torch.no_grad():
                logits = model(seq)
                pred_tok = logits[:, CITY_POS - 1, :].argmax(dim=-1).item()
                ent = evaluate_local(logits, CITY_POS - 1)[0].item()

            city_by_id = {v: k for k, v in city_map.items()}
            backbone_city = city_by_id.get(pred_tok, None)

            stored = mem.get("fact", name)
            used_mem = stored is not None

            confident = knowledge_boundary(ent, CONFIDENCE_THRESHOLD_NATS) or used_mem
            pipeline_city = stored if used_mem else (backbone_city if confident else "I do not know.")

            if backbone_city == true_city: queries_correct_backbone += 1
            if stored == true_city: queries_correct_memory += 1
            if pipeline_city == true_city: queries_correct_pipeline += 1

        policy_results[policy] = {
            "write_outcomes_counts": {k: write_outcomes.count(k) for k in set(write_outcomes)},
            "memory_final_size": len(mem.store),
            "memory_coverage": mem.coverage("fact", names),
            "mean_teach_entropy": float(np.mean(recorded_entropies)),
            "std_teach_entropy": float(np.std(recorded_entropies)),
            "backbone_accuracy": queries_correct_backbone / len(facts),
            "memory_accuracy": queries_correct_memory / len(facts),
            "pipeline_accuracy": queries_correct_pipeline / len(facts)
        }

    return policy_results

def run_battery_d(device, seed):
    """Battery D: Integrated System & DEC-006 Step 4 Accommodation Analysis"""
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)

    cities = [f"City_{i}" for i in range(15)]
    names = [f"Name_{i}" for i in range(40)]
    facts = [(n, rng.choice(cities)) for n in names]

    strategies = ["baseline_sip001", "sos001_unconditional_episodic", "exposure_aware_boundary", "micro_replay_5step"]
    strat_results = {}

    for strat in strategies:
        torch.manual_seed(seed)
        model = CausalTransformerLM(VOCAB_SIZE, SEQ_LEN).to(device)
        opt = torch.optim.Adam(model.parameters(), lr=3e-4)
        mem = EpisodicMemory(capacity=30)

        name_map, city_map = {}, {}
        def get_name_id(name):
            if name not in name_map: name_map[name] = NAME_BASE + len(name_map)
            return name_map[name]
        def get_city_id(city):
            if city not in city_map: city_map[city] = CITY_BASE + len(city_map)
            return city_map[city]

        # Teach
        for name, city in facts:
            nid, cid = get_name_id(name), get_city_id(city)
            seq = torch.tensor([fact_sequence(nid, cid)], dtype=torch.long, device=device)

            logits = model(seq)
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

            with torch.no_grad():
                ent = evaluate_local(logits, CITY_POS - 1)[0].item()

            if strat == "baseline_sip001":
                mem.gated_write("fact", name, city, ent)
            elif strat == "sos001_unconditional_episodic":
                key = mem.namespace("fact", name)
                if len(mem.store) >= mem.capacity and key not in mem.store:
                    first_k = next(iter(mem.store))
                    del mem.store[first_k]
                mem.store[key] = (city, ent)
            elif strat == "exposure_aware_boundary":
                mem.gated_write("fact", name, city, ent)
            elif strat == "micro_replay_5step":
                mem.unconditional_write("fact", name, city, ent)
                stored_facts = [k.split(":", 1)[1] for k in mem.store if k.startswith("fact:")]
                for _ in range(5):
                    sub_batch = rng.choice(stored_facts, size=min(8, len(stored_facts)), replace=True)
                    seqs = [fact_sequence(get_name_id(fn), get_city_id(mem.get("fact", fn))) for fn in sub_batch]
                    seqs_t = torch.tensor(seqs, dtype=torch.long, device=device)
                    l_rep = F.cross_entropy(model(seqs_t)[:, :-1, :].reshape(-1, VOCAB_SIZE), seqs_t[:, 1:].reshape(-1))
                    opt.zero_grad(); l_rep.backward(); opt.step()

        # Query
        pipeline_correct = 0
        for name, true_city in facts:
            nid = get_name_id(name)
            seq = torch.tensor([[nid, WAS, BORN, IN, DOT, DOT]], dtype=torch.long, device=device)
            with torch.no_grad():
                logits = model(seq)
                pred_tok = logits[:, CITY_POS - 1, :].argmax(dim=-1).item()
                ent = evaluate_local(logits, CITY_POS - 1)[0].item()

            city_by_id = {v: k for k, v in city_map.items()}
            backbone_city = city_by_id.get(pred_tok, None)

            stored = mem.get("fact", name)
            used_mem = stored is not None

            if strat == "exposure_aware_boundary":
                confident = (ent < 4.2) or used_mem
            else:
                confident = (ent < CONFIDENCE_THRESHOLD_NATS) or used_mem

            pipeline_city = stored if used_mem else (backbone_city if confident else "I do not know.")
            if pipeline_city == true_city:
                pipeline_correct += 1

        strat_results[strat] = {
            "pipeline_accuracy": pipeline_correct / len(facts),
            "memory_coverage": mem.coverage("fact", names),
            "final_memory_size": len(mem.store)
        }

    return strat_results

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Executing EXP-022 on device: {device}")

    seeds = [0, 1, 2, 3, 4]

    results_a = [run_battery_a(device, s) for s in seeds]
    results_b = [run_battery_b(device, s) for s in seeds]
    results_c = [run_battery_c(device, s) for s in seeds]
    results_d = [run_battery_d(device, s) for s in seeds]

    # Aggregate Battery A
    bug_detected_count = sum(r["bug_detected"] for r in results_a)
    mean_loss_delta = float(np.mean([r["loss_delta"] for r in results_a]))
    mean_grad_norm = float(np.mean([r["total_grad_norm"] for r in results_a]))

    # Aggregate Battery B
    lrs = ["0.0001", "0.0003", "0.001", "0.003", "0.01", "0.03", "0.1"]
    lr_sweep_summary = {}
    for lr in lrs:
        drops = [r["lr_sweep"][lr]["ent_drop"] for r in results_b]
        confidents = [r["lr_sweep"][lr]["confident"] for r in results_b]
        lr_sweep_summary[lr] = {
            "mean_ent_drop": float(np.mean(drops)),
            "confident_rate": float(np.mean(confidents))
        }

    k_step_summary = {}
    for lr in ["0.0003", "0.01"]:
        trajs = [r["step_trajectories"][lr] for r in results_b]
        steps_summary = []
        for step_idx in range(30):
            entropies = [t[step_idx]["entropy"] for t in trajs]
            accuracies = [t[step_idx]["correct"] for t in trajs]
            confidents = [t[step_idx]["confident"] for t in trajs]
            steps_summary.append({
                "step": step_idx + 1,
                "mean_entropy": float(np.mean(entropies)),
                "accuracy": float(np.mean(accuracies)),
                "confidence_rate": float(np.mean(confidents))
            })
        k_step_summary[lr] = steps_summary

    # Aggregate Battery C
    policies = ["gated_write", "unconditional_write", "absolute_threshold", "novel_key_write"]
    c_summary = {}
    for pol in policies:
        covs = [r[pol]["memory_coverage"] for r in results_c]
        mem_accs = [r[pol]["memory_accuracy"] for r in results_c]
        pipe_accs = [r[pol]["pipeline_accuracy"] for r in results_c]
        c_summary[pol] = {
            "mean_memory_coverage": float(np.mean(covs)),
            "mean_memory_accuracy": float(np.mean(mem_accs)),
            "mean_pipeline_accuracy": float(np.mean(pipe_accs)),
            "skip_not_surprising_count": int(np.mean([r[pol]["write_outcomes_counts"].get("skipped_not_surprising", 0) for r in results_c]))
        }

    # Aggregate Battery D
    strategies = ["baseline_sip001", "sos001_unconditional_episodic", "exposure_aware_boundary", "micro_replay_5step"]
    d_summary = {}
    for strat in strategies:
        accs = [r[strat]["pipeline_accuracy"] for r in results_d]
        covs = [r[strat]["memory_coverage"] for r in results_d]
        d_summary[strat] = {
            "mean_pipeline_accuracy": float(np.mean(accs)),
            "std_pipeline_accuracy": float(np.std(accs)),
            "mean_memory_coverage": float(np.mean(covs))
        }

    output = {
        "exp_id": "EXP-022",
        "n_seeds": len(seeds),
        "battery_a_implementation_bug": {
            "bug_detected": bug_detected_count > 0,
            "mean_loss_delta": mean_loss_delta,
            "mean_grad_norm": mean_grad_norm,
            "causal_mask_verified": all(r["causal_mask_correct"] for r in results_a)
        },
        "battery_b_optimization_artifact": {
            "lr_sweep": lr_sweep_summary,
            "k_step_trajectory": k_step_summary
        },
        "battery_c_algorithmic_limitation": c_summary,
        "battery_d_step4_accommodation": d_summary
    }

    print("\n=================== EXP-022 RESULTS SUMMARY ===================")
    print(json.dumps(output, indent=2))

    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(res_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved full results to {res_path}")

if __name__ == "__main__":
    main()
