**Status: Active**

# Rejected Ideas

This document logs hypotheses, architectures, and principles that were proposed but ultimately rejected after Council critique. We preserve these to avoid repeating past mistakes.

## 1. Single-Paradigm Cognition
* **Description:** The assumption that all forms of intelligence can be optimally handled by scaling a single architecture (e.g., Transformer).
* **Reason for Rejection:** Fails to account for the structural mismatch between different types of cognitive tasks (e.g., spatial vs. linguistic). Led to the pivot away from standard LLM approaches.

## 2. Web Design as the Ultimate Goal
* **Description:** The idea that the entirety of the architecture should be explicitly hardcoded or optimized solely for web design generation.
* **Reason for Rejection:** Design is an evaluation domain, not a foundational primitive. Optimizing only for design ignores the broader principles of general intelligence.

## 3. Generic Factorized Rule Modules Generalize Compositionally on Their Own
* **Description:** The hypothesis that merely factoring "which operator" from "which operand" in an architecture — with either a learned or fixed operand encoding — is sufficient for compositional generalization to unseen combinations.
* **Reason for Rejection:** Empirically falsified in EXP-002 across three separate attempts (learned embedding, fixed sin/cos features, and a weight-decay sweep from 0 to 1.0), all giving exactly 0% held-out accuracy. The architecture has enough free parameters to fit training data via solutions that don't generalize, and nothing in standard supervised training selects the generalizing one. A much more constrained version (2 parameters/operator matching the true symmetry family) does generalize — see `docs/03_foundations/ACCEPTED.md`, item 6.

## 4. Training-Loss-Driven or Fixed-Penalty-Regularized Structure Selection
* **Description:** The hypothesis that a model can automatically discover which of several candidate hypothesis-class families fits each sub-task by jointly training a soft mixture gate via ordinary cross-entropy, optionally with an added complexity/parsimony penalty.
* **Reason for Rejection:** Empirically falsified in EXP-003. Naive joint training collapsed the gate toward the more expressive (non-generalizing) family for every operator, including ones where the simple family was correct, achieving exactly 0% held-out accuracy at every tested penalty strength (0, 0.1, 0.5). At the higher penalty strength, the gate moved in a genuinely unpredicted direction — toward the simple family hardest on the one operator that should NOT use it. Validation-driven selection (choosing based on measured held-out performance, not training loss) does work — see `docs/03_foundations/ACCEPTED.md`, item 7.

## 5. A Single Unified EVALUATE Function (EXP-009)
* **Description:** The hypothesis that one label-free evaluation signal — computed from a system's own internal state, without the true label — could serve all of ARS-001's named EVALUATE consumers: memory gating, computation-family selection, planning termination, self-regulation, and deployment readiness. This was ARS-001 Section 5.7's central untested assumption, and the reason EVALUATE was identified as the specification's single most load-bearing function.
* **Reason for Rejection:** Empirically falsified in EXP-009. Three candidates (entropy, ensemble disagreement, a learned self-assessment head) all matched the true-label oracle at memory-gating and excelled at wrongness-detection — then entropy and the self-assessment head failed completely (0% held-out accuracy, every one of 5 seeds) at computation-family selection, always choosing the more expressive, non-generalizing option. The mechanism: both signals are proxies for output sharpness, and an overfit family achieves *higher* sharpness on selection-adjacent data precisely because it has overfit to it — the identical failure mode EXP-003 already proved for raw training loss, recurring one layer down. EVALUATE splits into EVALUATE-LOCAL (validated label-free — see `docs/03_foundations/ACCEPTED.md`, item 8) and EVALUATE-GENERALIZATION (no validated label-free realization found; ensemble disagreement partially works but is unreliable, 0.250 ± 0.158 against a 0.750 oracle).
* **Notes:** `docs/08_requirements/ARS-001.md` Section 6 and `docs/04_architecture/ACA_v0.4_Architecture.md` Section 2.2 record the resulting revision to the functional model and architecture. Per this file's and ARS-001's own historical-integrity rules, the original unified-EVALUATE hypothesis is preserved in both documents as the tested-and-falsified starting point, not deleted or silently corrected.

---

**Purpose:** Archive failed or rejected hypotheses for historical reference.
**Current Status:** Historical Record
**Historical Context:** Items 1–2 accumulated through the Council methodology; items 3–5 (added 2026-07-18) are entries in this file established by empirical falsification rather than argument, per DEC-005.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `docs/03_foundations/ACCEPTED.md`, `docs/01_background/HISTORY.md`, `docs/06_experiments/Completed.md`, `docs/08_requirements/ARS-001.md` (Section 6)

