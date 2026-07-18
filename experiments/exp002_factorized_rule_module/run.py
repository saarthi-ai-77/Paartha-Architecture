"""
EXP-002: Factorized (Operator x Operand) Rule Module vs. Black-Box MLP
on Held-Out Compositional Generalization

Hypothesis under test:
  A model that structurally FACTORS "which operator" from "which operand"
  (a shared operand embedding pathway, combined with a per-operator linear
  transform applied on top) generalizes correctly to (operator, operand)
  combinations it never saw jointly during training, whereas a black-box
  model given the same information as a single joint input (one-hot(op)
  concatenated with one-hot(x)) does not reliably do so -- because nothing
  in its architecture forces "operator" and "operand" to be combined
  compositionally rather than memorized jointly.

This directly tests the systematicity/compositional-generalization claim
(Fodor & Pylyshyn; SCAN-style failures of interpolative learners) with our
own from-scratch implementation, not by citing the literature.

Task: 4 operators (fixed, unknown-to-the-model arithmetic functions mod 10)
applied to operands 0..9. Some (operator, operand) PAIRS are held out from
training entirely, but every operator is seen with most operands, and every
operand is seen under most operators -- so correct generalization to the
held-out pairs is possible in principle from compositional structure alone,
with zero additional information.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import time

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device: {device}")

N_OPS = 4
N_VALUES = 10  # operands and outputs both in [0, 10)

# Fixed ground-truth functions (mod 10), unknown to the model.
def op0(x): return (x + 1) % 10
def op1(x): return (x * 2) % 10
def op2(x): return (9 - x) % 10
def op3(x): return (x + 5) % 10

OP_FNS = [op0, op1, op2, op3]

# Held-out (op, x) pairs: 2 operands held out per operator, no operand held
# out for ALL operators (so every operand is still seen under >=2 operators).
HELD_OUT = set()
for o in range(N_OPS):
    HELD_OUT.add((o, (2 * o) % 10))
    HELD_OUT.add((o, (2 * o + 1) % 10))

ALL_PAIRS = [(o, x) for o in range(N_OPS) for x in range(N_VALUES)]
TRAIN_PAIRS = [p for p in ALL_PAIRS if p not in HELD_OUT]
TEST_PAIRS = sorted(HELD_OUT)

print(f"total pairs: {len(ALL_PAIRS)}, train: {len(TRAIN_PAIRS)}, held-out test: {len(TEST_PAIRS)}")


def pairs_to_tensors(pairs):
    ops = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    xs = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    ys = torch.tensor([OP_FNS[p[0]](p[1]) for p in pairs], dtype=torch.long, device=device)
    return ops, xs, ys


TRAIN_OPS, TRAIN_XS, TRAIN_YS = pairs_to_tensors(TRAIN_PAIRS)
TEST_OPS, TEST_XS, TEST_YS = pairs_to_tensors(TEST_PAIRS)

HIDDEN = 64
EMBED_DIM = 16
TRAIN_STEPS = 3000
BATCH_SIZE = 16


class BlackBoxMLP(nn.Module):
    """Joint input: one-hot(op) concat one-hot(x) -> MLP -> logits.
    No architectural bias toward factorizing op and x."""
    def __init__(self):
        super().__init__()
        in_dim = N_OPS + N_VALUES
        self.net = nn.Sequential(
            nn.Linear(in_dim, HIDDEN), nn.ReLU(),
            nn.Linear(HIDDEN, HIDDEN), nn.ReLU(),
            nn.Linear(HIDDEN, N_VALUES),
        )

    def forward(self, ops, xs):
        op_oh = F.one_hot(ops, N_OPS).float()
        x_oh = F.one_hot(xs, N_VALUES).float()
        inp = torch.cat([op_oh, x_oh], dim=-1)
        return self.net(inp)


class FactorizedRuleModule(nn.Module):
    """Shared operand embedding pathway + per-operator linear transform.
    Operator and operand only combine at the final linear application,
    which is exactly the compositional inductive bias under test."""
    def __init__(self):
        super().__init__()
        self.x_embed = nn.Embedding(N_VALUES, EMBED_DIM)
        self.x_proj = nn.Sequential(nn.Linear(EMBED_DIM, HIDDEN), nn.ReLU())
        # One linear "rule" per operator: HIDDEN -> N_VALUES
        self.op_weight = nn.Parameter(torch.randn(N_OPS, N_VALUES, HIDDEN) * 0.05)
        self.op_bias = nn.Parameter(torch.zeros(N_OPS, N_VALUES))

    def forward(self, ops, xs):
        h = self.x_proj(self.x_embed(xs))              # [B, HIDDEN], shared across all ops
        W = self.op_weight[ops]                          # [B, N_VALUES, HIDDEN] gathered per-example
        b = self.op_bias[ops]                            # [B, N_VALUES]
        logits = torch.einsum('bh,bvh->bv', h, W) + b    # apply the selected operator's linear rule
        return logits


def param_count(m):
    return sum(p.numel() for p in m.parameters())


def run_condition(name, model_ctor, seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    model = model_ctor().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)

    n_train = len(TRAIN_PAIRS)
    history = []
    for step in range(1, TRAIN_STEPS + 1):
        idx = rng.choice(n_train, size=BATCH_SIZE, replace=True)
        ops = TRAIN_OPS[idx]
        xs = TRAIN_XS[idx]
        ys = TRAIN_YS[idx]
        logits = model(ops, xs)
        loss = F.cross_entropy(logits, ys)
        opt.zero_grad()
        loss.backward()
        opt.step()

        if step % 500 == 0 or step == TRAIN_STEPS:
            with torch.no_grad():
                train_logits = model(TRAIN_OPS, TRAIN_XS)
                train_acc = (train_logits.argmax(-1) == TRAIN_YS).float().mean().item()
                test_logits = model(TEST_OPS, TEST_XS)
                test_acc = (test_logits.argmax(-1) == TEST_YS).float().mean().item()
            history.append({"step": step, "train_acc": train_acc, "held_out_acc": test_acc})

    with torch.no_grad():
        final_train_acc = (model(TRAIN_OPS, TRAIN_XS).argmax(-1) == TRAIN_YS).float().mean().item()
        final_test_acc = (model(TEST_OPS, TEST_XS).argmax(-1) == TEST_YS).float().mean().item()

    return {
        "condition": name,
        "n_params": param_count(model),
        "final_train_acc": final_train_acc,
        "final_held_out_acc": final_test_acc,
        "history": history,
    }


SEEDS = [0, 1, 2, 3, 4]
CONDITIONS = [
    ("black_box_mlp", BlackBoxMLP),
    ("factorized_rule_module", FactorizedRuleModule),
]


def main():
    t0 = time.time()
    per_seed = {name: [] for name, _ in CONDITIONS}

    for seed in SEEDS:
        print(f"\n### seed {seed} ###")
        for name, ctor in CONDITIONS:
            r = run_condition(name, ctor, seed)
            per_seed[name].append(r)
            print(f"  {name:24s} params={r['n_params']:5d}  "
                  f"train_acc={r['final_train_acc']:.3f}  held_out_acc={r['final_held_out_acc']:.3f}")

    summary = {}
    for name, _ in CONDITIONS:
        held = np.array([r["final_held_out_acc"] for r in per_seed[name]])
        train = np.array([r["final_train_acc"] for r in per_seed[name]])
        summary[name] = {
            "held_out_acc_mean": float(held.mean()),
            "held_out_acc_std": float(held.std()),
            "held_out_acc_values": held.tolist(),
            "train_acc_mean": float(train.mean()),
            "train_acc_std": float(train.std()),
            "n_params": per_seed[name][0]["n_params"],
        }

    print("\n========== SUMMARY ACROSS SEEDS ==========")
    for name, _ in CONDITIONS:
        s = summary[name]
        print(f"{name:24s} params={s['n_params']:5d}  "
              f"train_acc={s['train_acc_mean']:.3f}+/-{s['train_acc_std']:.3f}  "
              f"HELD_OUT_acc={s['held_out_acc_mean']:.3f}+/-{s['held_out_acc_std']:.3f}")

    out = {
        "meta": {
            "n_ops": N_OPS, "n_values": N_VALUES,
            "n_train_pairs": len(TRAIN_PAIRS), "n_held_out_pairs": len(TEST_PAIRS),
            "held_out_pairs": TEST_PAIRS,
            "train_steps": TRAIN_STEPS, "batch_size": BATCH_SIZE,
            "seeds": SEEDS, "elapsed_sec": time.time() - t0,
        },
        "summary": summary,
        "per_seed": {name: [
            {"seed": seed, "final_train_acc": r["final_train_acc"],
             "final_held_out_acc": r["final_held_out_acc"], "n_params": r["n_params"]}
            for seed, r in zip(SEEDS, per_seed[name])
        ] for name, _ in CONDITIONS},
    }
    with open("results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote results.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
