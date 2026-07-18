**Status: Active**

# Previous Hypotheses

This document preserves hypotheses from the pre-DEC-005 (council-driven) era of the research, distinct from `docs/05_research/Hypotheses.md`, which now tracks hypotheses under the current build-experiment-validate methodology. Nothing below has been validated or invalidated by experiment — they were argued about, not tested. File was empty prior to 2026-07-18.

## HYP-001: The Multi-Primitive Hypothesis
* **Description:** True generalization requires an architecture composed of multiple, structurally distinct computational mechanisms rather than a single, monolithic process.
* **Status at time of archiving:** Active, Conceptual Phase, Confidence: Moderate.
* **Current relevance:** The broad spirit of this hypothesis is consistent with the current architecture direction (two structurally distinct components — memory allocation, rule/family selection — have since been validated independently), but this specific hypothesis was never itself tested; it was superseded as a research object by DEC-005's shift to testing individual mechanisms directly rather than arguing for multi-primitive architecture in the abstract.

## HYP-002: Dynamic Scheduling Viability
* **Description:** It is possible to engineer a scheduling layer that can inspect a problem state and dynamically invoke the correct computational primitive without relying on a static, pre-programmed rule engine.
* **Status at time of archiving:** Active, Conceptual Phase, Confidence: Low.
* **Current relevance:** Still untested — see `docs/04_architecture/Dynamic_Computation.md` and `docs/04_architecture/Scheduler.md`, both still open. EXP-003 (family selection) is a narrow, related result (selection among operators, not a full runtime scheduler) that establishes a real constraint any future scheduler must satisfy.

## HYP-003: Knowledge-Specific Computation Hypothesis
* **Description:** Different knowledge classes may require fundamentally different computational representations, learning objectives, and reasoning mechanisms rather than one universal computational framework.
* **Status at time of archiving:** Open, Confidence: Initial.
* **Current relevance:** This is the hypothesis the entire Knowledge Foundation Council track (Sprints 1–3A) attempted to validate through argument and never did (see `council/knowledge-foundation/`). The current architecture line does not re-attempt to validate this at the general level — it validates specific, narrow mechanisms directly (EXP-001, EXP-002, EXP-003) without requiring a prior general theory of knowledge classes.

---

**Purpose:** Preserve pre-DEC-005 hypotheses for historical reference.
**Current Status:** Active
**Historical Context:** Originally logged in `docs/05_research/Hypotheses.md` during the council-driven phase; moved here 2026-07-18 to distinguish from hypotheses under the current methodology.
**Known Facts:** N/A
**Hypotheses:** See above — preserved, not restated as current.
**Unknowns:** N/A
**References:** `docs/05_research/Hypotheses.md`, `docs/05_research/Decisions.md` (DEC-005)
