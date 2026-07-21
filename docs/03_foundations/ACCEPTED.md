**Status: Active**

# Accepted Principles

This document catalogues the foundational principles that have survived rigorous Council critique and are currently accepted as true within the context of this research.

## 1. The Limitation of Universal Computation
* **Description:** Intelligence should not be assumed to emerge optimally from one universal computational framework.
* **Confidence:** High
* **Notes:** This is the core principle driving the entire research effort.

## 2. Structural Diversity in Cognition
* **Description:** Different classes of cognition intrinsically require fundamentally different computational primitives.
* **Confidence:** High
* **Notes:** For example, spatial reasoning requires a different computational structure than temporal sequence prediction.

## 3. Dynamic Adaptation
* **Description:** Computation itself must dynamically adapt according to the structure of the problem at hand, rather than forcing the problem into a static pipeline.
* **Confidence:** High
* **Notes:** Requires a robust scheduler.

## 4. Language as Interface
* **Description:** Language is an interface for expressing and translating intelligence, not the underlying substrate of intelligence itself.
* **Confidence:** High
* **Notes:** Current LLMs conflate the interface with the intelligence.

## 5. Competence-Aware Memory Allocation Beats Naive Caching (EXP-001)
* **Description:** Under a fixed, limited episodic-memory capacity, a write/eviction policy that stores only what the parametric backbone currently gets wrong, and evicts whatever it has since mastered, achieves substantially higher tail-fact recall than naive caching (write on first sight, evict at random) at the identical capacity.
* **Confidence:** High — empirically confirmed, 5 seeds, ~2x tail recall improvement (18.2% vs 9.8%), consistent mechanism (naive caching wastes 73% of capacity on already-mastered facts vs. 2% for the competence-aware policy).
* **Notes:** Toy-task validation only (synthetic, near-orthogonal keys, exact-match retrieval). Not yet tested integrated into a real language-model backbone. See `docs/06_experiments/Completed.md`, EXP-001.

## 6. Compositional Generalization Requires Matching the Hypothesis Class to the True Structure (EXP-002)
* **Description:** A generic factorized (operator × operand) architecture does not reliably generalize to unseen combinations, regardless of whether the operand encoding is learned or fixed, and regardless of L2 regularization strength — because it has enough free parameters to fit training data via many solutions, only some of which generalize, and nothing in standard training selects the generalizing one. Constraining the operator to the actual symmetry family the true function belongs to (e.g. rotation/reflection, 2 parameters instead of ~30) gives exact, parameter-correct generalization.
* **Confidence:** High — empirically confirmed, 5 seeds, exact recovery of ground-truth parameters (2π/10, π), 100% held-out accuracy on in-family operators, correct 0% (not a partial score) on the one operator genuinely outside the family.
* **Notes:** This is a real design constraint, not a general endorsement of "rule modules" — it comes with a major open problem (how does a rule module discover the right family without being told?), tracked as an open question below. See `docs/06_experiments/Completed.md`, EXP-002.

## 7. Structure/Family Selection Must Be Driven by Held-Out Generalization, Not Training Loss (EXP-003)
* **Description:** Naive end-to-end training of a mixture over candidate hypothesis-class families always drifts toward the more expressive, non-generalizing option, because it fits training data at least as well. A fixed-strength complexity penalty does not reliably fix this either (and can misfire in unpredicted directions). Reserving a held-out selection split, and choosing per-case whichever family generalizes better on it, correctly recovers the right family and matches oracle (hand-picked) accuracy.
* **Confidence:** High — empirically confirmed, 5 seeds; naive and parsimony-regularized selection both measured at exactly 0% held-out accuracy across all settings tested, validation-driven selection matched the EXP-002 oracle exactly (75%).
* **Notes:** See `docs/06_experiments/Completed.md`, EXP-003, for an important caveat: the mechanism can select the "wrong" family for an operator that no available family actually handles, without this being detectable from the final metric alone.

## 8. EVALUATE-LOCAL Generalizes Label-Free; EVALUATE-GENERALIZATION Does Not (EXP-009)
* **Description:** A single per-instance confidence/discrepancy signal (entropy, ensemble disagreement, or a learned self-assessment head — none requiring the true label at decision time) is statistically interchangeable with the true-label oracle for memory write/eviction gating, and strong (entropy/ensemble: 0.990 AUC) at separating inputs the system will get right from ones it will get wrong. This validates that EVALUATE-LOCAL is a genuinely general, label-free-realizable function, not merely EXP-001's narrow fixed-threshold instance.
* **Confidence:** High — empirically confirmed, 5 seeds, three independent candidate realizations converging on the same result.
* **Notes:** This is the positive half of EXP-009's finding — see item 4 in `docs/03_foundations/REJECTED.md` for the negative half (the same candidates fail completely at a structurally different use). See `docs/06_experiments/Completed.md`, EXP-009.

---

**Purpose:** Track principles that act as the current ground-truth for the project.
**Current Status:** Active
**Historical Context:** Established post CCA v0.1 pivot. Items 1–4 predate DEC-005 and reflect philosophical consensus from the Council era; items 5–8 (added 2026-07-18) are principles in this file established by empirical experiment rather than argument, per DEC-005's build-experiment-validate methodology.
**Known Facts:** Items 1–4 rely on philosophical consensus from the Council; items 5–8 rely on reproducible, multi-seed experimental results with code preserved in `experiments/`.
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `RESEARCH_PHILOSOPHY.md`, `docs/03_foundations/REJECTED.md`, `docs/06_experiments/Completed.md`, `docs/05_research/Decisions.md` (DEC-005), `docs/08_requirements/ARS-001.md` (Section 6)

