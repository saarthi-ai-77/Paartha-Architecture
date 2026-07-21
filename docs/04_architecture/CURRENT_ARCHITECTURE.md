**Status: Active** (revised 2026-07-18 — a concrete architecture now exists; see redirect below)

# Current Architecture

## The current architecture is ACA v0.4 — see `docs/04_architecture/ACA_v0.4_Architecture.md`

As of 2026-07-18, this project has a designed architecture for the first time. It was derived exclusively from the four fundamental functions (EVALUATE, SELECT, UPDATE, COMPOSE) and state substrates identified in `docs/08_requirements/ARS-001.md` — not from Transformers, MoE, RNNs, memory networks, or cognitive architectures, which are used in that document only as reference implementations for individual components, never as overall templates. Every component in ACA v0.4 is traced back to a specific function, a specific ARS-001 requirement, and an explicit evidence tier (Validated by ACA experiments / Supported by external literature / Reasoned hypothesis / Speculative) — see that document's Section 6 for the full traceability table.

This file is kept short and points there rather than duplicating it, per the repository's "one canonical source" rule. The remaining sections below preserve historical context (why the project didn't have an architecture until now).

## Architecture Evolution

* **v0.1:** Static pipeline CCA model. (Archived — `archive/CCA_v0.1.md`.)
* **v0.2:** Conceptual stage of dynamic adaptive computation, pursued via council-driven first-principles derivation (Knowledge Foundation Council). Superseded by DEC-005 without ever producing a validated primitive.
* **v0.3:** Build-experiment-validate. Two components validated in isolation (episodic memory allocator, EXP-001; rule/family-selection module, EXP-002/003) plus their composability (EXP-004). No architecture yet — requirements work (ARS-001) came first, deliberately.
* **v0.4 (current):** First concrete architecture — see `ACA_v0.4_Architecture.md`. Designed, not yet implemented as an integrated system beyond the isolated/paired validations already completed.

## Relationship to the Archived CCA Architecture

CCA v0.1 introduced a static sequence of cognitive steps (Observation → Difference → Pattern → Concept → Memory → Composition → World Model → Prediction → Planning). ACA v0.4 does not inherit this pipeline structure — it was derived independently from ARS-001's functional decomposition, not from revising CCA's stages. Where the two overlap (e.g., CCA's "Memory" concept and ACA v0.4's S_episodic/S_semantic substrates), it is coincidental convergence on a similar idea, not lineage — ACA v0.4's design should be justified entirely by its own traceability table, not by resemblance to CCA.

---

**Purpose:** Orient a reader toward the actual current architecture and its evolution; the architecture's substantive content lives in `ACA_v0.4_Architecture.md`.
**Current Status:** Active
**Historical Context:** See "Architecture Evolution" above.
**Known Facts:** See `ACA_v0.4_Architecture.md` Section 6 for what is and isn't validated per component.
**Hypotheses:** See `ACA_v0.4_Architecture.md` Sections 1–3 and 6.
**Unknowns:** See `ACA_v0.4_Architecture.md` Section 7.
**References:** `archive/CCA_v0.1.md`, `docs/08_requirements/ARS-001.md`, `docs/04_architecture/ACA_v0.4_Architecture.md`, `docs/06_experiments/Completed.md`, `docs/05_research/Decisions.md` (DEC-005)
