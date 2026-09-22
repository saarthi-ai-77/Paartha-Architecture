"""
EXP-CCS-0: Empirical Evaluation of Closed-Loop Discrepancy Reduction (CDR)
versus Competing Orchestration Mechanisms for Capability Composition and Fault Recovery.

This experiment investigates four core empirical questions:
1. Is Discrepancy Reduction General? Does a heuristic discrepancy function D(s, G)
   guide composition, or does it suffer from metric misalignment, local minima traps,
   and epistemic blindness?
2. Does Search Scale? How do Static Planning, Greedy Selection, Tree Search (A*/BFS),
   and CDR with Rollback scale as sequence depth increases from 2 to 6?
3. Can Epistemic Actions be Discovered? Can discrepancy reduction select actions that
   gather information (reducing internal uncertainty) rather than altering physical data?
4. How Does Fault Recovery Operate? Does state checkpointing and rollback outperform
   open-loop planning and greedy execution when intermediate operators crash or corrupt state?
"""

import copy
import random
import time
import json
from typing import Dict, List, Tuple, Any, Optional, Set

SEED = 42
random.seed(SEED)

# ---------------------------------------------------------------------------
# 1. Domain & State
# ---------------------------------------------------------------------------

class State:
    def __init__(self, data: List[Dict[str, Any]], working: Optional[Dict[str, Any]] = None, history: Optional[List[str]] = None):
        self.data = copy.deepcopy(data)
        self.working = copy.deepcopy(working) if working is not None else {}
        self.history = copy.deepcopy(history) if history is not None else []
        self.faulted = False

    def clone(self) -> 'State':
        s = State(self.data, self.working, self.history)
        s.faulted = self.faulted
        return s

    def signature(self) -> str:
        if self.faulted:
            return "FAULTED"
        # Preserve row order for sorting discrimination
        rows = tuple(tuple(sorted(r.items())) for r in self.data)
        work = tuple(sorted(self.working.items()))
        return str((rows, work))


# ---------------------------------------------------------------------------
# 2. Primitives
# ---------------------------------------------------------------------------

class Primitive:
    def __init__(self, name: str, cost: float = 1.0):
        self.name = name
        self.cost = cost

    def can_apply(self, s: State) -> bool:
        return not s.faulted

    def apply(self, s: State) -> State:
        raise NotImplementedError()


class FilterCategory(Primitive):
    def __init__(self, target_cat: str):
        super().__init__(f"FILTER_CAT_{target_cat}")
        self.target_cat = target_cat

    def apply(self, s: State) -> State:
        new_s = s.clone()
        new_s.data = [r for r in new_s.data if r.get('cat') == self.target_cat]
        new_s.history.append(self.name)
        return new_s


class FilterValueMin(Primitive):
    def __init__(self, min_val: int):
        super().__init__(f"FILTER_VAL_MIN_{min_val}")
        self.min_val = min_val

    def apply(self, s: State) -> State:
        new_s = s.clone()
        new_s.data = [r for r in new_s.data if r.get('val', 0) >= self.min_val]
        new_s.history.append(self.name)
        return new_s


class SortByValue(Primitive):
    def __init__(self, ascending: bool = True):
        super().__init__(f"SORT_BY_VAL_{'ASC' if ascending else 'DESC'}")
        self.ascending = ascending

    def apply(self, s: State) -> State:
        new_s = s.clone()
        new_s.data = sorted(new_s.data, key=lambda r: r.get('val', 0), reverse=not self.ascending)
        new_s.history.append(self.name)
        return new_s


class ApplyScale(Primitive):
    def __init__(self, factor: int):
        super().__init__(f"SCALE_VAL_{factor}")
        self.factor = factor

    def apply(self, s: State) -> State:
        new_s = s.clone()
        for r in new_s.data:
            r['val'] = r.get('val', 0) * self.factor
        new_s.history.append(self.name)
        return new_s


class DeduplicateById(Primitive):
    def __init__(self):
        super().__init__("DEDUPLICATE_ID")

    def apply(self, s: State) -> State:
        new_s = s.clone()
        seen = set()
        unique = []
        for r in new_s.data:
            rid = r.get('id')
            if rid not in seen:
                seen.add(rid)
                unique.append(r)
        new_s.data = unique
        new_s.history.append(self.name)
        return new_s


class EpistemicProbeSchema(Primitive):
    """Epistemic action: inspects data encoding and updates internal working memory."""
    def __init__(self):
        super().__init__("EPISTEMIC_PROBE_METADATA")

    def apply(self, s: State) -> State:
        new_s = s.clone()
        hidden_encoding = any(r.get('encoded', False) for r in new_s.data)
        new_s.working['hidden_encoding_detected'] = hidden_encoding
        new_s.working['probed'] = True
        new_s.history.append(self.name)
        return new_s


class DecryptTransform(Primitive):
    def __init__(self):
        super().__init__("DECRYPT_ENCODED")

    def can_apply(self, s: State) -> bool:
        return s.working.get('probed', False) and not s.faulted

    def apply(self, s: State) -> State:
        new_s = s.clone()
        if not s.working.get('hidden_encoding_detected', False):
            new_s.faulted = True
            new_s.history.append(self.name + "_FAILED")
            return new_s
        for r in new_s.data:
            if r.get('encoded', False):
                r['val'] = r.get('val', 0) // 2
                r['encoded'] = False
        new_s.working['decrypted'] = True
        new_s.history.append(self.name)
        return new_s


class DestructiveClear(Primitive):
    """Distractor that wipes the dataset."""
    def __init__(self):
        super().__init__("DESTRUCTIVE_CLEAR")

    def apply(self, s: State) -> State:
        new_s = s.clone()
        new_s.data = []
        new_s.history.append(self.name)
        return new_s


class GreedyTrapShortcut(Primitive):
    """A trap operator: seems to fix values locally, but corrupts structural invariants."""
    def __init__(self):
        super().__init__("GREEDY_TRAP_SHORTCUT")

    def apply(self, s: State) -> State:
        new_s = s.clone()
        new_s.working['corrupted_ids'] = True
        for r in new_s.data:
            r['val'] = 999
        new_s.history.append(self.name)
        return new_s


class FaultySort(Primitive):
    """Simulates an operator that crashes intermittently."""
    def __init__(self, failure_rate: float = 0.6):
        super().__init__("FAULTY_SORT")
        self.failure_rate = failure_rate

    def apply(self, s: State) -> State:
        new_s = s.clone()
        if random.random() < self.failure_rate:
            new_s.faulted = True
            new_s.history.append(self.name + "_CRASH")
        else:
            new_s.data = sorted(new_s.data, key=lambda r: r.get('val', 0))
            new_s.history.append(self.name)
        return new_s


# ---------------------------------------------------------------------------
# 3. Goal & Discrepancy Metrics
# ---------------------------------------------------------------------------

class Goal:
    def __init__(self, target_predicate, description: str, target_len: Optional[int] = None, target_cats: Optional[Set[str]] = None, target_sorted: bool = False):
        self.target_predicate = target_predicate
        self.description = description
        self.target_len = target_len
        self.target_cats = target_cats
        self.target_sorted = target_sorted

    def is_satisfied(self, s: State) -> bool:
        if s.faulted or s.working.get('corrupted_ids', False):
            return False
        return self.target_predicate(s)

    def naive_discrepancy(self, s: State) -> float:
        """Naive discrepancy metric: penalizes size and inversions, vulnerable to empty-set hacking."""
        if s.faulted:
            return 9999.0
        if self.is_satisfied(s):
            return 0.0
        p = 10.0 + len(s.data) * 0.1
        vals = [r.get('val', 0) for r in s.data]
        inversions = sum(1 for i in range(len(vals)) for j in range(i+1, len(vals)) if vals[i] > vals[j])
        p += inversions * 0.5
        if any(r.get('encoded', False) for r in s.data):
            p += 15.0
        if s.working.get('corrupted_ids', False):
            p += 500.0
        return p

    def calibrated_discrepancy(self, s: State) -> float:
        """Calibrated discrepancy: explicitly penalizes difference from target row count and unmet predicates."""
        if s.faulted:
            return 9999.0
        if self.is_satisfied(s):
            return 0.0
        d = 0.0
        # Target length penalty
        if self.target_len is not None:
            d += abs(len(s.data) - self.target_len) * 5.0
            if len(s.data) == 0 and self.target_len > 0:
                d += 50.0  # Massive penalty for wiping data
        # Target category penalty
        if self.target_cats is not None:
            wrong_cats = sum(1 for r in s.data if r.get('cat') not in self.target_cats)
            d += wrong_cats * 15.0
        # Sorting penalty
        if self.target_sorted and len(s.data) > 1:
            vals = [r.get('val', 0) for r in s.data]
            inversions = sum(1 for i in range(len(vals)) for j in range(i+1, len(vals)) if vals[i] > vals[j])
            d += inversions * 2.0
        # Encoding penalty
        encoded_count = sum(1 for r in s.data if r.get('encoded', False))
        d += encoded_count * 10.0
        # Invariant corruption penalty
        if s.working.get('corrupted_ids', False):
            d += 500.0
        # Epistemic probe incentive if encoded data exists
        if encoded_count > 0 and not s.working.get('probed', False):
            d += 8.0
        return d + 1.0


# ---------------------------------------------------------------------------
# 4. Task Generator
# ---------------------------------------------------------------------------

class Task:
    def __init__(self, family: str, name: str, initial_state: State, goal: Goal, available_primitives: List[Primitive], optimal_length: int):
        self.family = family
        self.name = name
        self.initial_state = initial_state
        self.goal = goal
        self.available_primitives = available_primitives
        self.optimal_length = optimal_length


def create_all_tasks() -> List[Task]:
    tasks = []

    # Standard raw records
    raw_records = [
        {'id': 1, 'cat': 'A', 'val': 12},
        {'id': 2, 'cat': 'B', 'val': 5},
        {'id': 1, 'cat': 'A', 'val': 12},  # duplicate
        {'id': 3, 'cat': 'A', 'val': 25},
        {'id': 4, 'cat': 'B', 'val': 18},
        {'id': 5, 'cat': 'A', 'val': 8},
        {'id': 6, 'cat': 'B', 'val': 30},
    ]

    base_prims = [
        DeduplicateById(),
        FilterCategory('A'),
        FilterCategory('B'),
        FilterValueMin(10),
        SortByValue(ascending=True),
        SortByValue(ascending=False),
        ApplyScale(2),
        DestructiveClear()
    ]

    # Task 1: Deterministic Chaining (Dedupe -> Filter A -> Sort ASC)
    def f1_p(s: State) -> bool:
        return [r['id'] for r in s.data] == [5, 1, 3] and [r['val'] for r in s.data] == [8, 12, 25]
    g1 = Goal(f1_p, "Dedupe, filter A, sort asc", target_len=3, target_cats={'A'}, target_sorted=True)
    tasks.append(Task("F1_Deterministic", "T1_Dedupe_Filter_Sort", State(raw_records), g1, base_prims, optimal_length=3))

    # Task 2: Compositional Generalization (Scale -> Filter Min 20 -> Sort DESC -> Dedupe)
    def f2_p(s: State) -> bool:
        return len(s.data) == 4 and [r['val'] for r in s.data] == [60, 50, 36, 24]
    g2 = Goal(f2_p, "Scale x2, filter val >= 20, sort desc, dedupe", target_len=4, target_sorted=True)
    f2_prims = [ApplyScale(2), FilterValueMin(20), SortByValue(ascending=False), DeduplicateById(), DestructiveClear()]
    tasks.append(Task("F2_Compositional", "T2_Novel_4Step_Sequence", State(raw_records), g2, f2_prims, optimal_length=4))

    # Task 3: Fault Injection (Unsorted records; Sort operator is faulty; Robust SortByValue is fallback)
    raw_unsorted_b = [
        {'id': 10, 'cat': 'B', 'val': 50},
        {'id': 11, 'cat': 'B', 'val': 15},
        {'id': 12, 'cat': 'B', 'val': 35},
    ]
    def f3_p(s: State) -> bool:
        vals = [r['val'] for r in s.data]
        return vals == [15, 35, 50] and not s.faulted
    g3 = Goal(f3_p, "Sort B records under faulty primary operator", target_len=3, target_cats={'B'}, target_sorted=True)
    f3_prims = [FaultySort(failure_rate=0.7), SortByValue(ascending=True), DestructiveClear()]
    tasks.append(Task("F3_FaultInjection", "T3_Fault_Fallback_Sort", State(raw_unsorted_b), g3, f3_prims, optimal_length=1))

    # Task 4: Dead Ends / Greedy Trap (A tempting shortcut exists that sets val=999, but ruins invariant)
    def f4_p(s: State) -> bool:
        return len(s.data) == 2 and [r['val'] for r in s.data] == [12, 25] and not s.working.get('corrupted_ids', False)
    g4 = Goal(f4_p, "Dedupe, filter A, filter min 10 avoiding shortcut", target_len=2, target_cats={'A'})
    f4_prims = [GreedyTrapShortcut(), DeduplicateById(), FilterCategory('A'), FilterValueMin(10), DestructiveClear()]
    tasks.append(Task("F4_DeadEnds", "T4_Avoid_Greedy_Trap", State(raw_records), g4, f4_prims, optimal_length=3))

    # Task 5: Partial Observability (Requires Epistemic Probe before Decrypt can execute)
    encoded_recs = [
        {'id': 1, 'cat': 'A', 'val': 40, 'encoded': True},
        {'id': 2, 'cat': 'A', 'val': 24, 'encoded': True},
        {'id': 3, 'cat': 'B', 'val': 10, 'encoded': False},
    ]
    def f5_p(s: State) -> bool:
        if any(r.get('encoded', False) for r in s.data):
            return False
        return len(s.data) == 2 and [r['val'] for r in s.data] == [12, 20] and all(r['cat'] == 'A' for r in s.data)
    g5 = Goal(f5_p, "Probe, decrypt, filter A, sort asc", target_len=2, target_cats={'A'}, target_sorted=True)
    f5_prims = [EpistemicProbeSchema(), DecryptTransform(), FilterCategory('A'), SortByValue(ascending=True), DestructiveClear()]
    tasks.append(Task("F5_PartialObservability", "T5_Epistemic_Probe_Decrypt", State(encoded_recs), g5, f5_prims, optimal_length=4))

    # Task 6: Ambiguous Objective (Either Cat A or Cat B is valid)
    def f6_p(s: State) -> bool:
        if len(s.data) != 2:
            return False
        vals = [r['val'] for r in s.data]
        cats = [r['cat'] for r in s.data]
        return (all(c == 'A' for c in cats) or all(c == 'B' for c in cats)) and vals == sorted(vals)
    g6 = Goal(f6_p, "Filter either category, ensure length=2 and sorted", target_len=2, target_sorted=True)
    f6_prims = [DeduplicateById(), FilterCategory('A'), FilterCategory('B'), FilterValueMin(15), SortByValue(ascending=True)]
    tasks.append(Task("F6_AmbiguousObjective", "T6_Multi_Path_Satisfaction", State(raw_records), g6, f6_prims, optimal_length=2))

    return tasks


# ---------------------------------------------------------------------------
# 5. Algorithmic Baselines
# ---------------------------------------------------------------------------

class ExecutionResult:
    def __init__(self, success: bool, steps: int, transitions: int, time_ms: float, recovered: bool = False, trapped: bool = False):
        self.success = success
        self.steps = steps
        self.transitions = transitions
        self.time_ms = time_ms
        self.recovered = recovered
        self.trapped = trapped


def run_static_plan(task: Task, use_calibrated: bool = True) -> ExecutionResult:
    t0 = time.perf_counter()
    s_sim = task.initial_state.clone()
    transitions = 0
    plan = []

    # Upfront open-loop plan formation
    for _ in range(task.optimal_length):
        best_p = None
        best_d = float('inf')
        for p in task.available_primitives:
            transitions += 1
            if p.can_apply(s_sim):
                s_next = p.apply(s_sim)
                d = task.goal.calibrated_discrepancy(s_next) if use_calibrated else task.goal.naive_discrepancy(s_next)
                if d < best_d:
                    best_d = d
                    best_p = p
        if best_p:
            plan.append(best_p)
            s_sim = best_p.apply(s_sim)
            if task.goal.is_satisfied(s_sim):
                break

    # Open-loop execution (no monitoring/recovery)
    s_exec = task.initial_state.clone()
    steps = 0
    for p in plan:
        steps += 1
        if p.can_apply(s_exec):
            s_exec = p.apply(s_exec)
            if s_exec.faulted:
                break
        else:
            break

    success = task.goal.is_satisfied(s_exec)
    elapsed = (time.perf_counter() - t0) * 1000
    return ExecutionResult(success, steps, transitions, elapsed)


def run_greedy(task: Task, use_calibrated: bool = True, max_steps: int = 8) -> ExecutionResult:
    t0 = time.perf_counter()
    s = task.initial_state.clone()
    transitions = 0
    steps = 0
    trapped = False

    while steps < max_steps and not task.goal.is_satisfied(s):
        steps += 1
        best_p = None
        best_next_s = None
        best_d = float('inf')
        current_d = task.goal.calibrated_discrepancy(s) if use_calibrated else task.goal.naive_discrepancy(s)

        for p in task.available_primitives:
            transitions += 1
            if p.can_apply(s):
                s_cand = p.apply(s)
                d = task.goal.calibrated_discrepancy(s_cand) if use_calibrated else task.goal.naive_discrepancy(s_cand)
                if d < best_d:
                    best_d = d
                    best_p = p
                    best_next_s = s_cand

        if best_next_s is None or best_d >= current_d and not task.goal.is_satisfied(best_next_s):
            # Local minimum
            trapped = True
            break
        s = best_next_s

    success = task.goal.is_satisfied(s)
    elapsed = (time.perf_counter() - t0) * 1000
    return ExecutionResult(success, steps, transitions, elapsed, trapped=trapped)


def run_tree_search(task: Task, use_calibrated: bool = True, max_depth: int = 5) -> ExecutionResult:
    t0 = time.perf_counter()
    transitions = 0
    init_d = task.goal.calibrated_discrepancy(task.initial_state) if use_calibrated else task.goal.naive_discrepancy(task.initial_state)
    frontier = [(init_d, 0, task.initial_state.clone(), [])]
    visited = set()
    found_plan = None

    while frontier and len(visited) < 400:
        frontier.sort(key=lambda x: x[0])  # Best-first on discrepancy
        cost, depth, s, plan = frontier.pop(0)

        sig = s.signature()
        if sig in visited:
            continue
        visited.add(sig)

        if task.goal.is_satisfied(s):
            found_plan = plan
            break

        if depth >= max_depth:
            continue

        for p in task.available_primitives:
            transitions += 1
            if p.can_apply(s):
                s_next = p.apply(s)
                if not s_next.faulted:
                    d = task.goal.calibrated_discrepancy(s_next) if use_calibrated else task.goal.naive_discrepancy(s_next)
                    frontier.append((d + depth, depth + 1, s_next, plan + [p]))

    # Execute found plan
    s_exec = task.initial_state.clone()
    steps = 0
    if found_plan:
        for p in found_plan:
            steps += 1
            if p.can_apply(s_exec):
                s_exec = p.apply(s_exec)
                if s_exec.faulted:
                    break
            else:
                break

    success = task.goal.is_satisfied(s_exec)
    elapsed = (time.perf_counter() - t0) * 1000
    return ExecutionResult(success, steps, transitions, elapsed)


def run_cdr_rollback(task: Task, use_calibrated: bool = True, max_cycles: int = 60) -> ExecutionResult:
    t0 = time.perf_counter()
    transitions = 0
    steps = 0
    recovered = False

    # Stack: (checkpoint_state, set_of_tried_primitive_names)
    stack: List[Tuple[State, Set[str]]] = [(task.initial_state.clone(), set())]
    max_depth = task.optimal_length + 2
    current_state = task.initial_state.clone()

    while steps < max_cycles and stack:
        steps += 1
        curr_s, tried = stack[-1]

        if task.goal.is_satisfied(curr_s):
            current_state = curr_s
            break

        if len(stack) > max_depth:
            # Depth limit reached without satisfaction -> Rollback
            stack.pop()
            recovered = True
            continue

        # Rank all untried operators from current checkpoint by 1-step simulated discrepancy
        candidates = []
        for p in task.available_primitives:
            if p.name in tried:
                continue
            transitions += 1
            if p.can_apply(curr_s):
                s_sim = p.apply(curr_s)
                d = task.goal.calibrated_discrepancy(s_sim) if use_calibrated else task.goal.naive_discrepancy(s_sim)
                candidates.append((d, p))

        if not candidates:
            # All actions exhausted at this checkpoint -> Backtrack
            stack.pop()
            recovered = True
            continue

        candidates.sort(key=lambda x: x[0])
        best_d, best_p = candidates[0]
        stack[-1][1].add(best_p.name)

        # Execute candidate on state
        s_next = best_p.apply(curr_s)

        # Assertion / Invariant check
        d_next = task.goal.calibrated_discrepancy(s_next) if use_calibrated else task.goal.naive_discrepancy(s_next)
        if s_next.faulted or d_next >= 9000.0:
            # Runtime fault or hard invariant failure -> Rollback immediately
            recovered = True
        else:
            # Transition valid -> Push new checkpoint
            stack.append((s_next.clone(), set()))
            current_state = s_next

    success = task.goal.is_satisfied(current_state)
    elapsed = (time.perf_counter() - t0) * 1000
    return ExecutionResult(success, steps, transitions, elapsed, recovered=recovered)



def run_learned_policy(task: Task, max_steps: int = 8) -> ExecutionResult:
    """Simulates a nearest-neighbor supervised policy mapping state features to action."""
    t0 = time.perf_counter()
    s = task.initial_state.clone()
    transitions = 0
    steps = 0
    prim_map = {p.name: p for p in task.available_primitives}

    while steps < max_steps and not task.goal.is_satisfied(s):
        steps += 1
        transitions += 1
        has_dupes = len(s.data) != len(set(r.get('id') for r in s.data))
        has_encoded = any(r.get('encoded', False) for r in s.data)
        cats = set(r.get('cat') for r in s.data)
        vals = [r.get('val') for r in s.data]
        is_sorted = vals == sorted(vals)

        act = None
        if has_encoded and 'EPISTEMIC_PROBE_METADATA' in prim_map and not s.working.get('probed'):
            act = 'EPISTEMIC_PROBE_METADATA'
        elif s.working.get('hidden_encoding_detected') and 'DECRYPT_ENCODED' in prim_map and not s.working.get('decrypted'):
            act = 'DECRYPT_ENCODED'
        elif has_dupes and 'DEDUPLICATE_ID' in prim_map:
            act = 'DEDUPLICATE_ID'
        elif 'B' in cats and 'cat A' in task.goal.description and 'FILTER_CAT_A' in prim_map:
            act = 'FILTER_CAT_A'
        elif 'A' in cats and 'cat B' in task.goal.description and 'FILTER_CAT_B' in prim_map:
            act = 'FILTER_CAT_B'
        elif not is_sorted and 'SORT_BY_VAL_ASC' in prim_map:
            act = 'SORT_BY_VAL_ASC'
        elif not is_sorted and 'SORT_BY_VAL_DESC' in prim_map and 'desc' in task.goal.description:
            act = 'SORT_BY_VAL_DESC'
        elif 'min 10' in task.goal.description and 'FILTER_VAL_MIN_10' in prim_map:
            act = 'FILTER_VAL_MIN_10'
        elif 'min 20' in task.goal.description and 'FILTER_VAL_MIN_20' in prim_map:
            act = 'FILTER_VAL_MIN_20'
        elif 'Scale' in task.goal.description and 'SCALE_VAL_2' in prim_map:
            act = 'SCALE_VAL_2'

        if act and act in prim_map and prim_map[act].can_apply(s):
            s = prim_map[act].apply(s)
            if s.faulted:
                break
        else:
            break

    success = task.goal.is_satisfied(s)
    elapsed = (time.perf_counter() - t0) * 1000
    return ExecutionResult(success, steps, transitions, elapsed)


# ---------------------------------------------------------------------------
# 6. Main Evaluation Runner
# ---------------------------------------------------------------------------

def run_evaluation() -> Dict[str, Any]:
    tasks = create_all_tasks()
    num_seeds = 10

    # Experiment 1: Naive Discrepancy (Testing vulnerability to reward hacking and blind spots)
    exp1_results = {}
    for task in tasks:
        exp1_results[task.name] = {}
        for b_name, runner in [("StaticPlan", run_static_plan), ("Greedy", run_greedy), ("TreeSearch", run_tree_search), ("CDR_Rollback", run_cdr_rollback)]:
            succ_count = 0
            for seed in range(num_seeds):
                random.seed(SEED + seed * 10)
                res = runner(task, use_calibrated=False)
                if res.success:
                    succ_count += 1
            exp1_results[task.name][b_name] = round(succ_count / num_seeds, 2)

    # Experiment 2: Calibrated Discrepancy & Robustness Across Baselines
    exp2_results = {}
    for task in tasks:
        exp2_results[task.name] = {}
        for b_name, runner in [
            ("StaticPlan", lambda t: run_static_plan(t, True)),
            ("Greedy", lambda t: run_greedy(t, True)),
            ("TreeSearch", lambda t: run_tree_search(t, True)),
            ("CDR_Rollback", lambda t: run_cdr_rollback(t, True)),
            ("LearnedPolicy", lambda t: run_learned_policy(t))
        ]:
            succ_count = 0
            rec_count = 0
            transitions = []
            steps = []
            for seed in range(num_seeds):
                random.seed(SEED + seed * 10)
                res = runner(task)
                if res.success:
                    succ_count += 1
                if res.recovered:
                    rec_count += 1
                transitions.append(res.transitions)
                steps.append(res.steps)
            exp2_results[task.name][b_name] = {
                "success_rate": round(succ_count / num_seeds, 2),
                "recovery_rate": round(rec_count / num_seeds, 2),
                "avg_transitions": round(sum(transitions) / num_seeds, 1),
                "avg_steps": round(sum(steps) / num_seeds, 1)
            }

    # Experiment 3: Scaling with Compositional Depth (Chain lengths 2, 3, 4, 5)
    # Testing search transition explosion
    depth_results = {}
    depth_tasks = [
        ("Depth_2", 2, [FilterCategory('A'), SortByValue(ascending=True)]),
        ("Depth_3", 3, [DeduplicateById(), FilterCategory('A'), SortByValue(ascending=True)]),
        ("Depth_4", 4, [ApplyScale(2), FilterValueMin(20), SortByValue(ascending=False), DeduplicateById()]),
    ]
    for d_name, opt_len, prims in depth_tasks:
        d_task = Task("DepthScaling", d_name, tasks[0].initial_state, tasks[0].goal, prims + [DestructiveClear()], opt_len)
        depth_results[d_name] = {
            "Greedy_transitions": run_greedy(d_task, True).transitions,
            "TreeSearch_transitions": run_tree_search(d_task, True).transitions,
            "CDR_transitions": run_cdr_rollback(d_task, True).transitions
        }

    output = {
        "exp1_naive_discrepancy_success": exp1_results,
        "exp2_calibrated_discrepancy_benchmark": exp2_results,
        "exp3_depth_scaling": depth_results
    }
    return output


if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING EXP-CCS-0: RIGOROUS EMPIRICAL EVALUATION")
    print("=" * 80)
    data = run_evaluation()
    print(json.dumps(data, indent=2))
    with open("exp_ccs0_rigorous_results.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nBenchmark successfully saved to exp_ccs0_rigorous_results.json")
