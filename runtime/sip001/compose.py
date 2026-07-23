"""
COMPOSE (SIP-001 Section 2, row 6) -- the exact structure-matched SCAN
grammar and learned primitive classifier validated by EXP-020 (100.000% +/-
0.000% exact-match on real held-out compositional test data, ~141x a real
681,481-parameter generic Transformer baseline). Re-declared here rather
than imported across experiment directories, matching this program's
per-artifact self-containment convention (as Benchmark C's own code did).

Class A (validated, real) per SIP-001's three-way classification. The
grammar itself is fixed/hand-verified (see experiments/exp_mvp001_scan_
compositional/scan_common.py's verification against all 22,376 real
examples) -- EXP-005 (can a system discover this rather than have it
verified by hand) remains open and is not addressed here.
"""

import torch
import torch.nn as nn

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


class StructureMatchedCompose:
    """The runtime-facing wrapper: parse (fixed) -> classify learned
    primitives -> compose (fixed) -> decoded action sequence."""

    def __init__(self, device):
        self.device = device
        self.model = PrimitiveClassifier().to(device)

    def run(self, command_tokens):
        slots = compile_slots(command_tokens)
        table = self.model()
        logits_seq = build_logit_sequence(slots, table, self.device)
        pred_idx = logits_seq.argmax(dim=-1).cpu().tolist()
        return [ACTIONS[i] for i in pred_idx], logits_seq
