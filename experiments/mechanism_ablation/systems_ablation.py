"""
Modular System Implementations for Mechanism Ablation (A1 through A9).
Strictly separates:
- Information Advantage (what the model sees)
- Computational Advantage (what the runtime executes: Contracts, RESOLVE, Verification, Search)
"""

import copy
import json
import time
from typing import Dict, List, Tuple, Any, Optional

from decisive_paartha.tools.primitive_tools import (
    State, Capability, initialize_primitive_tools, ExecutionError, PreconditionError
)
from decisive_paartha.systems.llm_client import FrontierLLMClient


class AblationSystemA1_LLMAlone:
    """A1: Frontier LLM Alone (In-Context Single-Shot)."""
    def __init__(self, client: FrontierLLMClient):
        self.name = "A1_LLM_Alone"
        self.client = client

    def solve_task(self, task_description: str, initial_state: State) -> Dict[str, Any]:
        t0 = time.perf_counter()
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert computational assistant.\n"
                    "Transform the input tabular dataset to satisfy the user's task.\n"
                    "Return ONLY valid JSON representing the transformed table as a list of record objects."
                )
            },
            {
                "role": "user",
                "content": (
                    f"TASK:\n{task_description}\n\n"
                    f"INPUT SCHEMA: {list(initial_state.columns())}\n"
                    f"ROW COUNT: {initial_state.row_count()}\n"
                    f"INPUT DATA:\n{json.dumps(initial_state.to_dict_list(), indent=2)}\n\n"
                    "Provide the complete transformed JSON array:"
                )
            }
        ]
        resp = self.client.chat_completion(messages, tools=None)
        lat = (time.perf_counter() - t0) * 1000.0

        # Parse response
        records = []
        try:
            content = resp.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            data = json.loads(content)
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                for k in ["data", "records", "result", "rows"]:
                    if k in data and isinstance(data[k], list):
                        records = data[k]
                        break
        except Exception:
            records = initial_state.to_dict_list()

        return {
            "system": self.name,
            "final_state": State(records),
            "tool_calls_count": 0,
            "invalid_tool_calls": 0,
            "crashes": 0,
            "search_expansions": 0,
            "latency_ms": lat,
            "tokens": resp.tokens,
            "trace": []
        }


class ModularAblationAgent:
    """
    Unified modular execution agent for A2 through A9.
    Configurable flags enable precise causal isolation:
    - use_contracts: enforces precondition checks and schema validity
    - use_resolve: executes CSP parameter normalization against state schema
    - use_verification: executes independent post-execution invariant verification
    - use_search: allows multi-path tree search and checkpoint rollback
    """
    def __init__(
        self,
        name: str,
        client: FrontierLLMClient,
        tools: Optional[Dict[str, Capability]] = None,
        use_contracts: bool = False,
        use_resolve: bool = False,
        use_verification: bool = False,
        use_search: bool = False,
        search_budget: int = 4
    ):
        self.name = name
        self.client = client
        self.tools = tools or initialize_primitive_tools()
        self.use_contracts = use_contracts
        self.use_resolve = use_resolve
        self.use_verification = use_verification
        self.use_search = use_search
        self.search_budget = search_budget

    def resolve_params(self, cap: Capability, state: State, raw_args: Dict[str, Any]) -> Dict[str, Any]:
        """RESOLVE parameter normalization & CSP constraint matching."""
        if not self.use_resolve:
            return dict(raw_args)

        bound = dict(raw_args)
        all_cols = state.columns()
        num_cols = state.numeric_columns()
        req_params = cap.contract.parameters

        for p_name, p_type in req_params.items():
            if "col" in p_name and p_name in bound:
                val = bound[p_name]
                if isinstance(val, list):
                    bound[p_name] = [c for c in val if c in all_cols]
                elif val not in all_cols:
                    # Match case-insensitively
                    matched = None
                    for c in all_cols:
                        if str(val).lower() == c.lower():
                            matched = c
                            break
                    if matched:
                        bound[p_name] = matched
                    else:
                        # Fallback to valid column of matching type
                        if "num" in p_name or "numeric" in p_type.lower():
                            bound[p_name] = list(num_cols)[0] if num_cols else list(all_cols)[0]
                        else:
                            bound[p_name] = list(all_cols)[0]

            # Numeric normalization
            if ("threshold" in p_name or "val" in p_name) and p_name in bound:
                try:
                    bound[p_name] = float(bound[p_name])
                except Exception:
                    pass
            elif "k" in p_name and p_name in bound:
                try:
                    bound[p_name] = int(bound[p_name])
                except Exception:
                    bound[p_name] = 3
            elif "factor" in p_name and p_name in bound:
                try:
                    bound[p_name] = float(bound[p_name])
                except Exception:
                    bound[p_name] = 1.0

        return bound

    def check_step_validity(self, cap: Capability, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Contract precondition enforcement."""
        if not self.use_contracts:
            return True, None
        return cap.check_preconditions(state, params)

    def verify_postconditions(self, prev_state: State, next_state: State) -> Tuple[bool, Optional[str]]:
        """Sandboxed invariant verification."""
        if not self.use_verification:
            return True, None
        if next_state.row_count() < 0:
            return False, "InvariantViolation: Negative row count"
        # Non-empty table invariant for non-extreme filters
        if prev_state.row_count() > 0 and next_state.row_count() == 0:
            return False, "InvariantViolation: Operation produced empty table"
        return True, None

    def solve_task(self, task_description: str, initial_state: State, max_turns: int = 5) -> Dict[str, Any]:
        t0 = time.perf_counter()
        current_state = initial_state.clone()
        tool_schemas = [cap.contract.to_tool_schema() for cap in self.tools.values()]

        tool_calls_count = 0
        invalid_tool_calls = 0
        crashes = 0
        search_expansions = 0
        total_tokens = 0
        trace = []

        history: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are a computational assistant with access to typed data transformation tools.\n"
                    "Solve the task step-by-step by proposing tool calls.\n"
                    "When the transformation is complete, reply with 'TASK_COMPLETE'."
                )
            },
            {
                "role": "user",
                "content": (
                    f"TASK:\n{task_description}\n\n"
                    f"STATE SCHEMA: Columns={list(current_state.columns())}, Rows={current_state.row_count()}\n"
                    f"SAMPLE DATA:\n{json.dumps(current_state.to_dict_list()[:3], indent=2)}"
                )
            }
        ]

        # Stack for SET-CR search / rollback: (state, history, turn, depth)
        state_stack: List[Tuple[State, List[Dict[str, str]], int]] = []

        turn = 0
        while turn < max_turns:
            turn += 1
            resp = self.client.chat_completion(history, tools=tool_schemas)
            total_tokens += resp.tokens

            if "TASK_COMPLETE" in resp.content and not resp.tool_calls:
                break

            if not resp.tool_calls:
                break

            executed_any_in_turn = False
            for tc in resp.tool_calls:
                search_expansions += 1
                t_name = tc.get("name")
                t_args = tc.get("arguments", {})

                if t_name not in self.tools:
                    invalid_tool_calls += 1
                    trace.append({"turn": turn, "tool": t_name, "success": False, "error": "Unknown tool"})
                    history.append({"role": "assistant", "content": f"Called {t_name}({t_args})"})
                    history.append({"role": "user", "content": f"Error: Unknown tool '{t_name}'"})
                    continue

                cap = self.tools[t_name]

                # 1. RESOLVE parameter normalization
                bound_args = self.resolve_params(cap, current_state, t_args)

                # 2. Contract checking
                valid, err = self.check_step_validity(cap, current_state, bound_args)
                if not valid:
                    invalid_tool_calls += 1
                    trace.append({"turn": turn, "tool": t_name, "args": bound_args, "success": False, "error": f"ContractViolation: {err}"})
                    history.append({"role": "assistant", "content": f"Called {t_name}({bound_args})"})
                    history.append({"role": "user", "content": f"ContractViolation: {err}"})

                    # If search/rollback enabled, backtrack if stack has previous checkpoint
                    if self.use_search and state_stack and len(state_stack) > 0:
                        prev_s, prev_h, _ = state_stack.pop()
                        current_state = prev_s.clone()
                        history = list(prev_h)
                    continue

                # 3. Execution in sandbox
                tool_calls_count += 1
                checkpoint_state = current_state.clone()
                checkpoint_history = list(history)

                try:
                    next_s = cap.execute(current_state, bound_args)
                except Exception as ex:
                    crashes += 1
                    invalid_tool_calls += 1
                    trace.append({"turn": turn, "tool": t_name, "args": bound_args, "success": False, "error": f"ExecutionCrash: {str(ex)}"})
                    history.append({"role": "assistant", "content": f"Called {t_name}({bound_args})"})
                    history.append({"role": "user", "content": f"ExecutionError: {str(ex)}"})

                    if self.use_search and state_stack:
                        prev_s, prev_h, _ = state_stack.pop()
                        current_state = prev_s.clone()
                        history = list(prev_h)
                    continue

                # 4. Invariant Verification
                inv_ok, inv_err = self.verify_postconditions(current_state, next_s)
                if not inv_ok:
                    invalid_tool_calls += 1
                    trace.append({"turn": turn, "tool": t_name, "args": bound_args, "success": False, "error": inv_err})
                    history.append({"role": "assistant", "content": f"Called {t_name}({bound_args})"})
                    history.append({"role": "user", "content": f"VerificationFailure: {inv_err}"})

                    if self.use_search and state_stack:
                        prev_s, prev_h, _ = state_stack.pop()
                        current_state = prev_s.clone()
                        history = list(prev_h)
                    continue

                # Successful step commit
                if self.use_search and len(state_stack) < self.search_budget:
                    state_stack.append((checkpoint_state, checkpoint_history, turn))

                current_state = next_s
                executed_any_in_turn = True
                trace.append({"turn": turn, "tool": t_name, "args": bound_args, "success": True})
                history.append({"role": "assistant", "content": f"Executed {t_name}({bound_args})"})
                history.append({"role": "user", "content": f"StepSuccess: Row count = {current_state.row_count()}, Columns = {list(current_state.columns())}"})

            if not executed_any_in_turn:
                if self.use_search and state_stack:
                    prev_s, prev_h, _ = state_stack.pop()
                    current_state = prev_s.clone()
                    history = list(prev_h)
                else:
                    break

        lat = (time.perf_counter() - t0) * 1000.0

        return {
            "system": self.name,
            "final_state": current_state,
            "tool_calls_count": tool_calls_count,
            "invalid_tool_calls": invalid_tool_calls,
            "crashes": crashes,
            "search_expansions": search_expansions,
            "latency_ms": lat,
            "tokens": total_tokens,
            "trace": trace
        }


def create_ablation_system(system_id: str, client: FrontierLLMClient) -> Any:
    """Factory creating cleanly isolated ablation systems A1 through A9."""
    if system_id == "A1":
        return AblationSystemA1_LLMAlone(client)
    elif system_id == "A2":
        # LLM + Primitive Tools (Standard ReAct: no contracts, no resolve, no verification, no search)
        return ModularAblationAgent("A2_LLM_Primitive_Tools", client,
                                    use_contracts=False, use_resolve=False, use_verification=False, use_search=False)
    elif system_id == "A3":
        # LLM + Tools + Contracts
        return ModularAblationAgent("A3_LLM_Tools_Contracts", client,
                                    use_contracts=True, use_resolve=False, use_verification=False, use_search=False)
    elif system_id == "A4":
        # LLM + Tools + RESOLVE
        return ModularAblationAgent("A4_LLM_Tools_RESOLVE", client,
                                    use_contracts=False, use_resolve=True, use_verification=False, use_search=False)
    elif system_id == "A5":
        # LLM + Tools + Verification
        return ModularAblationAgent("A5_LLM_Tools_Verification", client,
                                    use_contracts=False, use_resolve=False, use_verification=True, use_search=False)
    elif system_id == "A6":
        # LLM + Tools + SET-CR (Search & Rollback)
        return ModularAblationAgent("A6_LLM_Tools_SETCR", client,
                                    use_contracts=False, use_resolve=False, use_verification=False, use_search=True, search_budget=4)
    elif system_id == "A7":
        # Contracts + RESOLVE + Verification (No Search)
        return ModularAblationAgent("A7_Contracts_RESOLVE_Verification", client,
                                    use_contracts=True, use_resolve=True, use_verification=True, use_search=False)
    elif system_id == "A8":
        # Contracts + RESOLVE + SET-CR (Minimal Verification)
        return ModularAblationAgent("A8_Contracts_RESOLVE_SETCR", client,
                                    use_contracts=True, use_resolve=True, use_verification=False, use_search=True, search_budget=4)
    elif system_id == "A9":
        # Full Paartha Runtime (Contracts + RESOLVE + Verification + SET-CR)
        return ModularAblationAgent("A9_Full_Paartha_Runtime", client,
                                    use_contracts=True, use_resolve=True, use_verification=True, use_search=True, search_budget=4)
    else:
        raise ValueError(f"Unknown system_id: {system_id}")
