"""
EXP-002 FIX ATTEMPT: Why did the factorized rule module fail, and does a
fixed (non-learned) operand encoding fix it?

Diagnosis of the original failure:
  nn.Embedding(N_VALUES, EMBED_DIM) is a completely free lookup table --
  10 independent learned vectors with NO enforced relationship between them.
  The model is therefore free to give x=3 whatever vector best fits
  whichever operators x=3 appeared with in training, and there is nothing
  forcing that vector to be the SAME vector a held-out operator would need
  to correctly compute its function on x=3. With only 4 operators and small
  per-operator training sets, this is a heavily underdetermined bilinear
  factorization problem -- many (embedding, per-op-matrix) solutions fit
  the training data perfectly without generalizing. The architecture LOOKS
  factorized, but nothing about training forces a canonical, reusable
  representation of x.

Fix under test: replace the learned free embedding with a FIXED, non-learned
numeric encoding of x (sin/cos position on a circle, i.e. treating x as a
point on Z/10Z), so the model cannot reassign x's representation per
operator -- it must work with the same encoding everywhere.

Expected (stated BEFORE running, so this is a real prediction, not
post-hoc rationalization): operators that are affine in circle coordinates
(op0: x+1 is a rotation; op2: 9-x is a reflection; op3: x+5 is a rotation)
should become linearly representable from (sin, cos) features and should
generalize to held-out combinations. op1 (x*2 mod 10, "angle doubling") is
QUADRATIC in (sin theta, cos theta), not linear/affine, so a single linear
per-operator layer over fixed (sin,cos) features should NOT be expected to
generalize op1 correctly. If that specific pattern shows up in the results,
it's evidence the diagnosis is right, not a coincidence.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import math
import time

device = 'cuda' if torch.cuda.is_available() else 'cpu'

N_OPS = 4
N_VALUES = 10

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

TRAIN_OPS, TRAIN_XS, TRAIN_YS = pairs_to_tensors(TRAIN_PAIRS)
TEST_OPS, TEST_XS, TEST_YS = pairs_to_tensors(TEST_PAIRS)

TRAIN_STEPS = 3000
BATCH_SIZE = 16

# Fixed (non-learned) circle encoding of x -- NOT an nn.Embedding.
_angles = torch.arange(N_VALUES, dtype=torch.float32) * (2 * math.pi / N_VALUES)
FIXED_X_FEATURES = torch.stack([torch.sin(_angles), torch.cos(_angles)], dim=-1).to(device)  # [10, 2]


class FixedFeatureRuleModule(nn.Module):
    """Fixed sin/cos operand encoding + per-operator LINEAR readout.
    No learned embedding table -- x's representation cannot be reassigned
    per operator."""
    def __init__(self):
        super().__init__()
        feat_dim = FIXED_X_FEATURES.shape[1]
        self.op_weight = nn.Parameter(torch.randn(N_OPS, N_VALUES, feat_dim) * 0.3)
        self.op_bias = nn.Parameter(torch.zeros(N_OPS, N_VALUES))

    def forward(self, ops, xs):
        h = FIXED_X_FEATURES[xs]                 # [B, 2], fixed, shared across all operators
        W = self.op_weight[ops]                  # [B, N_VALUES, 2]
        b = self.op_bias[ops]
        logits = torch.einsum('bh,bvh->bv', h, W) + b
        return logits


def run_condition(seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    model = FixedFeatureRuleModule().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=5e-3)

    n_train = len(TRAIN_PAIRS)
    for step in range(1, TRAIN_STEPS + 1):
        idx = rng.choice(n_train, size=BATCH_SIZE, replace=True)
        logits = model(TRAIN_OPS[idx], TRAIN_XS[idx])
        loss = F.cross_entropy(logits, TRAIN_YS[idx])
        opt.zero_grad(); loss.backward(); opt.step()

    with torch.no_grad():
        train_acc = (model(TRAIN_OPS, TRAIN_XS).argmax(-1) == TRAIN_YS).float().mean().item()
        # per-operator held-out accuracy, not just averaged -- this is the
        # specific thing the diagnosis predicts a pattern in.
        per_op_acc = {}
        for o in range(N_OPS):
            mask = TEST_OPS == o
            if mask.sum() == 0:
                continue
            acc = (model(TEST_OPS[mask], TEST_XS[mask]).argmax(-1) == TEST_YS[mask]).float().mean().item()
            per_op_acc[OP_NAMES[o]] = acc
        overall_held_out = (model(TEST_OPS, TEST_XS).argmax(-1) == TEST_YS).float().mean().item()

    return train_acc, overall_held_out, per_op_acc


def main():
    t0 = time.time()
    seeds = [0, 1, 2, 3, 4]
    all_train, all_held = [], []
    per_op_accum = {name: [] for name in OP_NAMES}

    for seed in seeds:
        train_acc, held_acc, per_op = run_condition(seed)
        all_train.append(train_acc)
        all_held.append(held_acc)
        for name, acc in per_op.items():
            per_op_accum[name].append(acc)
        print(f"seed {seed}: train_acc={train_acc:.3f} held_out_acc={held_acc:.3f} per_op={per_op}")

    print("\n========== SUMMARY ==========")
    print(f"train_acc: {np.mean(all_train):.3f} +/- {np.std(all_train):.3f}")
    print(f"held_out_acc (overall): {np.mean(all_held):.3f} +/- {np.std(all_held):.3f}")
    print("held_out_acc by operator (this is the diagnostic result):")
    summary_per_op = {}
    for name in OP_NAMES:
        vals = per_op_accum[name]
        m, s = float(np.mean(vals)), float(np.std(vals))
        summary_per_op[name] = {"mean": m, "std": s, "values": vals}
        print(f"  {name:24s} {m:.3f} +/- {s:.3f}")

    out = {
        "meta": {"seeds": seeds, "train_steps": TRAIN_STEPS, "elapsed_sec": time.time() - t0},
        "train_acc_mean": float(np.mean(all_train)),
        "held_out_acc_mean": float(np.mean(all_held)),
        "held_out_acc_std": float(np.std(all_held)),
        "held_out_acc_by_operator": summary_per_op,
    }
    with open("results_fix_attempt.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote results_fix_attempt.json in {out['meta']['elapsed_sec']:.1f}s")


if __name__ == "__main__":
    main()
