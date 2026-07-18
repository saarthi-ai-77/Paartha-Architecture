"""
EXP-002, stage 5: constrain each operator to a single learned rotation
angle + reflection sign (2 parameters per operator, instead of ~30 free
parameters in the generic factorized linear layer). This is the variant
that WORKED -- 100% held-out accuracy on op0/op2/op3 (all rotation- or
reflection-representable), with recovered parameters matching the exact
ground-truth transform, and a correct, honest 0% on op1 (x*2 mod 10),
which is quadratic in circle coordinates and genuinely not representable
by this constrained family.

See docs/06_experiments/Completed.md (EXP-002) for the full write-up and
what this result does and doesn't establish about the architecture.
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
OP_NAMES = ["op0_add1_rotation", "op1_double_QUADRATIC", "op2_reflect", "op3_add5_rotation"]

HELD_OUT = set()
for o in range(N_OPS):
    HELD_OUT.add((o, (2 * o) % 10))
    HELD_OUT.add((o, (2 * o + 1) % 10))
ALL_PAIRS = [(o, x) for o in range(N_OPS) for x in range(N_VALUES)]
TRAIN_PAIRS = [p for p in ALL_PAIRS if p not in HELD_OUT]
TEST_PAIRS = sorted(HELD_OUT)


def pairs_to_tensors(pairs):
    ops = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    xs = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    ys = torch.tensor([OP_FNS[p[0]](p[1]) for p in pairs], dtype=torch.long, device=device)
    return ops, xs, ys


TROPS, TRXS, TRYS = pairs_to_tensors(TRAIN_PAIRS)
TEOPS, TEXS, TEYS = pairs_to_tensors(TEST_PAIRS)

angles = torch.arange(N_VALUES, dtype=torch.float32) * (2 * math.pi / N_VALUES)
# Fixed circle points, reused as BOTH the operand encoding and the class
# ("where on the circle does each output label sit") prototypes.
FEAT = torch.stack([torch.cos(angles), torch.sin(angles)], dim=-1).to(device)  # [10, 2]

TRAIN_STEPS = 2000
BATCH_SIZE = 16
SEEDS = range(5)


def forward(theta, s_raw, xs):
    """theta: learned rotation angle per example's operator.
    s_raw: learned reflection sign (passed through tanh -> [-1, 1]) per
    example's operator. Only 2 real degrees of freedom per operator."""
    s = torch.tanh(s_raw)
    c, sn = torch.cos(theta), torch.sin(theta)
    x_feat = FEAT[xs]
    cx, sx = x_feat[:, 0], x_feat[:, 1]
    tx = c * cx - s * sn * sx
    ty = sn * cx + s * c * sx
    transformed = torch.stack([tx, ty], dim=-1)
    logits = transformed @ FEAT.T  # cosine-similarity-style match against each class prototype
    return logits


def run(seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    theta = nn.Parameter(torch.zeros(N_OPS, device=device))
    s_raw = nn.Parameter(torch.ones(N_OPS, device=device))
    opt = torch.optim.Adam([theta, s_raw], lr=2e-2)
    for _ in range(TRAIN_STEPS):
        idx = rng.choice(len(TRAIN_PAIRS), size=BATCH_SIZE, replace=True)
        ops, xs, ys = TROPS[idx], TRXS[idx], TRYS[idx]
        logits = forward(theta[ops], s_raw[ops], xs)
        loss = F.cross_entropy(logits, ys)
        opt.zero_grad(); loss.backward(); opt.step()

    with torch.no_grad():
        train_acc = (forward(theta[TROPS], s_raw[TROPS], TRXS).argmax(-1) == TRYS).float().mean().item()
        test_acc = (forward(theta[TEOPS], s_raw[TEOPS], TEXS).argmax(-1) == TEYS).float().mean().item()
        per_op = {}
        for o in range(N_OPS):
            mask = TEOPS == o
            acc = (forward(theta[TEOPS[mask]], s_raw[TEOPS[mask]], TEXS[mask]).argmax(-1) == TEYS[mask]).float().mean().item()
            per_op[OP_NAMES[o]] = acc
    return train_acc, test_acc, per_op, theta.tolist(), torch.tanh(s_raw).tolist()


def main():
    per_op_accum = {name: [] for name in OP_NAMES}
    overall = []
    for seed in SEEDS:
        train_acc, test_acc, per_op, thetas, s_vals = run(seed)
        overall.append(test_acc)
        for name, acc in per_op.items():
            per_op_accum[name].append(acc)
        print(f"seed {seed}: train_acc={train_acc:.3f} held_out_acc={test_acc:.3f} "
              f"theta={[round(t, 4) for t in thetas]} s={[round(s, 4) for s in s_vals]}")

    print("\nper-operator held-out accuracy across seeds:")
    summary = {}
    for name in OP_NAMES:
        v = per_op_accum[name]
        summary[name] = {"mean": float(np.mean(v)), "std": float(np.std(v))}
        print(f"  {name:24s} {np.mean(v):.3f} +/- {np.std(v):.3f}")
    print(f"overall held_out_acc: {np.mean(overall):.3f} +/- {np.std(overall):.3f}")

    with open("group_action_results.json", "w") as f:
        json.dump({
            "per_operator": summary,
            "overall_mean": float(np.mean(overall)),
            "overall_std": float(np.std(overall)),
        }, f, indent=2)


if __name__ == "__main__":
    main()
