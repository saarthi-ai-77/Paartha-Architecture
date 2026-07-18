**Status: Active** (populated 2026-07-18 per DEC-005; prior placeholder superseded)

# Planned Experiments

*Note: this file tracks experiments not yet run. Once an experiment is executed, its write-up moves to `docs/06_experiments/Completed.md` (or, if actively in progress, `Running.md`) with this entry marked accordingly.*

## EXP-004: Integration Test — Memory Allocator + Rule/Family-Selection Module
* **Objective:** Determine whether the two independently-validated components (EXP-001's competence-aware episodic memory allocator, and EXP-002/003's constrained, validation-selected rule module) can be combined into a single small model without either mechanism degrading the other.
* **Hypothesis:** A model containing both a memory pathway and a rule pathway will retain the validated benefits of each in isolation (tail-fact recall advantage from the memory allocator; exact compositional generalization from the rule module) when tested on a combined task requiring both kinds of knowledge.
* **Method:** Construct a synthetic task with two sub-components — a long-tail associative-recall slice (as in EXP-001) and a compositional operator-application slice (as in EXP-002/003) — routed to the appropriate validated component. Compare against (a) memory-only, (b) rule-only, and (c) a uniform baseline of matched parameter count.
* **Expected Outcome:** Combined model matches or exceeds each component's isolated performance on its respective task slice; no cross-interference (e.g. the memory write policy misfiring on rule-module inputs, or vice versa).
* **Status:** Next up — see `docs/07_future/Roadmap.md`.

---

**Purpose:** Document upcoming experiments designed to test currently open architectural questions.
**Current Status:** Active
**Historical Context:** Previously a bare placeholder. Populated 2026-07-18 alongside DEC-005's build-experiment-validate roadmap.
**Known Facts:** N/A — this file only tracks what hasn't been run yet.
**Hypotheses:** See EXP-004 above.
**Unknowns:** Outcome of EXP-004.
**References:** `docs/06_experiments/Completed.md`, `docs/06_experiments/PLANNED_EXPERIMENTS.md`, `docs/07_future/Roadmap.md`
