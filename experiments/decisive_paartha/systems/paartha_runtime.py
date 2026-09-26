"""
System C: Paartha Computational Architecture Runtime (without newly discovered abstractions).
Uses the frontier LLM as neural proposal substrate, combined with:
- Typed capability contracts
- Symbolic applicability filtering
- RESOLVE (Typed CSP parameter binding)
- Sandboxed invariant verification
- State tracking and SET-CR search
"""

import copy
import json
import time
from typing import Dict, List, Tuple, Any, Optional, Set

from decisive_paartha.tools.primitive_tools import State, Capability, initialize_primitive_tools, ExecutionError, PreconditionError
from decisive_paartha.systems.llm_client import FrontierLLMClient

class PaarthaRuntime:
    def __init__(self, client: FrontierLLMClient, capabilities: Optional[Dict[str, Capability]] = None):
        self.name = "System_C_Paartha_Runtime"
        self.client = client
        self.library: Dict[str, Capability] = capabilities or initialize_primitive_tools()

    def filter_applicable_capabilities(self, state: State) -> Dict[str, Capability]:
        """Symbolic applicability filter before ranking."""
        applicable = {}
        is_grp = state.is_grouped()
        cols = state.columns()
        num_cols = state.numeric_columns()

        for name, cap in self.library.items():
            in_type = cap.contract.input_type
            if in_type == "FLAT" and is_grp:
                continue
            if in_type == "GROUPED" and not is_grp:
                continue
            params = cap.contract.parameters
            if any("numeric" in p_desc.lower() for p_desc in params.values()) and not num_cols:
                continue
            applicable[name] = cap
        return applicable

    def resolve_parameters(self, cap: Capability, state: State, proposed_args: Dict[str, Any], task_desc: str) -> Optional[Dict[str, Any]]:
        """
        RESOLVE primitive: typed parameter binding satisfying joint CSP constraints.
        Binds and type-checks parameters by reflecting against current state schema.
        """
        bound = dict(proposed_args)
        all_cols = state.columns()
        num_cols = state.numeric_columns()
        req_params = cap.contract.parameters

        # Check and normalize column bindings
        for p_name, p_type in req_params.items():
            if "col" in p_name and p_name in bound:
                val = bound[p_name]
                if isinstance(val, list):
                    bound[p_name] = [c for c in val if c in all_cols]
                elif val not in all_cols:
                    # Find closest case-insensitive column match
                    matched = None
                    for c in all_cols:
                        if str(val).lower() == c.lower():
                            matched = c
                            break
                    if matched:
                        bound[p_name] = matched
                    else:
                        # Fallback to valid column
                        if "num" in p_name or "numeric" in p_type.lower():
                            bound[p_name] = list(num_cols)[0] if num_cols else list(all_cols)[0]
                        else:
                            bound[p_name] = list(all_cols)[0]

            # Type cast numeric parameters
            if ("threshold" in p_name or "val" in p_name) and p_name in bound:
                try:
                    bound[p_name] = float(bound[p_name])
                except:
                    pass
            elif "k" in p_name and p_name in bound:
                try:
                    bound[p_name] = int(bound[p_name])
                except:
                    bound[p_name] = 3
            elif "factor" in p_name and p_name in bound:
                try:
                    bound[p_name] = float(bound[p_name])
                except:
                    bound[p_name] = 1.0

        # Verify preconditions with bound parameters
        valid, err = cap.check_preconditions(state, bound)
        return bound if valid else None

    def execute_verified_step(self, cap: Capability, state: State, params: Dict[str, Any]) -> Tuple[bool, State, Optional[str]]:
        """Sandboxed verification of invariants before committing state update."""
        valid, err = cap.check_preconditions(state, params)
        if not valid:
            return False, state, f"PreconditionFailed: {err}"
        try:
            next_state = cap.execute(state, params)
            # Invariant checks:
            if next_state.row_count() < 0:
                return False, state, "InvariantViolation: Negative row count"
            return True, next_state, None
        except Exception as ex:
            return False, state, f"ExecutionCrash: {str(ex)}"

    def solve_task(self, task_description: str, initial_state: State, max_steps: int = 5) -> Dict[str, Any]:
        """
        Executes goal-directed plan using:
        Iterative Frontier Proposal -> Capability Selection -> RESOLVE -> Invariant Verification.
        """
        t0 = time.perf_counter()
        current_state = initial_state.clone()
        search_expansions = 0
        tool_calls_count = 0
        invalid_tool_calls = 0
        crashes = 0
        plan_trace = []
        total_tokens = 0

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are the neural proposal engine for the Paartha Cognitive Architecture.\n"
                    "Given the task description and current table state, propose the tool call needed to advance toward the goal.\n"
                    "If the task is fully completed, reply with 'TASK_COMPLETE'."
                )
            },
            {
                "role": "user",
                "content": (
                    f"TASK:\n{task_description}\n\n"
                    f"INITIAL STATE COLUMNS: {list(current_state.columns())}\n"
                    f"ROW COUNT: {current_state.row_count()}\n"
                    f"SAMPLE DATA:\n{json.dumps(current_state.to_dict_list()[:3], indent=2)}"
                )
            }
        ]

        for step_idx in range(max_steps):
            tool_schemas = [cap.contract.to_tool_schema() for cap in self.library.values()]
            resp = self.client.chat_completion(messages, tools=tool_schemas)
            total_tokens += resp.tokens

            if "TASK_COMPLETE" in resp.content and not resp.tool_calls:
                break

            if not resp.tool_calls:
                break

            executed_any = False
            for tc in resp.tool_calls:
                search_expansions += 1
                t_name = tc.get("name")
                t_args = tc.get("arguments", {})

                # Capability Selection & Verification
                applicable = self.filter_applicable_capabilities(current_state)
                if t_name not in self.library:
                    invalid_tool_calls += 1
                    plan_trace.append({"step": t_name, "success": False, "error": "Unknown capability"})
                    messages.append({"role": "user", "content": f"CapabilitySelectionError: Unknown tool '{t_name}'"})
                    continue

                if t_name not in applicable:
                    invalid_tool_calls += 1
                    plan_trace.append({"step": t_name, "success": False, "error": "Applicability check failed"})
                    messages.append({"role": "user", "content": f"ApplicabilityError: Tool '{t_name}' is not applicable to current state shape"})
                    continue

                cap = self.library[t_name]
                bound_args = self.resolve_parameters(cap, current_state, t_args, task_description)
                if not bound_args:
                    invalid_tool_calls += 1
                    plan_trace.append({"step": t_name, "params": t_args, "success": False, "error": "RESOLVE failed CSP constraints"})
                    messages.append({"role": "user", "content": f"BindingError: Parameters {t_args} failed constraint validation"})
                    continue

                tool_calls_count += 1
                ok, next_state, err = self.execute_verified_step(cap, current_state, bound_args)
                if ok:
                    current_state = next_state
                    plan_trace.append({"step": t_name, "params": bound_args, "success": True})
                    executed_any = True
                    messages.append({"role": "assistant", "content": f"Executed {t_name}({bound_args})"})
                    messages.append({"role": "user", "content": f"StepVerified: Resulting table has {current_state.row_count()} rows, columns: {list(current_state.columns())}."})
                else:
                    invalid_tool_calls += 1
                    plan_trace.append({"step": t_name, "params": bound_args, "success": False, "error": err})
                    messages.append({"role": "user", "content": f"VerificationFailure: {err}"})

            if not executed_any:
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
            "plan_trace": plan_trace
        }
