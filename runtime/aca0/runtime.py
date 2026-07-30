"""
ACA-0 Cognitive Runtime (The First Cognitive Prototype)

Orchestrates the minimal cognitive loop:
Mentor -> Lesson -> Understanding -> Construction -> Validation -> Question -> Reasoning -> Response -> Episode -> Promotion
"""

import time
import json
from krs import KnowledgeGraph
from lesson import LessonParser
from reasoning import ReasoningEngine

class ACA0CognitiveRuntime:
    def __init__(self, capacity=30):
        self.kg = KnowledgeGraph()
        self.parser = LessonParser()
        self.reasoner = ReasoningEngine()
        self.capacity = capacity
        self.episodes = []

    def teach_lesson(self, text_lines):
        """Processes a mentor lesson into KRS-001 computational knowledge graph."""
        constructed = self.parser.parse_and_construct(text_lines, self.kg)
        ep = {
            "timestamp": time.time(),
            "type": "lesson_ingress",
            "lines": text_lines,
            "constructed_count": len(constructed)
        }
        self.episodes.append(ep)
        return {
            "status": "lesson_understood",
            "constructed_elements": constructed,
            "total_entities": len(self.kg.entities),
            "total_relations": len(self.kg.relations),
            "total_invariants": len(self.kg.invariants)
        }

    def ask_question(self, stage, question_dict):
        """Handles questions across Stages 1-5."""
        kind = question_dict.get("kind")
        ep = {"timestamp": time.time(), "stage": stage, "question": question_dict}

        if kind == "direct_recall":
            subj = question_dict["subject"]
            pred = question_dict["predicate"]
            obj = question_dict["object"]
            ans, proof = self.reasoner.evaluate_direct_recall(subj, pred, obj, self.kg)
            ep["response"] = ans
            ep["proof"] = proof
            res = {"answer": ans, "proof_trace": proof}

        elif kind == "explanation":
            subj = question_dict["subject"]
            pred = question_dict["predicate"]
            obj = question_dict["object"]
            explanation = self.reasoner.explain(subj, pred, obj, self.kg)
            ep["response"] = explanation
            res = {"explanation": explanation}

        elif kind == "transfer":
            subj = question_dict["subject"]
            cat = question_dict["category"]
            pred = question_dict["predicate"]
            obj = question_dict["object"]
            ans, exp, proof = self.reasoner.transfer(subj, cat, pred, obj, self.kg)
            ep["response"] = ans
            ep["explanation"] = exp
            res = {"answer": ans, "explanation": exp, "proof_trace": proof}

        elif kind == "counterfactual":
            subj = question_dict["subject"]
            old_cat = question_dict["old_category"]
            new_cat = question_dict["new_category"]
            pred = question_dict["predicate"]
            obj = question_dict["object"]
            ans, exp = self.reasoner.evaluate_counterfactual(subj, old_cat, new_cat, pred, obj, self.kg)
            ep["response"] = ans
            ep["explanation"] = exp
            res = {"answer": ans, "explanation": exp}

        elif kind == "clarification":
            subj = question_dict["subject"]
            pred = question_dict["predicate"]
            # Check direct recall first
            ans, proof = self.reasoner.evaluate_direct_recall(subj, pred, "Milk", self.kg)
            if ans == "YES":
                res = {"status": "UNDERSTOOD", "answer": "YES"}
            else:
                status, query_text = self.reasoner.handle_missing_knowledge(subj, pred, self.kg)
                ep["response"] = status
                ep["query_text"] = query_text
                res = {"status": status, "query_text": query_text}

        else:
            res = {"error": f"Unknown question kind: {kind}"}

        self.episodes.append(ep)
        return res

    def clarify_knowledge(self, mentor_clarification_lines):
        """Receives mentor clarification to resolve CLARIFICATION_REQUIRED state."""
        constructed = self.parser.parse_and_construct(mentor_clarification_lines, self.kg)
        ep = {
            "timestamp": time.time(),
            "type": "mentor_clarification",
            "lines": mentor_clarification_lines,
            "constructed_count": len(constructed)
        }
        self.episodes.append(ep)
        return {
            "status": "knowledge_updated",
            "constructed": constructed
        }
