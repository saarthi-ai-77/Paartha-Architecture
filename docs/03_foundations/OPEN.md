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
* **ACA v0.4 (`docs/04_architecture/ACA_v0.4_Architecture.md`):** the first concrete architecture, derived from ARS-001, fully traced (function → requirement → evidence). Designed, not yet implemented as an integrated system. **EXP-009 (complete) falsified its central assumption that EVALUATE is one function** — it splits into EVALUATE-LOCAL (validated, label-free realizable) and EVALUATE-GENERALIZATION (no label-free realization found adequate). **EXP-013** (is there any adequate label-free proxy for EVALUATE-GENERALIZATION at all?) is now the most important unresolved question in the entire research program. EXP-014 (where RC-04/planning-termination falls), EXP-010 (consolidation via replay), EXP-011 (routing-as-episodic-content), and EXP-012 (novel-input fallback) are the other named gaps.

**Superseded, retained for history:** this file previously mirrored the Knowledge Foundation Council's Sprint-3A-era working hypotheses (primitive candidates such as Distinction/Constraint, the draft three-layer research standard). That material was never validated under any methodology and is preserved in place at `council/knowledge-foundation/` rather than repeated here — see `docs/05_research/Decisions.md` (DEC-005) for why the primary research line moved away from it.

**Quarantined, not reconciled:** `council/main/` contains an unrelated RP-001 taxonomy thread (C1/C2/C3 knowledge classes) that references undocumented prior artifacts (RP-003, GTC, a "subsumption decision") with no recoverable provenance in this repository. It is not represented above and must not be treated as ACA research until its provenance is resolved.

---

**Purpose:** Centralize all active research questions to guide future work.
**Current Status:** Active
**Historical Context:** Derived from the shift to adaptive computation, and updated 2026-07-18 per DEC-005 to reflect the build-experiment-validate track's open questions rather than the superseded council-driven track's.
**Known Facts:** N/A
**Hypotheses:** Multiple competing hypotheses exist for each question.
**Unknowns:** Solutions to all listed questions.
**References:** `docs/04_architecture/CURRENT_ARCHITECTURE.md`, `docs/07_future/Roadmap.md`, `docs/06_experiments/Completed.md`

