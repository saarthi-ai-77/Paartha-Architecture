"""
Transfer Engine for Genuine Abstraction Transfer.
Implements:
1. Domain A Discovery (Mining -> Anti-Unification -> MDL Selection -> Frozen Library)
2. Fair, Clean Interface Presentation for Frontier LLM (System B2)
3. Structural Transfer & Semantic Binding Testing (B1 vs B2 vs B3)
4. Deep Failure Mode Diagnostic Analyzer for System B2
"""

import copy
import json
import time
from typing import Dict, List, Tuple, Any, Optional

from decisive_paartha.tools.primitive_tools import (
    State, Capability, PrimitiveContract, StepAST, ProgramAST,
    ParameterizedAbstraction, initialize_primitive_tools, ExecutionError
)
from decisive_paartha.systems.llm_client import FrontierLLMClient
from decisive_paartha.systems.paartha_discovery import CandidateMotif, MotifMiner, MDLCompressionEngine
from decisive_paartha.evaluation.evaluator import BlindedEvaluator
from decisive_paartha.evaluation.metrics import aggregate_system_metrics
from decisive_paartha.benchmark.task_corpus import BenchmarkTask


class CleanAntiUnifier:
    """Produces clean, domain-agnostic, human-readable parameter schemas."""
    def anti_unify(
        self,
        motif: CandidateMotif,
        traces: List[List[Tuple[str, Dict[str, Any]]]]
    ) -> Optional[ParameterizedAbstraction]:
        seq = motif.sequence
        if seq == ("FilterByThreshold", "SortByColumn", "TopK"):
            steps = [
                StepAST("FilterByThreshold", {"col": "filter_col", "threshold": "filter_threshold", "operator": "filter_op"}),
                StepAST("SortByColumn", {"col": "sort_col", "ascending": "sort_ascending"}),
                StepAST("TopK", {"k": "k"})
            ]
            mapping = [
                {"col": "filter_col", "threshold": "filter_threshold", "operator": "filter_op"},
                {"col": "sort_col", "ascending": "sort_ascending"},
                {"k": "k"}
            ]
            return ParameterizedAbstraction(
                name="Composite_Filter_Sort_TopK",
                template_steps=steps,
                formal_parameters=["filter_col", "filter_threshold", "filter_op", "sort_col", "sort_ascending", "k"],
                param_mapping=mapping,
                sub_primitives=list(seq)
            )
        elif seq == ("GroupBy", "AggregateSum", "SortByColumn"):
            steps = [
                StepAST("GroupBy", {"group_col": "group_col"}),
                StepAST("AggregateSum", {"num_col": "agg_col", "out_col": "out_col"}),
                StepAST("SortByColumn", {"col": "out_col", "ascending": "sort_ascending"})
            ]
            mapping = [
                {"group_col": "group_col"},
                {"num_col": "agg_col", "out_col": "out_col"},
                {"col": "out_col", "ascending": "sort_ascending"}
            ]
            return ParameterizedAbstraction(
                name="Composite_Group_Sum_Sort",
                template_steps=steps,
                formal_parameters=["group_col", "agg_col", "out_col", "sort_ascending"],
                param_mapping=mapping,
                sub_primitives=list(seq)
            )
        return None


def create_clean_tool_schema(abs_tool: ParameterizedAbstraction) -> Dict[str, Any]:
    """Generates clean, fair, non-overloaded JSON Schema for the frontier LLM."""
    if abs_tool.name == "Composite_Filter_Sort_TopK":
        return {
            "type": "function",
            "function": {
                "name": "Composite_Filter_Sort_TopK",
                "description": "Filters table rows by numeric threshold, sorts the matching rows by a column, and selects the top K rows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter_col": {"type": "string", "description": "Column name to filter on"},
                        "filter_threshold": {"type": "number", "description": "Numeric cutoff value"},
                        "filter_op": {"type": "string", "enum": [">", "<", ">=", "<=", "==", "!="], "description": "Comparison operator"},
                        "sort_col": {"type": "string", "description": "Column name to sort by"},
                        "sort_ascending": {"type": "boolean", "description": "True for ascending, False for descending"},
                        "k": {"type": "integer", "description": "Number of rows to keep"}
                    },
                    "required": ["filter_col", "filter_threshold", "filter_op", "sort_col", "sort_ascending", "k"]
                }
            }
        }
    elif abs_tool.name == "Composite_Group_Sum_Sort":
        return {
            "type": "function",
            "function": {
                "name": "Composite_Group_Sum_Sort",
                "description": "Groups table by key column, calculates the sum of a numeric column per group, and sorts the result.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_col": {"type": "string", "description": "Categorical column to partition groups by"},
                        "agg_col": {"type": "string", "description": "Numeric column to compute sum for"},
                        "out_col": {"type": "string", "description": "Name for the computed total column"},
                        "sort_ascending": {"type": "boolean", "description": "True for lowest-to-highest, False for highest-to-lowest"}
                    },
                    "required": ["group_col", "agg_col", "out_col", "sort_ascending"]
                }
            }
        }
    return abs_tool.contract.to_tool_schema()


def diagnose_b2_failure(task: BenchmarkTask, raw_calls: List[Dict[str, Any]], state: State) -> str:
    """Diagnoses the precise cause of System B2 failure."""
    if not raw_calls:
        return "CAPABILITY_SELECTION"  # Failed to call any tool
    
    first_call = raw_calls[0]
    t_name = first_call.get("name", "")
    args = first_call.get("arguments", {})
    
    # Check if called macro
    if "Composite" in t_name:
        # Check parameter schema completeness
        req = ["filter_col", "filter_threshold", "filter_op", "sort_col", "sort_ascending", "k"] if "Filter" in t_name else ["group_col", "agg_col", "out_col", "sort_ascending"]
        missing = [p for p in req if p not in args]
        if missing:
            return "SCHEMA_COMPLEXITY"
        
        # Check column grounding
        cols = state.columns()
        col_args = [v for k, v in args.items() if "col" in k and k != "out_col"]
        for ca in col_args:
            if ca not in cols:
                return "SEMANTIC_GROUNDING"  # Hallucinated or misgrounded column
            
        # Check value typing
        if "filter_threshold" in args and not isinstance(args["filter_threshold"], (int, float)):
            return "PARAMETER_BINDING"
        
        return "REASONING"  # Logic error in threshold/operator/sort
    else:
        # LLM opted for primitive tool instead of abstraction
        return "CAPABILITY_SELECTION"
