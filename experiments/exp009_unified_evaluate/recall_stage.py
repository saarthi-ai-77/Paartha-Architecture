"""
EXP-009, Stage 1 + Stage 3: Does a label-free EVALUATE signal work for
(1) memory write/eviction gating and (3) wrongness-detection, on EXP-001's
validated recall task?

Three label-free candidates, none of which see the true label at decision
time (only during training/calibration, exactly as a deployed system would
be constrained):

  ENTROPY      -- H(softmax(logits)). Cheapest, most common baseline.
  ENSEMBLE     -- K independently-initialized backbones, same data stream;
                  mean pairwise KL divergence between their output
                  distributions as the disagreement signal.
  SELFASSESS   -- a small auxiliary head trained to predict the backbone's
                  OWN cross-entropy loss from its hidden representation
                  (Yoo & Kweon, "Learning Loss for Active Learning", 2019 --
                  an established technique, not invented here). Trained
                  using the true loss as a regression target (available
                  during training); used at decision time via its own
                  output only, never the label.

Compared against the ORACLE (EXP-001's actual validated signal: true
cross-entropy loss against the real label) and a NO-MEMORY baseline.

Stage 1 (gating): substitute each candidate for the oracle's write/evict
gate, using an adaptive (running-median) threshold so differently-scaled
signals are compared fairly, and measure tail-fact recall accuracy.

Stage 3 (wrongness-detection): does each candidate's value, ranked, separate
inputs the model gets right from inputs it gets wrong? Measured by AUC
(computed manually via the rank-sum identity, no sklearn dependency).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import time

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device: {device}")

# ---------------------------------------------------------------------------
# World setup -- identical to EXP-001
# ---------------------------------------------------------------------------
N_FACTS = 1000
KEY_DIM = 32
HIDDEN = 128
MEMORY_CAPACITY = 200
ZIPF_EXPONENT = 1.3
TRAIN_STEPS = 1250
BATCH_SIZE = 32
ENSEMBLE_K = 3

key_vectors = torch.randn(N_FACTS, KEY_DIM)
key_vectors = (key_vectors / key_vectors.norm(dim=-1, keepdim=True)).to(device)
value_ids = torch.arange(N_FACTS).to(device)

ranks = np.arange(1, N_FACTS + 1)
weights = 1.0 / (ranks ** ZIPF_EXPONENT)
weights = weights / weights.sum()

expected_exposures = weights * TRAIN_STEPS * BATCH_SIZE
TAIL_FACTS = set(np.where(expected_exposures <= 3)[0].tolist())
HEAD_FACTS = set(np.where(expected_exposures >= 30)[0].tolist())


def sample_batch(batch_size, rng):
    idx = rng.choice(N_FACTS, size=batch_size, p=weights)
    idx_t = torch.tensor(idx, dtype=torch.long, device=device)
    return idx_t, key_vectors[idx_t], value_ids[idx_t]


class Backbone(nn.Module):
    """Same architecture as EXP-001, but exposes its hidden representation
    (needed by the self-assessment head and, optionally, for inspection)."""
    def __init__(self):
        super().__init__()
        self.l1 = nn.Linear(KEY_DIM, HIDDEN)
        self.l2 = nn.Linear(HIDDEN, HIDDEN)
        self.out = nn.Linear(HIDDEN, N_FACTS)

    def forward(self, keys, return_hidden=False):
        h1 = F.relu(self.l1(keys))
        h2 = F.relu(self.l2(h1))
        logits = self.out(h2)
        if return_hidden:
            return logits, h2
        return logits


class SelfAssessHead(nn.Module):
    """Predicts the backbone's own cross-entropy loss from its hidden state.
    Trained with the true loss as a regression target; used at decision
    time via its output only (Yoo & Kweon, 2019)."""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(HIDDEN, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, hidden):
        return self.net(hidden).squeeze(-1)


class SlotMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}  # fact_id -> (value_id, last_signal_value)

    def get(self, fact_id):
        return self.store.get(fact_id, (None, None))[0]

    def __len__(self):
        return len(self.store)


def running_median_write_evict(memory, fact_ids, signal_values, value_targets, running_signals):
    """Adaptive-threshold gating: write if signal exceeds the running
    median observed so far (label-free, scale-agnostic across candidate
    signal types); evict the stored entry with the LOWEST current signal
    (most 'confident'/mastered) when full."""
    for fid, sig, val in zip(fact_ids, signal_values, value_targets):
        fid = int(fid); sig = float(sig); val = int(val)
        running_signals.append(sig)
        if fid in memory.store:
            continue
        median = np.median(running_signals[-500:]) if len(running_signals) >= 10 else sig
        if sig <= median:
            continue  # not surprising relative to recent experience -> don't write
        if len(memory) >= memory.capacity:
            worst_id, worst_sig = None, None
            for sid, (sval, ssig) in memory.store.items():
                if worst_sig is None or ssig < worst_sig:
                    worst_id, worst_sig = sid, ssig
            if worst_sig is not None and worst_sig < median:
                del memory.store[worst_id]
            else:
                continue
        memory.store[fid] = (val, sig)


def eval_recall_with_memory(backbone, memory, fact_id_set):
    if not fact_id_set:
        return None
    ids = torch.tensor(sorted(fact_id_set), dtype=torch.long, device=device)
    keys = key_vectors[ids]
    targets = value_ids[ids]
    with torch.no_grad():
        logits = backbone(keys)
        param_preds = logits.argmax(dim=-1)
    final_preds = param_preds.clone()
    for i, fid in enumerate(ids.tolist()):
        v = memory.get(fid)
        if v is not None:
            final_preds[i] = v
    mem_acc = (final_preds == targets).float().mean().item()
    coverage = sum(1 for fid in ids.tolist() if memory.get(fid) is not None) / len(ids)
    return {"with_memory_acc": mem_acc, "coverage": coverage}


def manual_auc(scores, labels):
    """AUC via the rank-sum (Mann-Whitney U) identity -- no sklearn needed.
    labels: 1 = wrong (positive class we want the signal to catch), 0 = right."""
    scores = np.asarray(scores); labels = np.asarray(labels)
    n_pos = labels.sum(); n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float('nan')
    order = np.argsort(scores)
    ranks = np.empty(len(scores))
    ranks[order] = np.arange(1, len(scores) + 1)
    rank_sum_pos = ranks[labels == 1].sum()
    auc = (rank_sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc)


def run_seed(seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)

    # --- Train the primary backbone + self-assessment head jointly ---
    backbone = Backbone().to(device)
    assess_head = SelfAssessHead().to(device)
    opt = torch.optim.Adam(list(backbone.parameters()) + list(assess_head.parameters()), lr=1e-3)

    # --- Train an ensemble of K independent backbones on the SAME stream ---
    ensemble = [Backbone().to(device) for _ in range(ENSEMBLE_K)]
    ens_opts = [torch.optim.Adam(m.parameters(), lr=1e-3) for m in ensemble]

    for step in range(1, TRAIN_STEPS + 1):
        fact_ids, keys, targets = sample_batch(BATCH_SIZE, rng)

        logits, hidden = backbone(keys, return_hidden=True)
        per_ex_loss = F.cross_entropy(logits, targets, reduction='none')
        loss = per_ex_loss.mean()
        opt.zero_grad()
        pred_loss = assess_head(hidden.detach())
        assess_loss = F.mse_loss(pred_loss, per_ex_loss.detach())
        (loss + assess_loss).backward()
        opt.step()

        for m, o in zip(ensemble, ens_opts):
            m_logits = m(keys)
            m_loss = F.cross_entropy(m_logits, targets)
            o.zero_grad(); m_loss.backward(); o.step()

    # --- Build the four gated memories (three candidates + oracle), using
    #     the SAME trained backbone/ensemble/head, replayed over the SAME
    #     data stream so gating decisions are directly comparable ---
    rng2 = np.random.RandomState(seed)  # replay identical stream
    memories = {name: SlotMemory(MEMORY_CAPACITY) for name in
                ["oracle_true_loss", "entropy", "ensemble", "selfassess"]}
    running = {name: [] for name in memories}

    # Collect wrongness-detection data as we go (Stage 3)
    detect_scores = {name: [] for name in ["entropy", "ensemble", "selfassess"]}
    detect_labels = []

    for step in range(1, TRAIN_STEPS + 1):
        fact_ids, keys, targets = sample_batch(BATCH_SIZE, rng2)
        with torch.no_grad():
            logits, hidden = backbone(keys, return_hidden=True)
            true_loss = F.cross_entropy(logits, targets, reduction='none')
            preds = logits.argmax(dim=-1)
            wrong = (preds != targets).long()

            probs = F.softmax(logits, dim=-1)
            entropy = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)

            ens_probs = [F.softmax(m(keys), dim=-1) for m in ensemble]
            disagreement = torch.zeros(len(fact_ids), device=device)
            pairs = 0
            for i in range(ENSEMBLE_K):
                for j in range(i + 1, ENSEMBLE_K):
                    p, q = ens_probs[i].clamp_min(1e-9), ens_probs[j].clamp_min(1e-9)
                    kl = (p * (p.log() - q.log())).sum(dim=-1)
                    disagreement += kl
                    pairs += 1
            disagreement /= pairs

            selfassess = assess_head(hidden)

        detect_scores["entropy"].extend(entropy.cpu().tolist())
        detect_scores["ensemble"].extend(disagreement.cpu().tolist())
        detect_scores["selfassess"].extend(selfassess.cpu().tolist())
        detect_labels.extend(wrong.cpu().tolist())

        fid_list = fact_ids.tolist(); val_list = targets.tolist()
        running_median_write_evict(memories["oracle_true_loss"], fid_list, true_loss.cpu().tolist(), val_list, running["oracle_true_loss"])
        running_median_write_evict(memories["entropy"], fid_list, entropy.cpu().tolist(), val_list, running["entropy"])
        running_median_write_evict(memories["ensemble"], fid_list, disagreement.cpu().tolist(), val_list, running["ensemble"])
        running_median_write_evict(memories["selfassess"], fid_list, selfassess.cpu().tolist(), val_list, running["selfassess"])

    stage1 = {}
    for name, mem in memories.items():
        stage1[name] = {
            "tail": eval_recall_with_memory(backbone, mem, TAIL_FACTS),
            "head": eval_recall_with_memory(backbone, mem, HEAD_FACTS),
            "memory_size": len(mem),
        }
    no_mem_tail = eval_recall_with_memory(backbone, SlotMemory(0), TAIL_FACTS)
    stage1["no_memory_baseline"] = {"tail": no_mem_tail, "head": eval_recall_with_memory(backbone, SlotMemory(0), HEAD_FACTS), "memory_size": 0}

    stage3 = {}
    for name in ["entropy", "ensemble", "selfassess"]:
        stage3[name] = manual_auc(detect_scores[name], detect_labels)

    return stage1, stage3


def main():
    t0 = time.time()
    SEEDS = range(5)
    all_stage1 = {name: [] for name in ["oracle_true_loss", "entropy", "ensemble", "selfassess", "no_memory_baseline"]}
    all_stage3 = {name: [] for name in ["entropy", "ensemble", "selfassess"]}

    for seed in SEEDS:
        print(f"\n### seed {seed} ###")
        s1, s3 = run_seed(seed)
        for name, res in s1.items():
            all_stage1[name].append(res)
            print(f"  [gating] {name:20s} tail_acc={res['tail']['with_memory_acc']:.3f} "
                  f"tail_cov={res['tail']['coverage']:.3f} mem_size={res['memory_size']}")
        for name, auc in s3.items():
            all_stage3[name].append(auc)
            print(f"  [detect] {name:20s} AUC={auc:.3f}")

    print("\n========== STAGE 1 SUMMARY (memory-gating, tail recall acc) ==========")
    stage1_summary = {}
    for name in all_stage1:
        accs = [r["tail"]["with_memory_acc"] for r in all_stage1[name]]
        stage1_summary[name] = {"mean": float(np.mean(accs)), "std": float(np.std(accs))}
        print(f"{name:20s} {np.mean(accs):.3f} +/- {np.std(accs):.3f}")

    print("\n========== STAGE 3 SUMMARY (wrongness-detection AUC) ==========")
    stage3_summary = {}
    for name in all_stage3:
        aucs = all_stage3[name]
        stage3_summary[name] = {"mean": float(np.mean(aucs)), "std": float(np.std(aucs))}
        print(f"{name:20s} {np.mean(aucs):.3f} +/- {np.std(aucs):.3f}")

    out = {
        "meta": {"seeds": list(SEEDS), "elapsed_sec": time.time() - t0, "ensemble_k": ENSEMBLE_K},
        "stage1_gating_summary": stage1_summary,
        "stage3_detection_summary": stage3_summary,
        "stage1_raw": {name: [{"tail_acc": r["tail"]["with_memory_acc"], "tail_cov": r["tail"]["coverage"],
                                "head_acc": r["head"]["with_memory_acc"], "mem_size": r["memory_size"]}
                               for r in results] for name, results in all_stage1.items()},
        "stage3_raw": all_stage3,
    }
    with open("recall_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote recall_results.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
