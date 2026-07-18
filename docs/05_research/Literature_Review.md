**Status: Active** (populated 2026-07-18 per DEC-005)

# Literature Review

*This document previously stated it would be populated only from Scientific Reviewer council outputs. Under the build-experiment-validate methodology (DEC-005), literature connections are instead identified as they become relevant to a specific experiment's design or interpretation, and recorded here directly rather than waiting on a council role.*

## Relevant to EXP-001 (Episodic Memory Allocation)
* **kNN-LM (Khandelwal et al.) and RETRO (Borgeaud et al.)** — prior demonstrations that a smaller parametric model plus a retrieval/memory mechanism can match a larger pure-parametric model's performance, by offloading long-tail memorization to the retrieval component. EXP-001's contribution is narrower and more specific: it isolates the *write/eviction policy* under a fixed, limited memory budget, which these works do not directly address (they generally index available data more exhaustively rather than testing competence-aware, capacity-constrained allocation).

## Relevant to EXP-002 and EXP-003 (Rule Module, Family Selection)
* **Fodor & Pylyshyn (1988), "Connectionism and Cognitive Architecture"** — the foundational systematicity critique of connectionist models: symbolic, rule-governed knowledge exhibits systematic generalization that plain pattern-matching historically fails at. EXP-002 is a small, direct, from-scratch empirical test of a version of this critique, not a citation-only appeal to it.
* **SCAN benchmark literature (Lake & Baroni and follow-ups)** — empirical documentation of compositional-generalization failures in sequence models. EXP-002's held-out-combination task is a much smaller, simplified analogue of the same failure mode, built to isolate *why* it happens (excess free parameters, no training signal for generalization) rather than just document that it happens.
* **Geometric Deep Learning (Bronstein, Bruna, Cohen, Veličković)** — the broader research program proposing that architectures should be derived from the symmetry/invariance structure of their data, in the spirit of the Erlangen Program. EXP-002's finding — that constraining an operator to its true symmetry group (rotation/reflection) gives exact generalization where a generic factorization fails — is a small, self-contained confirmation of this program's central thesis, arrived at independently through our own experiment rather than adopted from the literature. (Note: this literature connection was first surfaced in the quarantined `council/main` thread — see `docs/03_foundations/OPEN.md` — before its provenance issue was identified; the connection itself is sound regardless of that thread's quarantine status, since it rests on established, citable external work, not on the quarantined thread's own claims.)
* **Model selection / regularization literature (general)** — EXP-003's finding that L2/parsimony regularization does not reliably recover a generalizing solution is consistent with the broader understood limitation that "small weights" and "the generalizing solution" are not guaranteed to coincide outside of specific, provable cases (e.g. certain convex settings) — EXP-003 demonstrates a case where they clearly do not coincide, empirically, rather than relying on this as received wisdom.

## Explicitly Not Yet Reviewed
* Broader memory-augmented neural network literature (Neural Turing Machines, Differentiable Neural Computers) — relevant to any future, richer memory-module design; not yet compared against EXP-001's simpler slot-memory approach.
* Mixture-of-Experts and routing literature — directly relevant to the still-open Dynamic Scheduling problem (`docs/04_architecture/Dynamic_Computation.md`); not yet reviewed against EXP-003's validation-driven-selection constraint.

---

**Purpose:** Track literature connections relevant to validated or in-progress experiments.
**Current Status:** Active
**Historical Context:** Previously a placeholder deferring to council outputs; populated 2026-07-18 per DEC-005 to track literature directly against experiments as they're run.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** Coverage is partial — see "Explicitly Not Yet Reviewed" above.
**References:** `docs/06_experiments/Completed.md`
