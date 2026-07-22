**Status: Active**

# Open Questions

This document tracks unresolved questions and active hypotheses that require further research, discussion, or empirical testing.

## 1. Taxonomy of Primitives
* **Question:** What is the complete, minimal set of computational primitives required to achieve generalized adaptive intelligence?
* **Status:** Active Research
* **Notes:** Needs extensive literature review and architectural experimentation.

## 2. Dynamic Scheduling Mechanism
* **Question:** How does the architecture dynamically detect problem structure and accurately schedule the correct primitive without relying on a static, rule-based router?
* **Status:** Active Research
* **Notes:** The core engineering challenge of the current phase.

## 3. Representation Substrate
* **Question:** If language is merely an interface, what is the universal internal representation substrate that allows different primitives to share data?
* **Status:** Active Research
* **Notes:** Relates closely to the 'Concept' and 'Pattern' ideas from CCA v0.1.

---

## Open Questions from the Build-Experiment-Validate Track (post-DEC-005, current)

* **The central open problem (from EXP-002/EXP-003):** how does a rule module discover which constrained transform family applies to an unknown domain, rather than requiring a human to hand-design the correct family per task? EXP-003 showed validation-driven selection works when at least one family in the library actually fits the operator — the harder, unresolved case is when the library needs to be extended or discovered, not just selected from.
* **Composability (targeted by EXP-004, in progress):** do the independently-validated memory-allocation mechanism (EXP-001) and rule/family-selection mechanism (EXP-002/003) interfere with each other when combined in one model, or compose cleanly?
* **Scale transfer:** every validated result so far is on a synthetic toy task with a small MLP-scale model. Does any of it survive integration into a real transformer/language-model backbone, on real (or semi-real) data? None of this has been tested yet.
* **Retrieval robustness:** EXP-001's memory retrieval was exact-match by construction (near-orthogonal random keys). Real facts/concepts are not orthogonal — does the competence-aware allocation policy still help once retrieval itself can misfire on similar/confusable keys?
* **Dynamic scheduling:** no experiment so far has built or tested an actual scheduler that routes between multiple heterogeneous computation types at runtime (see `docs/04_architecture/Dynamic_Computation.md`, `Scheduler.md`) — this remains open and is downstream of the composability question above.
* **Normative Foundation Council:** still approved in principle, still not commenced (`research/normative_foundation_council/README.md`) — gated on the architecture line producing something worth applying normative research to, not on any council methodology being frozen (that gating condition no longer applies post-DEC-005).
* **Developmental/mentor-society training proposal:** formally evaluated (`docs/05_research/proposals/developmental_mentor_paradigm.md`), recommendation "Requires Prerequisite Research" — not an accepted ACA direction. The proposed EXP-008 (multi-role mentor society vs. YODA-style single-teacher progressive learning) is logged in `docs/07_future/Roadmap.md` but not yet greenlit or run.
* **ARS-001 (`docs/08_requirements/ARS-001.md`):** Architecture Requirement Specification complete through two reduction passes — 15 requirements, 4 fundamental functions (EVALUATE/SELECT/UPDATE/COMPOSE).
* **ACA v1.0 (`docs/04_architecture/ACA_v1.0_Architecture.md`):** the full architecture specification, derived from ARS-001, fully traced (function → requirement → evidence), audited once for redundancy (Section 17). Synthesized, not yet implemented as an integrated system. EVALUATE is formalized as **three** realizations: LOCAL (validated, entropy is the required default), GENERALIZATION (validated only with real labels; falsified label-free by EXP-009), and **STRUCTURAL** (new, `docs/08_requirements/ARS-001.md` §7 — a reasoned hypothesis, not yet tested).
* **IVS-001 (`docs/09_validation/IVS-001.md`):** the Integrated Validation Strategy — the program has moved from architecture design to validation. **EXP-016** (does EVALUATE-LOCAL's calibration survive extended, concurrent continual learning, not just a static snapshot?) is now the highest-priority open question in the entire program — ranked above EXP-015 because failure would retract already-validated infrastructure, not just fail to add new capability. Full risk register, kill criteria, and re-ranked roadmap in IVS-001.
* **DAS-001 (`docs/10_deployment/DAS-001.md`):** the Deployment & Runtime Architecture Specification, derived from ACA v1.0 and IVS-001. Concludes ACA does not require a new runtime paradigm for anything currently validated — routing must be frozen at deployment (a direct consequence of EXP-009), memory can update live. Surfaces a new, untested failure mode (cross-timescale version skew between independently-updating semantic weights and routing tables) and corrects a proposed five-timescale learning model to four, adding a "Routing Revalidation" timescale the original proposal omitted. All conclusions tagged Reasoned hypothesis except where directly inherited from EXP-001–009.
* **ACA-MVP-001 / EXP-018 + EXP-010 (`docs/11_mvp/ACA-MVP-001.md`, `docs/06_experiments/Completed.md`):** the first real-Transformer experiments in this program. EXP-018 tested ME-03 (competence-gated memory) under staged, non-rehearsed continual training — the pre-registered 2x-improvement criterion **failed cleanly**; memory coverage of the oldest facts was exactly 0.0 at evaluation time in every seed, for both naive and competence-gated policies. Mechanism: point-in-time "mastered" is evicted as if permanently safe, exactly when it becomes vulnerable to being forgotten by subsequent training. Generalizes a risk IVS-001 §2 had scoped to routing entries only. EXP-010 then tested the most direct candidate fix (a one-time consolidation-replay burst at each stage boundary) — **also failed** (0.160 ± 0.028 vs. 0.158 ± 0.027 baseline). **Now the central open question:** whether ME-03 survives staged continual training under a structurally larger fix — interleaved rehearsal throughout subsequent training, or explicit weight-importance protection (EWC-style) — both untested, both bigger changes than what's been ruled out so far.

**Superseded, retained for history:** this file previously mirrored the Knowledge Foundation Council's Sprint-3A-era working hypotheses (primitive candidates such as Distinction/Constraint, the draft three-layer research standard). That material was never validated under any methodology and is preserved in place at `council/knowledge-foundation/` rather than repeated here — see `docs/05_research/Decisions.md` (DEC-005) for why the primary research line moved away from it.

**Quarantined, not reconciled:** `council/main/` contains an unrelated RP-001 taxonomy thread (C1/C2/C3 knowledge classes) that references undocumented prior artifacts (RP-003, GTC, a "subsumption decision") with no recoverable provenance in this repository. It is not represented above and must not be treated as ACA research until its provenance is resolved.

---

**Purpose:** Centralize all active research questions to guide future work.
**Current Status:** Active
**Historical Context:** Derived from the shift to adaptive computation, and updated 2026-07-18 per DEC-005 to reflect the build-experiment-validate track's open questions rather than the superseded council-driven track's. Updated 2026-07-22 with ACA-MVP-001 Benchmark A's result (EXP-018) and its stretch ablation's result (EXP-010).
**Known Facts:** N/A
**Hypotheses:** Multiple competing hypotheses exist for each question.
**Unknowns:** Solutions to all listed questions.
**References:** `docs/04_architecture/CURRENT_ARCHITECTURE.md`, `docs/07_future/Roadmap.md`, `docs/06_experiments/Completed.md`

