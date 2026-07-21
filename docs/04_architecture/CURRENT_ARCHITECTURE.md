**Status: Active** (revised 2026-07-18 — ACA v1.0 supersedes v0.4)

# Current Architecture

## The current architecture is ACA v1.0 — see `docs/04_architecture/ACA_v1.0_Architecture.md`

ACA v1.0 is a full architecture specification (state model, computational functions, execution/learning/memory/evaluation pipelines, lifecycle, dependency graph, risk register, assumptions register, experimental roadmap, revision policy) synthesized from `docs/08_requirements/ARS-001.md`. It supersedes v0.4 by formalizing EVALUATE as three realizations — LOCAL (validated), GENERALIZATION (validated only with real labels; falsified label-free), and STRUCTURAL (a new, theoretically-motivated but untested third category, verifying outputs against known domain invariants rather than statistical confidence or held-out labels) — and by adding a third state substrate, S_invariants, to hold that domain knowledge.

Every component in ACA v1.0 is traced back to a specific function, a specific ARS-001 requirement, and an explicit evidence tier. This file is kept short and points there rather than duplicating it, per the repository's "one canonical source" rule.

## Architecture Evolution

* **v0.1:** Static pipeline CCA model. (Archived — `archive/CCA_v0.1.md`.)
* **v0.2:** Conceptual stage of dynamic adaptive computation, pursued via council-driven first-principles derivation (Knowledge Foundation Council). Superseded by DEC-005 without ever producing a validated primitive.
* **v0.3:** Build-experiment-validate. Two components validated in isolation (episodic memory allocator, EXP-001; rule/family-selection module, EXP-002/003) plus their composability (EXP-004). No architecture yet.
* **v0.4:** First concrete architecture — `ACA_v0.4_Architecture.md` (preserved). Its EVALUATE design was later falsified in part by EXP-009.
* **v1.0 (current):** EVALUATE formalized as three realizations (LOCAL/GENERALIZATION/STRUCTURAL); S_invariants added as a third state substrate; full lifecycle, risk, and roadmap detail — see `ACA_v1.0_Architecture.md`. Synthesized, not yet implemented as an integrated system.

## Relationship to the Archived CCA Architecture

CCA v0.1 introduced a static sequence of cognitive steps (Observation → Difference → Pattern → Concept → Memory → Composition → World Model → Prediction → Planning). ACA v1.0 does not inherit this pipeline structure — it was derived independently from ARS-001's functional decomposition, not from revising CCA's stages. Where the two overlap (e.g., CCA's "Memory" concept and ACA v1.0's S_episodic/S_semantic substrates), it is coincidental convergence on a similar idea, not lineage — ACA v1.0's design should be justified entirely by its own traceability table, not by resemblance to CCA.

---

**Purpose:** Orient a reader toward the actual current architecture and its evolution; the architecture's substantive content lives in `ACA_v1.0_Architecture.md`.
**Current Status:** Active
**Historical Context:** See "Architecture Evolution" above.
**Known Facts:** See `ACA_v1.0_Architecture.md` Section 2 (per-function evidence) and Section 11 (falsification table).
**Hypotheses:** See `ACA_v1.0_Architecture.md` Sections 1–2 and 12–14.
**Unknowns:** See `ACA_v1.0_Architecture.md` Sections 12 (roadmap) and 13 (risk register).
**References:** `archive/CCA_v0.1.md`, `docs/08_requirements/ARS-001.md`, `docs/04_architecture/ACA_v0.4_Architecture.md`, `docs/04_architecture/ACA_v1.0_Architecture.md`, `docs/06_experiments/Completed.md`, `docs/05_research/Decisions.md` (DEC-005)
