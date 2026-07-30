"""
Reasoning Execution Engine (KRS-001 / ACA-0)

Executes deductive reasoning, explanation synthesis, transfer binding,
counterfactual simulation, and clarification request generation over KRS-001 Knowledge Graphs.
"""

from krs import KnowledgeGraph, RelationEdge

class ReasoningEngine:
    def __init__(self):
        pass

    def evaluate_direct_recall(self, subj, pred, obj, kg):
        # 1. Direct match in relations
        if kg.has_relation(subj, pred, obj):
            return "YES", [f"Direct fact stored: {subj} {pred} {obj}"]

        # 2. Rule deduction
        for rule in kg.invariants:
            if rule.impl_pred == pred and rule.impl_target == obj:
                edge, trace = rule.evaluate(subj, kg)
                if edge is not None:
                    # Record proof trace
                    kg.proof_traces[f"{subj}_{pred}_{obj}"] = [
                        f"{subj} is_a {rule.cond_target}",
                        f"Rule: All {rule.cond_target}s {rule.impl_pred} {rule.impl_target}",
                        f"Conclusion: {subj} {pred} {obj}"
                    ]
                    return "YES", kg.proof_traces[f"{subj}_{pred}_{obj}"]

        return "UNKNOWN", []

    def explain(self, subj, pred, obj, kg):
        ans, proof = self.evaluate_direct_recall(subj, pred, obj, kg)
        if ans == "YES":
            for rule in kg.invariants:
                if rule.impl_pred == pred and rule.impl_target == obj:
                    return f"Because {subj}s are {rule.cond_target}s, and all {rule.cond_target}s {rule.impl_pred} {rule.impl_target}."
            return f"Because it is a direct fact stored in memory that {subj} {pred} {obj}."
        return f"I cannot explain why {subj} {pred} {obj} because that fact is not established in my knowledge graph."

    def transfer(self, new_subj, category, target_pred, target_obj, kg):
        # Add new entity relation temporarily or permanently
        kg.add_relation(new_subj, "is_a", category)
        ans, proof = self.evaluate_direct_recall(new_subj, target_pred, target_obj, kg)
        if ans == "YES":
            explanation = f"Because {new_subj}s are {category}s, and all {category}s {target_pred} {target_obj}."
            return "YES", explanation, proof
        return "NO", "Transfer failed: category does not imply property.", []

    def evaluate_counterfactual(self, subj, old_cat, new_cat, target_pred, target_obj, kg):
        # Create counterfactual copy S'_counter
        kg_counter = kg.copy()

        # Remove old category relation (Whale is_a Mammal) and target predicate relation (Whale breathes Air)
        kg_counter.relations = [
            r for r in kg_counter.relations
            if not (r.subject == subj and r.predicate == "is_a" and r.object == old_cat)
            and not (r.subject == subj and r.predicate == target_pred and r.object == target_obj)
        ]

        # Add counterfactual category relation (Whale is_a Fish)
        kg_counter.add_relation(subj, "is_a", new_cat)

        # Re-evaluate under counterfactual state
        ans, proof = self.evaluate_direct_recall(subj, target_pred, target_obj, kg_counter)

        if ans == "NO" or ans == "UNKNOWN":
            explanation = f"If {subj}s were {new_cat}s instead of {old_cat}s, the rule 'All {old_cat}s {target_pred} {target_obj}' would no longer imply that {subj}s {target_pred} {target_obj}."
            return "NO", explanation
        else:
            explanation = f"Even if {subj}s were {new_cat}s, the conclusion would still hold."
            return "YES", explanation

    def handle_missing_knowledge(self, subj, target_pred, kg):
        # Check if subject exists
        cat = kg.query_relation(subj, "is_a")
        if not cat:
            return "CLARIFICATION_REQUIRED", f"I do not know what kind of entity '{subj}' is. Is {subj} a Mammal, or does {subj} belong to another category?"
        else:
            return "CLARIFICATION_REQUIRED", f"I know {subj} is a {cat[0]}, but I lack a rule connecting {cat[0]} to {target_pred}."
