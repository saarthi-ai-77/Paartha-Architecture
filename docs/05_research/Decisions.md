**Status: Active**

# Decision Log

Every major research and architectural change receives a Decision ID in this log.

### DEC-001: Pivot from Design to Foundations
* **Date:** Pre-documentation formalization.
* **Description:** Abandoned the goal of building a web design foundation model to pursue general computational foundations of intelligence. Web design designated as an evaluation domain.
* **Rationale:** Current architectures fail at design because they lack structural primitives, not just domain data.
* **Status:** Accepted and Executed.

### DEC-002: Archive CCA v0.1
* **Date:** Pre-documentation formalization.
* **Description:** Retired the static pipeline architecture known as CCA v0.1.
* **Rationale:** Intelligence requires dynamic adaptation, not a fixed sequence of cognitive operations.
* **Status:** Accepted and Executed.

### DEC-003: Repository Initialization
* **Date:** Day 0 of formal repository structure.
* **Description:** Implementation of strict documentation standards, historical preservation, and separation of philosophy from architecture.
* **Rationale:** Required to ensure institutional memory and allow new researchers to understand the complex evolution of the project without losing context.
* **Status:** Accepted and Executed.

### DEC-004: Research Roadmap Reordered
* **Date:** Post repository initialization.
* **Description:** The project no longer begins by searching for computational primitives. Instead, research now begins by studying the structure of knowledge itself.
* **Reason:** Architecture should emerge from the intrinsic computational requirements of different knowledge classes rather than from preconceived modules.
* **Impact:** Research priorities have changed. No architectural changes have been accepted.

### DEC-005: Methodology Pivot — From Council-First Derivation to Build-Experiment-Validate-Iterate
* **Date:** 2026-07-18.
* **Description:** ACA's primary research methodology changes from council-driven first-principles derivation (propose a theory → critique it → reduce it → repeat, as run across Knowledge Foundation Council Sprints 1–3A) to an empirical build-experiment-validate-iterate loop: propose a concrete, small, trainable architectural mechanism; implement it; test it against an honest baseline with multiple seeds; report the result whether it confirms or falsifies the hypothesis; diagnose failures and retry with a revised mechanism; only generalize a finding after it has actually been observed to work.
* **Rationale:** After three-plus sprints (Knowledge Foundation Council Sprints 1, 2, 3, 3A) and a parallel unresolved thread (`council/main`'s RP-001 taxonomy work, since quarantined for provenance — see `docs/03_foundations/OPEN.md`), the research had produced an increasingly refined *methodology for evaluating claims* but zero validated primitives, zero code, and zero empirical contact with data. Each sprint's conclusion was "the previous rigor wasn't rigorous enough," with no external signal forcing convergence — a pattern with a poor historical track record (cybernetics-era first-principles programs such as Wiener/Ashby/Maturana-Varela produced rich philosophy but very little that became a buildable, competitive system). The CTO's assessment of this risk, delivered before this decision, is preserved in the conversational record and should inform any future reconsideration of this decision.
* **What changes:** Architecture proposals are now tested as small, real, trainable PyTorch models on synthetic tasks specifically designed to expose the mechanism under test, with honest baselines, multiple seeds, and negative results reported as prominently as positive ones. See `docs/06_experiments/Completed.md` for EXP-001 (confirmed), EXP-002 (falsified-then-confirmed-narrower, with an important open caveat), and EXP-003 (confirmed, with an unexplained side-finding flagged rather than smoothed over).
* **What does not change:** The underlying research vision (`shared/RESEARCH_VISION.md`) and foundational principles (`shared/FOUNDATIONAL_PRINCIPLES.md`) are unaffected — this is a change in *how* claims are validated, not in *what* ACA is ultimately trying to build.
* **Status of prior methodology:** Not rejected, not deleted. The Knowledge Foundation Council's Sprint 1–3A output (`council/knowledge-foundation/`) and the quarantined `council/main/` material remain the permanent research record, preserved in place. The council system itself is retained as a **secondary, diagnostic tool** — used going forward for root-cause analysis when an experiment fails, not as the primary discovery method. See `council/README.md`.
* **Impact:** `docs/07_future/Roadmap.md`, `docs/07_future/Milestones.md`, `docs/04_architecture/CURRENT_ARCHITECTURE.md`, and `docs/03_foundations/{ACCEPTED,REJECTED,OPEN}.md` are updated accordingly. `docs/02_vision/Success_Criteria.md` is revised — its prior wording had already treated the quarantined `council/main` taxonomy (the "C2⊗C3 interactive manifold" framing) as settled, which this decision also corrects.
* **Status:** Accepted and Executed.

---

**Purpose:** Maintain an immutable record of all major project decisions.
**Current Status:** Active
**Historical Context:** N/A
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `docs/05_research/COUNCIL_DISCUSSIONS.md`

