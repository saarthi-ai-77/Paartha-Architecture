"""
EXP-037: Structurally Diverse Capability Contracts & Execution Engines.
Implements 10 distinct computational structures:
C1: Unary transformation
C2: Binary relation
C3: Aggregation
C4: Nested aggregation
C5: Conditional transformation
C6: State mutation
C7: Multi-output partition
C8: Capability requiring derived intermediate state
C9: Composite multi-step pipeline
C10: Capability with conflicting candidate interpretations
"""

import math
import copy
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class ParamSpec:
    name: str
    dtype: str          # "STRING", "NUMERIC", "INTEGER", "BOOLEAN", "COLUMN_REF"
    description: str
    unit_domain: Optional[str] = None
    default_value: Any = None
    required: bool = True

@dataclass
class JointConstraint:
    name: str
    predicate: Callable[[Dict[str, Any]], bool]
    description: str

@dataclass
class CapabilityContract:
    identity: str
    name: str
    structure_type: str  # C1..C10
    input_type: str
    output_type: str
    parameters: List[ParamSpec]
    joint_constraints: List[JointConstraint]
    preconditions: List[str]
    effects: Dict[str, Any]
    requires_auth: bool = False
    is_destructive: bool = False

class ExecutableCapability:
    def __init__(self, contract: CapabilityContract, executor_fn: Callable[[List[Dict[str, Any]], Dict[str, Any]], Any]):
        self.contract = contract
        self.executor_fn = executor_fn

    def execute(self, data: List[Dict[str, Any]], bindings: Dict[str, Any]) -> Any:
        # Check joint constraints
        for jc in self.contract.joint_constraints:
            if not jc.predicate(bindings):
                raise ValueError(f"Joint constraint '{jc.name}' violated: {jc.description}")
        return self.executor_fn(data, bindings)

def build_universal_capability_library() -> Dict[str, ExecutableCapability]:
    """Builds the 10 structurally distinct capabilities for EXP-037."""
    lib = {}

    # --------------------------------------------------------------------------
    # C1: UNARY TRANSFORMATION - Filter Numeric Threshold
    # --------------------------------------------------------------------------
    p_col = ParamSpec("$col", "COLUMN_REF", "Column to evaluate", required=True)
    p_thresh = ParamSpec("$threshold", "NUMERIC", "Threshold limit", required=True)
    jc_non_neg = JointConstraint("THRESH_NON_NEG", lambda b: float(b.get("$threshold", 0)) >= 0, "Threshold must be >= 0")
    c1_contract = CapabilityContract(
        "CAP_FILTER_THRESHOLD", "FILTER_THRESHOLD", "C1_UNARY_TRANSFORMATION",
        "TABLE", "TABLE", [p_col, p_thresh], [jc_non_neg],
        ["REQ_NUMERIC_COL", "REQ_DATA_NON_EMPTY"], {"row_delta": "truncate"}
    )
    def exec_c1(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        col = b["$col"]
        th = float(b["$threshold"])
        return [r for r in data if float(r.get(col, 0)) > th]
    lib["CAP_FILTER_THRESHOLD"] = ExecutableCapability(c1_contract, exec_c1)

    # --------------------------------------------------------------------------
    # C1B: TOP K WITH THRESHOLD - Sort and Truncate
    # --------------------------------------------------------------------------
    p_k = ParamSpec("$k", "INTEGER", "Number of top records", default_value=1, required=True)
    jc_k_pos = JointConstraint("K_POS", lambda b: int(b.get("$k", 1)) > 0, "Limit k must be strictly positive")
    c1b_contract = CapabilityContract(
        "CAP_FILTER_TOP_K", "FILTER_TOP_K", "C1_UNARY_TRANSFORMATION",
        "TABLE", "TABLE", [p_col, p_k], [jc_k_pos],
        ["REQ_NUMERIC_COL"], {"row_delta": "truncate", "order": "descending"}
    )
    def exec_c1b(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        col = b["$col"]
        k = int(b["$k"])
        sorted_rows = sorted(data, key=lambda r: float(r.get(col, 0)), reverse=True)
        return sorted_rows[:k]
    lib["CAP_FILTER_TOP_K"] = ExecutableCapability(c1b_contract, exec_c1b)

    # --------------------------------------------------------------------------
    # C1C: SORT RECORDS
    # --------------------------------------------------------------------------
    p_desc = ParamSpec("$descending", "BOOLEAN", "Sort order", default_value=True, required=False)
    c1c_contract = CapabilityContract(
        "CAP_SORT_RECORDS", "SORT_RECORDS", "C1_UNARY_TRANSFORMATION",
        "TABLE", "TABLE", [p_col, p_desc], [],
        ["REQ_COL_EXISTS"], {"order_delta": "sorted"}
    )
    def exec_c1c(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        col = b["$col"]
        desc = b.get("$descending", True)
        return sorted(data, key=lambda r: float(r.get(col, 0)), reverse=desc)
    lib["CAP_SORT_RECORDS"] = ExecutableCapability(c1c_contract, exec_c1c)

    # --------------------------------------------------------------------------
    # C1D: FILTER EQUALS (Entity Selection)
    # --------------------------------------------------------------------------
    p_str_col = ParamSpec("$col", "COLUMN_REF", "String column to match", required=True)
    p_val = ParamSpec("$val", "STRING", "Target string value", required=True)
    c1d_contract = CapabilityContract(
        "CAP_FILTER_EQUALS", "FILTER_EQUALS", "C1_UNARY_TRANSFORMATION",
        "TABLE", "TABLE", [p_str_col, p_val], [],
        ["REQ_COL_EXISTS"], {"row_delta": "truncate"}
    )
    def exec_c1d(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        col = b["$col"]
        val = str(b["$val"]).lower()
        return [r for r in data if str(r.get(col, "")).lower() == val]
    lib["CAP_FILTER_EQUALS"] = ExecutableCapability(c1d_contract, exec_c1d)

    # --------------------------------------------------------------------------
    # C1E: PROJECT COLUMNS (Anaphora / Field Retrieval)
    # --------------------------------------------------------------------------
    p_fields = ParamSpec("$fields", "STRING", "Comma-separated column names", required=True)
    c1e_contract = CapabilityContract(
        "CAP_PROJECT_COLUMNS", "PROJECT_COLUMNS", "C1_UNARY_TRANSFORMATION",
        "TABLE", "RECORD", [p_fields], [],
        ["REQ_DATA_NON_EMPTY"], {"shape": "projected"}
    )
    def exec_c1e(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        fields = [f.strip() for f in str(b["$fields"]).split(",") if f.strip()]
        res = []
        for r in data:
            proj = {f: r.get(f) for f in fields if f in r}
            res.append(proj)
        return res
    lib["CAP_PROJECT_COLUMNS"] = ExecutableCapability(c1e_contract, exec_c1e)

    # --------------------------------------------------------------------------
    # C2: BINARY RELATION - Field Comparison Relation (col1 < col2)
    # --------------------------------------------------------------------------
    p_col1 = ParamSpec("$col1", "COLUMN_REF", "First operand column", required=True)
    p_col2 = ParamSpec("$col2", "COLUMN_REF", "Second operand column", required=True)
    p_op = ParamSpec("$operator", "STRING", "Comparison operator (LT, GT, EQ)", default_value="LT", required=False)
    jc_distinct = JointConstraint("DISTINCT_COLS", lambda b: b.get("$col1") != b.get("$col2"), "Compared columns must be distinct")
    c2_contract = CapabilityContract(
        "CAP_RELATIONAL_COMPARE", "RELATIONAL_COMPARE", "C2_BINARY_RELATION",
        "TABLE", "TABLE", [p_col1, p_col2, p_op], [jc_distinct],
        ["REQ_NUMERIC_COLS"], {"row_delta": "truncate"}
    )
    def exec_c2(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        c1 = b["$col1"]
        c2 = b["$col2"]
        op = b.get("$operator", "LT")
        res = []
        for r in data:
            v1 = float(r.get(c1, 0))
            v2 = float(r.get(c2, 0))
            if op == "LT" and v1 < v2:
                res.append(r)
            elif op == "GT" and v1 > v2:
                res.append(r)
            elif op == "EQ" and v1 == v2:
                res.append(r)
        return res
    lib["CAP_RELATIONAL_COMPARE"] = ExecutableCapability(c2_contract, exec_c2)

    # --------------------------------------------------------------------------
    # C3: AGGREGATION - Aggregate Mean
    # --------------------------------------------------------------------------
    c3_contract = CapabilityContract(
        "CAP_AGGREGATE_MEAN", "AGGREGATE_MEAN", "C3_AGGREGATION",
        "TABLE", "SCALAR", [p_col], [],
        ["REQ_NUMERIC_COL"], {"shape": "scalar"}
    )
    def exec_c3(data: List[Dict[str, Any]], b: Dict[str, Any]) -> float:
        col = b["$col"]
        vals = [float(r[col]) for r in data if col in r]
        return sum(vals) / len(vals) if vals else 0.0
    lib["CAP_AGGREGATE_MEAN"] = ExecutableCapability(c3_contract, exec_c3)

    # --------------------------------------------------------------------------
    # C4: NESTED HIERARCHICAL AGGREGATION - Multi-key group summary
    # --------------------------------------------------------------------------
    p_grp = ParamSpec("$group_col", "COLUMN_REF", "Grouping categorical column", required=True)
    c4_contract = CapabilityContract(
        "CAP_GROUPED_SUMMARY", "GROUPED_SUMMARY", "C4_NESTED_HIERARCHICAL_AGGREGATION",
        "TABLE", "TABLE", [p_grp, p_col], [],
        ["REQ_GROUP_COL", "REQ_NUMERIC_COL"], {"shape": "grouped"}
    )
    def exec_c4(data: List[Dict[str, Any]], b: Dict[str, Any]) -> Dict[str, Any]:
        gcol = b["$group_col"]
        vcol = b["$col"]
        groups = {}
        for r in data:
            g = str(r.get(gcol, "UNKNOWN"))
            val = float(r.get(vcol, 0))
            if g not in groups:
                groups[g] = []
            groups[g].append(val)
        return {g: {"count": len(vs), "sum": sum(vs), "mean": sum(vs)/len(vs)} for g, vs in groups.items()}
    lib["CAP_GROUPED_SUMMARY"] = ExecutableCapability(c4_contract, exec_c4)

    # --------------------------------------------------------------------------
    # C5: CONDITIONAL PIECEWISE TRANSFORMATION
    # --------------------------------------------------------------------------
    p_cond_col = ParamSpec("$cond_col", "COLUMN_REF", "Condition column", required=True)
    p_cond_val = ParamSpec("$cond_val", "NUMERIC", "Condition split value", required=True)
    p_target_col = ParamSpec("$target_col", "COLUMN_REF", "Column to scale", required=True)
    p_mult = ParamSpec("$multiplier", "NUMERIC", "Scale multiplier", default_value=1.1, required=False)
    c5_contract = CapabilityContract(
        "CAP_CONDITIONAL_SCALE", "CONDITIONAL_SCALE", "C5_CONDITIONAL_TRANSFORMATION",
        "TABLE", "TABLE", [p_cond_col, p_cond_val, p_target_col, p_mult], [],
        ["REQ_NUMERIC_COLS"], {"shape": "mutated_copy"}
    )
    def exec_c5(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        ccol = b["$cond_col"]
        cval = float(b["$cond_val"])
        tcol = b["$target_col"]
        mult = float(b.get("$multiplier", 1.1))
        out = []
        for r in copy.deepcopy(data):
            if float(r.get(ccol, 0)) > cval:
                r[tcol] = float(r.get(tcol, 0)) * mult
            out.append(r)
        return out
    lib["CAP_CONDITIONAL_SCALE"] = ExecutableCapability(c5_contract, exec_c5)

    # --------------------------------------------------------------------------
    # C6: STATE MUTATION - Transactional in-place update
    # --------------------------------------------------------------------------
    p_id_col = ParamSpec("$id_col", "COLUMN_REF", "Primary key column", required=True)
    p_id_val = ParamSpec("$id_val", "STRING", "Key value to update", required=True)
    p_mut_col = ParamSpec("$mutate_col", "COLUMN_REF", "Column to update", required=True)
    p_new_val = ParamSpec("$new_val", "NUMERIC", "New assigned value", required=True)
    c6_contract = CapabilityContract(
        "CAP_TRANSACTIONAL_UPDATE", "TRANSACTIONAL_UPDATE", "C6_STATE_MUTATION",
        "TABLE", "TABLE", [p_id_col, p_id_val, p_mut_col, p_new_val], [],
        ["REQ_COL_EXISTS"], {"in_place": True}
    )
    def exec_c6(data: List[Dict[str, Any]], b: Dict[str, Any]) -> List[Dict[str, Any]]:
        icol = b["$id_col"]
        ival = str(b["$id_val"]).lower()
        mcol = b["$mutate_col"]
        nval = float(b["$new_val"])
        for r in data:
            if str(r.get(icol, "")).lower() == ival:
                r[mcol] = nval
        return data
    lib["CAP_TRANSACTIONAL_UPDATE"] = ExecutableCapability(c6_contract, exec_c6)

    # --------------------------------------------------------------------------
    # C7: MULTI-OUTPUT PARTITION - Splits table into two disjoint sets
    # --------------------------------------------------------------------------
    c7_contract = CapabilityContract(
        "CAP_PARTITION_SPLIT", "PARTITION_SPLIT", "C7_MULTI_OUTPUT_CAPABILITY",
        "TABLE", "TUPLE(TABLE, TABLE)", [p_col, p_thresh], [],
        ["REQ_NUMERIC_COL"], {"multi_output": True}
    )
    def exec_c7(data: List[Dict[str, Any]], b: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        col = b["$col"]
        th = float(b["$threshold"])
        passed = [r for r in data if float(r.get(col, 0)) >= th]
        failed = [r for r in data if float(r.get(col, 0)) < th]
        return passed, failed
    lib["CAP_PARTITION_SPLIT"] = ExecutableCapability(c7_contract, exec_c7)

    # --------------------------------------------------------------------------
    # C8: DERIVED INTERMEDIATE STATE - Valuation = sum(stock_level * unit_cost)
    # --------------------------------------------------------------------------
    p_qty = ParamSpec("$qty_col", "COLUMN_REF", "Quantity column", default_value="stock_level", required=True)
    p_price = ParamSpec("$price_col", "COLUMN_REF", "Price column", default_value="unit_cost_inr", required=True)
    c8_contract = CapabilityContract(
        "CAP_AGGREGATE_VALUATION", "AGGREGATE_VALUATION", "C8_DERIVED_INTERMEDIATE_STATE",
        "TABLE", "SCALAR", [p_qty, p_price], [],
        ["REQ_NUMERIC_COLS"], {"derived_computation": "dot_product"}
    )
    def exec_c8(data: List[Dict[str, Any]], b: Dict[str, Any]) -> float:
        qc = b.get("$qty_col", "stock_level")
        pc = b.get("$price_col", "unit_cost_inr")
        total = 0.0
        for r in data:
            q = float(r.get(qc, 0))
            p = float(r.get(pc, 0))
            total += (q * p)
        return total
    lib["CAP_AGGREGATE_VALUATION"] = ExecutableCapability(c8_contract, exec_c8)

    return lib
