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

**ACA has reached v1.0 (`docs/04_architecture/ACA_v1.0_Architecture.md`), a full architecture specification synthesized from ARS-001** (state model, computational functions, execution/learning/memory/evaluation pipelines, dependency graph, risk register, assumptions register, revision policy). EVALUATE is now formalized as **three** realizations, not two: LOCAL (validated), GENERALIZATION (validated only with real labels; falsified label-free by EXP-009), and **STRUCTURAL** (new — verification against known domain invariants rather than statistical confidence, `docs/08_requirements/ARS-001.md` §7 — a reasoned hypothesis, not yet tested, but theoretically targeted at exactly the mechanism that broke GENERALIZATION).

**The program has moved from architecture design to validation** (`docs/09_validation/IVS-001.md`). The roadmap is now IVS-001 Section 6, re-ranked by blast radius (how much changes if the experiment fails) rather than chronologically or even by the impact-ranking ACA v1.0 originally proposed:

1. **EXP-016 (new, now highest priority): does EVALUATE-LOCAL's calibration hold up under extended, concurrent continual learning**, rather than only on the static post-training snapshot EXP-009 tested? Ranked above EXP-015 because a failure here *retracts already-validated infrastructure* relied on everywhere (ME-03, SR-01/02) — a bigger shock than a new capability not panning out.
2. **EXP-015: does structural/algebraic-consistency evaluation correctly reject the non-generalizing family, label-free?** If it fails, S_invariants and EVALUATE-STRUCTURAL are removed.
3. **EXP-011 + EXP-017 (folded together): routing-as-episodic-content, including a longitudinal regression check** (does a routing decision ever get evicted as "redundant" while still load-bearing?) — sharper than the original EXP-011 scope.
4. **EXP-013, EXP-014, EXP-010, EXP-012** — unchanged relative ordering, all lower blast-radius than the above.

A prerequisite audit (IVS-001, performed before this ranking) also pruned ACA v1.0 itself: EVALUATE-LOCAL now defaults to entropy alone (not three co-required realizations); variable compute-amount SELECT is excluded pending evidence it's needed; RC-03 is confirmed to be S_episodic reused, not separate machinery; a key-namespacing gap in the shared-substrate design was patched directly rather than deferred to an experiment. See `docs/04_architecture/ACA_v1.0_Architecture.md` Section 17 for the full list. EXP-005/006/007/008 remain relevant but are superseded in priority by the above.

## Update Following ACA-MVP-001 Benchmark A / EXP-018 (2026-07-22)

**The program moved from validation planning to actual real-Transformer execution** (`docs/11_mvp/ACA-MVP-001.md`), ahead of the full IVS-001 minimal integrated prototype, to test ME-03 (competence-gated memory) in isolation at real scale first. Result: **the pre-registered success criterion failed** — competence-gated memory showed zero measurable advantage over naive caching or no memory at all under staged, non-rehearsed continual training, with memory coverage of the oldest facts at exactly 0.0 at evaluation time. Full account: `docs/06_experiments/Completed.md` (EXP-018); architecture-level consequences: `docs/04_architecture/ACA_v1.0_Architecture.md` Section 18; validation-strategy consequences: `docs/09_validation/IVS-001.md` Section 9.

**Immediate next step, not a new item but this list's own pre-registered stretch ablation (`docs/11_mvp/ACA-MVP-001.md` §4):** test active consolidation-via-replay (EXP-010) on the same Benchmark A task, same constrained capacity — the one candidate mechanism that could plausibly rescue ME-03 under staged training. This is now higher priority than its position in the numbered list above (#4, folded in with EXP-013/014/012) reflects — that ranking assumed EXP-010 was a lower-stakes refinement; EXP-018 shows it may be a precondition for ME-03's validated status to extend beyond a static distribution at all. The numbered list above is left as originally written, per this document's own revision discipline; this note records why it is due for re-ranking, not a silent re-ordering.

**EXP-010 has since run (same day) and also failed:** a one-time replay burst at each stage boundary produced no measurable improvement (0.160 ± 0.028 vs. 0.158 ± 0.027 baseline — `docs/06_experiments/Completed.md`, EXP-010). Benchmark A's full ablation set (core + stretch) is now complete; both ME-03 itself and its most direct minimal fix are falsified for staged, non-rehearsed continual training. Two structurally larger, untested candidates remain open — interleaved rehearsal throughout subsequent-stage training, and explicit weight-importance protection (EWC-style) — neither yet scheduled. Benchmark B (SCAN, an independent claim unaffected by this outcome) is the appropriate next benchmark; ME-03's open status is tracked here, not a blocker.

**Benchmark B has since run (2026-07-23) and succeeded decisively:** structure-matched COMPOSE (fixed, real-data-verified SCAN grammar + a 326-parameter learned lookup) scored 100.000% ± 0.000% exact-match on real SCAN `addprim_jump`, against 0.71% ± 0.39% for a 681,481-parameter generic Transformer (closely matching Lake & Baroni's own published ~1% baseline) — a ~141x margin against a 2x pre-registered threshold (`docs/06_experiments/Completed.md`, EXP-020). This directly extends EXP-002's toy-scale finding to a real, cited benchmark. **The open problem is unchanged, not resolved by this result:** EXP-005 (family discovery — can a system find this grammar itself, rather than have it hand-specified?) remains the central unresolved question, exactly as EXP-002 first flagged it. Benchmark C (joint test) is next per the Implementation Order above.

## Dual-Track Directive (2026-07-23): CTX-001 and EXP-019

Per CTO directive, research is now split into two parallel tracks. **Track A** continues this roadmap unchanged (Benchmark B in progress). **Track B** produced `docs/12_cognition/CTX-001.md`, investigating whether EXP-018/010, conversation-context representation, and "known unknown" tracking share a root cause. Two concrete additions to this roadmap, both **proposed, not yet run or adopted**:

* **EXP-019 (proposed): Structured Working State vs. Schema-Tagged S_episodic for Multi-Turn Context.** Falsification test for CTX-001's tentative "S_working" substrate — compare a dedicated small, fixed-field, overwrite-in-place context representation against the existing competence-gated S_episodic policy under a fourth schema tag, over an extended multi-turn task. If the schema-tagged S_episodic approach shows no measurable degradation as interaction length grows, S_working is unnecessary and RC-03's original "~90% reducible" framing (`docs/08_requirements/ARS-001.md` §1.4) was, in practice, closer to 100%. Not yet scheduled relative to EXP-010's follow-ups (interleaved rehearsal, weight-protection) — blast-radius ranking between them has not been done.
* **"Gap Curriculum Generation" (proposed, offered to `docs/10_deployment/DAS-001.md`, not self-adopted in that document):** a candidate fifth learning timescale for periodic, scheduled pattern-detection across accumulated "unknown"-schema episodic entries — CTX-001 §3 shows this is the one part of the proposed unknown-handling pipeline that doesn't reduce to existing functions applied per-query, though it does reduce to existing functions applied per-corpus, on a schedule. DAS-001 has not yet reviewed this against its own four-timescale model.

## Outstanding Unknowns
See `docs/07_future/Unknowns.md` for the full, current list (this section previously duplicated it inline; consolidated 2026-07-18 to avoid drift between the two files).

## Research Risks
* **Toy-task overfitting to the researcher's own expectations:** every completed experiment (EXP-001–003) was designed by the same process that interprets its results. Mitigation: the falsification track record so far (EXP-002's original hypothesis, EXP-003's naive/parsimony conditions) shows the process does produce and report negative results rather than only confirming hypotheses — but this risk doesn't go away and should be watched for in EXP-004 onward.
* **Scale-transfer risk:** every validated finding is on a small synthetic task. None of it has been tested at any scale closer to a real SLM. This is the single biggest open risk to the entire roadmap.
* **Scheduler complexity:** as before — a dynamic scheduler could become a bottleneck or an overly rigid rule engine, defeating the purpose of adaptive computation. Now additionally informed by EXP-003: a scheduler trained the naive way is expected to fail structurally, not just be suboptimal.

---

**Purpose:** Outline the forward-looking trajectory of the research program.
**Current Status:** Active. ACA-MVP-001 Benchmark A complete, including its stretch ablation (2026-07-22) — pre-registered success criterion failed (EXP-018), most direct candidate fix also failed (EXP-010). Benchmark B complete (2026-07-23) — pre-registered success criterion exceeded decisively (EXP-020, ~141x vs. a 2x threshold). Dual-track directive (2026-07-23) added Track B (CTX-001) alongside Track A.
**Historical Context:** Revised 2026-07-18 per DEC-005. The prior RP-001…RP-006 taxonomy-first roadmap (itself a revision of an earlier Phase 1–4 plan per DEC-004) is preserved in `docs/archive/Deprecated.md`. Updated 2026-07-22 following EXP-018, then again the same day following EXP-010. Updated 2026-07-23 with CTX-001's proposed EXP-019/"Gap Curriculum Generation," then again the same day following EXP-020 (Benchmark B).
**Known Facts:** EXP-001 through EXP-004, EXP-009, EXP-018, EXP-010, EXP-020 complete and validated/falsified as documented in `docs/06_experiments/Completed.md`.
**Hypotheses:** N/A
**Unknowns:** See `docs/07_future/Unknowns.md`. Whether ME-03 survives staged continual training under interleaved rehearsal or explicit weight-protection — both untested, both larger changes than what's been ruled out. Whether EXP-019 confirms or falsifies CTX-001's S_working hypothesis. Whether EXP-005 (family discovery) can ever recover a grammar like EXP-020's without it being hand-specified — unchanged by EXP-020's success, still the central open problem.
**References:** `docs/03_foundations/OPEN.md`, `docs/06_experiments/Completed.md`, `docs/05_research/Decisions.md` (DEC-005), `docs/11_mvp/ACA-MVP-001.md`, `docs/12_cognition/CTX-001.md`

