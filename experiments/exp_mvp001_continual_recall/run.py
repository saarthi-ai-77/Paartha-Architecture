"""
ACA-MVP-001, Benchmark A: Staged Continual Factual Recall with a REAL
Transformer -- the first experiment in this research program to use an
actual multi-head self-attention Transformer decoder rather than an MLP.

Task: word-level causal language modeling over short template sentences
"NAME_i was born in CITY_j ." (6 tokens). 300 distinct (name, city) facts,
introduced in three SEQUENTIAL STAGES of 100 facts each, with NO rehearsal
of earlier stages during later training -- a deliberately harsh catastrophic-
forgetting stress test, sharper than EXP-001's single static distribution.

Honesty note: tokens are procedurally generated identifiers (NAME_000,
CITY_00, ...), not real English words -- this tests real Transformer
architecture and real staged-continual-learning structure, not real-world
language content. Stated explicitly to avoid overclaiming.

Three conditions, 5 seeds each:
  no_memory            -- plain Transformer baseline.
  naive_cache_memory   -- write every name's city on first sight, evict
                          randomly at capacity (EXP-001's naive baseline,
                          now on a real Transformer).
  competence_gated     -- write only when the Transformer's own prediction
                          for the city-token position is uncertain (entropy-
                          gated, EXP-001/009's validated policy), evict the
                          least-uncertain (most "mastered") entry at capacity.

Evaluated on STAGE-1 fact recall specifically, measured only after all
three stages complete -- directly testing whether competence-gated memory
prevents forgetting of the OLDEST facts, not just improves overall recall.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import json
import time

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device: {device}")

# ---------------------------------------------------------------------------
# Vocabulary and staged fact set
# ---------------------------------------------------------------------------
N_NAMES = 300
N_CITIES = 40
FACTS_PER_STAGE = 100
N_STAGES = 3
MEMORY_CAPACITY = 60  # ~20% of total facts, forcing real eviction pressure

# Token ids: 0..N_NAMES-1 = names, N_NAMES..N_NAMES+N_CITIES-1 = cities,
# then function words.
WAS, BORN, IN, DOT = N_NAMES + N_CITIES, N_NAMES + N_CITIES + 1, N_NAMES + N_CITIES + 2, N_NAMES + N_CITIES + 3
VOCAB_SIZE = N_NAMES + N_CITIES + 4

rng_world = np.random.RandomState(0)
NAME_TO_CITY = {i: int(rng_world.randint(0, N_CITIES)) for i in range(N_NAMES)}

def city_token(name_id):
    return N_NAMES + NAME_TO_CITY[name_id]

def make_sequence(name_id):
    # [NAME, was, born, in, CITY, .]
    return [name_id, WAS, BORN, IN, city_token(name_id), DOT]

CITY_POS = 4  # position of the city token in the 6-token sequence

STAGE_NAME_RANGES = [range(s * FACTS_PER_STAGE, (s + 1) * FACTS_PER_STAGE) for s in range(N_STAGES)]

# ---------------------------------------------------------------------------
# A REAL Transformer decoder (causal self-attention), not an MLP.
# ---------------------------------------------------------------------------
D_MODEL = 128
N_HEAD = 4
N_LAYERS = 4
FFN_DIM = 256
SEQ_LEN = 6

class CausalTransformerLM(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok_embed = nn.Embedding(VOCAB_SIZE, D_MODEL)
        self.pos_embed = nn.Embedding(SEQ_LEN, D_MODEL)
        layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL, nhead=N_HEAD, dim_feedforward=FFN_DIM,
            batch_first=True, activation='gelu',
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=N_LAYERS)
        self.ln_out = nn.LayerNorm(D_MODEL)
        self.lm_head = nn.Linear(D_MODEL, VOCAB_SIZE)
        causal_mask = torch.triu(torch.full((SEQ_LEN, SEQ_LEN), float('-inf')), diagonal=1)
        self.register_buffer('causal_mask', causal_mask)

    def forward(self, tokens, return_hidden=False):
        B, T = tokens.shape
        pos = torch.arange(T, device=tokens.device).unsqueeze(0).expand(B, T)
        h = self.tok_embed(tokens) + self.pos_embed(pos)
        h = self.encoder(h, mask=self.causal_mask[:T, :T])
        h = self.ln_out(h)
        logits = self.lm_head(h)
        if return_hidden:
            return logits, h
        return logits


def param_count(m):
    return sum(p.numel() for p in m.parameters())


# ---------------------------------------------------------------------------
# Memory: fixed-capacity name -> city store.
# ---------------------------------------------------------------------------
class SlotMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}  # name_id -> (city_id, last_signal)

    def get(self, name_id):
        v = self.store.get(name_id)
        return v[0] if v else None

    def __len__(self):
        return len(self.store)


def naive_write(memory, name_ids, rng):
    for nid in name_ids:
        nid = int(nid)
        if nid in memory.store:
            continue
        if len(memory) >= memory.capacity:
            evict_id = rng.choice(list(memory.store.keys()))
            del memory.store[evict_id]
        memory.store[nid] = (NAME_TO_CITY[nid], 0.0)


def gated_write(memory, name_ids, entropies, running):
    for nid, ent in zip(name_ids, entropies):
        nid = int(nid); ent = float(ent)
        running.append(ent)
        if nid in memory.store:
            continue
        median = np.median(running[-500:]) if len(running) >= 10 else ent
        if ent <= median:
            continue
        if len(memory) >= memory.capacity:
            worst_id, worst_ent = None, None
            for sid, (_, sent) in memory.store.items():
                if worst_ent is None or sent < worst_ent:
                    worst_id, worst_ent = sid, sent
            if worst_ent is not None and worst_ent < median:
                del memory.store[worst_id]
            else:
                continue
        memory.store[nid] = (NAME_TO_CITY[nid], ent)


def refresh_gated_confidences(memory, model):
    """Recompute stored entries' current entropy so eviction reflects the
    backbone's CURRENT mastery, not the value at write time (mirrors
    EXP-001's mastery-based eviction, which re-checks live)."""
    if not memory.store:
        return
    ids = list(memory.store.keys())
    seqs = torch.tensor([make_sequence(i) for i in ids], dtype=torch.long, device=device)
    with torch.no_grad():
        logits = model(seqs)
        probs = F.softmax(logits[:, CITY_POS - 1, :], dim=-1)  # predict token at CITY_POS from prefix ending at CITY_POS-1
        ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
    for i, nid in enumerate(ids):
        city, _ = memory.store[nid]
        memory.store[nid] = (city, float(ent[i]))


def eval_recall(model, memory, name_ids):
    ids = torch.tensor(sorted(name_ids), dtype=torch.long, device=device)
    seqs = torch.stack([torch.tensor(make_sequence(int(i)), device=device) for i in ids])
    with torch.no_grad():
        logits = model(seqs)
        pred_city_tok = logits[:, CITY_POS - 1, :].argmax(dim=-1)
    true_city_tok = torch.tensor([city_token(int(i)) for i in ids], device=device)
    param_acc = (pred_city_tok == true_city_tok).float().mean().item()

    if memory is None:
        return {"param_only_acc": param_acc, "with_memory_acc": param_acc, "coverage": 0.0}

    final_pred = pred_city_tok.clone()
    covered = 0
    for i, nid in enumerate(ids.tolist()):
        v = memory.get(nid)
        if v is not None:
            final_pred[i] = N_NAMES + v
            covered += 1
    mem_acc = (final_pred == true_city_tok).float().mean().item()
    return {"param_only_acc": param_acc, "with_memory_acc": mem_acc, "coverage": covered / len(ids)}


STEPS_PER_STAGE = 800
BATCH_SIZE = 32
LR = 3e-4


def run_condition(name, use_memory, policy, seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    model = CausalTransformerLM().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    memory = SlotMemory(MEMORY_CAPACITY) if use_memory else None
    running_ent = []

    for stage in range(N_STAGES):
        stage_names = list(STAGE_NAME_RANGES[stage])
        for step in range(STEPS_PER_STAGE):
            batch_names = rng.choice(stage_names, size=BATCH_SIZE, replace=True)
            seqs = torch.tensor([make_sequence(int(n)) for n in batch_names], dtype=torch.long, device=device)
            logits = model(seqs)
            # Standard next-token LM loss over the whole sequence.
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seqs[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

            if use_memory:
                with torch.no_grad():
                    probs = F.softmax(logits[:, CITY_POS - 1, :], dim=-1)
                    ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
                if policy == "naive":
                    naive_write(memory, batch_names.tolist(), rng)
                elif policy == "gated":
                    gated_write(memory, batch_names.tolist(), ent.cpu().tolist(), running_ent)
        if use_memory and policy == "gated":
            refresh_gated_confidences(memory, model)  # mastery re-check at stage boundary

    results = {}
    for stage in range(N_STAGES):
        stage_names = list(STAGE_NAME_RANGES[stage])
        results[f"stage{stage+1}"] = eval_recall(model, memory, stage_names)
    return results, param_count(model)


SEEDS = range(5)
CONDITIONS = [
    ("no_memory", False, None),
    ("naive_cache_memory", True, "naive"),
    ("competence_gated_memory", True, "gated"),
]


def main():
    t0 = time.time()
    all_results = {name: [] for name, _, _ in CONDITIONS}
    n_params = None

    for seed in SEEDS:
        print(f"\n### seed {seed} ###")
        for name, use_mem, policy in CONDITIONS:
            r, np_ = run_condition(name, use_mem, policy, seed)
            all_results[name].append(r)
            n_params = np_
            print(f"  {name:26s} stage1_acc={r['stage1']['with_memory_acc']:.3f} "
                  f"(param_only={r['stage1']['param_only_acc']:.3f}) "
                  f"stage3_acc={r['stage3']['with_memory_acc']:.3f}")

    print(f"\nModel parameter count: {n_params}")
    print("\n========== SUMMARY: Stage-1 (oldest facts) recall after full continual run ==========")
    summary = {}
    for name, _, _ in CONDITIONS:
        accs = [r["stage1"]["with_memory_acc"] for r in all_results[name]]
        param_accs = [r["stage1"]["param_only_acc"] for r in all_results[name]]
        s3 = [r["stage3"]["with_memory_acc"] for r in all_results[name]]
        summary[name] = {
            "stage1_acc_mean": float(np.mean(accs)), "stage1_acc_std": float(np.std(accs)),
            "stage1_param_only_mean": float(np.mean(param_accs)),
            "stage3_acc_mean": float(np.mean(s3)), "stage3_acc_std": float(np.std(s3)),
        }
        print(f"{name:26s} stage1_acc={np.mean(accs):.3f}+/-{np.std(accs):.3f}  "
              f"(backbone-only stage1={np.mean(param_accs):.3f})  stage3_acc={np.mean(s3):.3f}+/-{np.std(s3):.3f}")

    out = {
        "meta": {"n_names": N_NAMES, "n_cities": N_CITIES, "facts_per_stage": FACTS_PER_STAGE,
                 "memory_capacity": MEMORY_CAPACITY, "steps_per_stage": STEPS_PER_STAGE,
                 "batch_size": BATCH_SIZE, "seeds": list(SEEDS), "param_count": n_params,
                 "elapsed_sec": time.time() - t0},
        "summary": summary,
        "raw": {name: [{"stage1": r["stage1"], "stage3": r["stage3"]} for r in res]
                for name, res in all_results.items()},
    }
    with open("results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote results.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
