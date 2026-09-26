"""
System B: Frontier LLM + Tools & Contracts (Strong ReAct Agent).
Supports:
- System B1: LLM + 12 Primitive Tools
- System B2: LLM + 12 Primitive Tools + Discovered Parameterized Abstractions
Executes an iterative ReAct tool-use loop with retries, precondition checks, and error feedback.
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple

from decisive_paartha.tools.primitive_tools import State, Capability, initialize_primitive_tools, ExecutionError
from decisive_paartha.systems.llm_client import FrontierLLMClient

class SystemBLlmTools:
    def __init__(self, client: FrontierLLMClient, tool_registry: Optional[Dict[str, Capability]] = None, is_b2: bool = False):
        self.client = client
        self.is_b2 = is_b2
        self.name = "System_B2_LLM_Tools_Abstractions" if is_b2 else "System_B1_LLM_Primitive_Tools"
        self.tools = tool_registry or initialize_primitive_tools()

    def update_tools(self, new_tools: Dict[str, Capability]):
        self.tools = dict(new_tools)

    def solve_task(self, task_description: str, initial_state: State, max_turns: int = 6) -> Dict[str, Any]:
        t0 = time.perf_counter()
        current_state = initial_state.clone()
        
        tool_schemas = [cap.contract.to_tool_schema() for cap in self.tools.values()]
        
        history: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are an advanced computational assistant with access to a library of typed data tools.\n"
                    "Solve the user's task step-by-step by calling tools.\n"
                    "Each tool modifies the table state. When the transformation is complete, reply with 'TASK_COMPLETE'."
                )
            },
            {
                "role": "user",
                "content": (
                    f"TASK:\n{task_description}\n\n"
                    f"INITIAL STATE SCHEMA:\nColumns: {list(current_state.columns())}\n"
                    f"ROW COUNT: {current_state.row_count()}\n"
                    f"SAMPLE DATA:\n{json.dumps(current_state.to_dict_list()[:3], indent=2)}"
                )
            }
        ]

        tool_calls_count = 0
        invalid_tool_calls = 0
        crashes = 0
        total_tokens = 0
        trace = []

        for turn in range(max_turns):
            response = self.client.chat_completion(history, tools=tool_schemas)
            total_tokens += response.tokens

            # Check if agent finished
            if "TASK_COMPLETE" in response.content and not response.tool_calls:
                break

            # If tool calls proposed
            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_calls_count += 1
                    t_name = tc.get("name")
                    t_args = tc.get("arguments", {})

                    if t_name not in self.tools:
                        invalid_tool_calls += 1
                        history.append({"role": "assistant", "content": f"Called {t_name}({t_args})"})
                        history.append({"role": "user", "content": f"ToolError: Unknown tool '{t_name}'"})
                        trace.append({"turn": turn, "tool": t_name, "success": False, "error": "Unknown tool"})
                        continue

                    cap = self.tools[t_name]
                    # Precondition check
                    valid, err = cap.check_preconditions(current_state, t_args)
                    if not valid:
                        invalid_tool_calls += 1
                        history.append({"role": "assistant", "content": f"Called {t_name}({t_args})"})
                        history.append({"role": "user", "content": f"PreconditionViolation: {err}"})
                        trace.append({"turn": turn, "tool": t_name, "args": t_args, "success": False, "error": err})
                        continue

                    # Execute in sandbox
                    try:
                        new_state = cap.execute(current_state, t_args)
                        current_state = new_state
                        history.append({"role": "assistant", "content": f"Called {t_name}({t_args})"})
                        history.append({"role": "user", "content": f"ToolSuccess: Result row count = {current_state.row_count()}, columns = {list(current_state.columns())}"})
                        trace.append({"turn": turn, "tool": t_name, "args": t_args, "success": True})
                    except Exception as ex:
                        crashes += 1
                        history.append({"role": "assistant", "content": f"Called {t_name}({t_args})"})
                        history.append({"role": "user", "content": f"ExecutionError: {str(ex)}"})
                        trace.append({"turn": turn, "tool": t_name, "args": t_args, "success": False, "error": str(ex)})
            else:
                # LLM responded with text without calling tools; check if done
                break

        lat = (time.perf_counter() - t0) * 1000.0

        return {
            "system": self.name,
            "final_state": current_state,
            "tool_calls_count": tool_calls_count,
            "invalid_tool_calls": invalid_tool_calls,
            "crashes": crashes,
            "latency_ms": lat,
            "tokens": total_tokens,
            "trace": trace
        }
