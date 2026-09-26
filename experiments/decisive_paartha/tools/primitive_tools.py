"""
Primitive Tools and Contracts for Paartha Decisive Experiment.
Defines 12 deterministic, typed data-processing tools with full contracts.
Shared by System B (LLM + Tools) and Paartha (Systems C & D).
"""

import copy
from typing import Dict, List, Tuple, Any, Optional, Set

class ExecutionError(Exception):
    pass

class PreconditionError(ExecutionError):
    pass

class TypeErrorCustom(ExecutionError):
    pass

# ==============================================================================
# STATE REPRESENTATION
# ==============================================================================

class State:
    """Relational state containing flat rows or grouped partitions."""
    def __init__(self, data: List[Dict[str, Any]], grouped: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self.data = copy.deepcopy(data)
        self.grouped = copy.deepcopy(grouped) if grouped is not None else None

    def clone(self) -> 'State':
        return State(self.data, self.grouped)

    def is_grouped(self) -> bool:
        return self.grouped is not None

    def columns(self) -> Set[str]:
        if self.grouped is not None:
            for rows in self.grouped.values():
                if rows:
                    return set(rows[0].keys())
            return set()
        if not self.data:
            return set()
        return set(self.data[0].keys())

    def numeric_columns(self) -> Set[str]:
        cols = self.columns()
        num_cols = set()
        sample_rows = self.data if self.data else [r for group in (self.grouped.values() if self.grouped else []) for r in group]
        for c in cols:
            for r in sample_rows[:10]:
                val = r.get(c)
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    num_cols.add(c)
                    break
        return num_cols

    def row_count(self) -> int:
        if self.grouped is not None:
            return sum(len(g) for g in self.grouped.values())
        return len(self.data)

    def signature(self) -> str:
        if self.grouped is not None:
            g_repr = []
            for k in sorted(self.grouped.keys()):
                rows = tuple(tuple(sorted((rk, str(rv)) for rk, rv in r.items())) for r in self.grouped[k])
                g_repr.append((k, rows))
            return str(("GROUPED", tuple(g_repr)))
        rows = tuple(tuple(sorted((k, str(v)) for k, v in r.items())) for r in self.data)
        return str(("FLAT", rows))

    def equals(self, other: 'State') -> bool:
        if not isinstance(other, State):
            return False
        return self.signature() == other.signature()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        if self.grouped is not None:
            out = []
            for g_name, g_rows in sorted(self.grouped.items()):
                for r in g_rows:
                    rc = dict(r)
                    rc["_group"] = g_name
                    out.append(rc)
            return out
        return copy.deepcopy(self.data)


# ==============================================================================
# CONTRACT SPECIFICATION
# ==============================================================================

class PrimitiveContract:
    def __init__(
        self,
        name: str,
        description: str,
        input_type: str,
        output_type: str,
        parameters: Dict[str, str], # param_name -> type_desc
        preconditions: List[str],
        effects: str,
        constraints: Optional[List[str]] = None
    ):
        self.name = name
        self.description = description
        self.input_type = input_type
        self.output_type = output_type
        self.parameters = parameters
        self.preconditions = preconditions
        self.effects = effects
        self.constraints = constraints or []

    def to_tool_schema(self) -> Dict[str, Any]:
        """Exposes standard tool contract schema for LLM tool selection."""
        properties = {}
        required = []
        for p_name, p_type in self.parameters.items():
            required.append(p_name)
            if "int" in p_type.lower():
                prop_type = "integer"
            elif "float" in p_type.lower() or "number" in p_type.lower():
                prop_type = "number"
            elif "bool" in p_type.lower():
                prop_type = "boolean"
            elif "list" in p_type.lower():
                prop_type = "array"
            else:
                prop_type = "string"
            properties[p_name] = {"type": prop_type, "description": f"Parameter {p_name} ({p_type})"}
        
        return {
            "name": self.name,
            "description": f"{self.description} [Effects: {self.effects}]",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            },
            "contract": {
                "input_type": self.input_type,
                "output_type": self.output_type,
                "preconditions": self.preconditions,
                "constraints": self.constraints
            }
        }


class Capability:
    def __init__(self, name: str, contract: PrimitiveContract):
        self.name = name
        self.contract = contract
        self.is_composite = False
        self.sub_primitives: List[str] = []

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        raise NotImplementedError()

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        raise NotImplementedError()


# ==============================================================================
# 12 ATOMIC PRIMITIVE TOOLS
# ==============================================================================

class FilterByThreshold(Capability):
    def __init__(self):
        super().__init__(
            "FilterByThreshold",
            PrimitiveContract(
                name="FilterByThreshold",
                description="Filters rows where numerical column matches threshold via operator (> , >= , < , <= , == , !=)",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"col": "STRING (numeric column)", "threshold": "FLOAT", "operator": "STRING (> , >= , < , <= , == , !=)"},
                preconditions=["state is FLAT", "col in state.columns", "col is numeric"],
                effects="Retains only rows where row[col] (operator) threshold"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED; expected FLAT"
        col = params.get("col")
        if not col or col not in state.columns(): return False, f"Column '{col}' not found in state"
        if col not in state.numeric_columns(): return False, f"Column '{col}' is not numeric"
        op = params.get("operator", ">")
        if op not in [">", ">=", "<", "<=", "==", "!="]: return False, f"Unsupported operator '{op}'"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        col, thresh, op = params["col"], float(params["threshold"]), params.get("operator", ">")
        res = []
        for r in state.data:
            val = r.get(col)
            if val is None: continue
            if op == ">" and val > thresh: res.append(r)
            elif op == ">=" and val >= thresh: res.append(r)
            elif op == "<" and val < thresh: res.append(r)
            elif op == "<=" and val <= thresh: res.append(r)
            elif op == "==" and val == thresh: res.append(r)
            elif op == "!=" and val != thresh: res.append(r)
        return State(res)


class FilterEquals(Capability):
    def __init__(self):
        super().__init__(
            "FilterEquals",
            PrimitiveContract(
                name="FilterEquals",
                description="Filters rows where column equals literal value (string or categorical)",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"col": "STRING", "val": "ANY (literal value)"},
                preconditions=["state is FLAT", "col in state.columns"],
                effects="Retains rows where row[col] == val"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        col = params.get("col")
        if not col or col not in state.columns(): return False, f"Column '{col}' missing"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        col, val = params["col"], params["val"]
        return State([r for r in state.data if str(r.get(col)) == str(val)])


class SortByColumn(Capability):
    def __init__(self):
        super().__init__(
            "SortByColumn",
            PrimitiveContract(
                name="SortByColumn",
                description="Sorts rows by given column ascending or descending",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"col": "STRING", "ascending": "BOOLEAN"},
                preconditions=["state is FLAT", "col in state.columns"],
                effects="Orders rows deterministically by col"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        col = params.get("col")
        if not col or col not in state.columns(): return False, f"Column '{col}' missing"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        col = params["col"]
        ascending = bool(params.get("ascending", True))
        sorted_rows = sorted(state.data, key=lambda r: (r.get(col) is None, r.get(col)), reverse=not ascending)
        return State(sorted_rows)


class TopK(Capability):
    def __init__(self):
        super().__init__(
            "TopK",
            PrimitiveContract(
                name="TopK",
                description="Takes first k rows of current table",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"k": "INTEGER"},
                preconditions=["state is FLAT", "k > 0"],
                effects="Slices table to first k rows"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        k = params.get("k")
        if k is None or int(k) <= 0: return False, f"Invalid k={k}; must be positive integer"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        k = int(params["k"])
        return State(state.data[:k])


class TailK(Capability):
    def __init__(self):
        super().__init__(
            "TailK",
            PrimitiveContract(
                name="TailK",
                description="Takes last k rows of current table",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"k": "INTEGER"},
                preconditions=["state is FLAT", "k > 0"],
                effects="Slices table to last k rows"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        k = params.get("k")
        if k is None or int(k) <= 0: return False, f"Invalid k={k}; must be positive integer"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        k = int(params["k"])
        return State(state.data[-k:])


class GroupBy(Capability):
    def __init__(self):
        super().__init__(
            "GroupBy",
            PrimitiveContract(
                name="GroupBy",
                description="Partitions flat table into groups based on values in group_col",
                input_type="FLAT",
                output_type="GROUPED",
                parameters={"group_col": "STRING"},
                preconditions=["state is FLAT", "group_col in state.columns"],
                effects="Transforms flat rows into grouped partitions keyed by group_col values"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is already GROUPED"
        gc = params.get("group_col")
        if not gc or gc not in state.columns(): return False, f"Column '{gc}' missing"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        gc = params["group_col"]
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for r in state.data:
            key = str(r.get(gc, "UNKNOWN"))
            if key not in grouped: grouped[key] = []
            grouped[key].append(r)
        return State(data=[], grouped=grouped)


class AggregateSum(Capability):
    def __init__(self):
        super().__init__(
            "AggregateSum",
            PrimitiveContract(
                name="AggregateSum",
                description="Aggregates numeric column by summing values. If GROUPED, outputs one row per group with group_col and out_col. If FLAT, outputs single total row.",
                input_type="ANY",
                output_type="FLAT",
                parameters={"num_col": "STRING", "out_col": "STRING"},
                preconditions=["num_col in state.columns", "num_col is numeric"],
                effects="Reduces rows to summary sum rows"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        nc = params.get("num_col")
        if not nc or nc not in state.columns(): return False, f"Column '{nc}' missing"
        if nc not in state.numeric_columns(): return False, f"Column '{nc}' is not numeric"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        nc, out_col = params["num_col"], params.get("out_col", "total_sum")
        if state.is_grouped() and state.grouped is not None:
            rows = []
            for g_name, g_items in sorted(state.grouped.items()):
                s = sum(float(r.get(nc, 0)) for r in g_items if r.get(nc) is not None)
                rows.append({"group": g_name, out_col: round(s, 4)})
            return State(rows)
        else:
            s = sum(float(r.get(nc, 0)) for r in state.data if r.get(nc) is not None)
            return State([{out_col: round(s, 4)}])


class AggregateMean(Capability):
    def __init__(self):
        super().__init__(
            "AggregateMean",
            PrimitiveContract(
                name="AggregateMean",
                description="Aggregates numeric column by computing mean average. If GROUPED, outputs one row per group. If FLAT, outputs single mean row.",
                input_type="ANY",
                output_type="FLAT",
                parameters={"num_col": "STRING", "out_col": "STRING"},
                preconditions=["num_col in state.columns", "num_col is numeric"],
                effects="Reduces rows to summary mean rows"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        nc = params.get("num_col")
        if not nc or nc not in state.columns(): return False, f"Column '{nc}' missing"
        if nc not in state.numeric_columns(): return False, f"Column '{nc}' is not numeric"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        nc, out_col = params["num_col"], params.get("out_col", "mean_val")
        if state.is_grouped() and state.grouped is not None:
            rows = []
            for g_name, g_items in sorted(state.grouped.items()):
                valid_vals = [float(r.get(nc, 0)) for r in g_items if r.get(nc) is not None]
                mean_v = sum(valid_vals) / max(1, len(valid_vals))
                rows.append({"group": g_name, out_col: round(mean_v, 4)})
            return State(rows)
        else:
            valid_vals = [float(r.get(nc, 0)) for r in state.data if r.get(nc) is not None]
            mean_v = sum(valid_vals) / max(1, len(valid_vals))
            return State([{out_col: round(mean_v, 4)}])


class ProjectColumns(Capability):
    def __init__(self):
        super().__init__(
            "ProjectColumns",
            PrimitiveContract(
                name="ProjectColumns",
                description="Projects (selects) only specified columns from flat table",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"cols": "LIST[STRING]"},
                preconditions=["state is FLAT", "all cols in state.columns"],
                effects="Restricts table schema to specified subset of columns"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        cols = params.get("cols", [])
        if not cols: return False, "Empty cols list"
        for c in cols:
            if c not in state.columns(): return False, f"Column '{c}' not found in state"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        cols = params["cols"]
        res = [{c: r.get(c) for c in cols} for r in state.data]
        return State(res)


class ScaleColumn(Capability):
    def __init__(self):
        super().__init__(
            "ScaleColumn",
            PrimitiveContract(
                name="ScaleColumn",
                description="Multiplies numerical column in-place by scaling factor",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"col": "STRING", "factor": "FLOAT"},
                preconditions=["state is FLAT", "col in state.columns", "col is numeric"],
                effects="Multiplies each value in col by factor"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        col = params.get("col")
        if not col or col not in state.columns(): return False, f"Column '{col}' missing"
        if col not in state.numeric_columns(): return False, f"Column '{col}' is not numeric"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        col, factor = params["col"], float(params.get("factor", 1.0))
        res = []
        for r in state.data:
            rc = dict(r)
            if rc.get(col) is not None:
                rc[col] = round(float(rc[col]) * factor, 4)
            res.append(rc)
        return State(res)


class Deduplicate(Capability):
    def __init__(self):
        super().__init__(
            "Deduplicate",
            PrimitiveContract(
                name="Deduplicate",
                description="Removes duplicate rows based on unique key column",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"key_col": "STRING"},
                preconditions=["state is FLAT", "key_col in state.columns"],
                effects="Retains only first occurrence of each unique key_col value"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        kc = params.get("key_col")
        if not kc or kc not in state.columns(): return False, f"Column '{kc}' missing"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        kc = params["key_col"]
        seen = set()
        res = []
        for r in state.data:
            val = r.get(kc)
            if val not in seen:
                seen.add(val)
                res.append(r)
        return State(res)


class DropNull(Capability):
    def __init__(self):
        super().__init__(
            "DropNull",
            PrimitiveContract(
                name="DropNull",
                description="Drops rows where specified column contains null/None value",
                input_type="FLAT",
                output_type="FLAT",
                parameters={"col": "STRING"},
                preconditions=["state is FLAT", "col in state.columns"],
                effects="Removes any row where row[col] is null/None"
            )
        )

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        col = params.get("col")
        if not col or col not in state.columns(): return False, f"Column '{col}' missing"
        return True, None

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        valid, err = self.check_preconditions(state, params)
        if not valid: raise PreconditionError(err)
        col = params["col"]
        return State([r for r in state.data if r.get(col) is not None])


def initialize_primitive_tools() -> Dict[str, Capability]:
    """Returns the standardized registry of 12 primitive capabilities."""
    tools: List[Capability] = [
        FilterByThreshold(),
        FilterEquals(),
        SortByColumn(),
        TopK(),
        TailK(),
        GroupBy(),
        AggregateSum(),
        AggregateMean(),
        ProjectColumns(),
        ScaleColumn(),
        Deduplicate(),
        DropNull()
    ]
    return {t.name: t for t in tools}


# ==============================================================================
# AST & COMPOSITE ABSTRACTION SUPPORT
# ==============================================================================

class StepAST:
    def __init__(self, capability_name: str, params: Dict[str, Any]):
        self.capability_name = capability_name
        self.params = copy.deepcopy(params)

    def clone(self) -> 'StepAST':
        return StepAST(self.capability_name, self.params)


class ProgramAST:
    def __init__(self, steps: List[StepAST]):
        self.steps = steps

    def execute(self, state: State, registry: Dict[str, Capability]) -> State:
        curr = state.clone()
        for s in self.steps:
            if s.capability_name not in registry:
                raise ExecutionError(f"Missing capability: {s.capability_name}")
            cap = registry[s.capability_name]
            curr = cap.execute(curr, s.params)
        return curr

    def sequence_signature(self) -> List[str]:
        return [s.capability_name for s in self.steps]

    def complexity_bits(self) -> int:
        bits = 0
        for s in self.steps:
            bits += 16
            bits += 8 * len(s.params)
        return bits


class ParameterizedAbstraction(Capability):
    """
    Discovered parameterized abstraction with formal parameter mappings.
    Example: lambda(col, thresh, k) -> FilterByThreshold(col, thresh, '>') -> SortByColumn(col, False) -> TopK(k)
    """
    def __init__(
        self,
        name: str,
        template_steps: List[StepAST],
        formal_parameters: List[str],
        param_mapping: List[Dict[str, str]],
        sub_primitives: List[str]
    ):
        contract = PrimitiveContract(
            name=name,
            description=f"Autonomous parameterized macro: {' -> '.join(sub_primitives)}",
            input_type="FLAT",
            output_type="FLAT",
            parameters={p: "PARAM" for p in formal_parameters},
            preconditions=["Input must be FLAT"],
            effects=f"Composes {' -> '.join(sub_primitives)}"
        )
        super().__init__(name, contract)
        self.is_composite = True
        self.template_steps = template_steps
        self.formal_parameters = formal_parameters
        self.param_mapping = param_mapping
        self.sub_primitives = sub_primitives

    def instantiate(self, actual_args: Dict[str, Any]) -> List[StepAST]:
        concrete_steps = []
        for step, mapping in zip(self.template_steps, self.param_mapping):
            bound_params = dict(step.params)
            for step_key, formal_param in mapping.items():
                if formal_param in actual_args:
                    bound_params[step_key] = actual_args[formal_param]
            concrete_steps.append(StepAST(step.capability_name, bound_params))
        return concrete_steps

    def check_preconditions(self, state: State, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if state.is_grouped(): return False, "State is GROUPED"
        return True, None

    def execute_with_registry(self, state: State, registry: Dict[str, Capability], actual_args: Dict[str, Any]) -> State:
        concrete_steps = self.instantiate(actual_args)
        curr = state.clone()
        for s in concrete_steps:
            if s.capability_name not in registry:
                raise ExecutionError(f"Missing sub-primitive: {s.capability_name}")
            cap = registry[s.capability_name]
            curr = cap.execute(curr, s.params)
        return curr

    def execute(self, state: State, params: Dict[str, Any]) -> State:
        return self.execute_with_registry(state, initialize_primitive_tools(), params)

    def complexity_bits(self) -> int:
        bits = 32
        for s in self.template_steps:
            bits += 16 + 8 * len(s.params)
        return bits
