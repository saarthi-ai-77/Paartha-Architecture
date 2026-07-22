"""
ACA-MVP-001, Benchmark A -- Consolidation Stretch Ablation (EXP-010 test).

Direct follow-up to EXP-018 (docs/06_experiments/Completed.md), which found
that competence-gated memory provides ZERO measurable protection against
catastrophic forgetting under staged, non-rehearsed continual training --
traced to a specific mechanism: entries are evicted for being "mastered"
right at the moment they become vulnerable to being forgotten by subsequent
training, because point-in-time mastery is treated as permanent safety.

This ablation tests the most direct candidate fix: consolidation-via-replay
(EXP-010, previously unvalidated, already scoped in ACA-MVP-001.md Section 4
as this benchmark's own stretch ablation). At each stage boundary except the
last, before the usual competence-based eviction bookkeeping proceeds, every
entry currently in memory is replayed into a short burst of extra gradient
steps -- reinforcing it directly into the backbone's own weights, not just
leaving it as an external copy -- on the theory that this is what should let
the backbone retain the fact even after its external memory copy is later
evicted to make room for new content. Eviction timing/logic is left
completely unchanged from EXP-018, so this isolates exactly one new
variable: does backbone-side reinforcement help, independent of whether the
external memory copy itself survives?

One new condition only (consolidated_gated_memory), same task/model/capacity/
seeds as EXP-018, compared directly against EXP-018's already-logged
competence_gated_memory (0.158 +/- 0.027) and no_memory (0.158 +/- 0.039)
baselines -- reused rather than re-run, since nothing about their code changes.

REPLAY_STEPS=20 / REPLAY_BATCH=32 are a reasonable first choice, not tuned --
flagged honestly, same as EXP-001's threshold constants.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import time

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device: {device}")

# Identical task/model setup to EXP-018 (experiments/exp_mvp001_continual_recall/run.py)
N_NAMES = 300
N_CITIES = 40
FACTS_PER_STAGE = 100
N_STAGES = 3
MEMORY_CAPACITY = 60

WAS, BORN, IN, DOT = N_NAMES + N_CITIES, N_NAMES + N_CITIES + 1, N_NAMES + N_CITIES + 2, N_NAMES + N_CITIES + 3
VOCAB_SIZE = N_NAMES + N_CITIES + 4

rng_world = np.random.RandomState(0)
NAME_TO_CITY = {i: int(rng_world.randint(0, N_CITIES)) for i in range(N_NAMES)}


def city_token(name_id):
    return N_NAMES + NAME_TO_CITY[name_id]


def make_sequence(name_id):
    return [name_id, WAS, BORN, IN, city_token(name_id), DOT]


CITY_POS = 4
STAGE_NAME_RANGES = [range(s * FACTS_PER_STAGE, (s + 1) * FACTS_PER_STAGE) for s in range(N_STAGES)]

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

    def forward(self, tokens):
        B, T = tokens.shape
        pos = torch.arange(T, device=tokens.device).unsqueeze(0).expand(B, T)
        h = self.tok_embed(tokens) + self.pos_embed(pos)
        h = self.encoder(h, mask=self.causal_mask[:T, :T])
        h = self.ln_out(h)
        return self.lm_head(h)


def param_count(m):
    return sum(p.numel() for p in m.parameters())


class SlotMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}  # name_id -> (city_id, last_signal)

    def get(self, name_id):
        v = self.store.get(name_id)
        return v[0] if v else None

    def __len__(self):
        return len(self.store)


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


def consolidate_and_refresh(memory, model, opt, replay_steps, replay_batch, rng):
    """EXP-010 test: before refreshing eviction-readiness, actively reinforce
    every currently-stored fact into the backbone via extra gradient steps --
    the candidate fix for EXP-018's mastered-then-forgotten mechanism. Does
    NOT change eviction logic/timing -- isolates backbone reinforcement as
    the only new variable."""
    if not memory.store:
        return
    ids = list(memory.store.keys())
    for _ in range(replay_steps):
        batch_ids = rng.choice(ids, size=min(replay_batch, len(ids)), replace=True)
        seqs = torch.tensor([make_sequence(int(i)) for i in batch_ids], dtype=torch.long, device=device)
        logits = model(seqs)
        loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seqs[:, 1:].reshape(-1))
        opt.zero_grad(); loss.backward(); opt.step()

    seqs = torch.tensor([make_sequence(i) for i in ids], dtype=torch.long, device=device)
    with torch.no_grad():
        logits = model(seqs)
        probs = F.softmax(logits[:, CITY_POS - 1, :], dim=-1)
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
REPLAY_STEPS = 20
REPLAY_BATCH = 32


def run_condition(seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    replay_rng = np.random.RandomState(seed + 1000)
    model = CausalTransformerLM().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    memory = SlotMemory(MEMORY_CAPACITY)
    running_ent = []

    for stage in range(N_STAGES):
        stage_names = list(STAGE_NAME_RANGES[stage])
        for step in range(STEPS_PER_STAGE):
            batch_names = rng.choice(stage_names, size=BATCH_SIZE, replace=True)
            seqs = torch.tensor([make_sequence(int(n)) for n in batch_names], dtype=torch.long, device=device)
            logits = model(seqs)
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seqs[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

            with torch.no_grad():
                probs = F.softmax(logits[:, CITY_POS - 1, :], dim=-1)
                ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
            gated_write(memory, batch_names.tolist(), ent.cpu().tolist(), running_ent)

        if stage < N_STAGES - 1:  # no future stage to protect against after the last one
            consolidate_and_refresh(memory, model, opt, REPLAY_STEPS, REPLAY_BATCH, replay_rng)

    results = {}
    for stage in range(N_STAGES):
        stage_names = list(STAGE_NAME_RANGES[stage])
        results[f"stage{stage+1}"] = eval_recall(model, memory, stage_names)
    return results, param_count(model)


SEEDS = range(5)


def main():
    t0 = time.time()
    all_results = []
    n_params = None
    for seed in SEEDS:
        r, np_ = run_condition(seed)
        all_results.append(r)
        n_params = np_
        print(f"seed {seed}: stage1_acc={r['stage1']['with_memory_acc']:.3f} "
              f"(param_only={r['stage1']['param_only_acc']:.3f}, coverage={r['stage1']['coverage']:.3f}) "
              f"stage3_acc={r['stage3']['with_memory_acc']:.3f}")

    accs = [r["stage1"]["with_memory_acc"] for r in all_results]
    param_accs = [r["stage1"]["param_only_acc"] for r in all_results]
    covs = [r["stage1"]["coverage"] for r in all_results]
    s3 = [r["stage3"]["with_memory_acc"] for r in all_results]

    print(f"\nModel parameter count: {n_params}")
    print("\n========== SUMMARY: consolidated_gated_memory, Stage-1 recall after full continual run ==========")
    print(f"stage1_acc={np.mean(accs):.3f}+/-{np.std(accs):.3f}  "
          f"(backbone-only stage1={np.mean(param_accs):.3f})  "
          f"coverage={np.mean(covs):.3f}  stage3_acc={np.mean(s3):.3f}+/-{np.std(s3):.3f}")
    print("\nEXP-018 baselines for direct comparison (same task/model/capacity/seeds, no consolidation):")
    print("  no_memory                stage1_acc=0.158+/-0.039")
    print("  naive_cache_memory       stage1_acc=0.150+/-0.023")
    print("  competence_gated_memory  stage1_acc=0.158+/-0.027  (coverage=0.0, every seed)")

    out = {
        "meta": {"n_names": N_NAMES, "n_cities": N_CITIES, "facts_per_stage": FACTS_PER_STAGE,
                 "memory_capacity": MEMORY_CAPACITY, "steps_per_stage": STEPS_PER_STAGE,
                 "batch_size": BATCH_SIZE, "replay_steps": REPLAY_STEPS, "replay_batch": REPLAY_BATCH,
                 "seeds": list(SEEDS), "param_count": n_params, "elapsed_sec": time.time() - t0},
        "summary": {
            "stage1_acc_mean": float(np.mean(accs)), "stage1_acc_std": float(np.std(accs)),
            "stage1_param_only_mean": float(np.mean(param_accs)),
            "stage1_coverage_mean": float(np.mean(covs)),
            "stage3_acc_mean": float(np.mean(s3)), "stage3_acc_std": float(np.std(s3)),
        },
        "baselines_from_exp018": {
            "no_memory": {"stage1_acc_mean": 0.1579999953508377, "stage1_acc_std": 0.03867815915615009},
            "naive_cache_memory": {"stage1_acc_mean": 0.1499999940395355, "stage1_acc_std": 0.022803506358636903},
            "competence_gated_memory": {"stage1_acc_mean": 0.1579999953508377, "stage1_acc_std": 0.02712931581082347},
        },
        "raw": [{"stage1": r["stage1"], "stage3": r["stage3"]} for r in all_results],
    }
    with open("results_consolidation_ablation.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote results_consolidation_ablation.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
