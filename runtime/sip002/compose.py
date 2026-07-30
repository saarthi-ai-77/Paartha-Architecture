"""
StructureMatchedCompose (SIP-002 / EXP-020) -- SCAN compositional pathway.
"""

import os
import sys
import torch

import importlib.util

SIP001_COMPOSE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sip001", "compose.py")
spec = importlib.util.spec_from_file_location("sip001_compose", SIP001_COMPOSE_PATH)
sip001_compose = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sip001_compose)

ACTIONS = sip001_compose.ACTIONS
ACTION_STOI = sip001_compose.ACTION_STOI
compile_slots = sip001_compose.compile_slots
build_logit_sequence = sip001_compose.build_logit_sequence

class StructureMatchedCompose:
    def __init__(self, device):
        self.device = device
        self.model = sip001_compose.PrimitiveClassifier().to(device)

    def run(self, input_tokens):
        slots = compile_slots(input_tokens)
        table = self.model()
        logits_seq = build_logit_sequence(slots, table, self.device)
        preds = logits_seq.argmax(dim=-1).tolist()
        actions = [ACTIONS[i] for i in preds]
        return actions, logits_seq
