"""
EVALUATE (SIP-002) -- EVALUATE-LOCAL (entropy) + Knowledge Boundary Detection.
"""

import torch
import torch.nn.functional as F

def evaluate_local(logits, position):
    with torch.no_grad():
        probs = F.softmax(logits[:, position, :], dim=-1)
        ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
    return ent

def knowledge_boundary(entropy, threshold=1.5):
    return entropy < threshold

def evaluate_generalization(candidate_preds, held_out_labels):
    if held_out_labels is None:
        return None, "skipped_no_labels_available"
    correct = sum(1 for p, t in zip(candidate_preds, held_out_labels) if p == t)
    return correct / len(held_out_labels), "evaluated_with_real_labels"
