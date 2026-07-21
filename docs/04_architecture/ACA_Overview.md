**Status: Active** (revised 2026-07-18 — ACA v1.0 supersedes v0.4)

# ACA Overview

This is a short entry point into the architecture documentation; `CURRENT_ARCHITECTURE.md` points to `ACA_v1.0_Architecture.md`, the canonical, detailed architecture document. This page summarizes how the sub-topic documents in this directory relate to it.

## The Picture as of ACA v1.0

ACA now has a full architecture specification, built from three state substrates (S_episodic, S_semantic, and the new S_invariants) and four computational functions — one of which, EVALUATE, is now formalized as three distinct realizations rather than one:

| Component | Status | Document |
|---|---|---|
| S_episodic / S_semantic substrates, memory write/eviction/consolidation | Write/eviction **Validated** (EXP-001); consolidation **Reasoned hypothesis** | `Memory.md`, `ACA_v1.0_Architecture.md` §1, §6 |
| S_invariants (new) — externally-supplied domain invariants | **Reasoned hypothesis**, contingent on EXP-015 | `ACA_v1.0_Architecture.md` §1.3 |
| COMPOSE library (structure-matched computation types) | **Validated, narrow** (EXP-002, EXP-003) | `Cognitive_Primitives.md`, `ACA_v1.0_Architecture.md` §2.1 |
| EVALUATE-LOCAL (per-instance confidence) | **Validated**, label-free (EXP-001, EXP-009) | `ACA_v1.0_Architecture.md` §2.2a |
| EVALUATE-GENERALIZATION (does this generalize) | **Validated only with real labels** (EXP-002/003); label-free realizations **falsified** (EXP-009) | `ACA_v1.0_Architecture.md` §2.2b |
| EVALUATE-STRUCTURAL (new — verification against known invariants) | **Reasoned hypothesis**, untested — highest-priority next experiment (EXP-015) | `ACA_v1.0_Architecture.md` §2.2c, `docs/08_requirements/ARS-001.md` §7 |
| SELECT (family choice validated with labels; action policy, compute allocation not) | Partial — see traceability table | `ACA_v1.0_Architecture.md` §2.3 |
| Component composability | **Validated** (EXP-004), under a disjoint-parameter design only | `docs/06_experiments/Completed.md` |
| Routing/scheduling logic | **Designed** (now with a structural pre-filter), not implemented or tested | `Dynamic_Computation.md`, `ACA_v1.0_Architecture.md` §4 |

Each validated piece's confidence comes from a specific, reproducible, multi-seed experiment with code preserved in `experiments/`, not from architectural argument alone. `ACA_v1.0_Architecture.md` is the single authoritative source for exactly what is and isn't validated per component (Section 2's per-function tags, Section 11's falsification table) — the per-topic files in this directory summarize and link to it rather than duplicating it.

---

**Purpose:** Give a one-page orientation to the architecture documentation for a new reader.
**Current Status:** Active
**Historical Context:** Previously described ACA v0.4; revised 2026-07-18 once v1.0 formalized the EVALUATE split (EXP-009) and added structural evaluation (ARS-001 §7).
**Known Facts:** See the table above and `ACA_v1.0_Architecture.md` Section 2 and Section 11.
**Hypotheses:** N/A — this page only summarizes, it does not introduce new claims.
**Unknowns:** See `docs/03_foundations/OPEN.md` and `ACA_v1.0_Architecture.md` Sections 12–14.
**References:** `docs/04_architecture/CURRENT_ARCHITECTURE.md`, `docs/04_architecture/ACA_v1.0_Architecture.md`, `docs/08_requirements/ARS-001.md`, `docs/06_experiments/Completed.md`
