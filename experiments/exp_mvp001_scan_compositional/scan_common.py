"""
Shared data loading and grammar for ACA-MVP-001 Benchmark B (SCAN, Lake & Baroni 2018).

The grammar below was NOT taken on trust from a secondary description -- it was
reverse-engineered and CONFIRMED against the real, downloaded addprim_jump
train/test files by exact token-count matching on multiple real examples,
including the special-cased "turn" primitive (see docs/06_experiments/Completed.md,
EXP-020, "Grammar Verification" for the worked derivation). This module is
shared between the generic and structure-matched models specifically so the
grammar exists in exactly one place -- duplicating it would risk the two
models silently testing against subtly different notions of "correct
structure," which would invalidate the whole comparison.

Verified rules (D = left/right, U = walk/look/run/jump, "turn" special-cased):
  U            -> I_U                          (1 token)
  U D          -> TURN_D, I_U                  (2 tokens)
  U opposite D -> TURN_D, TURN_D, I_U           (3 tokens)
  U around D   -> (TURN_D, I_U) x4              (8 tokens)
  turn D       -> TURN_D                        (1 token -- no extra action appended)
  turn opposite D -> TURN_D, TURN_D             (2 tokens)
  turn around D   -> (TURN_D) x4                (4 tokens)
  X twice  -> seq(X) seq(X)
  X thrice -> seq(X) seq(X) seq(X)
  X and Y  -> seq(X) seq(Y)
  X after Y -> seq(Y) seq(X)
Confirmed: real data never chains more than one "and"/"after" per command
(0 of 22,376 lines have 2+ connectives) -- so C -> S | S and S | S after S,
never deeper.
"""

import os

PRIMITIVES = ["walk", "look", "run", "jump", "turn"]
DIRECTIONS = ["left", "right"]
ACTIONS = ["I_WALK", "I_LOOK", "I_RUN", "I_JUMP", "I_TURN_LEFT", "I_TURN_RIGHT"]
PRIM_TO_ACTION_TRUE = {"walk": "I_WALK", "look": "I_LOOK", "run": "I_RUN", "jump": "I_JUMP"}
TURN_TOK = {"left": "I_TURN_LEFT", "right": "I_TURN_RIGHT"}

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def load_pairs(filename):
    path = os.path.join(DATA_DIR, filename)
    pairs = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            assert line.startswith("IN: ") and " OUT: " in line, f"unexpected line format: {line}"
            in_part, out_part = line[len("IN: "):].split(" OUT: ")
            pairs.append((in_part.split(" "), out_part.split(" ")))
    return pairs


# ---------------------------------------------------------------------------
# Fixed, hand-specified SCAN grammar: recursive-descent parser (structure is
# externally supplied, not learned -- matching ACA-MVP-001 Section 2's
# "family assignment fixed by hand, not auto-routed").
# ---------------------------------------------------------------------------

def parse_command(tokens):
    """C -> S | S and S | S after S (verified: never deeper)."""
    if "and" in tokens:
        i = tokens.index("and")
        return ("and", parse_clause(tokens[:i]), parse_clause(tokens[i + 1:]))
    if "after" in tokens:
        i = tokens.index("after")
        return ("after", parse_clause(tokens[:i]), parse_clause(tokens[i + 1:]))
    return ("single", parse_clause(tokens), None)


def parse_clause(tokens):
    """S -> V twice | V thrice | V"""
    if tokens[-1] == "twice":
        return (parse_verb_phrase(tokens[:-1]), 2)
    if tokens[-1] == "thrice":
        return (parse_verb_phrase(tokens[:-1]), 3)
    return (parse_verb_phrase(tokens), 1)


def parse_verb_phrase(tokens):
    """V -> U opposite D | U around D | U D | U"""
    u = tokens[0]
    assert u in PRIMITIVES, f"unknown primitive: {u}"
    if len(tokens) == 1:
        return ("bare", u, None)
    if len(tokens) == 2:
        assert tokens[1] in DIRECTIONS
        return ("plain", u, tokens[1])
    if len(tokens) == 3:
        assert tokens[1] in ("opposite", "around") and tokens[2] in DIRECTIONS
        return (tokens[1], u, tokens[2])
    raise ValueError(f"unparseable verb phrase: {tokens}")


def eval_verb_phrase(v, primitive_action_fn):
    """Fixed composition rules; primitive_action_fn(u) -> action token (or
    logit vector, for the differentiable structure-matched model) is the
    ONLY thing that varies between the true/oracle grammar and the learned
    structure-matched model."""
    kind, u, d = v
    if kind == "bare":
        return [primitive_action_fn(u)]
    turn_tok = primitive_action_fn("turn") if False else None  # placeholder, unused path
    turn_symbol = TURN_TOK[d]
    if u == "turn":
        # Special-cased primitive: the direction change IS the entire action,
        # no separate "do turn" token is appended (verified against real data:
        # "turn right thrice and turn opposite right twice" has exactly 7
        # I_TURN_RIGHT tokens, matching 3 + 4, not the 6 + 9 a naive
        # non-special-cased rule would produce).
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
    raise ValueError(f"unhandled verb phrase: {v}")


def eval_clause(s, primitive_action_fn):
    v, repeat = s
    seq = eval_verb_phrase(v, primitive_action_fn)
    return seq * repeat


def eval_command(c, primitive_action_fn):
    kind, left, right = c
    if kind == "single":
        return eval_clause(left, primitive_action_fn)
    left_seq = eval_clause(left, primitive_action_fn)
    right_seq = eval_clause(right, primitive_action_fn)
    if kind == "and":
        return left_seq + right_seq
    if kind == "after":
        return right_seq + left_seq
    raise ValueError(f"unhandled command: {c}")


def oracle_primitive_action(u):
    """The TRUE mapping -- used only to self-check the grammar against real
    data before training anything (see verify_grammar below). The trainable
    structure-matched model never calls this; it uses a learned classifier
    instead (see run_structure_matched.py)."""
    return PRIM_TO_ACTION_TRUE[u]


def verify_grammar(pairs, n_check=None):
    """Self-check: parse+evaluate every (or n_check) real example with the
    ORACLE primitive mapping and confirm exact match against the true output.
    This is the actual verification step -- not just the worked examples in
    this file's docstring -- run once before any model is trained."""
    checked = 0
    for in_toks, out_toks in (pairs if n_check is None else pairs[:n_check]):
        tree = parse_command(in_toks)
        pred = eval_command(tree, oracle_primitive_action)
        if pred != out_toks:
            return False, checked, (in_toks, out_toks, pred)
        checked += 1
    return True, checked, None


if __name__ == "__main__":
    train_pairs = load_pairs("tasks_train_addprim_jump.txt")
    test_pairs = load_pairs("tasks_test_addprim_jump.txt")
    print(f"train examples: {len(train_pairs)}, test examples: {len(test_pairs)}")
    ok, n, failure = verify_grammar(train_pairs)
    print(f"train grammar verification: {'PASS' if ok else 'FAIL'} ({n} examples checked)")
    if not ok:
        print("FIRST FAILURE:", failure)
    ok, n, failure = verify_grammar(test_pairs)
    print(f"test grammar verification: {'PASS' if ok else 'FAIL'} ({n} examples checked)")
    if not ok:
        print("FIRST FAILURE:", failure)
