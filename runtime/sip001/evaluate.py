"""
EVALUATE (SIP-001 Section 2, rows 5/11/15). EVALUATE-LOCAL (entropy,
label-free) is Class A -- validated by EXP-001/009. EVALUATE-GENERALIZATION
is Class B -- validated only with real labels (EXP-003/009); label-free
substitutes were directly falsified by EXP-009 (0% held-out accuracy for
entropy/self-assessment at family-selection despite matching the oracle at
memory-gating). This module does not attempt a label-free version -- doing
so would contradict EXP-009 directly, exactly the "Theoretical
Contradiction" failure category SIP-001 Section 9 reserves for the most
serious class of finding.
"""

import torch
import torch.nn.functional as F


def evaluate_local(logits, position):
    """(output, self) -> discrepancy_score, via entropy. EXP-001/009."""
    with torch.no_grad():
        probs = F.softmax(logits[:, position, :], dim=-1)
        ent = -(probs * torch.log(probs.clamp_min(1e-9))).sum(dim=-1)
    return ent


def knowledge_boundary(entropy, threshold):
    """Knowledge Boundary Detection (SIP-001 Section 2, row 11) -- a
    direct threshold on EVALUATE-LOCAL. Confident iff entropy is below
    threshold; the runtime does not claim this threshold is itself
    validated as a general-purpose calibrated cutoff (ARS-001's own
    SR-01 entry flags this: "a fixed hyperparameter... not a general-
    purpose, calibrated signal usable across arbitrary inputs" -- that
    generalization is Reasoned, not Validated)."""
    return entropy < threshold


def evaluate_generalization(candidate_score, held_out_labels):
    """(output, held-out reference) -> discrepancy_score. Runs ONLY if
    real labels are supplied -- this runtime does not manufacture labels
    for genuine unknowns (that would defeat the point of them being
    unknown). Returns None, clearly, if no labels are available, rather
    than silently falling back to a label-free proxy EXP-009 already
    falsified."""
    if held_out_labels is None:
        return None, "skipped_no_labels_available"
    correct = sum(1 for pred, true in zip(candidate_score, held_out_labels) if pred == true)
    return correct / len(held_out_labels), "evaluated_with_real_labels"
