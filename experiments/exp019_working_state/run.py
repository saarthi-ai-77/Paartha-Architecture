"""
EXP-019: Is a dedicated "S_working" substrate genuinely irreducible, or does
a disciplined interaction of the existing state model (S_episodic with a
reserved capacity partition) resolve the same problem?

Directly resolves the open question `docs/12_cognition/CTX-001.md` Section 4
left as a Reasoned Hypothesis: whether conversation/reasoning "context" (a
small, fixed number of continuously-overwritten fields -- topic, goal, etc.)
needs a structurally distinct substrate, or whether the existing S_episodic
mechanism suffices once used more carefully.

HYPOTHESIS (stated before running):
  (a) naive_shared_schema -- context slots written into the SAME
      capacity-constrained, competence-gated S_episodic store as ordinary
      facts (just another schema, no special handling) -- is expected to
      show real recall failures: a slot can be evicted by ordinary-fact
      write pressure (EXP-018's mechanism, now hitting context instead of
      facts), and/or skipped by the surprise-gate if the model is not
      currently "surprised" by a reassignment it must nonetheless record.
  (b) dedicated_working_state -- context slots live in a wholly separate,
      small, fixed-size buffer (never evicted, always unconditionally
      overwritten) -- is expected to recall the true current value of every
      slot perfectly, since nothing can ever evict it and every reassignment
      is unconditionally recorded.
  (c) reserved_partition -- context slots live in the SAME S_episodic
      mechanism/class as facts, but in a capacity partition ordinary-fact
      eviction is structurally forbidden from touching, written
      unconditionally (bypassing the surprise-gate, which makes no sense
      for "record the current value regardless of surprise"). This is the
      "disciplined interaction of existing substrates" candidate --
      matching IVS-001's own already-named mitigation for a structurally
      similar risk ("reserve per-schema capacity sub-allocations").

FALSIFYING OUTCOME for a genuinely new S_working substrate: if (c) performs
as well as (b), a disciplined policy change to the existing S_episodic
mechanism suffices -- no new substrate is needed, and CTX-001's Reasoned
Hypothesis is falsified in favor of reduction.
CONFIRMING OUTCOME: if (c) performs like (a) and only (b) succeeds, something
about genuine structural separation matters beyond capacity-reservation and
unconditional writes -- real evidence for irreducibility.

Reuses ACA-MVP-001 Benchmark A's validated CausalTransformerLM and
gated-write/refresh mechanism unchanged for the fact side, so this
experiment differs from Benchmark A in exactly one added dimension (the
context-slot stream and its three candidate storage disciplines), not in
the underlying validated apparatus.
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
# Vocabulary: Benchmark A's fact vocabulary, extended with a context-slot
# assignment vocabulary.
# ---------------------------------------------------------------------------
N_NAMES = 300
N_CITIES = 40
FACTS_PER_STAGE = 100
N_STAGES = 3
FACT_MEMORY_CAPACITY = 60

N_SLOTS = 4
N_VALUES = 20
SLOT_KEY_OFFSET = 10_000  # keeps slot keys out of the name_id (0..299) key space

WAS, BORN, IN, DOT = N_NAMES + N_CITIES, N_NAMES + N_CITIES + 1, N_NAMES + N_CITIES + 2, N_NAMES + N_CITIES + 3
SLOT_BASE = DOT + 1
VALUE_BASE = SLOT_BASE + N_SLOTS
IS_TOK = VALUE_BASE + N_VALUES
NOW_TOK = IS_TOK + 1
VOCAB_SIZE = NOW_TOK + 1

rng_world = np.random.RandomState(0)
NAME_TO_CITY = {i: int(rng_world.randint(0, N_CITIES)) for i in range(N_NAMES)}


def city_token(name_id):
    return N_NAMES + NAME_TO_CITY[name_id]


def make_fact_sequence(name_id):
    return [name_id, WAS, BORN, IN, city_token(name_id), DOT]


def make_slot_sequence(slot_id, value_id):
    return [SLOT_BASE + slot_id, IS_TOK, NOW_TOK, VALUE_BASE + value_id, DOT]


CITY_POS = 4     # in a 6-token fact sequence, predict from position 3
VAL_POS = 3      # in a 5-token slot sequence, predict from position 2
STAGE_NAME_RANGES = [range(s * FACTS_PER_STAGE, (s + 1) * FACTS_PER_STAGE) for s in range(N_STAGES)]

# ---------------------------------------------------------------------------
# Model: identical to ACA-MVP-001 Benchmark A's CausalTransformerLM.
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

    def forward(self, tokens):
        B, T = tokens.shape
        pos = torch.arange(T, device=tokens.device).unsqueeze(0).expand(B, T)
        h = self.tok_embed(tokens) + self.pos_embed(pos)
        h = self.encoder(h, mask=self.causal_mask[:T, :T])
        h = self.ln_out(h)
        return self.lm_head(h)


def param_count(m):
    return sum(p.numel() for p in m.parameters())


# ---------------------------------------------------------------------------
# Fact memory: EXACTLY Benchmark A's SlotMemory + gated_write + refresh,
# unchanged, with one addition for condition (c): eviction candidates can be
# restricted to a given key set (the reserved partition is invisible to it).
# ---------------------------------------------------------------------------
class SlotMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}  # key -> (value, signal)

    def get(self, key):
        v = self.store.get(key)
        return v[0] if v else None

    def __len__(self):
        return len(self.store)


def gated_write(memory, keys, values, entropies, running, evictable_keys_only=None):
    """Benchmark A's validated write/evict policy. If evictable_keys_only is
    given, eviction candidates are restricted to that set (used for
    condition (c) so ordinary-fact writes can never evict a reserved slot
    entry, even though both live in the same SlotMemory instance)."""
    for key, val, ent in zip(keys, values, entropies):
        key = int(key); ent = float(ent)
        running.append(ent)
        if key in memory.store:
            continue
        median = np.median(running[-500:]) if len(running) >= 10 else ent
        if ent <= median:
            continue
        if len(memory) >= memory.capacity:
            candidates = memory.store.items() if evictable_keys_only is None else \
                [(k, v) for k, v in memory.store.items() if k in evictable_keys_only]
            worst_id, worst_ent = None, None
            for sid, (_, sent) in candidates:
                if worst_ent is None or sent < worst_ent:
                    worst_id, worst_ent = sid, sent
            if worst_ent is not None and worst_ent < median:
                del memory.store[worst_id]
            else:
                continue
        memory.store[key] = (val, ent)


def unconditional_write(memory, key, value):
    """Context slots need "always record the latest value," not "record it
    if the model finds it surprising" -- overwriting the current belief is
    warranted regardless of surprise. Never evicts (capacity is exactly
    sized to N_SLOTS in condition (b); reserved in condition (c))."""
    memory.store[key] = (value, None)


def refresh_gated_confidences(memory, model, keys_to_refresh, seq_fn):
    if not keys_to_refresh:
        return
    seqs = torch.tensor([seq_fn(k) for k in keys_to_refresh], dtype=torch.long, device=device)
    pred_pos = seqs.size(1) - 2  # CITY_POS-1 / VAL_POS-1 equivalent for whichever seq_fn is used
    with torch.no_grad():
        logits = model(seqs)
        probs = F.softmax(logits[:, pred_pos, :], dim=-1)
        ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
    for i, key in enumerate(keys_to_refresh):
        val, _ = memory.store[key]
        memory.store[key] = (val, float(ent[i]))


def eval_facts(model, memory, name_ids):
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


def eval_slots(model, memory_lookup_fn, true_current_values):
    """true_current_values: dict slot_id -> value_id (the LATEST assignment)."""
    slot_ids = list(range(N_SLOTS))
    seqs = torch.tensor([make_slot_sequence(s, true_current_values[s]) for s in slot_ids],
                         dtype=torch.long, device=device)
    with torch.no_grad():
        logits = model(seqs)
        pred_val_tok = logits[:, VAL_POS - 1, :].argmax(dim=-1)
    true_val_tok = torch.tensor([VALUE_BASE + true_current_values[s] for s in slot_ids], device=device)
    param_acc = (pred_val_tok == true_val_tok).float().mean().item()
    final_pred = pred_val_tok.clone()
    covered = 0
    for i, s in enumerate(slot_ids):
        v = memory_lookup_fn(s)
        if v is not None:
            final_pred[i] = VALUE_BASE + v
            covered += 1
    mem_acc = (final_pred == true_val_tok).float().mean().item()
    return {"param_only_acc": param_acc, "with_memory_acc": mem_acc, "coverage": covered / N_SLOTS}


STEPS_PER_STAGE = 800
BATCH_SIZE = 32
LR = 3e-4
SLOT_EVENT_EVERY = 100  # 24 reassignment events across the full 2400-step run


def run_condition(condition, seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    slot_rng = np.random.RandomState(seed + 5000)
    model = CausalTransformerLM().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)

    running_ent_facts = []
    current_slot_values = {s: slot_rng.randint(0, N_VALUES) for s in range(N_SLOTS)}  # initial values

    if condition == "naive_shared_schema":
        fact_memory = SlotMemory(FACT_MEMORY_CAPACITY)
        working_memory = None
    elif condition == "dedicated_working_state":
        fact_memory = SlotMemory(FACT_MEMORY_CAPACITY)
        working_memory = SlotMemory(N_SLOTS)
    elif condition == "reserved_partition":
        fact_memory = SlotMemory(FACT_MEMORY_CAPACITY + N_SLOTS)  # same instance, extra reserved room
        working_memory = None
    else:
        raise ValueError(condition)

    reserved_keys = {SLOT_KEY_OFFSET + s for s in range(N_SLOTS)}
    global_step = 0

    def do_slot_event(s, v):
        current_slot_values[s] = v
        slot_seq = make_slot_sequence(s, v)
        slot_batch = torch.tensor([slot_seq] * BATCH_SIZE, dtype=torch.long, device=device)
        slot_logits = model(slot_batch)
        slot_loss = F.cross_entropy(slot_logits[:, :-1, :].reshape(-1, VOCAB_SIZE),
                                     slot_batch[:, 1:].reshape(-1))
        opt.zero_grad(); slot_loss.backward(); opt.step()
        if condition == "naive_shared_schema":
            with torch.no_grad():
                sp = F.softmax(slot_logits[:, VAL_POS - 1, :], dim=-1)[0:1]
                sent = float(-(sp * torch.log(sp.clamp_min(1e-9))).sum(dim=-1).item())
            gated_write(fact_memory, [SLOT_KEY_OFFSET + s], [v], [sent], running_ent_facts)
        elif condition == "dedicated_working_state":
            unconditional_write(working_memory, SLOT_KEY_OFFSET + s, v)
        elif condition == "reserved_partition":
            unconditional_write(fact_memory, SLOT_KEY_OFFSET + s, v)

    # Guarantee every slot has been the subject of at least one real
    # training+write event before evaluation ever checks it -- otherwise a
    # slot that happens to never be hit by the random reassignment schedule
    # would be evaluated against an arbitrary, never-trained-on initial
    # value, purely by chance (low probability, but a real confound worth
    # eliminating rather than tolerating).
    for s in range(N_SLOTS):
        do_slot_event(s, current_slot_values[s])

    for stage in range(N_STAGES):
        stage_names = list(STAGE_NAME_RANGES[stage])
        for step in range(STEPS_PER_STAGE):
            batch_names = rng.choice(stage_names, size=BATCH_SIZE, replace=True)
            seqs = torch.tensor([make_fact_sequence(int(n)) for n in batch_names], dtype=torch.long, device=device)
            logits = model(seqs)
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seqs[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

            with torch.no_grad():
                probs = F.softmax(logits[:, CITY_POS - 1, :], dim=-1)
                ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
            keys = batch_names.tolist()
            vals = [NAME_TO_CITY[int(n)] for n in keys]
            evictable = None if condition != "reserved_partition" else \
                (set(fact_memory.store.keys()) - reserved_keys)
            gated_write(fact_memory, keys, vals, ent.cpu().tolist(), running_ent_facts,
                        evictable_keys_only=evictable)

            global_step += 1
            if global_step % SLOT_EVENT_EVERY == 0:
                s = int(slot_rng.randint(0, N_SLOTS))
                v = int(slot_rng.randint(0, N_VALUES))
                do_slot_event(s, v)

        # Stage boundary: refresh fact confidences exactly as Benchmark A did.
        fact_keys_now = [k for k in fact_memory.store.keys() if k not in reserved_keys]
        refresh_gated_confidences(fact_memory, model, fact_keys_now, make_fact_sequence)

    # ---- Evaluation ----
    fact_results = {}
    for stage in range(N_STAGES):
        stage_names = list(STAGE_NAME_RANGES[stage])
        fact_results[f"stage{stage+1}"] = eval_facts(model, fact_memory, stage_names)

    if condition == "dedicated_working_state":
        lookup = lambda s: working_memory.get(SLOT_KEY_OFFSET + s)
    else:
        lookup = lambda s: fact_memory.get(SLOT_KEY_OFFSET + s)
    slot_results = eval_slots(model, lookup, current_slot_values)

    return fact_results, slot_results, param_count(model)


CONDITIONS = ["naive_shared_schema", "dedicated_working_state", "reserved_partition"]
SEEDS = range(5)


def main():
    t0 = time.time()
    all_results = {c: [] for c in CONDITIONS}
    n_params = None

    for seed in SEEDS:
        print(f"\n### seed {seed} ###")
        for cond in CONDITIONS:
            fact_r, slot_r, np_ = run_condition(cond, seed)
            n_params = np_
            all_results[cond].append({"facts": fact_r, "slots": slot_r})
            print(f"  {cond:26s} slot_acc={slot_r['with_memory_acc']:.3f} "
                  f"(param_only={slot_r['param_only_acc']:.3f}, coverage={slot_r['coverage']:.3f}) "
                  f"stage1_fact_acc={fact_r['stage1']['with_memory_acc']:.3f}")

    print(f"\nModel parameter count: {n_params}")
    print("\n========== SUMMARY: context-slot recall (true CURRENT value) after full run ==========")
    summary = {}
    for cond in CONDITIONS:
        slot_accs = [r["slots"]["with_memory_acc"] for r in all_results[cond]]
        slot_param = [r["slots"]["param_only_acc"] for r in all_results[cond]]
        slot_cov = [r["slots"]["coverage"] for r in all_results[cond]]
        fact_stage1 = [r["facts"]["stage1"]["with_memory_acc"] for r in all_results[cond]]
        summary[cond] = {
            "slot_acc_mean": float(np.mean(slot_accs)), "slot_acc_std": float(np.std(slot_accs)),
            "slot_param_only_mean": float(np.mean(slot_param)),
            "slot_coverage_mean": float(np.mean(slot_cov)),
            "fact_stage1_acc_mean": float(np.mean(fact_stage1)),
        }
        print(f"{cond:26s} slot_acc={np.mean(slot_accs):.3f}+/-{np.std(slot_accs):.3f}  "
              f"(param_only={np.mean(slot_param):.3f}, coverage={np.mean(slot_cov):.3f})  "
              f"fact_stage1_acc={np.mean(fact_stage1):.3f}")

    out = {
        "meta": {"n_names": N_NAMES, "n_slots": N_SLOTS, "n_values": N_VALUES,
                 "fact_memory_capacity": FACT_MEMORY_CAPACITY, "slot_event_every": SLOT_EVENT_EVERY,
                 "steps_per_stage": STEPS_PER_STAGE, "seeds": list(SEEDS), "param_count": n_params,
                 "elapsed_sec": time.time() - t0},
        "summary": summary,
        "raw": {c: [{"facts_stage1": r["facts"]["stage1"], "slots": r["slots"]} for r in res]
                for c, res in all_results.items()},
    }
    with open("results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote results.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
