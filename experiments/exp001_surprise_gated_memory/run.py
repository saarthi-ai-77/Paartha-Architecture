"""
EXP-001: Surprise-Gated Capacity-Constrained Episodic Memory
vs. Naive Caching vs. Pure Parametric Baseline

Hypothesis under test:
  Under a FIXED, LIMITED memory capacity (smaller than the number of distinct
  facts), a write/eviction policy that only stores facts the parametric
  backbone still gets wrong, and evicts facts the backbone has since
  "mastered" (low current loss), achieves higher recall on rare/long-tail
  facts than a naive cache (write on first sight, evict at random) at the
  SAME capacity -- and both beat a pure parametric model with no memory.

This isolates the specific novel design choice (competence-aware, adaptive
memory allocation) from the well-established claim that "external memory
helps" (kNN-LM, RETRO already showed that). We are not testing whether
memory helps in general -- we are testing whether OUR allocation policy is
actually better than the obvious naive alternative at equal capacity.

Task: synthetic associative recall. N_FACTS distinct facts, each a
(random fixed key vector -> value id) pair with NO shared structure between
facts (key vectors are near-orthogonal random unit vectors), so there is
zero possibility of parametric generalization across facts -- purely a
memorization stress test. Facts are sampled during training according to a
Zipfian (power-law) distribution, so most facts are rare (seen a handful of
times) while a few are frequent -- mirroring long-tail real-world knowledge.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import time

torch.manual_seed(0)
np.random.seed(0)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device: {device}")

# ---------------------------------------------------------------------------
# Task setup
# ---------------------------------------------------------------------------
N_FACTS = 1000
KEY_DIM = 32
HIDDEN = 128
MEMORY_CAPACITY = 200          # 20% of facts -- forces real eviction pressure
TRAIN_STEPS = 1250
BATCH_SIZE = 32
EVAL_EVERY = 100
ZIPF_EXPONENT = 1.3
SURPRISE_WRITE_THRESHOLD = 2.0   # nats; roughly "wrong prediction" territory
MASTERED_THRESHOLD = 0.3         # nats; "backbone has learned this well"

# Fixed random near-orthogonal keys (unit vectors), fixed random value labels.
key_vectors = torch.randn(N_FACTS, KEY_DIM)
key_vectors = key_vectors / key_vectors.norm(dim=-1, keepdim=True)
key_vectors = key_vectors.to(device)
value_ids = torch.arange(N_FACTS).to(device)  # each fact's correct class == its own id

# Zipfian sampling weights over facts (rank 1 = most frequent)
ranks = np.arange(1, N_FACTS + 1)
weights = 1.0 / (ranks ** ZIPF_EXPONENT)
weights = weights / weights.sum()

# Ground-truth exposure count each fact will get across TRAIN_STEPS*BATCH_SIZE
# samples, used post-hoc to define "tail" (rare) vs "head" (frequent) facts.
expected_exposures = weights * TRAIN_STEPS * BATCH_SIZE
TAIL_FACTS = set(np.where(expected_exposures <= 3)[0].tolist())
HEAD_FACTS = set(np.where(expected_exposures >= 30)[0].tolist())
print(f"tail facts (<=3 expected exposures): {len(TAIL_FACTS)}")
print(f"head facts (>=30 expected exposures): {len(HEAD_FACTS)}")


def sample_batch(batch_size, rng: np.random.RandomState):
    idx = rng.choice(N_FACTS, size=batch_size, p=weights)
    idx_t = torch.tensor(idx, dtype=torch.long, device=device)
    keys = key_vectors[idx_t]
    vals = value_ids[idx_t].to(device)
    return idx_t, keys, vals


# ---------------------------------------------------------------------------
# Parametric backbone (shared architecture across all three conditions)
# ---------------------------------------------------------------------------
class Backbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(KEY_DIM, HIDDEN), nn.ReLU(),
            nn.Linear(HIDDEN, HIDDEN), nn.ReLU(),
            nn.Linear(HIDDEN, N_FACTS),
        )

    def forward(self, keys):
        return self.net(keys)


def make_backbone_and_opt():
    m = Backbone().to(device)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    return m, opt


# ---------------------------------------------------------------------------
# Episodic memory: fixed-capacity slot store over fact ids -> value ids.
# Retrieval is exact (fact id lookup) since keys are fixed per fact --
# the interesting variable under test is the WRITE/EVICTION POLICY, not
# retrieval mechanics.
# ---------------------------------------------------------------------------
class SlotMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}  # fact_id -> value_id

    def get(self, fact_id):
        return self.store.get(fact_id, None)

    def __len__(self):
        return len(self.store)


def naive_write(memory: SlotMemory, fact_ids, rng: np.random.RandomState):
    """Write on first sight. Evict a UNIFORMLY RANDOM existing slot if full."""
    for fid in fact_ids:
        fid = int(fid)
        if fid in memory.store:
            continue
        if len(memory) >= memory.capacity:
            evict_key = rng.choice(list(memory.store.keys()))
            del memory.store[evict_key]
        memory.store[fid] = fid  # value == fact id in this task


def surprise_gated_write(memory: SlotMemory, fact_ids, losses, backbone, rng):
    """Only write facts the backbone currently gets wrong (high loss).
    When full, evict whichever CURRENTLY STORED fact the backbone now
    predicts best (lowest current loss) -- i.e. free capacity from facts
    the backbone has since mastered parametrically."""
    for fid, loss in zip(fact_ids, losses):
        fid = int(fid)
        loss = float(loss)
        if fid in memory.store:
            continue  # already retained, no action needed
        if loss <= SURPRISE_WRITE_THRESHOLD:
            continue  # backbone already handles this fine, no need to store
        if len(memory) >= memory.capacity:
            # Recompute current backbone loss for every stored fact, evict
            # the one the backbone now handles best (most "mastered").
            stored_ids = list(memory.store.keys())
            stored_idx = torch.tensor(stored_ids, dtype=torch.long, device=device)
            with torch.no_grad():
                logits = backbone(key_vectors[stored_idx])
                targets = value_ids[stored_idx].to(device)
                cur_losses = F.cross_entropy(logits, targets, reduction='none')
            worst_mastery_idx = torch.argmin(cur_losses).item()
            evict_key = stored_ids[worst_mastery_idx]
            # Only evict if that stored fact is actually mastered now;
            # otherwise everything in memory is still needed -- skip write.
            if cur_losses[worst_mastery_idx].item() > MASTERED_THRESHOLD:
                continue
            del memory.store[evict_key]
        memory.store[fid] = fid


# ---------------------------------------------------------------------------
# Evaluation: for each condition, measure accuracy split by head/tail facts,
# with and without the memory override at inference time.
# ---------------------------------------------------------------------------
def evaluate(backbone, memory, fact_id_set, label):
    if not fact_id_set:
        return None
    ids = torch.tensor(sorted(fact_id_set), dtype=torch.long, device=device)
    keys = key_vectors[ids]
    targets = value_ids[ids].to(device)
    with torch.no_grad():
        logits = backbone(keys)
        param_preds = logits.argmax(dim=-1)
    param_acc = (param_preds == targets).float().mean().item()

    if memory is not None:
        final_preds = param_preds.clone()
        for i, fid in enumerate(ids.tolist()):
            v = memory.get(fid)
            if v is not None:
                final_preds[i] = v
        mem_acc = (final_preds == targets).float().mean().item()
        mem_coverage = sum(1 for fid in ids.tolist() if memory.get(fid) is not None) / len(ids)
    else:
        mem_acc = param_acc
        mem_coverage = 0.0
    return {
        "label": label,
        "param_only_acc": param_acc,
        "with_memory_acc": mem_acc,
        "memory_coverage": mem_coverage,
        "n": len(ids),
    }


# ---------------------------------------------------------------------------
# Run all three conditions
# ---------------------------------------------------------------------------
def run_condition(name, use_memory, seed):
    # Identical backbone init AND identical sampled-fact sequence across
    # conditions for a given seed -- the write/eviction policy is the only
    # thing allowed to differ.
    torch.manual_seed(seed)
    sample_rng = np.random.RandomState(seed)
    evict_rng = np.random.RandomState(seed + 10_000)

    backbone, opt = make_backbone_and_opt()
    memory = SlotMemory(MEMORY_CAPACITY) if use_memory else None
    history = []

    for step in range(1, TRAIN_STEPS + 1):
        fact_ids, keys, targets = sample_batch(BATCH_SIZE, sample_rng)
        logits = backbone(keys)
        per_ex_loss = F.cross_entropy(logits, targets, reduction='none')
        loss = per_ex_loss.mean()
        opt.zero_grad()
        loss.backward()
        opt.step()

        if use_memory:
            if name == "naive_cache":
                naive_write(memory, fact_ids.tolist(), evict_rng)
            elif name == "surprise_gated":
                with torch.no_grad():
                    cur_logits = backbone(keys)
                    cur_losses = F.cross_entropy(cur_logits, targets, reduction='none')
                surprise_gated_write(memory, fact_ids.tolist(), cur_losses.tolist(), backbone, evict_rng)

        if step % EVAL_EVERY == 0 or step == TRAIN_STEPS:
            tail = evaluate(backbone, memory, TAIL_FACTS, "tail")
            head = evaluate(backbone, memory, HEAD_FACTS, "head")
            entry = {"step": step, "tail": tail, "head": head,
                     "memory_size": len(memory) if memory else 0}
            history.append(entry)

    final_tail = evaluate(backbone, memory, TAIL_FACTS, "tail")
    final_head = evaluate(backbone, memory, HEAD_FACTS, "head")
    return {
        "condition": name,
        "final_tail": final_tail,
        "final_head": final_head,
        "final_memory_size": len(memory) if memory else 0,
        "history": history,
    }


SEEDS = [0, 1, 2, 3, 4]
CONDITIONS = [
    ("no_memory_baseline", False),
    ("naive_cache", True),
    ("surprise_gated", True),
]


def main():
    t0 = time.time()
    per_seed_results = {name: [] for name, _ in CONDITIONS}

    for seed in SEEDS:
        print(f"\n########## SEED {seed} ##########")
        for name, use_memory in CONDITIONS:
            r = run_condition(name, use_memory, seed)
            per_seed_results[name].append(r)
            ft, fh = r["final_tail"], r["final_head"]
            print(f"[seed {seed}] {name:20s} tail: param={ft['param_only_acc']:.3f} "
                  f"mem={ft['with_memory_acc']:.3f} cov={ft['memory_coverage']:.3f} | "
                  f"head: param={fh['param_only_acc']:.3f} mem={fh['with_memory_acc']:.3f} "
                  f"cov={fh['memory_coverage']:.3f}")

    def agg(name, key_path):
        vals = []
        for r in per_seed_results[name]:
            d = r
            for k in key_path:
                d = d[k]
            vals.append(d)
        arr = np.array(vals, dtype=float)
        return {"mean": float(arr.mean()), "std": float(arr.std()), "values": vals}

    summary = {}
    for name, _ in CONDITIONS:
        summary[name] = {
            "tail_with_memory_acc": agg(name, ["final_tail", "with_memory_acc"]),
            "tail_param_only_acc": agg(name, ["final_tail", "param_only_acc"]),
            "tail_memory_coverage": agg(name, ["final_tail", "memory_coverage"]),
            "head_with_memory_acc": agg(name, ["final_head", "with_memory_acc"]),
            "head_memory_coverage": agg(name, ["final_head", "memory_coverage"]),
        }

    print("\n========== SUMMARY ACROSS SEEDS ==========")
    for name, _ in CONDITIONS:
        s = summary[name]
        print(f"{name:20s} tail_mem_acc={s['tail_with_memory_acc']['mean']:.3f}"
              f"+/-{s['tail_with_memory_acc']['std']:.3f}  "
              f"tail_coverage={s['tail_memory_coverage']['mean']:.3f}  "
              f"head_coverage={s['head_memory_coverage']['mean']:.3f}")

    out = {
        "meta": {
            "n_facts": N_FACTS,
            "memory_capacity": MEMORY_CAPACITY,
            "train_steps": TRAIN_STEPS,
            "batch_size": BATCH_SIZE,
            "zipf_exponent": ZIPF_EXPONENT,
            "n_tail_facts": len(TAIL_FACTS),
            "n_head_facts": len(HEAD_FACTS),
            "surprise_write_threshold": SURPRISE_WRITE_THRESHOLD,
            "mastered_threshold": MASTERED_THRESHOLD,
            "seeds": SEEDS,
            "elapsed_sec": time.time() - t0,
        },
        "summary": summary,
        "per_seed": {name: [
            {"seed": seed, "final_tail": r["final_tail"], "final_head": r["final_head"],
             "final_memory_size": r["final_memory_size"]}
            for seed, r in zip(SEEDS, per_seed_results[name])
        ] for name, _ in CONDITIONS},
    }

    out_path = "results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {out_path} in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
