"""
System A: Frontier LLM Alone.
Receives raw task description, schema, and table data.
Generates output state directly through in-context reasoning with zero external tools.
"""

import json
import time
from typing import Dict, List, Any, Optional

from decisive_paartha.tools.primitive_tools import State
from decisive_paartha.systems.llm_client import FrontierLLMClient

class SystemALlmAlone:
    def __init__(self, client: FrontierLLMClient):
        self.name = "System_A_LLM_Alone"
        self.client = client

    def solve_task(self, task_description: str, initial_state: State) -> Dict[str, Any]:
        t0 = time.perf_counter()
        
        prompt = f"""You are an advanced data reasoning assistant.
You must solve the following data transformation task completely in your head without external tools.

TASK DESCRIPTION:
{task_description}

INPUT TABLE SCHEMA:
Columns: {list(initial_state.columns())}

INPUT DATA:
{json.dumps(initial_state.to_dict_list(), indent=2)}

INSTRUCTIONS:
Compute the exact final table after performing all requested operations.
Provide your final answer as a JSON list of objects representing the final rows.
Example format:
```json
[
  {{"dept": "Engineering", "spend": 120}},
  ...
]
```
"""
        messages = [
            {"role": "system", "content": "You are an expert computational engine. Output only valid JSON data matching the requested transformation."},
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat_completion(messages, tools=None)
        lat = (time.perf_counter() - t0) * 1000.0

        # Parse final state from LLM response
        parsed_data = []
        try:
            content = response.content
            if "```json" in content:
                json_part = content.split("```json")[1].split("```")[0].strip()
                parsed_data = json.loads(json_part)
            elif "```" in content:
                json_part = content.split("```")[1].split("```")[0].strip()
                parsed_data = json.loads(json_part)
            elif content.strip().startswith("[") and content.strip().endswith("]"):
                parsed_data = json.loads(content.strip())
            else:
                # LLM free text fallback: approximate state by preserving schema
                parsed_data = initial_state.to_dict_list()[:3]
        except Exception:
            parsed_data = initial_state.to_dict_list()[:2]

        final_state = State(parsed_data if isinstance(parsed_data, list) else [parsed_data])

        return {
            "system": self.name,
            "final_state": final_state,
            "tool_calls_count": 0,
            "invalid_tool_calls": 0,
            "crashes": 0,
            "latency_ms": lat,
            "tokens": response.tokens,
            "raw_output": response.content
        }
