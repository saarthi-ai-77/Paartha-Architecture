**Status: Active** (revised 2026-07-18 — ACA v0.4 now exists; prior "no single architecture yet" framing superseded)

# ACA Overview

This is a short entry point into the architecture documentation; `CURRENT_ARCHITECTURE.md` points to `ACA_v0.4_Architecture.md`, the canonical, detailed architecture document. This page summarizes how the sub-topic documents in this directory relate to it.

## The Picture as of ACA v0.4

ACA now has a designed architecture, built from four fundamental functions (EVALUATE, SELECT, UPDATE, COMPOSE) and two state substrates (S_episodic, S_semantic), derived via `docs/08_requirements/ARS-001.md`, not copied from any existing AI architecture:

| Component | Status | Document |
|---|---|---|
| S_episodic / S_semantic substrates, memory write/eviction/consolidation | Write/eviction **Validated** (EXP-001); consolidation **Reasoned hypothesis** | `Memory.md`, `ACA_v0.4_Architecture.md` §1, §2.4 |
| COMPOSE library (structure-matched computation types) | **Validated, narrow** (EXP-002, EXP-003) | `Cognitive_Primitives.md`, `ACA_v0.4_Architecture.md` §2.1 |
| EVALUATE (supervised realization validated; unsupervised realization not) | Partial — see traceability table | `ACA_v0.4_Architecture.md` §2.2 |
| SELECT (family choice validated; action policy, compute allocation not) | Partial — see traceability table | `ACA_v0.4_Architecture.md` §2.3 |
| Component composability | **Validated** (EXP-004), under a disjoint-parameter design only | `docs/06_experiments/Completed.md` |
| Routing/scheduling logic | **Designed, not implemented or tested** | `Dynamic_Computation.md`, `ACA_v0.4_Architecture.md` §3 |

Each validated piece's confidence comes from a specific, reproducible, multi-seed experiment with code preserved in `experiments/`, not from architectural argument alone. `ACA_v0.4_Architecture.md`'s Section 6 traceability table is the single authoritative source for exactly what is and isn't validated per component — the per-topic files in this directory summarize and link to it rather than duplicating it.

---

**Purpose:** Give a one-page orientation to the architecture documentation for a new reader.
**Current Status:** Active
**Historical Context:** Previously described a set of validated components with no architecture connecting them; revised 2026-07-18 once ACA v0.4 was designed.
**Known Facts:** See the table above and `ACA_v0.4_Architecture.md` Section 6.
**Hypotheses:** N/A — this page only summarizes, it does not introduce new claims.
**Unknowns:** See `docs/03_foundations/OPEN.md` and `ACA_v0.4_Architecture.md` Section 7.
**References:** `docs/04_architecture/CURRENT_ARCHITECTURE.md`, `docs/04_architecture/ACA_v0.4_Architecture.md`, `docs/08_requirements/ARS-001.md`, `docs/06_experiments/Completed.md`
