"""
EXP-009, Stage 2: Does a label-free EVALUATE signal work for computation-
family SELECTION, on EXP-003's validated rule-family task?

EXP-003 validated that selection must be driven by measured held-out
ACCURACY (which requires the true label) rather than training loss. This
stage asks a narrower, different question: if no label is available at
selection time at all (matching the SR-01/planning-termination use case,
where ground truth often isn't available), can a label-free confidence
signal substitute for held-out accuracy and still pick the right family?

Same three candidates as recall_stage.py: entropy, ensemble disagreement
(K=2 per family here, to bound compute), and a self-assessment head
(operating on logits -> predicted loss, trained on the FIT split where
labels ARE available, applied on the SEL split without its labels).

Compared against EXP-003's oracle: true-accuracy-driven selection, which
picked family A for all 4 operators (3 correct: op0/op2/op3 are truly
rotations; 1 incorrect but inconsequential: op1 is not, but family B does
not solve it either) and achieved 0.750 final held-out accuracy.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import json
import time

device = 'cuda' if torch.cuda.is_available() else 'cpu'
N_OPS, N_VALUES = 4, 10

def op0(x): return (x + 1) % 10
def op1(x): return (x * 2) % 10
def op2(x): return (9 - x) % 10
def op3(x): return (x + 5) % 10
OP_FNS = [op0, op1, op2, op3]
TRUE_SIMPLE = [True, False, True, True]

HELD_OUT = set()
for o in range(N_OPS):
    HELD_OUT.add((o, (2 * o) % 10))
    HELD_OUT.add((o, (2 * o + 1) % 10))
ALL_PAIRS = [(o, x) for o in range(N_OPS) for x in range(N_VALUES)]
TRAIN_PAIRS = [p for p in ALL_PAIRS if p not in HELD_OUT]

FIT_PAIRS, SEL_PAIRS = [], []
for o in range(N_OPS):
    op_train_xs = sorted(x for (oo, x) in TRAIN_PAIRS if oo == o)
    sel_xs = set(op_train_xs[:2])
    for x in op_train_xs:
        (SEL_PAIRS if x in sel_xs else FIT_PAIRS).append((o, x))


def pairs_to_tensors(pairs):
    ops = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=device)
    xs = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=device)
    ys = torch.tensor([OP_FNS[p[0]](p[1]) for p in pairs], dtype=torch.long, device=device)
    return ops, xs, ys


FIT_OPS, FIT_XS, FIT_YS = pairs_to_tensors(FIT_PAIRS)
SEL_OPS, SEL_XS, SEL_YS = pairs_to_tensors(SEL_PAIRS)
TE_OPS, TE_XS, TE_YS = pairs_to_tensors(sorted(HELD_OUT))

angles = torch.arange(N_VALUES, dtype=torch.float32) * (2 * math.pi / N_VALUES)
FEAT = torch.stack([torch.cos(angles), torch.sin(angles)], dim=-1).to(device)


class FamilyA(nn.Module):
    """Rotation/reflection-constrained (2 params/op) -- EXP-002/003's
    validated structure-matched family."""
    def __init__(self):
        super().__init__()
        self.theta = nn.Parameter(torch.zeros(N_OPS, device=device))
        self.s_raw = nn.Parameter(torch.ones(N_OPS, device=device))

    def forward(self, ops, xs):
        theta = self.theta[ops]; s = torch.tanh(self.s_raw[ops])
        c, sn = torch.cos(theta), torch.sin(theta)
        x_feat = FEAT[xs]; cx, sx = x_feat[:, 0], x_feat[:, 1]
        tx = c * cx - s * sn * sx
        ty = sn * cx + s * c * sx
        return torch.stack([tx, ty], dim=-1) @ FEAT.T


class FamilyB(nn.Module):
    """Generic linear over fixed features (~30 params/op) -- EXP-002/003's
    falsified-for-generalization, more expressive family."""
    def __init__(self):
        super().__init__()
        self.W = nn.Parameter(torch.randn(N_OPS, N_VALUES, 2, device=device) * 0.3)
        self.b = nn.Parameter(torch.zeros(N_OPS, N_VALUES, device=device))

    def forward(self, ops, xs):
        h = FEAT[xs]
        return torch.einsum('bh,bvh->bv', h, self.W[ops]) + self.b[ops]


class SelfAssessHead(nn.Module):
    """Predicts a family's own CE loss from its logits (10-d -> scalar)."""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(N_VALUES, 16), nn.ReLU(), nn.Linear(16, 1))

    def forward(self, logits):
        return self.net(logits).squeeze(-1)


def train_family(cls, seed, steps=2000, lr=1e-2):
    torch.manual_seed(seed)
    rng = np.random.RandomState(seed)
    model = cls().to(device)
    head = SelfAssessHead().to(device)
    opt = torch.optim.Adam(list(model.parameters()) + list(head.parameters()), lr=lr)
    n_fit = len(FIT_PAIRS)
    for _ in range(steps):
        idx = rng.choice(n_fit, size=16, replace=True)
        ops, xs, ys = FIT_OPS[idx], FIT_XS[idx], FIT_YS[idx]
        logits = model(ops, xs)
        ce = F.cross_entropy(logits, ys, reduction='none')
        pred_loss = head(logits)
        loss = ce.mean() + F.mse_loss(pred_loss, ce.detach())
        opt.zero_grad(); loss.backward(); opt.step()
    return model, head


def per_op_signal(model, head, ops_t, xs_t, mode):
    with torch.no_grad():
        logits = model(ops_t, xs_t)
        if mode == "entropy":
            probs = F.softmax(logits, dim=-1)
            return -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
        elif mode == "selfassess":
            return head(logits)
    raise ValueError(mode)


def run_seed(seed):
    # Train family A and family B once (primary instance, used for
    # entropy + selfassess signals and for final TEST evaluation).
    model_a, head_a = train_family(FamilyA, seed)
    model_b, head_b = train_family(FamilyB, seed)

    # Small ensembles (K=2 each) for the ensemble-disagreement signal only.
    ens_a = [train_family(FamilyA, seed * 100 + k)[0] for k in range(2)]
    ens_b = [train_family(FamilyB, seed * 100 + k)[0] for k in range(2)]

    results = {}
    for mode in ["entropy", "ensemble", "selfassess"]:
        chosen = []
        for o in range(N_OPS):
            mask = SEL_OPS == o
            sel_ops, sel_xs = SEL_OPS[mask], SEL_XS[mask]
            if mode == "ensemble":
                with torch.no_grad():
                    probs_a = [F.softmax(m(sel_ops, sel_xs), dim=-1) for m in ens_a]
                    probs_b = [F.softmax(m(sel_ops, sel_xs), dim=-1) for m in ens_b]
                    kl_a = (probs_a[0].clamp_min(1e-9) * (probs_a[0].clamp_min(1e-9).log() - probs_a[1].clamp_min(1e-9).log())).sum(-1).mean().item()
                    kl_b = (probs_b[0].clamp_min(1e-9) * (probs_b[0].clamp_min(1e-9).log() - probs_b[1].clamp_min(1e-9).log())).sum(-1).mean().item()
                sig_a, sig_b = kl_a, kl_b
            else:
                sig_a = per_op_signal(model_a, head_a, sel_ops, sel_xs, mode).mean().item()
                sig_b = per_op_signal(model_b, head_b, sel_ops, sel_xs, mode).mean().item()
            # Lower signal (entropy/disagreement/predicted-loss) = more confident.
            chosen.append('A' if sig_a <= sig_b else 'B')

        with torch.no_grad():
            per_op_test_acc = {}
            for o in range(N_OPS):
                mask = TE_OPS == o
                m = model_a if chosen[o] == 'A' else model_b
                acc = (m(TE_OPS[mask], TE_XS[mask]).argmax(-1) == TE_YS[mask]).float().mean().item()
                per_op_test_acc[o] = acc
            overall = float(np.mean(list(per_op_test_acc.values())))

        correct_selections = sum(1 for o in range(N_OPS) if (chosen[o] == 'A') == TRUE_SIMPLE[o])
        results[mode] = {"chosen_family": chosen, "test_acc": overall, "correct_selections": correct_selections}

    return results


def main():
    t0 = time.time()
    SEEDS = range(5)
    all_results = {mode: [] for mode in ["entropy", "ensemble", "selfassess"]}

    for seed in SEEDS:
        print(f"\n### seed {seed} ###")
        r = run_seed(seed)
        for mode, res in r.items():
            all_results[mode].append(res)
            print(f"  {mode:12s} chosen={res['chosen_family']} test_acc={res['test_acc']:.3f} "
                  f"correct_selections={res['correct_selections']}/4")

    print("\n========== STAGE 2 SUMMARY (family selection, label-free) ==========")
    print(f"{'oracle (EXP-003, true accuracy)':32s} test_acc=0.750 (reference, not re-run here)")
    summary = {}
    for mode in all_results:
        accs = [r["test_acc"] for r in all_results[mode]]
        sels = [r["correct_selections"] for r in all_results[mode]]
        summary[mode] = {"test_acc_mean": float(np.mean(accs)), "test_acc_std": float(np.std(accs)),
                          "correct_selections_mean": float(np.mean(sels))}
        print(f"{mode:32s} test_acc={np.mean(accs):.3f}+/-{np.std(accs):.3f}  "
              f"correct_selections={np.mean(sels):.2f}/4")

    with open("rule_results.json", "w") as f:
        json.dump({"meta": {"seeds": list(SEEDS), "elapsed_sec": time.time() - t0,
                             "oracle_test_acc_reference": 0.750},
                   "summary": summary,
                   "raw": {mode: [{"chosen_family": r["chosen_family"], "test_acc": r["test_acc"],
                                    "correct_selections": r["correct_selections"]} for r in res]
                            for mode, res in all_results.items()}}, f, indent=2)
    print(f"\nWrote rule_results.json in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
