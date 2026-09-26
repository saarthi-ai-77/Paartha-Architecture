"""
Failure Attribution Taxonomy for Paartha Decisive Experiment.
Classifies failed task runs into 12 pre-defined bottleneck categories without retrospective bias.
"""

from typing import Dict, Any, Optional

TAXONOMY_CATEGORIES = [
    "REPRESENTATION",
    "UNDERSTANDING",
    "CAPABILITY_SELECTION",
    "PARAMETER_BINDING",
    "EXECUTION",
    "VERIFICATION",
    "SEARCH",
    "ABSTRACTION",
    "MEMORY",
    "GENERATION",
    "MODEL_LIMITATION",
    "TOOL_LIMITATION"
]

def attribute_failure(task_record: Dict[str, Any]) -> str:
    """
    Deterministically attributes failure based on trace and execution signatures.
    """
    if task_record.get("exact_match", False):
        return "SUCCESS"

    crashes = task_record.get("crashes", 0)
    invalid_calls = task_record.get("invalid_tool_calls", 0)
    system = task_record.get("system", "")
    trace = task_record.get("trace", []) or task_record.get("plan_trace", [])

    # Check crash signatures
    if crashes > 0:
        for step in trace:
            err = str(step.get("error", ""))
            if "Precondition" in err:
                return "PARAMETER_BINDING"
            if "Type" in err:
                return "REPRESENTATION"
        return "EXECUTION"

    # Check invalid tool call signatures
    if invalid_calls > 0:
        for step in trace:
            err = str(step.get("error", ""))
            if "Unknown tool" in err or "Missing capability" in err:
                return "CAPABILITY_SELECTION"
            if "Precondition" in err or "Column missing" in err:
                return "PARAMETER_BINDING"
        return "PARAMETER_BINDING"

    # If system is LLM alone and failed exact match
    if "LLM_Alone" in system:
        return "MODEL_LIMITATION"

    # If plan trace failed to find matching capability
    if not trace:
        return "CAPABILITY_SELECTION"

    # Default to semantic understanding or search budget exhaustion
    if len(trace) >= 5:
        return "SEARCH"
    
    return "UNDERSTANDING"
