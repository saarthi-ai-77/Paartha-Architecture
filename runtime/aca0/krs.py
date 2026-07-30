"""
Knowledge Representation Engine (KRS-001 / ACA-0)

Implements the formal computational knowledge graph tuple:
K = < V_E, E_R, C_I >

Where:
- V_E: Entity nodes (symbols, properties)
- E_R: Relation edges (subject, predicate, object)
- C_I: Invariant rules / logical constraints in S_invariants
"""

import copy

class EntityNode:
    def __init__(self, symbol, category=None):
        self.symbol = symbol
        self.category = category
        self.properties = set()

    def __repr__(self):
        return f"Entity({self.symbol})"

class RelationEdge:
    def __init__(self, subject, predicate, obj):
        self.subject = subject
        self.predicate = predicate
        self.object = obj

    def __repr__(self):
        return f"Relation({self.subject} --{self.predicate}--> {self.object})"

class InvariantRule:
    """Formal logical rule in S_invariants:
    e.g. forall x: is_a(x, Mammal) => breathes(x, Air)
    """
    def __init__(self, rule_id, cond_pred, cond_target, impl_pred, impl_target):
        self.rule_id = rule_id
        self.cond_pred = cond_pred
        self.cond_target = cond_target
        self.impl_pred = impl_pred
        self.impl_target = impl_target

    def evaluate(self, subj, kg):
        # Check if kg has relation: subj cond_pred cond_target
        if kg.has_relation(subj, self.cond_pred, self.cond_target):
            return RelationEdge(subj, self.impl_pred, self.impl_target), f"Applied rule {self.rule_id}: {subj} is {self.cond_target} => {self.impl_pred} {self.impl_target}"
        return None, None

    def __repr__(self):
        return f"Rule({self.rule_id}: forall x, {self.cond_pred}(x, {self.cond_target}) => {self.impl_pred}(x, {self.impl_target}))"

class KnowledgeGraph:
    def __init__(self):
        self.entities = {}   # symbol -> EntityNode
        self.relations = []  # list of RelationEdge
        self.invariants = [] # list of InvariantRule
        self.proof_traces = {} # goal_str -> list of step strings

    def get_or_create_entity(self, symbol, category=None):
        if symbol not in self.entities:
            self.entities[symbol] = EntityNode(symbol, category)
        return self.entities[symbol]

    def add_relation(self, subject, predicate, obj):
        self.get_or_create_entity(subject)
        self.get_or_create_entity(obj)
        # Avoid duplicate relation
        for r in self.relations:
            if r.subject == subject and r.predicate == predicate and r.object == obj:
                return r
        edge = RelationEdge(subject, predicate, obj)
        self.relations.append(edge)
        return edge

    def add_invariant(self, rule):
        for inv in self.invariants:
            if inv.rule_id == rule.rule_id:
                return inv
        self.invariants.append(rule)
        return rule

    def has_relation(self, subject, predicate, obj):
        for r in self.relations:
            if r.subject == subject and r.predicate == predicate and r.object == obj:
                return True
        return False

    def query_relation(self, subject, predicate):
        results = []
        for r in self.relations:
            if r.subject == subject and r.predicate == predicate:
                results.append(r.object)
        return results

    def copy(self):
        new_kg = KnowledgeGraph()
        new_kg.entities = copy.deepcopy(self.entities)
        new_kg.relations = copy.deepcopy(self.relations)
        new_kg.invariants = copy.deepcopy(self.invariants)
        new_kg.proof_traces = copy.deepcopy(self.proof_traces)
        return new_kg
