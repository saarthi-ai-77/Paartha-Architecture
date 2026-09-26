"""
System D: Paartha + Experience + Abstraction Discovery.
Extends PaarthaRuntime with:
- Execution trace recording
- Frequent structural motif mining
- Plotkin anti-unification (parameter lifting)
- Minimum Description Length (MDL) compression selection
- Contract synthesis and synthetic verification
- Frozen evaluation on held-out and cross-domain tasks
"""

import copy
import time
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional, Set

from decisive_paartha.tools.primitive_tools import (
    State, Capability, PrimitiveContract, StepAST, ProgramAST,
    ParameterizedAbstraction, initialize_primitive_tools, ExecutionError
)
from decisive_paartha.systems.paartha_runtime import PaarthaRuntime
from decisive_paartha.systems.llm_client import FrontierLLMClient

class CandidateMotif:
    def __init__(self, sequence: Tuple[str, ...], occurrences: List[Tuple[int, int]]):
        self.sequence = sequence
        self.occurrences = occurrences
        self.support = len(set(t_idx for t_idx, _ in occurrences))

    def length(self) -> int:
        return len(self.sequence)


class MotifMiner:
    def __init__(self, min_length: int = 2, max_length: int = 4, min_support: int = 2):
        self.min_length = min_length
        self.max_length = max_length
        self.min_support = min_support

    def mine(self, traces: List[List[Tuple[str, Dict[str, Any]]]]) -> List[CandidateMotif]:
        motif_map: Dict[Tuple[str, ...], List[Tuple[int, int]]] = defaultdict(list)
        for t_idx, trace in enumerate(traces):
            seq = [step[0] for step in trace]
            n = len(seq)
            for length in range(self.min_length, min(self.max_length + 1, n + 1)):
                for start in range(n - length + 1):
                    sub = tuple(seq[start : start + length])
                    motif_map[sub].append((t_idx, start))

        candidates = []
        for seq, occs in motif_map.items():
            distinct = len(set(t_idx for t_idx, _ in occs))
            if distinct >= self.min_support:
                candidates.append(CandidateMotif(seq, occs))
        candidates.sort(key=lambda m: (m.support * m.length(), m.length()), reverse=True)
        return candidates


class AntiUnifier:
    """Plotkin's least-general-generalization algorithm."""
    def anti_unify(
        self,
        motif: CandidateMotif,
        traces: List[List[Tuple[str, Dict[str, Any]]]]
    ) -> Optional[ParameterizedAbstraction]:
        instances: List[List[Tuple[str, Dict[str, Any]]]] = []
        for t_idx, start in motif.occurrences:
            sub = traces[t_idx][start : start + motif.length()]
            instances.append(sub)

        if not instances:
            return None

        template_steps: List[StepAST] = []
        formal_parameters: List[str] = []
        param_mappings: List[Dict[str, str]] = []

        for step_idx in range(motif.length()):
            cap_name = instances[0][step_idx][0]
            param_keys = sorted(list(instances[0][step_idx][1].keys()))

            template_params: Dict[str, Any] = {}
            step_mapping: Dict[str, str] = {}

            for p_key in param_keys:
                all_vals = [inst[step_idx][1].get(p_key) for inst in instances]
                distinct = set(str(v) for v in all_vals)

                if len(distinct) > 1 or p_key in ["col", "num_col", "threshold", "val", "k", "group_col"]:
                    formal_name = f"p_{p_key}_{step_idx}"
                    formal_parameters.append(formal_name)
                    step_mapping[p_key] = formal_name
                    template_params[p_key] = None
                else:
                    template_params[p_key] = all_vals[0]

            template_steps.append(StepAST(cap_name, template_params))
            param_mappings.append(step_mapping)

        # Unify identical variables across steps (e.g. col used in Filter then Sort)
        unified_params = list(formal_parameters)
        for i in range(motif.length()):
            for j in range(i + 1, motif.length()):
                p_i = f"p_col_{i}"
                p_j = f"p_col_{j}"
                if p_i in unified_params and p_j in unified_params:
                    # Check if all instances had identical values for col_i and col_j
                    identical = all(inst[i][1].get("col") == inst[j][1].get("col") for inst in instances)
                    if identical:
                        for m in param_mappings:
                            for k, v in m.items():
                                if v == p_j: m[k] = p_i
                        if p_j in unified_params:
                            unified_params.remove(p_j)

        abs_name = f"ABS_{'_'.join(motif.sequence)}"
        return ParameterizedAbstraction(
            name=abs_name,
            template_steps=template_steps,
            formal_parameters=unified_params,
            param_mapping=param_mappings,
            sub_primitives=list(motif.sequence)
        )


class MDLCompressionEngine:
    """Calculates Description Length reduction of adding an abstraction to the library."""
    def evaluate_gain(
        self,
        abstraction: ParameterizedAbstraction,
        traces: List[List[Tuple[str, Dict[str, Any]]]]
    ) -> int:
        seq = tuple(abstraction.sub_primitives)
        L = len(seq)
        match_count = 0
        total_primitive_bits_saved = 0

        for tr in traces:
            s_seq = [s[0] for s in tr]
            for i in range(len(s_seq) - L + 1):
                if tuple(s_seq[i : i + L]) == seq:
                    match_count += 1
                    step_bits = sum(16 + 8 * len(tr[i + j][1]) for j in range(L))
                    total_primitive_bits_saved += step_bits

        if match_count == 0:
            return -999

        # Call site overhead: 1 call opcode + formal parameter arguments
        call_bits_added = match_count * (16 + 8 * len(abstraction.formal_parameters))
        bits_saved = total_primitive_bits_saved - call_bits_added
        # Complexity cost: storing the abstraction definition in the library
        bits_cost = abstraction.complexity_bits()
        delta_mdl = bits_saved - bits_cost
        return delta_mdl


class PaarthaDiscovery(PaarthaRuntime):
    def __init__(self, client: FrontierLLMClient):
        super().__init__(client)
        self.name = "System_D_Paartha_Discovery"
        self.recorded_traces: List[List[Tuple[str, Dict[str, Any]]]] = []
        self.discovered_abstractions: Dict[str, ParameterizedAbstraction] = {}
        self.is_frozen = False
        self.discovery_metrics = {
            "motifs_mined": 0,
            "abstractions_accepted": 0,
            "abstractions_rejected": 0,
            "total_mdl_gain": 0
        }

    def record_execution_trace(self, trace: List[Tuple[str, Dict[str, Any]]]):
        if not self.is_frozen:
            self.recorded_traces.append(trace)

    def discover_abstractions(self) -> List[ParameterizedAbstraction]:
        """Runs offline discovery pipeline: Mining -> Anti-Unification -> MDL -> Verification."""
        if not self.recorded_traces:
            return []

        miner = MotifMiner(min_length=2, max_length=3, min_support=2)
        motifs = miner.mine(self.recorded_traces)
        self.discovery_metrics["motifs_mined"] = len(motifs)

        anti_unifier = AntiUnifier()
        mdl_engine = MDLCompressionEngine()
        accepted = []

        for motif in motifs:
            candidate = anti_unifier.anti_unify(motif, self.recorded_traces)
            if not candidate:
                continue

            delta_mdl = mdl_engine.evaluate_gain(candidate, self.recorded_traces)
            if delta_mdl > 0:
                # Synthetic verification test with generic schema
                test_state = State([
                    {"num_dim_1": 100.0, "num_dim_2": 20.0, "cat_dim_1": "G1", "str_id": "ID_01"},
                    {"num_dim_1": 50.0, "num_dim_2": 15.0, "cat_dim_1": "G2", "str_id": "ID_02"},
                    {"num_dim_1": 150.0, "num_dim_2": 50.0, "cat_dim_1": "G1", "str_id": "ID_03"}
                ])
                try:
                    # Construct valid test args for probing
                    test_args = {}
                    for p in candidate.formal_parameters:
                        p_lower = p.lower()
                        if "group" in p_lower:
                            test_args[p] = "cat_dim_1"
                        elif "col" in p_lower:
                            test_args[p] = "num_dim_1"
                        elif "thresh" in p_lower or "val" in p_lower:
                            test_args[p] = 75.0
                        elif "k" in p_lower:
                            test_args[p] = 2
                        elif "op" in p_lower:
                            test_args[p] = ">"
                        elif "asc" in p_lower:
                            test_args[p] = False
                        elif "out" in p_lower:
                            test_args[p] = "out_metric"
                        else:
                            test_args[p] = "num_dim_1"

                    candidate.execute(test_state, test_args)
                    # Successfully verified!
                    accepted.append(candidate)
                    self.discovered_abstractions[candidate.name] = candidate
                    self.library[candidate.name] = candidate
                    self.discovery_metrics["abstractions_accepted"] += 1
                    self.discovery_metrics["total_mdl_gain"] += delta_mdl
                except Exception as ex:
                    self.discovery_metrics["abstractions_rejected"] += 1
            else:
                self.discovery_metrics["abstractions_rejected"] += 1

        return accepted

    def freeze(self):
        """Freezes all learning: library is locked."""
        self.is_frozen = True
