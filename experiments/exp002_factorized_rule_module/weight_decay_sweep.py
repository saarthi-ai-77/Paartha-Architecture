"""
EXP-002, stage 4: does L2 weight decay on the fixed-feature factorized
rule module recover compositional generalization? (It does not -- see
docs/06_experiments/Completed.md for the full write-up.)
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
FEAT = torch.stack([torch.sin(angles), torch.cos(angles)], dim=-1).to(device)

WEIGHT_DECAYS = [0.0, 1e-3, 1e-2, 1e-1, 3e-1, 1.0]
SEEDS = range(5)
TRAIN_STEPS = 3000
BATCH_SIZE = 16


def run(wd, seed):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    W = nn.Parameter((torch.randn(N_OPS, N_VALUES, 2) * 0.3).to(device))
    b = nn.Parameter(torch.zeros(N_OPS, N_VALUES).to(device))
    opt = torch.optim.Adam([W, b], lr=5e-3, weight_decay=wd)
    for _ in range(TRAIN_STEPS):
        idx = rng.choice(len(TRAIN_PAIRS), size=BATCH_SIZE, replace=True)
        h = FEAT[TRXS[idx]]
        logits = torch.einsum('bh,bvh->bv', h, W[TROPS[idx]]) + b[TROPS[idx]]
        loss = F.cross_entropy(logits, TRYS[idx])
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        train_logits = torch.einsum('bh,bvh->bv', FEAT[TRXS], W[TROPS]) + b[TROPS]
        train_acc = (train_logits.argmax(-1) == TRYS).float().mean().item()
        test_logits = torch.einsum('bh,bvh->bv', FEAT[TEXS], W[TEOPS]) + b[TEOPS]
        test_acc = (test_logits.argmax(-1) == TEYS).float().mean().item()
    return train_acc, test_acc


def main():
    results = {}
    for wd in WEIGHT_DECAYS:
        train_accs, test_accs = [], []
        for seed in SEEDS:
            tr, te = run(wd, seed)
            train_accs.append(tr); test_accs.append(te)
        results[str(wd)] = {
            "train_acc_mean": float(np.mean(train_accs)),
            "held_out_acc_mean": float(np.mean(test_accs)),
            "held_out_acc_std": float(np.std(test_accs)),
        }
        print(f"weight_decay={wd:6.3f}  train_acc={np.mean(train_accs):.3f}  "
              f"held_out_acc={np.mean(test_accs):.3f}+/-{np.std(test_accs):.3f}")
    with open("weight_decay_sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
