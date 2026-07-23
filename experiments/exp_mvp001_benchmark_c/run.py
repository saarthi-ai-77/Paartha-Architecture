"""
ACA-MVP-001, Benchmark C: Joint Composability Test at Real Scale.

Combines Benchmark A's recall pathway (real causal Transformer + competence-
gated episodic memory) and Benchmark B's compose pathway (fixed, verified
SCAN grammar + a small learned primitive classifier) into ONE model with
disjoint parameters, ONE optimizer, trained on mixed batches every step --
directly extending EXP-004's toy-scale composability finding ("do two
independently-validated mechanisms interfere when trained together in one
model, one optimizer") to real backbones and real tasks, per
docs/11_mvp/ACA-MVP-001.md Section 3.

This is a composability test, not a re-litigation of either pathway's own
result: ME-03 (memory) is already known, honestly, to provide no benefit
under staged continual training (EXP-018/010); RC-01 (structure-matched
compose) is already known to succeed decisively on real SCAN (EXP-020). The
question here is narrower and different: does training both pathways
TOGETHER, in one model, cause either one's performance to degrade relative
to its OWN already-measured isolated result? EXP-004 found no such
interference at toy scale under a disjoint-parameter design; this is the
first test of whether that finding survives real backbones and real,
unrelated tasks (facts vs. SCAN commands) sharing one training loop.

Pre-registered comparison (stated before running):
  Recall pathway, joint vs. isolated:   EXP-018 competence_gated_memory
                                          stage-1 acc = 0.158 +/- 0.027
  Compose pathway, joint vs. isolated:  EXP-020 structure-matched
                                          test acc = 1.000 +/- 0.000
No interference: joint-trained numbers statistically indistinguishable from
these isolated baselines. Interference: a real, measurable gap.
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import time

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device: {device}")

SCAN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exp_mvp001_scan_compositional")

# ---------------------------------------------------------------------------
# Recall pathway vocabulary/model -- identical to Benchmark A (EXP-018).
# ---------------------------------------------------------------------------
N_NAMES = 300
N_CITIES = 40
FACTS_PER_STAGE = 100
N_STAGES = 3
MEMORY_CAPACITY = 60

RWAS, RBORN, RIN, RDOT = N_NAMES + N_CITIES, N_NAMES + N_CITIES + 1, N_NAMES + N_CITIES + 2, N_NAMES + N_CITIES + 3
RECALL_VOCAB_SIZE = RDOT + 1

recall_rng_world = np.random.RandomState(0)
NAME_TO_CITY = {i: int(recall_rng_world.randint(0, N_CITIES)) for i in range(N_NAMES)}


def city_token(name_id):
    return N_NAMES + NAME_TO_CITY[name_id]


def make_fact_sequence(name_id):
    return [name_id, RWAS, RBORN, RIN, city_token(name_id), RDOT]


CITY_POS = 4
STAGE_NAME_RANGES = [range(s * FACTS_PER_STAGE, (s + 1) * FACTS_PER_STAGE) for s in range(N_STAGES)]

D_MODEL, N_HEAD, N_LAYERS, FFN_DIM, RECALL_SEQ_LEN = 128, 4, 4, 256, 6


class CausalTransformerLM(nn.Module):
    """Identical architecture to Benchmark A (EXP-018)."""
    def __init__(self, vocab_size, seq_len):
        super().__init__()
        self.tok_embed = nn.Embedding(vocab_size, D_MODEL)
        self.pos_embed = nn.Embedding(seq_len, D_MODEL)
        layer = nn.TransformerEncoderLayer(D_MODEL, N_HEAD, FFN_DIM, batch_first=True, activation='gelu')
        self.encoder = nn.TransformerEncoder(layer, N_LAYERS)
        self.ln_out = nn.LayerNorm(D_MODEL)
        self.lm_head = nn.Linear(D_MODEL, vocab_size)
        causal_mask = torch.triu(torch.ones((seq_len, seq_len), dtype=torch.bool), diagonal=1)
        self.register_buffer('causal_mask', causal_mask)

    def forward(self, tokens):
        B, T = tokens.shape
        pos = torch.arange(T, device=tokens.device).unsqueeze(0).expand(B, T)
        h = self.tok_embed(tokens) + self.pos_embed(pos)
        h = self.encoder(h, mask=self.causal_mask[:T, :T])
        h = self.ln_out(h)
        return self.lm_head(h)


class SlotMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}

    def get(self, key):
        v = self.store.get(key)
        return v[0] if v else None

    def __len__(self):
        return len(self.store)


def gated_write(memory, keys, values, entropies, running):
    for key, val, ent in zip(keys, values, entropies):
        key = int(key); ent = float(ent)
        running.append(ent)
        if key in memory.store:
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
        memory.store[key] = (val, ent)


def refresh_gated_confidences(memory, model):
    if not memory.store:
        return
    ids = list(memory.store.keys())
    seqs = torch.tensor([make_fact_sequence(i) for i in ids], dtype=torch.long, device=device)
    with torch.no_grad():
        logits = model(seqs)
        probs = F.softmax(logits[:, CITY_POS - 1, :], dim=-1)
        ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
    for i, nid in enumerate(ids):
        city, _ = memory.store[nid]
        memory.store[nid] = (city, float(ent[i]))


def eval_recall(model, memory, name_ids):
    ids = torch.tensor(sorted(name_ids), dtype=torch.long, device=device)
    seqs = torch.stack([torch.tensor(make_fact_sequence(int(i)), device=device) for i in ids])
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


# ---------------------------------------------------------------------------
# Compose pathway: the fixed, verified SCAN grammar + learned primitive
# classifier -- identical mechanism to Benchmark B's structure-matched model
# (EXP-020). Grammar functions re-declared here (not imported across
# experiment directories), matching this program's convention of each
# experiment being a self-contained, re-runnable artifact.
# ---------------------------------------------------------------------------
def load_pairs(filename):
    path = os.path.join(SCAN_DIR, filename)
    pairs = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            in_part, out_part = line[len("IN: "):].split(" OUT: ")
            pairs.append((in_part.split(" "), out_part.split(" ")))
    return pairs


SCAN_PRIMITIVES = ["walk", "look", "run", "jump", "turn"]
SCAN_DIRECTIONS = ["left", "right"]
ACTIONS = ["I_WALK", "I_LOOK", "I_RUN", "I_JUMP", "I_TURN_LEFT", "I_TURN_RIGHT"]
TURN_TOK = {"left": "I_TURN_LEFT", "right": "I_TURN_RIGHT"}
ACTION_STOI = {a: i for i, a in enumerate(ACTIONS)}
LEARNABLE_PRIMS = ["walk", "look", "run", "jump"]
PRIM_IDX = {p: i for i, p in enumerate(LEARNABLE_PRIMS)}
LEARNED_SENTINEL = "__LEARNED__"


def parse_command(tokens):
    if "and" in tokens:
        i = tokens.index("and")
        return ("and", parse_clause(tokens[:i]), parse_clause(tokens[i + 1:]))
    if "after" in tokens:
        i = tokens.index("after")
        return ("after", parse_clause(tokens[:i]), parse_clause(tokens[i + 1:]))
    return ("single", parse_clause(tokens), None)


def parse_clause(tokens):
    if tokens[-1] == "twice":
        return (parse_verb_phrase(tokens[:-1]), 2)
    if tokens[-1] == "thrice":
        return (parse_verb_phrase(tokens[:-1]), 3)
    return (parse_verb_phrase(tokens), 1)


def parse_verb_phrase(tokens):
    u = tokens[0]
    if len(tokens) == 1:
        return ("bare", u, None)
    if len(tokens) == 2:
        return ("plain", u, tokens[1])
    return (tokens[1], u, tokens[2])


def eval_verb_phrase(v, primitive_action_fn):
    kind, u, d = v
    if kind == "bare":
        return [primitive_action_fn(u)]
    turn_symbol = TURN_TOK[d]
    if u == "turn":
        if kind == "plain":
            return [turn_symbol]
        if kind == "opposite":
            return [turn_symbol, turn_symbol]
        if kind == "around":
            return [turn_symbol] * 4
    else:
        u_out = primitive_action_fn(u)
        if kind == "plain":
            return [turn_symbol, u_out]
        if kind == "opposite":
            return [turn_symbol, turn_symbol, u_out]
        if kind == "around":
            seq = []
            for _ in range(4):
                seq += [turn_symbol, u_out]
            return seq


def eval_clause(s, primitive_action_fn):
    v, repeat = s
    return eval_verb_phrase(v, primitive_action_fn) * repeat


def eval_command(c, primitive_action_fn):
    kind, left, right = c
    if kind == "single":
        return eval_clause(left, primitive_action_fn)
    left_seq, right_seq = eval_clause(left, primitive_action_fn), eval_clause(right, primitive_action_fn)
    return left_seq + right_seq if kind == "and" else right_seq + left_seq


def sentinel_fn(u):
    return (LEARNED_SENTINEL, PRIM_IDX[u])


def compile_slots(tokens):
    raw = eval_command(parse_command(tokens), sentinel_fn)
    slots = []
    for item in raw:
        if isinstance(item, tuple) and item[0] == LEARNED_SENTINEL:
            slots.append(("learned", item[1]))
        else:
            slots.append(("fixed", ACTION_STOI[item]))
    return slots


class PrimitiveClassifier(nn.Module):
    def __init__(self, d=32):
        super().__init__()
        self.embed = nn.Embedding(len(LEARNABLE_PRIMS), d)
        self.proj = nn.Linear(d, len(ACTIONS))

    def forward(self):
        idx = torch.arange(len(LEARNABLE_PRIMS), device=self.embed.weight.device)
        return self.proj(self.embed(idx))


FIXED_BIG = 15.0


def build_logit_sequence(slots, table, device):
    rows = []
    for kind, val in slots:
        if kind == "fixed":
            row = torch.full((len(ACTIONS),), -FIXED_BIG, device=device)
            row[val] = FIXED_BIG
            rows.append(row)
        else:
            rows.append(table[val])
    return torch.stack(rows)


def precompute(pairs):
    compiled = []
    for in_toks, out_toks in pairs:
        slots = compile_slots(in_toks)
        assert len(slots) == len(out_toks)
        true_idx = torch.tensor([ACTION_STOI[t] for t in out_toks], dtype=torch.long)
        compiled.append((slots, true_idx))
    return compiled


@torch.no_grad()
def evaluate_compose(model, compiled):
    table = model()
    correct = 0
    for slots, true_idx in compiled:
        logits_seq = build_logit_sequence(slots, table, device)
        pred = logits_seq.argmax(dim=-1).cpu()
        correct += int(torch.equal(pred, true_idx))
    return correct / len(compiled)


# ---------------------------------------------------------------------------
# Joint training loop: one model (two disjoint sub-networks), one optimizer,
# mixed batches every step -- EXP-004's methodology, at real scale.
# ---------------------------------------------------------------------------
STEPS_PER_STAGE = 960          # 3 stages x 960 = 2880 total steps
RECALL_BATCH_SIZE = 32
COMPOSE_BATCH_SIZE = 32        # smaller than Benchmark B's 128: the compose sub-network is a
                                # 326-parameter classifier (EXP-020), converges well within 2880
                                # steps at this batch size too -- reduces the per-example Python-loop
                                # overhead (the known bottleneck in EXP-020's structure-matched run)
                                # without changing the joint-training methodology itself
LR = 3e-4


def run_seed(seed, train_compiled, test_compiled):
    torch.manual_seed(seed)
    fact_rng = np.random.RandomState(seed)
    compose_rng = np.random.RandomState(seed + 9000)

    recall_net = CausalTransformerLM(RECALL_VOCAB_SIZE, RECALL_SEQ_LEN).to(device)
    compose_net = PrimitiveClassifier().to(device)
    opt = torch.optim.Adam(list(recall_net.parameters()) + list(compose_net.parameters()), lr=LR)

    memory = SlotMemory(MEMORY_CAPACITY)
    running_ent = []
    n_train = len(train_compiled)

    for stage in range(N_STAGES):
        stage_names = list(STAGE_NAME_RANGES[stage])
        for step in range(STEPS_PER_STAGE):
            # -- recall batch --
            batch_names = fact_rng.choice(stage_names, size=RECALL_BATCH_SIZE, replace=True)
            seqs = torch.tensor([make_fact_sequence(int(n)) for n in batch_names], dtype=torch.long, device=device)
            recall_logits = recall_net(seqs)
            recall_loss = F.cross_entropy(recall_logits[:, :-1, :].reshape(-1, RECALL_VOCAB_SIZE),
                                           seqs[:, 1:].reshape(-1))

            # -- compose batch --
            idx = compose_rng.randint(0, n_train, size=COMPOSE_BATCH_SIZE)
            table = compose_net()
            compose_loss = 0.0
            for i in idx:
                slots, true_idx = train_compiled[i]
                logits_seq = build_logit_sequence(slots, table, device)
                compose_loss = compose_loss + F.cross_entropy(logits_seq, true_idx.to(device))
            compose_loss = compose_loss / len(idx)

            loss = recall_loss + compose_loss
            opt.zero_grad(); loss.backward(); opt.step()

            with torch.no_grad():
                probs = F.softmax(recall_logits[:, CITY_POS - 1, :], dim=-1)
                ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
            keys = batch_names.tolist()
            vals = [NAME_TO_CITY[int(n)] for n in keys]
            gated_write(memory, keys, vals, ent.cpu().tolist(), running_ent)

        refresh_gated_confidences(memory, recall_net)

    recall_results = {}
    for stage in range(N_STAGES):
        recall_results[f"stage{stage+1}"] = eval_recall(recall_net, memory, list(STAGE_NAME_RANGES[stage]))
    compose_test_acc = evaluate_compose(compose_net, test_compiled)

    return recall_results, compose_test_acc


SEEDS = range(5)

ISOLATED_RECALL_STAGE1 = {"mean": 0.1579999953508377, "std": 0.02712931581082347}   # EXP-018 competence_gated_memory
ISOLATED_COMPOSE_ACC = {"mean": 1.0, "std": 0.0}                                    # EXP-020 structure-matched


def main():
    t0 = time.time()
    print("Loading and compiling real SCAN data (shared with EXP-020's directory)...")
    train_pairs = load_pairs("tasks_train_addprim_jump.txt")
    test_pairs = load_pairs("tasks_test_addprim_jump.txt")
    train_compiled = precompute(train_pairs)
    test_compiled = precompute(test_pairs)
    print(f"train={len(train_pairs)} test={len(test_pairs)}")

    results = []
    for seed in SEEDS:
        recall_r, compose_acc = run_seed(seed, train_compiled, test_compiled)
        print(f"seed {seed}: recall_stage1_acc={recall_r['stage1']['with_memory_acc']:.3f} "
              f"(coverage={recall_r['stage1']['coverage']:.3f})  compose_test_acc={compose_acc:.4f}")
        results.append({"recall_stage1": recall_r["stage1"], "recall_stage3": recall_r["stage3"],
                         "compose_test_acc": compose_acc})

    recall_accs = [r["recall_stage1"]["with_memory_acc"] for r in results]
    compose_accs = [r["compose_test_acc"] for r in results]

    print(f"\n========== SUMMARY: Benchmark C joint training ==========")
    print(f"recall_stage1_acc  = {np.mean(recall_accs):.3f} +/- {np.std(recall_accs):.3f}   "
          f"(isolated EXP-018: {ISOLATED_RECALL_STAGE1['mean']:.3f} +/- {ISOLATED_RECALL_STAGE1['std']:.3f})")
    print(f"compose_test_acc   = {np.mean(compose_accs):.4f} +/- {np.std(compose_accs):.4f}   "
          f"(isolated EXP-020: {ISOLATED_COMPOSE_ACC['mean']:.4f} +/- {ISOLATED_COMPOSE_ACC['std']:.4f})")

    out = {
        "meta": {"steps_per_stage": STEPS_PER_STAGE, "total_steps": STEPS_PER_STAGE * N_STAGES,
                 "recall_batch_size": RECALL_BATCH_SIZE, "compose_batch_size": COMPOSE_BATCH_SIZE,
                 "seeds": list(SEEDS), "elapsed_sec": time.time() - t0},
        "summary": {
            "recall_stage1_acc_mean": float(np.mean(recall_accs)), "recall_stage1_acc_std": float(np.std(recall_accs)),
            "compose_test_acc_mean": float(np.mean(compose_accs)), "compose_test_acc_std": float(np.std(compose_accs)),
        },
        "isolated_baselines": {"recall_stage1": ISOLATED_RECALL_STAGE1, "compose_test_acc": ISOLATED_COMPOSE_ACC},
        "raw": results,
    }
    with open("results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote results.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
