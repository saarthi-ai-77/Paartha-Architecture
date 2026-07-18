"""
EXP-004: Integration Test -- Does the EXP-001 memory pathway and the
EXP-002 rule pathway compose in one model, trained jointly, without either
degrading relative to its own isolated (single-pathway) training?

Design choice made deliberately: the two pathways are kept with DISJOINT,
non-shared parameters (the rule pathway keeps its validated fixed sin/cos
operand encoding -- giving it a learned, shared embedding table would
reintroduce exactly the free-embedding degree of freedom EXP-002 falsified,
undermining the very mechanism being tested for composability). This means
the test is specifically about whether ONE model class, ONE optimizer, and
ONE training loop can carry both validated mechanisms simultaneously
without engineering interference (loss-scale imbalance, optimizer-state
coupling, code-level bugs) -- not about whether they can share a substrate,
which is a separate, harder question for a later experiment (real
integration with a shared backbone/embedding space).

Three conditions, each over 5 seeds:
  (a) recall_isolated  -- EXP-001's validated surprise-gated memory
      pathway, trained alone (replicating EXP-001's condition, re-run here
      for an apples-to-apples comparison under identical code/eval).
  (b) rule_isolated     -- EXP-002 stage 5's validated group-action-
      constrained rule pathway, trained alone.
  (c) joint             -- both pathways in one model, one optimizer, one
      training loop, trained on mixed batches (some recall examples, some
      rule examples, every step), losses summed before a single backward
      pass.

Prediction stated before running: since the two pathways share no
parameters, joint training should closely match each isolated baseline.
A meaningful gap would indicate an engineering interaction worth
diagnosing (e.g. a bug, or an unexpected optimizer-level interaction),
since there is no principled reason for disjoint-parameter pathways to
interfere mathematically under Adam.
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
# Recall sub-task setup (identical world to EXP-001)
# ---------------------------------------------------------------------------
N_FACTS = 1000
KEY_DIM = 32
HIDDEN = 128
MEMORY_CAPACITY = 200
ZIPF_EXPONENT = 1.3
SURPRISE_WRITE_THRESHOLD = 2.0
MASTERED_THRESHOLD = 0.3

key_vectors = torch.randn(N_FACTS, KEY_DIM)
key_vectors = (key_vectors / key_vectors.norm(dim=-1, keepdim=True)).to(device)
value_ids = torch.arange(N_FACTS).to(device)

ranks = np.arange(1, N_FACTS + 1)
recall_weights = 1.0 / (ranks ** ZIPF_EXPONENT)
recall_weights = recall_weights / recall_weights.sum()

RECALL_STEPS = 2000          # combined run trains longer than EXP-001's 1250
RECALL_BATCH = 32
EVAL_EVERY = 500

expected_exposures = recall_weights * RECALL_STEPS * RECALL_BATCH
TAIL_FACTS = set(np.where(expected_exposures <= 3)[0].tolist())
HEAD_FACTS = set(np.where(expected_exposures >= 30)[0].tolist())


def sample_recall_batch(batch_size, rng):
    idx = rng.choice(N_FACTS, size=batch_size, p=recall_weights)
    idx_t = torch.tensor(idx, dtype=torch.long, device=device)
    return idx_t, key_vectors[idx_t], value_ids[idx_t]


class RecallBackbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(KEY_DIM, HIDDEN), nn.ReLU(),
            nn.Linear(HIDDEN, HIDDEN), nn.ReLU(),
            nn.Linear(HIDDEN, N_FACTS),
        )

    def forward(self, keys):
        return self.net(keys)


class SlotMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}

    def get(self, fact_id):
        return self.store.get(fact_id, None)

    def __len__(self):
        return len(self.store)


def surprise_gated_write(memory, fact_ids, losses, backbone):
    for fid, loss in zip(fact_ids, losses):
        fid = int(fid); loss = float(loss)
        if fid in memory.store:
            continue
        if loss <= SURPRISE_WRITE_THRESHOLD:
            continue
        if len(memory) >= memory.capacity:
            stored_ids = list(memory.store.keys())
            stored_idx = torch.tensor(stored_ids, dtype=torch.long, device=device)
            with torch.no_grad():
                logits = backbone(key_vectors[stored_idx])
                targets = value_ids[stored_idx]
                cur_losses = F.cross_entropy(logits, targets, reduction='none')
            worst_idx = torch.argmin(cur_losses).item()
            if cur_losses[worst_idx].item() > MASTERED_THRESHOLD:
                continue
            del memory.store[stored_ids[worst_idx]]
        memory.store[fid] = fid


def eval_recall(backbone, memory, fact_id_set):
    if not fact_id_set:
        return None
    ids = torch.tensor(sorted(fact_id_set), dtype=torch.long, device=device)
    keys = key_vectors[ids]
    targets = value_ids[ids]
    with torch.no_grad():
        logits = backbone(keys)
        param_preds = logits.argmax(dim=-1)
    param_acc = (param_preds == targets).float().mean().item()
    final_preds = param_preds.clone()
    for i, fid in enumerate(ids.tolist()):
        v = memory.get(fid)
        if v is not None:
            final_preds[i] = v
    mem_acc = (final_preds == targets).float().mean().item()
    coverage = sum(1 for fid in ids.tolist() if memory.get(fid) is not None) / len(ids)
    return {"param_only_acc": param_acc, "with_memory_acc": mem_acc, "coverage": coverage}


# ---------------------------------------------------------------------------
# Rule sub-task setup (identical world to EXP-002 stage 5)
# ---------------------------------------------------------------------------
N_OPS, N_VALUES = 4, 10

def op0(x): return (x + 1) % 10
def op1(x): return (x * 2) % 10
def op2(x): return (9 - x) % 10
def op3(x): return (x + 5) % 10
OP_FNS = [op0, op1, op2, op3]

RULE_HELD_OUT = set()
for o in range(N_OPS):
    RULE_HELD_OUT.add((o, (2 * o) % 10))
    RULE_HELD_OUT.add((o, (2 * o + 1) % 10))
RULE_ALL_PAIRS = [(o, x) for o in range(N_OPS) for x in range(N_VALUES)]
RULE_TRAIN_PAIRS = [p for p in RULE_ALL_PAIRS if p not in RULE_HELD_OUT]
RULE_TEST_PAIRS = sorted(RULE_HELD_OUT)


def rule_pairs_to_tensors(pairs):
    ops = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    xs = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    ys = torch.tensor([OP_FNS[p[0]](p[1]) for p in pairs], dtype=torch.long, device=device)
    return ops, xs, ys


RULE_TR_OPS, RULE_TR_XS, RULE_TR_YS = rule_pairs_to_tensors(RULE_TRAIN_PAIRS)
RULE_TE_OPS, RULE_TE_XS, RULE_TE_YS = rule_pairs_to_tensors(RULE_TEST_PAIRS)

rule_angles = torch.arange(N_VALUES, dtype=torch.float32) * (2 * math.pi / N_VALUES)
RULE_FEAT = torch.stack([torch.cos(rule_angles), torch.sin(rule_angles)], dim=-1).to(device)

RULE_STEPS = 2000
RULE_BATCH = 16


class RulePathway(nn.Module):
    """Identical mechanism to EXP-002 stage 5: fixed sin/cos operand
    encoding (NOT shared/learned -- kept disjoint on purpose, see module
    docstring), per-operator learned rotation angle + reflection sign."""
    def __init__(self):
        super().__init__()
        self.theta = nn.Parameter(torch.zeros(N_OPS, device=device))
        self.s_raw = nn.Parameter(torch.ones(N_OPS, device=device))

    def forward(self, ops, xs):
        theta = self.theta[ops]
        s = torch.tanh(self.s_raw[ops])
        c, sn = torch.cos(theta), torch.sin(theta)
        x_feat = RULE_FEAT[xs]
        cx, sx = x_feat[:, 0], x_feat[:, 1]
        tx = c * cx - s * sn * sx
        ty = sn * cx + s * c * sx
        transformed = torch.stack([tx, ty], dim=-1)
        return transformed @ RULE_FEAT.T


def eval_rule(rule_module):
    with torch.no_grad():
        train_acc = (rule_module(RULE_TR_OPS, RULE_TR_XS).argmax(-1) == RULE_TR_YS).float().mean().item()
        test_acc = (rule_module(RULE_TE_OPS, RULE_TE_XS).argmax(-1) == RULE_TE_YS).float().mean().item()
    return {"train_acc": train_acc, "held_out_acc": test_acc}


# ---------------------------------------------------------------------------
# Condition (a): recall isolated
# ---------------------------------------------------------------------------
def run_recall_isolated(seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    backbone = RecallBackbone().to(device)
    opt = torch.optim.Adam(backbone.parameters(), lr=1e-3)
    memory = SlotMemory(MEMORY_CAPACITY)
    for step in range(1, RECALL_STEPS + 1):
        fact_ids, keys, targets = sample_recall_batch(RECALL_BATCH, rng)
        logits = backbone(keys)
        loss = F.cross_entropy(logits, targets)
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad():
            cur_logits = backbone(keys)
            cur_losses = F.cross_entropy(cur_logits, targets, reduction='none')
        surprise_gated_write(memory, fact_ids.tolist(), cur_losses.tolist(), backbone)
    return eval_recall(backbone, memory, TAIL_FACTS), eval_recall(backbone, memory, HEAD_FACTS)


# ---------------------------------------------------------------------------
# Condition (b): rule isolated
# ---------------------------------------------------------------------------
def run_rule_isolated(seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    rule_module = RulePathway().to(device)
    opt = torch.optim.Adam(rule_module.parameters(), lr=2e-2)
    n_train = len(RULE_TRAIN_PAIRS)
    for step in range(1, RULE_STEPS + 1):
        idx = rng.choice(n_train, size=RULE_BATCH, replace=True)
        logits = rule_module(RULE_TR_OPS[idx], RULE_TR_XS[idx])
        loss = F.cross_entropy(logits, RULE_TR_YS[idx])
        opt.zero_grad(); loss.backward(); opt.step()
    return eval_rule(rule_module)


# ---------------------------------------------------------------------------
# Condition (c): joint -- both pathways, one model, one optimizer, mixed
# batches, summed loss, single backward/step per training iteration.
# ---------------------------------------------------------------------------
class JointModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.recall = RecallBackbone()
        self.rule = RulePathway()


def run_joint(seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    model = JointModel().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    # rule pathway needs a higher effective LR than the shared 1e-3 (it used
    # 2e-2 in isolation); rather than silently disadvantage it, give it its
    # own param group at its validated LR within the SAME optimizer/step --
    # this is still one optimizer and one .step() call, i.e. still a fair
    # test of joint optimization, not two separate training loops.
    opt = torch.optim.Adam([
        {"params": model.recall.parameters(), "lr": 1e-3},
        {"params": model.rule.parameters(), "lr": 2e-2},
    ])
    memory = SlotMemory(MEMORY_CAPACITY)
    n_rule_train = len(RULE_TRAIN_PAIRS)

    recall_loss_hist, rule_loss_hist = [], []

    for step in range(1, RECALL_STEPS + 1):
        fact_ids, keys, r_targets = sample_recall_batch(RECALL_BATCH, rng)
        recall_logits = model.recall(keys)
        recall_loss = F.cross_entropy(recall_logits, r_targets)

        idx = rng.choice(n_rule_train, size=RULE_BATCH, replace=True)
        rule_logits = model.rule(RULE_TR_OPS[idx], RULE_TR_XS[idx])
        rule_loss = F.cross_entropy(rule_logits, RULE_TR_YS[idx])

        loss = recall_loss + rule_loss
        opt.zero_grad()
        loss.backward()
        opt.step()

        recall_loss_hist.append(recall_loss.item())
        rule_loss_hist.append(rule_loss.item())

        with torch.no_grad():
            cur_logits = model.recall(keys)
            cur_losses = F.cross_entropy(cur_logits, r_targets, reduction='none')
        surprise_gated_write(memory, fact_ids.tolist(), cur_losses.tolist(), model.recall)

    recall_tail = eval_recall(model.recall, memory, TAIL_FACTS)
    recall_head = eval_recall(model.recall, memory, HEAD_FACTS)
    rule_result = eval_rule(model.rule)
    return recall_tail, recall_head, rule_result, recall_loss_hist, rule_loss_hist


def main():
    t0 = time.time()
    SEEDS = range(5)
    results = {"recall_isolated": [], "rule_isolated": [], "joint": []}

    print("\n=== Condition (a): recall_isolated ===")
    for seed in SEEDS:
        tail, head = run_recall_isolated(seed)
        results["recall_isolated"].append({"seed": seed, "tail": tail, "head": head})
        print(f"  seed {seed}: tail_mem_acc={tail['with_memory_acc']:.3f} "
              f"tail_coverage={tail['coverage']:.3f} head_mem_acc={head['with_memory_acc']:.3f}")

    print("\n=== Condition (b): rule_isolated ===")
    for seed in SEEDS:
        r = run_rule_isolated(seed)
        results["rule_isolated"].append({"seed": seed, **r})
        print(f"  seed {seed}: train_acc={r['train_acc']:.3f} held_out_acc={r['held_out_acc']:.3f}")

    print("\n=== Condition (c): joint (both pathways, one model, one optimizer) ===")
    for seed in SEEDS:
        tail, head, rule_r, recall_losses, rule_losses = run_joint(seed)
        results["joint"].append({
            "seed": seed, "tail": tail, "head": head, "rule": rule_r,
            "final_recall_loss": recall_losses[-1], "final_rule_loss": rule_losses[-1],
        })
        print(f"  seed {seed}: tail_mem_acc={tail['with_memory_acc']:.3f} "
              f"tail_coverage={tail['coverage']:.3f} head_mem_acc={head['with_memory_acc']:.3f} "
              f"| rule_held_out_acc={rule_r['held_out_acc']:.3f}")

    print("\n========== SUMMARY ==========")
    ri_tail = [r["tail"]["with_memory_acc"] for r in results["recall_isolated"]]
    j_tail = [r["tail"]["with_memory_acc"] for r in results["joint"]]
    rule_i = [r["held_out_acc"] for r in results["rule_isolated"]]
    rule_j = [r["rule"]["held_out_acc"] for r in results["joint"]]

    print(f"Recall tail acc  -- isolated: {np.mean(ri_tail):.3f}+/-{np.std(ri_tail):.3f}   "
          f"joint: {np.mean(j_tail):.3f}+/-{np.std(j_tail):.3f}")
    print(f"Rule held-out acc -- isolated: {np.mean(rule_i):.3f}+/-{np.std(rule_i):.3f}   "
          f"joint: {np.mean(rule_j):.3f}+/-{np.std(rule_j):.3f}")

    with open("results.json", "w") as f:
        json.dump({
            "meta": {"seeds": list(SEEDS), "elapsed_sec": time.time() - t0},
            "results": results,
            "summary": {
                "recall_tail_isolated_mean": float(np.mean(ri_tail)),
                "recall_tail_isolated_std": float(np.std(ri_tail)),
                "recall_tail_joint_mean": float(np.mean(j_tail)),
                "recall_tail_joint_std": float(np.std(j_tail)),
                "rule_held_out_isolated_mean": float(np.mean(rule_i)),
                "rule_held_out_isolated_std": float(np.std(rule_i)),
                "rule_held_out_joint_mean": float(np.mean(rule_j)),
                "rule_held_out_joint_std": float(np.std(rule_j)),
            }
        }, f, indent=2)
    print(f"\nWrote results.json in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
