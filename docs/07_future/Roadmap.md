**Status: Active** (revised 2026-07-18 per DEC-005; prior RP-001…RP-006 roadmap preserved in `docs/archive/Deprecated.md`)

# Future Research

## Working Research Model (DEC-005)

`Propose a small, concrete, trainable mechanism` &rarr; `Implement it in code` &rarr; `Test against an honest baseline, multiple seeds` &rarr; `Report the result, including falsification` &rarr; `Diagnose and revise on failure` &rarr; `Promote to docs/03_foundations/ACCEPTED.md only after actually working`

Architecture is not derived from a prior knowledge taxonomy. It is built one validated component at a time, and any taxonomy this program eventually needs will be derived from what those components' experiments actually show.

## Current Roadmap

* **EXP-001: Episodic Memory Allocation** — ✅ Complete. Competence-aware write/eviction beats naive caching ~2x on tail-fact recall at equal capacity.
* **EXP-002: Rule Module for Compositional Generalization** — ✅ Complete. Falsified in general form; confirmed in a narrow, mechanistically-understood form (constrain the operator to the true symmetry family).
* **EXP-003: Automatic Family Selection** — ✅ Complete. Confirmed that selection must be validation-driven, not loss-driven.
* **EXP-004: Integration Test** — ✅ Complete. Confirmed: the two mechanisms compose in one model, one optimizer, without interference — under a disjoint-parameter design that deliberately did not test a shared substrate or learned routing (both remain open, see below).
* **EXP-005 (planned): Family Discovery** — Extend EXP-003's selection-among-a-known-library result toward discovering/constructing a suitable family for an unfamiliar domain — the central open problem flagged by EXP-002/003.
* **EXP-006 (planned): Shared-Substrate Integration** — Test whether the two pathways can share a real substrate (e.g. one token embedding space) without the rule pathway's validated constraint breaking, per EXP-004's flagged limitation.
* **EXP-007 (planned): Dynamic Scheduler Prototype** — Replace EXP-004's explicit, non-learned dispatch with a learned router, built to satisfy the validation-driven-selection constraint from EXP-003 (see `docs/04_architecture/Dynamic_Computation.md`).
* **EXP-008 (proposed, not yet run): Multi-Role Mentor Society vs. Single-Teacher Progressive Learning** — from an external research proposal, formally evaluated and logged at `docs/05_research/proposals/developmental_mentor_paradigm.md` (recommendation: Requires Prerequisite Research, not yet an accepted ACA direction). Tests whether a multi-role mentor society (separate explain/question/correct/fade roles) beats YODA-style single-teacher progressive learning on the EXP-002/003 rule-family task, measuring both sample efficiency and total compute cost including mentor inference.
* **Beyond EXP-006:** real-backbone/real-data integration, then a small trainable SLM POC benchmarked on English fluency (with the architecture kept extensible to code/math/reasoning, per standing design constraint — see conversational record and `docs/02_vision/Success_Criteria.md`), then India AI compute grant readiness.

## Immediate Research Priorities

**ARS-001 (`docs/08_requirements/ARS-001.md`) is now complete through two reduction passes, and architecture design may begin per its Section 5.9.** Its deeper functional-decomposition pass (Section 5) reduced the 15 requirements to 4 fundamental functions — EVALUATE, SELECT, UPDATE, COMPOSE — and reconfirmed, at a deeper level, that **EVALUATE** (the function underlying SR-01) is the single most load-bearing capability in the entire specification: SELECT and UPDATE both strictly depend on it, while COMPOSE does not. ACA has only validated a narrow, fixed-threshold instance of EVALUATE (EXP-001's surprise gate), not a general-purpose one — this is now the most consequential open question in the program at *both* the requirement and function level. ARS-001 also flagged the consolidation-transfer half of the memory pipeline (moving episodic content *into* semantic weights, not just evicting mastered entries) as a real, currently untested gap (ME-03).

1. EXP-004 complete and confirmed (see `docs/06_experiments/Completed.md`).
2. Next decision is between continuing the previously-planned EXP-005/006/007/008 versus prioritizing a new experiment that tests SR-01's generalization directly (does a calibrated self-evaluation signal generalize beyond EXP-001's fixed threshold?) or ME-03's consolidation-transfer gap — both surfaced by ARS-001 as more foundational than any single item on the pre-existing list. Not yet decided; awaiting direction.

## Outstanding Unknowns
See `docs/07_future/Unknowns.md` for the full, current list (this section previously duplicated it inline; consolidated 2026-07-18 to avoid drift between the two files).

## Research Risks
* **Toy-task overfitting to the researcher's own expectations:** every completed experiment (EXP-001–003) was designed by the same process that interprets its results. Mitigation: the falsification track record so far (EXP-002's original hypothesis, EXP-003's naive/parsimony conditions) shows the process does produce and report negative results rather than only confirming hypotheses — but this risk doesn't go away and should be watched for in EXP-004 onward.
* **Scale-transfer risk:** every validated finding is on a small synthetic task. None of it has been tested at any scale closer to a real SLM. This is the single biggest open risk to the entire roadmap.
* **Scheduler complexity:** as before — a dynamic scheduler could become a bottleneck or an overly rigid rule engine, defeating the purpose of adaptive computation. Now additionally informed by EXP-003: a scheduler trained the naive way is expected to fail structurally, not just be suboptimal.

---

**Purpose:** Outline the forward-looking trajectory of the research program.
**Current Status:** Active
**Historical Context:** Revised 2026-07-18 per DEC-005. The prior RP-001…RP-006 taxonomy-first roadmap (itself a revision of an earlier Phase 1–4 plan per DEC-004) is preserved in `docs/archive/Deprecated.md`.
**Known Facts:** EXP-001 through EXP-003 complete and validated/falsified as documented in `docs/06_experiments/Completed.md`.
**Hypotheses:** N/A
**Unknowns:** See `docs/07_future/Unknowns.md`.
**References:** `docs/03_foundations/OPEN.md`, `docs/06_experiments/Completed.md`, `docs/05_research/Decisions.md` (DEC-005)

