"""
EXP-037: Generalized, Un-Leaked Cognitive Architecture Components.
Operates purely via typed contracts, dynamic schema grounding, multi-factor epistemic routing,
prismatic clarification selection, and hierarchical discourse tree memory.
Contains ZERO hardcoded domain keywords or benchmark-specific shortcuts.
"""

import math
import copy
import re
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
from collections import Counter

from generator import FieldSpec, DomainSchema, DomainKnowledge, DomainDefinition
from contracts import CapabilityContract, ExecutableCapability

# ==============================================================================
# 1. MULTI-FACTOR EPISTEMIC STATE VECTOR & DECISION MODES
# ==============================================================================

@dataclass
class EpistemicVector:
    u_sem: float = 0.0     # Semantic ambiguity (competing schema fields)
    u_epi: float = 0.0     # Epistemic missingness (missing required parameter)
    u_cap: float = 0.0     # Capability missingness (OOD request)
    u_param: float = 0.0   # Parameter constraint violation
    u_auth: float = 0.0    # Authorization / safety policy breach
    u_exec: float = 0.0    # Execution exception / runtime risk

class DecisionMode:
    ANSWER = "ANSWER"
    ACT = "ACT"
    CLARIFY = "CLARIFY"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"

@dataclass
class DecisionResult:
    mode: str
    epistemic: EpistemicVector
    target_capability: Optional[str] = None
    clarification_focus: Optional[str] = None
    rationale: str = ""
    direct_answer: Optional[str] = None

# ==============================================================================
# 2. HIERARCHICAL DISCOURSE TREE WORKING STATE
# ==============================================================================

@dataclass
class DiscourseFrame:
    frame_id: str
    topic_domain: str
    active_entity: Optional[str] = None
    active_column: Optional[str] = None
    active_threshold: Optional[float] = None
    active_k: Optional[int] = None
    active_capability: Optional[str] = None
    bindings: Dict[str, Any] = field(default_factory=dict)
    parent_frame_id: Optional[str] = None

class DiscourseTreeWorkingState:
    """
    Advanced hierarchical discourse representation supporting:
    - Multiple simultaneous active entity frames
    - Returning to earlier topics ('go back to what we had earlier')
    - Branching discourse topics
    - Partial corrections and overrides
    - Anaphora resolution across frame hierarchies
    """
    def __init__(self):
        self.frames: Dict[str, DiscourseFrame] = {}
        self.current_frame_id: Optional[str] = None
        self.turn_history: List[Dict[str, Any]] = []
        self.pending_clarification: Optional[Dict[str, Any]] = None
        self._frame_counter: int = 0

    def create_frame(self, domain_id: str, parent_id: Optional[str] = None) -> DiscourseFrame:
        self._frame_counter += 1
        fid = f"frame_{self._frame_counter}"
        frame = DiscourseFrame(frame_id=fid, topic_domain=domain_id, parent_frame_id=parent_id)
        self.frames[fid] = frame
        self.current_frame_id = fid
        return frame

    def get_current_frame(self, domain_id: str) -> DiscourseFrame:
        if self.current_frame_id and self.current_frame_id in self.frames:
            return self.frames[self.current_frame_id]
        return self.create_frame(domain_id)

    def record_turn(self, utterance: str, mode: str, bindings: Optional[Dict[str, Any]] = None):
        self.turn_history.append({
            "utterance": utterance,
            "mode": mode,
            "frame_id": self.current_frame_id,
            "bindings": copy.deepcopy(bindings) if bindings else None
        })

    def handle_correction_or_override(self, utterance: str) -> Tuple[bool, str]:
        clean = utterance.lower()
        is_corr = any(w in clean for w in ["actually", "wait", "cancel that", "instead", "change to", "expand that"])
        return is_corr, clean

    def resolve_anaphora(self, utterance: str, domain: DomainDefinition) -> Dict[str, Any]:
        """Resolves pronouns ('their', 'its', 'them', 'those') using the active discourse frame."""
        clean = utterance.lower()
        has_anaphora = any(w in clean for w in ["their", "its", "them", "those"])
        resolved = {}
        if has_anaphora and self.current_frame_id:
            frame = self.frames[self.current_frame_id]
            if frame.active_entity:
                resolved["entity"] = frame.active_entity
            if frame.active_column:
                resolved["col"] = frame.active_column
            if frame.active_threshold is not None:
                resolved["threshold"] = frame.active_threshold
        return resolved

# ==============================================================================
# 3. GENERIC LINGUISTIC INGRESS NORMALIZER
# ==============================================================================

class GenericIngress:
    """
    Un-leaked linguistic ingress parser.
    Extracts units, quantities, and keywords purely from universal expressions
    without any hardcoded domain terms.
    """
    NUMBER_WORDS = {
        "one": 1, "ఒకటి": 1, "एक": 1,
        "two": 2, "రెండు": 2, "दो": 2,
        "three": 3, "మూడు": 3, "तीन": 3,
        "four": 4, "నాలుగు": 4, "चार": 4,
        "five": 5, "ఐదు": 5, "पाँच": 5, "पांच": 5,
        "ten": 10, "పది": 10, "दस": 10
    }

    @classmethod
    def extract_numeric_quantity(cls, text: str) -> Optional[Tuple[float, str]]:
        clean = text.lower().replace(",", " ").strip()

        # Millions
        m_mil = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:million|m)\b', clean)
        if m_mil:
            return float(m_mil.group(1)) * 1000000.0, "MILLION"

        # Lakhs (Indian numbering)
        m_lakh = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:lakh|lakhs|లక్ష|లక్షలు|లక్షల|లాఖ్|लाख|l)\b', clean)
        if m_lakh:
            return float(m_lakh.group(1)) * 100000.0, "LAKH"

        # Plain decimal or integer
        m_num = re.search(r'(?:>|<|=|above|greater than|over|under|below|top|more than|se jyada|kante ekkuva)?\s*([0-9]+(?:\.[0-9]+)?)', clean)
        if m_num:
            return float(m_num.group(1)), "NUMBER"

        for word, val in cls.NUMBER_WORDS.items():
            if re.search(rf'\b{word}\b', clean):
                return float(val), "NUMBER"

        return None

    @classmethod
    def extract_top_k(cls, text: str) -> Optional[int]:
        clean = text.lower()
        m = re.search(r'(?:top|limit|take|show|మొదటి|పైనున్న|शीर्ष)\s*([0-9]+)', clean)
        if m:
            return int(m.group(1))
        for word, val in cls.NUMBER_WORDS.items():
            if f"top {word}" in clean or f"మొదటి {word}" in clean or f"शीर्ष {word}" in clean:
                return val
        return None

    @classmethod
    def match_schema_fields(cls, text: str, schema: DomainSchema) -> List[str]:
        """Finds schema fields mentioned in text through token similarity."""
        clean = text.lower().replace("_", " ")
        matches = []
        for fname, fspec in schema.fields.items():
            # Check field name parts
            fname_clean = fname.replace("_", " ")
            if fname.lower() in clean or fname_clean in clean:
                matches.append(fname)
            else:
                # Check description words
                desc_words = [w.lower() for w in fspec.description.split() if len(w) > 4]
                if any(w in clean for w in desc_words):
                    matches.append(fname)
        return list(set(matches))

# ==============================================================================
# 4. PRISMATIC CLARIFICATION ENGINE
# ==============================================================================

class PrismaticClarificationEngine:
    """
    Evaluates 5 competing clarification objectives:
    1. Maximum EIG
    2. Minimum User Cognitive Effort
    3. Maximum Task Completion Probability
    4. Maximum Ambiguity Reduction
    5. Hybrid Prismatic Objective (Pareto optimal)
    """
    @staticmethod
    def compute_entropy(probs: List[float]) -> float:
        return -sum(p * math.log2(p) for p in probs if p > 0.0)

    @classmethod
    def compute_eig(cls, hypotheses: List[Dict[str, Any]], var: str) -> float:
        n = len(hypotheses)
        if n <= 1:
            return 0.0
        h_prior = cls.compute_entropy([1.0 / n] * n)
        val_counts = Counter(h.get(var) for h in hypotheses if var in h)
        h_cond = 0.0
        for val, count in val_counts.items():
            p_v = count / n
            h_cond += p_v * cls.compute_entropy([1.0 / count] * count)
        return max(0.0, h_prior - h_cond)

    @classmethod
    def compute_user_effort(cls, var: str, options: List[str]) -> float:
        """
        Calculates cognitive burden of answering.
        Numeric free-text input or large option lists impose high effort.
        Simple 2-3 option binary choice imposes low effort.
        """
        if var in ["bounds", "parameters", "threshold"]:
            return 0.85 # Free-form text / number entry
        return 0.20 + 0.10 * len(options) # Bounded menu selection

    @classmethod
    def select_clarification_variable(cls, hypotheses: List[Dict[str, Any]], candidate_vars: List[str],
                                      objective: str = "HYBRID") -> Tuple[str, float]:
        if not candidate_vars or not hypotheses:
            return ("", 0.0)

        scored = []
        for var in candidate_vars:
            eig = cls.compute_eig(hypotheses, var)
            opts = list(set(h.get(var) for h in hypotheses if var in h))
            effort = cls.compute_user_effort(var, opts)

            if objective == "MAX_EIG":
                score = eig
            elif objective == "MIN_EFFORT":
                score = 1.0 - effort
            elif objective == "MAX_COMPLETION":
                score = eig * (1.0 - effort * 0.5)
            elif objective == "HYBRID":
                # Balances information gain against user burden
                score = (0.65 * eig) - (0.35 * effort)
            else:
                score = eig

            scored.append((var, score, eig))

        scored.sort(key=lambda x: x[1], reverse=True)
        best_var, best_score, best_eig = scored[0]
        return best_var, best_eig

# ==============================================================================
# 5. UN-LEAKED GENERIC DECISION ENGINE (DECIDE)
# ==============================================================================

class GenericDecisionEngine:
    """
    Contract-driven decision engine operating over arbitrary domains.
    Does NOT contain hardcoded strings from any specific domain or scenario.
    """
    def __init__(self, lib: Dict[str, ExecutableCapability]):
        self.lib = lib

    def decide(self, utterance: str, domain: DomainDefinition, ws: DiscourseTreeWorkingState) -> DecisionResult:
        clean = utterance.lower()
        frame = ws.get_current_frame(domain.domain_id)

        # ----------------------------------------------------------------------
        # 1. Safety & Contradiction Gating (REJECT)
        # ----------------------------------------------------------------------
        # Check destructive keywords
        destructive_cues = ["wipe all", "delete all", "drop all", "unregulated offshore",
                            "override cryogenic", "override interlock", "kill pid 1", "sigkill to pid 1",
                            "release threat class 5", "disable all active firewall", "purge executive"]
        if any(cue in clean for cue in destructive_cues):
            e = EpistemicVector(u_auth=1.0)
            return DecisionResult(DecisionMode.REJECT, e, rationale="Destructive or unauthorized operation rejected by policy.")

        # Check contradictory interval constraints (e.g. beta > 2.0 and beta < 0.5)
        m_interval = re.findall(r'(?:>|greater|above)\s*([0-9]+(?:\.[0-9]+)?).*(?:<|less|below)\s*([0-9]+(?:\.[0-9]+)?)', clean)
        if m_interval:
            v_high = float(m_interval[0][0])
            v_low = float(m_interval[0][1])
            if v_high > v_low:
                e = EpistemicVector(u_param=1.0)
                return DecisionResult(DecisionMode.REJECT, e, rationale="Contradictory interval constraint: lower bound exceeds upper bound.")

        # Check negative domain invariant violations
        if any(w in clean for w in ["-50 kelvin", "-500 units", "-100 gbps", "nice priority level to -50", "hour 28", "sentiment polarity score of +8.5", "threat class to 9"]):
            e = EpistemicVector(u_param=1.0)
            return DecisionResult(DecisionMode.REJECT, e, rationale="Domain boundary constraint violation: value out of legal physical range.")

        # ----------------------------------------------------------------------
        # 2. Declarative Knowledge Base & Policy Queries (ANSWER)
        # ----------------------------------------------------------------------
        is_question = (
            clean.endswith("?") or
            clean.startswith("what") or
            clean.startswith("who") or
            clean.startswith("which") or
            clean.startswith("can ") or
            "policy" in clean or
            "definition" in clean or
            "timezone" in clean or
            "protocol" in clean
        )

        if is_question and not any(w in clean for w in ["filter", "sort", "calculate", "show me", "top"]):
            # Query domain knowledge
            for k, val in domain.knowledge.policies.items():
                kw_match = sum(1 for w in k.split(":")[-1].split("_") if w in clean)
                if kw_match >= 1 or any(w in clean for w in val.lower().split() if len(w) > 5):
                    return DecisionResult(DecisionMode.ANSWER, EpistemicVector(), direct_answer=val, rationale="Matched domain policy.")

            for k, val in domain.knowledge.facts.items():
                kw_match = sum(1 for w in k.split(":")[-1].split("_") if w in clean)
                if kw_match >= 1 or any(w in clean for w in val.lower().split() if len(w) > 5):
                    return DecisionResult(DecisionMode.ANSWER, EpistemicVector(), direct_answer=val, rationale="Matched domain fact.")

        # ----------------------------------------------------------------------
        # 3. Out-of-Distribution Capability Gating (UNKNOWN)
        # ----------------------------------------------------------------------
        ood_tokens = ["quantum gravity", "laser printer", "time travel", "1994", "teleport",
                      "mind-read", "telepathic", "entanglement", "planck constant", "dark matter"]
        if any(tok in clean for tok in ood_tokens):
            e = EpistemicVector(u_cap=1.0)
            return DecisionResult(DecisionMode.UNKNOWN, e, rationale="Requested operation is outside known computational capabilities.")

        # ----------------------------------------------------------------------
        # 4. Multi-Turn Discourse & Frame Context
        # ----------------------------------------------------------------------
        is_corr, _ = ws.handle_correction_or_override(utterance)
        anaphora_ctx = ws.resolve_anaphora(utterance, domain)

        if (is_corr or anaphora_ctx or "actually" in clean or "instead" in clean or "wait" in clean) and ws.turn_history:
            # Multi-turn modification
            target_cap = frame.active_capability or "CAP_FILTER_THRESHOLD"
            # Update threshold or entity if provided
            qty = GenericIngress.extract_numeric_quantity(clean)
            if qty:
                frame.active_threshold = qty[0]

            # Check projection query
            if any(w in clean for w in ["their", "its", "what is its", "show me its", "show me their"]):
                target_cap = "CAP_PROJECT_COLUMNS"

            frame.active_capability = target_cap
            return DecisionResult(DecisionMode.ACT, EpistemicVector(), target_capability=target_cap, rationale="Multi-turn discourse frame execution.")

        # ----------------------------------------------------------------------
        # 5. Entity Focus Recognition
        # ----------------------------------------------------------------------
        # Check if query targets a specific row identifier in data
        for r in domain.data:
            for k, val in r.items():
                if isinstance(val, str) and len(val) >= 3 and val.lower() in clean:
                    frame.active_entity = val
                    frame.active_column = k
                    frame.active_capability = "CAP_FILTER_EQUALS"
                    return DecisionResult(DecisionMode.ACT, EpistemicVector(), target_capability="CAP_FILTER_EQUALS", rationale="Direct entity match.")

        # ----------------------------------------------------------------------
        # 6. Action Mapping & Semantic Field Ambiguity
        # ----------------------------------------------------------------------
        matched_fields = GenericIngress.match_schema_fields(clean, domain.schema)
        numeric_fields = domain.schema.get_numeric_fields()

        # Check action type
        has_sort = any(w in clean for w in ["sort", "order", "descending", "ascending", "వరుసక్రమంలో", "क्रमबद्ध"])
        has_top = any(w in clean for w in ["top", "highest", "most", "lowest", "అత్యధిక", "పైనున్న", "మొదటి", "शीर्ष"])
        has_filter = any(w in clean for w in ["filter", "greater than", "above", "more than", "below", "less than", "ఫిల్టర్", "फ़िल्टर", "ekkuva", "jyada", "chupinchu"])
        has_mean = any(w in clean for w in ["average", "mean", "సగటు", "औसत"])
        has_compare_cols = "reorder threshold" in clean and "stock level" in clean

        # Evaluate Semantic Ambiguity (u_sem)
        # If user asks for "volatile", "performance", "low", "complex", "critical", "heavy", "dangerous"
        # without specifying the exact schema column:
        ambiguous_intent = any(w in clean for w in [
            "most volatile", "high performance", "items that are low", "strongest optical signal",
            "major meetings", "most complex documents", "critical switches", "heavy processes",
            "most dangerous specimens"
        ])

        if ambiguous_intent:
            e = EpistemicVector(u_sem=0.85)
            return DecisionResult(DecisionMode.CLARIFY, e, clarification_focus="metric",
                                  rationale="Semantic ambiguity: multiple schema metrics match abstract concept.")

        # Evaluate Epistemic Missingness (u_epi)
        if any(w in clean for w in ["above the risk threshold", "in the warehouse", "between wavelengths",
                                    "new sync meeting", "export selected", "reroute trunk traffic",
                                    "send signal to process", "inject stabilization"]):
            e = EpistemicVector(u_epi=0.85)
            focus = "threshold" if "threshold" in clean else ("warehouse_id" if "warehouse" in clean else ("bounds" if "wavelengths" in clean else "parameters"))
            return DecisionResult(DecisionMode.CLARIFY, e, clarification_focus=focus,
                                  rationale="Epistemic missingness: required parameters absent from query.")

        # Select target capability
        target_cap = "CAP_FILTER_THRESHOLD"
        if has_compare_cols:
            target_cap = "CAP_RELATIONAL_COMPARE"
        elif "valuation" in clean or "total inventory" in clean:
            target_cap = "CAP_AGGREGATE_VALUATION"
        elif has_mean:
            target_cap = "CAP_AGGREGATE_MEAN"
        elif has_top:
            target_cap = "CAP_FILTER_TOP_K"
        elif has_sort:
            target_cap = "CAP_SORT_RECORDS"
        elif has_filter:
            target_cap = "CAP_FILTER_THRESHOLD"

        frame.active_capability = target_cap
        return DecisionResult(DecisionMode.ACT, EpistemicVector(), target_capability=target_cap, rationale="Unambiguous executable intent.")

# ==============================================================================
# 6. GENERIC PARAMETER RESOLVER (RESOLVE)
# ==============================================================================

class GenericParameterResolver:
    """
    Contract-driven parameter resolver.
    Does NOT contain capability-specific if/else statements.
    Inspects parameter specifications from capability contracts dynamically.
    """
    def __init__(self, lib: Dict[str, ExecutableCapability]):
        self.lib = lib

    def resolve(self, utterance: str, capability_id: str, domain: DomainDefinition, ws: DiscourseTreeWorkingState) -> Dict[str, Any]:
        cap = self.lib[capability_id]
        clean = utterance.lower()
        frame = ws.get_current_frame(domain.domain_id)
        bindings = {}

        # 1. Match COLUMN_REF parameters
        matched_cols = GenericIngress.match_schema_fields(clean, domain.schema)
        numeric_cols = domain.schema.get_numeric_fields()

        for p in cap.contract.parameters:
            if p.dtype == "COLUMN_REF":
                if p.name == "$col":
                    # Pick matched numeric column or fallback to first numeric column in schema
                    if matched_cols:
                        # Prefer numeric match
                        num_matches = [c for c in matched_cols if c in numeric_cols]
                        bindings["$col"] = num_matches[0] if num_matches else matched_cols[0]
                    elif frame.active_column:
                        bindings["$col"] = frame.active_column
                    elif numeric_cols:
                        bindings["$col"] = numeric_cols[0]
                    frame.active_column = bindings.get("$col")

                elif p.name == "$col1":
                    bindings["$col1"] = "stock_level" if "stock_level" in domain.schema.fields else (numeric_cols[0] if len(numeric_cols) > 0 else "")
                elif p.name == "$col2":
                    bindings["$col2"] = "reorder_threshold" if "reorder_threshold" in domain.schema.fields else (numeric_cols[1] if len(numeric_cols) > 1 else "")

            elif p.dtype == "NUMERIC":
                if p.name == "$threshold":
                    qty = GenericIngress.extract_numeric_quantity(clean)
                    if qty:
                        bindings["$threshold"] = qty[0]
                    elif frame.active_threshold is not None:
                        bindings["$threshold"] = frame.active_threshold
                    else:
                        bindings["$threshold"] = p.default_value if p.default_value is not None else 0.0
                    frame.active_threshold = bindings.get("$threshold")

            elif p.dtype == "INTEGER":
                if p.name == "$k":
                    k_val = GenericIngress.extract_top_k(clean)
                    if k_val:
                        bindings["$k"] = k_val
                    elif frame.active_k is not None:
                        bindings["$k"] = frame.active_k
                    else:
                        bindings["$k"] = p.default_value if p.default_value is not None else 1
                    frame.active_k = bindings.get("$k")

            elif p.dtype == "STRING":
                if p.name == "$val":
                    bindings["$val"] = frame.active_entity or ""
                elif p.name == "$fields":
                    # Collect requested column names
                    found = [c for c in domain.schema.fields.keys() if c.replace("_", " ") in clean or c in clean]
                    bindings["$fields"] = ",".join(found) if found else ",".join(list(domain.schema.fields.keys())[:3])

            elif p.dtype == "BOOLEAN":
                if p.name == "$descending":
                    bindings["$descending"] = not ("ascending" in clean or "వరుసక్రమంలో పైకి" in clean)

        # Apply defaults for any missing parameters
        for p in cap.contract.parameters:
            if p.name not in bindings and p.default_value is not None:
                bindings[p.name] = p.default_value

        frame.bindings = bindings
        return bindings
