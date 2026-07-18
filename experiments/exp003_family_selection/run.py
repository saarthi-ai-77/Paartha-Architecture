"""
EXP-003: Can a model discover WHICH constrained transform family applies
to each operator, instead of a human hand-picking it?

This is the direct follow-up to EXP-002. EXP-002 showed that constraining
an operator to a rotation/reflection family (2 params) gives perfect,
exact held-out generalization for operators that truly are rotations, but
we only got that result because we, the designers, already knew which
operators were rotations. This experiment tests three candidate mechanisms
for AUTOMATIC family selection, given a small library of two candidate
families:
  Family A ("simple"): rotation/reflection, 2 parameters per operator.
  Family B ("expressive"): generic free linear map, ~30 parameters/operator.

Prediction stated BEFORE running (so this is a real test, not a post-hoc
story):
  (i) Naive joint end-to-end training (both families' params AND a
      learned mixture gate, all trained by ordinary cross-entropy on the
      training pairs) should FAIL to prefer the simple family even where
      it is correct -- because family B fits the training data at least
      as well as family A (it has strictly more capacity), and nothing in
      a standard training loss rewards a family for generalizing better
      to points it has never seen. We expect the naive gate to drift
      toward the expressive family for most/all operators.
  (ii) Adding an explicit parsimony penalty (prefer the simple family
      unless the expressive one measurably reduces training loss) might
      partially fix this, but the penalty strength is an arbitrary
      hyperparameter with no principled way to set it from training data
      alone -- we expect this to be fragile.
  (iii) Reserving a small slice of the training data purely for family
      SELECTION (fit both families' parameters on a fit-split, then
      choose per-operator whichever family generalizes better to a
      disjoint selection-split, never touching the final held-out test
      pairs) should correctly recover the right family per operator,
      because this is the only one of the three mechanisms that actually
      measures generalization, rather than training fit, before choosing.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import json

device = 'cuda' if torch.cuda.is_available() else 'cpu'
N_OPS, N_VALUES = 4, 10

def op0(x): return (x + 1) % 10
def op1(x): return (x * 2) % 10
def op2(x): return (9 - x) % 10
def op3(x): return (x + 5) % 10
OP_FNS = [op0, op1, op2, op3]
OP_NAMES = ["op0_rotation", "op1_QUADRATIC", "op2_reflect", "op3_rotation"]
TRUE_SIMPLE = [True, False, True, True]  # ground truth: which ops truly belong to family A

# Final held-out test pairs -- NEVER touched by fitting or selection.
FINAL_TEST = set()
for o in range(N_OPS):
    FINAL_TEST.add((o, (2 * o) % 10))
    FINAL_TEST.add((o, (2 * o + 1) % 10))

ALL_PAIRS = [(o, x) for o in range(N_OPS) for x in range(N_VALUES)]
TRAIN_PAIRS = [p for p in ALL_PAIRS if p not in FINAL_TEST]  # 32 pairs, 8 per operator

# For condition (iii): further split each operator's 8 training x-values
# into a 6-point FIT split and a 2-point SELECTION split.
FIT_PAIRS, SEL_PAIRS = [], []
for o in range(N_OPS):
    op_train_xs = sorted(x for (oo, x) in TRAIN_PAIRS if oo == o)
    sel_xs = set(op_train_xs[:2])   # first 2 (deterministic, not random) as selection-only
    for x in op_train_xs:
        (SEL_PAIRS if x in sel_xs else FIT_PAIRS).append((o, x))

print(f"train pairs: {len(TRAIN_PAIRS)}  fit: {len(FIT_PAIRS)}  sel: {len(SEL_PAIRS)}  final_test: {len(FINAL_TEST)}")


def pairs_to_tensors(pairs):
    ops = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    xs = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    ys = torch.tensor([OP_FNS[p[0]](p[1]) for p in pairs], dtype=torch.long, device=device)
    return ops, xs, ys


TR_OPS, TR_XS, TR_YS = pairs_to_tensors(TRAIN_PAIRS)
FIT_OPS, FIT_XS, FIT_YS = pairs_to_tensors(FIT_PAIRS)
SEL_OPS, SEL_XS, SEL_YS = pairs_to_tensors(SEL_PAIRS)
TE_OPS, TE_XS, TE_YS = pairs_to_tensors(sorted(FINAL_TEST))

angles = torch.arange(N_VALUES, dtype=torch.float32) * (2 * math.pi / N_VALUES)
FEAT = torch.stack([torch.cos(angles), torch.sin(angles)], dim=-1).to(device)


def family_a_logits(theta, s_raw, xs):
    s = torch.tanh(s_raw)
    c, sn = torch.cos(theta), torch.sin(theta)
    x_feat = FEAT[xs]
    cx, sx = x_feat[:, 0], x_feat[:, 1]
    tx = c * cx - s * sn * sx
    ty = sn * cx + s * c * sx
    return torch.stack([tx, ty], dim=-1) @ FEAT.T


def family_b_logits(W, b, xs):
    h = FEAT[xs]
    return torch.einsum('bh,bvh->bv', h, W) + b


class Params(nn.Module):
    def __init__(self):
        super().__init__()
        self.theta = nn.Parameter(torch.zeros(N_OPS, device=device))
        self.s_raw = nn.Parameter(torch.ones(N_OPS, device=device))
        self.W = nn.Parameter((torch.randn(N_OPS, N_VALUES, 2, device=device)) * 0.3)
        self.b = nn.Parameter(torch.zeros(N_OPS, N_VALUES, device=device))

    def logits_a(self, ops, xs):
        return family_a_logits(self.theta[ops], self.s_raw[ops], xs)

    def logits_b(self, ops, xs):
        return family_b_logits(self.W[ops], self.b[ops], xs)


# --- Condition (i): naive joint end-to-end selection -----------------------
def run_naive(seed, steps=3000, lr=1e-2):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    p = Params()
    raw_gate = nn.Parameter(torch.zeros(N_OPS, device=device))  # sigmoid(0)=0.5 init
    opt = torch.optim.Adam(list(p.parameters()) + [raw_gate], lr=lr)
    for _ in range(steps):
        idx = rng.choice(len(TRAIN_PAIRS), size=16, replace=True)
        ops, xs, ys = TR_OPS[idx], TR_XS[idx], TR_YS[idx]
        gate = torch.sigmoid(raw_gate[ops])
        logits = gate.unsqueeze(-1) * p.logits_a(ops, xs) + (1 - gate).unsqueeze(-1) * p.logits_b(ops, xs)
        loss = F.cross_entropy(logits, ys)
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        gate = torch.sigmoid(raw_gate)
        mixed = gate[TE_OPS].unsqueeze(-1) * p.logits_a(TE_OPS, TE_XS) + \
                (1 - gate[TE_OPS]).unsqueeze(-1) * p.logits_b(TE_OPS, TE_XS)
        test_acc = (mixed.argmax(-1) == TE_YS).float().mean().item()
        per_op_gate = gate.tolist()
    return test_acc, per_op_gate


# --- Condition (ii): parsimony-regularized joint selection ------------------
def run_parsimony(seed, lam, steps=3000, lr=1e-2):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    p = Params()
    raw_gate = nn.Parameter(torch.zeros(N_OPS, device=device))
    opt = torch.optim.Adam(list(p.parameters()) + [raw_gate], lr=lr)
    for _ in range(steps):
        idx = rng.choice(len(TRAIN_PAIRS), size=16, replace=True)
        ops, xs, ys = TR_OPS[idx], TR_XS[idx], TR_YS[idx]
        gate = torch.sigmoid(raw_gate[ops])
        logits = gate.unsqueeze(-1) * p.logits_a(ops, xs) + (1 - gate).unsqueeze(-1) * p.logits_b(ops, xs)
        ce = F.cross_entropy(logits, ys)
        parsimony_penalty = (1 - gate).mean()  # penalize leaning on the expressive family
        loss = ce + lam * parsimony_penalty
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        gate = torch.sigmoid(raw_gate)
        mixed = gate[TE_OPS].unsqueeze(-1) * p.logits_a(TE_OPS, TE_XS) + \
                (1 - gate[TE_OPS]).unsqueeze(-1) * p.logits_b(TE_OPS, TE_XS)
        test_acc = (mixed.argmax(-1) == TE_YS).float().mean().item()
        per_op_gate = gate.tolist()
    return test_acc, per_op_gate


# --- Condition (iii): validation-driven hard selection ----------------------
def run_validation_selection(seed, steps=2000, lr=1e-2):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    p = Params()
    opt = torch.optim.Adam(p.parameters(), lr=lr)
    n_fit = len(FIT_PAIRS)
    for _ in range(steps):
        idx = rng.choice(n_fit, size=16, replace=True)
        ops, xs, ys = FIT_OPS[idx], FIT_XS[idx], FIT_YS[idx]
        loss = F.cross_entropy(p.logits_a(ops, xs), ys) + F.cross_entropy(p.logits_b(ops, xs), ys)
        opt.zero_grad(); loss.backward(); opt.step()

    chosen_family = []  # per operator: 'A' or 'B'
    with torch.no_grad():
        for o in range(N_OPS):
            mask = SEL_OPS == o
            acc_a = (p.logits_a(SEL_OPS[mask], SEL_XS[mask]).argmax(-1) == SEL_YS[mask]).float().mean().item()
            acc_b = (p.logits_b(SEL_OPS[mask], SEL_XS[mask]).argmax(-1) == SEL_YS[mask]).float().mean().item()
            chosen_family.append('A' if acc_a >= acc_b else 'B')

        per_op_test_acc = {}
        for o in range(N_OPS):
            mask = TE_OPS == o
            fn = p.logits_a if chosen_family[o] == 'A' else p.logits_b
            acc = (fn(TE_OPS[mask], TE_XS[mask]).argmax(-1) == TE_YS[mask]).float().mean().item()
            per_op_test_acc[OP_NAMES[o]] = acc
        overall = float(np.mean(list(per_op_test_acc.values())))
    return overall, chosen_family, per_op_test_acc


def main():
    SEEDS = range(5)
    results = {"naive": [], "parsimony_0.1": [], "parsimony_0.5": [], "validation_driven": []}

    print("\n=== Condition (i): naive joint selection ===")
    for seed in SEEDS:
        acc, gates = run_naive(seed)
        results["naive"].append({"seed": seed, "held_out_acc": acc, "gates": gates})
        print(f"  seed {seed}: held_out_acc={acc:.3f}  gates(weight on simple family)={[round(g,2) for g in gates]}")

    for lam in [0.1, 0.5]:
        print(f"\n=== Condition (ii): parsimony-regularized (lambda={lam}) ===")
        for seed in SEEDS:
            acc, gates = run_parsimony(seed, lam)
            results[f"parsimony_{lam}"].append({"seed": seed, "held_out_acc": acc, "gates": gates})
            print(f"  seed {seed}: held_out_acc={acc:.3f}  gates={[round(g,2) for g in gates]}")

    print("\n=== Condition (iii): validation-driven hard selection ===")
    for seed in SEEDS:
        acc, chosen, per_op = run_validation_selection(seed)
        results["validation_driven"].append({"seed": seed, "held_out_acc": acc, "chosen_family": chosen, "per_op": per_op})
        print(f"  seed {seed}: held_out_acc={acc:.3f}  chosen_family={chosen} (true_simple={TRUE_SIMPLE})")

    print("\n========== SUMMARY ==========")
    for name in ["naive", "parsimony_0.1", "parsimony_0.5"]:
        accs = [r["held_out_acc"] for r in results[name]]
        avg_gates = np.mean([r["gates"] for r in results[name]], axis=0)
        print(f"{name:20s} held_out_acc={np.mean(accs):.3f}+/-{np.std(accs):.3f}  "
              f"mean_gate_per_op={[round(g,2) for g in avg_gates]}  (true_simple={TRUE_SIMPLE})")
    vd_accs = [r["held_out_acc"] for r in results["validation_driven"]]
    correct_selections = [
        sum(1 for o in range(N_OPS) if (r["chosen_family"][o] == 'A') == TRUE_SIMPLE[o])
        for r in results["validation_driven"]
    ]
    print(f"{'validation_driven':20s} held_out_acc={np.mean(vd_accs):.3f}+/-{np.std(vd_accs):.3f}  "
          f"correct_family_selections_per_seed(/4 ops)={correct_selections}")

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
