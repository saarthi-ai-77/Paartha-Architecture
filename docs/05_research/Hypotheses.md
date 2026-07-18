**Status: Active**

# Hypothesis Register

This register tracks all formal hypotheses formulated by the research program.

**HYP-001 through HYP-003 (pre-DEC-005) have moved to `docs/archive/Previous_Hypotheses.md`** — they were never tested empirically under either methodology and are preserved there as historical record rather than restated here. The hypotheses below are from the current build-experiment-validate line and are each tied to a specific, executed experiment.

### HYP-004: Competence-Aware Memory Allocation
* **Description:** Under fixed episodic-memory capacity, a write/eviction policy driven by the parametric backbone's own current competence (write what it gets wrong, evict what it's mastered) outperforms naive caching (write on first sight, evict at random) on rare/long-tail fact recall.
* **Status:** CONFIRMED.
* **Confidence:** High.
* **Evidence:** EXP-001 — 5 seeds, ~2x tail recall (18.2% vs 9.8%), consistent mechanism (73% vs 2% of capacity wasted on already-mastered facts).
* **Next Action:** Test under non-orthogonal (confusable) keys; integrate with a real backbone (see `docs/03_foundations/OPEN.md`).

### HYP-005: Compositional Generalization Requires Matched Hypothesis-Class Constraints
* **Description:** A generic, high-parameter factorized rule module does not generalize to unseen combinations regardless of encoding choice or regularization; a module constrained to the true symmetry family of its domain does, exactly.
* **Status:** Original general form REJECTED; narrow constrained form CONFIRMED.
* **Confidence:** High.
* **Evidence:** EXP-002 — three falsification attempts (learned embedding, fixed features, weight-decay sweep 0–1.0, all 0% held-out) followed by exact, parameter-correct generalization (100% held-out, recovered ground-truth rotation angles) once constrained to the correct family.
* **Next Action:** Family discovery for domains without a pre-known correct family (see EXP-005 in `docs/07_future/Roadmap.md`).

### HYP-006: Structure Selection Must Be Validation-Driven
* **Description:** Automatic selection among candidate hypothesis-class families must be driven by measured held-out generalization, not training loss or a fixed complexity penalty, or it will collapse toward the more expressive, non-generalizing option.
* **Status:** Naive and parsimony-regularized selection REJECTED; validation-driven selection CONFIRMED.
* **Confidence:** High.
* **Evidence:** EXP-003 — naive and parsimony-regularized selection both measured at exactly 0% held-out accuracy across all tested settings; validation-driven selection matched oracle accuracy (75%) exactly.
* **Next Action:** Test at larger family-library scale; investigate the unexplained parsimony-penalty "backwards" pattern noted in `docs/06_experiments/Completed.md`.

---

**Purpose:** Register and track the status of all scientific hypotheses.
**Current Status:** Active
**Historical Context:** Formulated after the pivot to adaptive computation; revised 2026-07-18 per DEC-005 to separate untested pre-pivot hypotheses (moved to `docs/archive/Previous_Hypotheses.md`) from experimentally confirmed/rejected ones.
**Known Facts:** HYP-004 through HYP-006 are each backed by reproducible, multi-seed experimental code in `experiments/`.
**Hypotheses:** See above.
**Unknowns:** Scale transfer of all three (see `docs/03_foundations/OPEN.md`).
**References:** `docs/04_architecture/CURRENT_ARCHITECTURE.md`, `docs/06_experiments/Completed.md`, `docs/archive/Previous_Hypotheses.md`

