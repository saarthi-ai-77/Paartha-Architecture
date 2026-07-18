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

---

**Purpose:** Archive failed or rejected hypotheses for historical reference.
**Current Status:** Historical Record
**Historical Context:** Items 1–2 accumulated through the Council methodology; items 3–4 (added 2026-07-18) are the first entries in this file established by empirical falsification rather than argument, per DEC-005.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `docs/03_foundations/ACCEPTED.md`, `docs/01_background/HISTORY.md`, `docs/06_experiments/Completed.md`

