**Status: Active** (populated 2026-07-18 per DEC-005; prior placeholder content preserved below is superseded, not deleted)

# Assumptions

This document tracks assumptions explicitly relied upon by the current (build-experiment-validate) research line, so they are visible and can be challenged rather than silently baked into results.

## A1: Small synthetic toy tasks are informative proxies for the mechanisms under test
Every experiment so far (EXP-001, EXP-002, EXP-003) uses a small, fully-synthetic task (hundreds to thousands of examples, tiny models) rather than real data or a real backbone. The assumption is that a mechanism which fails on a *clean, deliberately favorable* synthetic task designed to expose exactly the effect it claims will fail worse, not better, on messy real data — so a synthetic-task success is necessary but not sufficient evidence, and a synthetic-task failure is strong evidence against the mechanism. This assumption is untested for the reverse direction (does synthetic success transfer to real data?) — flagged as an open question in `docs/03_foundations/OPEN.md`.

## A2: Five seeds is an adequate (not ideal) reproducibility bar at this scale
All three completed experiments report results across 5 seeds. This is enough to distinguish a real, consistent effect (e.g. EXP-001's memory allocation result, EXP-003's family-selection result) from single-seed noise, but is a small sample for statistical purposes. Effects reported with tight seed-to-seed variance (e.g. EXP-002's exact 0.000 ± 0.000 falsification results, EXP-003's exact 0.750 ± 0.000 confirmation) are trusted more than this assumption alone would justify, because the variance itself is near-zero, not because 5 seeds is inherently sufficient.

## A3: GPU-scale small-model experiments (tens to low hundreds of parameters/model in the current tests) give directionally valid signal about mechanism design, not about absolute performance at production scale
The experiments validate *design principles* (e.g. "competence-aware allocation beats naive caching," "match the hypothesis class to the true structure") rather than specific hyperparameter values or absolute accuracy numbers, which are not assumed to transfer as-is to a larger model.

## A4: A negative result (falsification) is as valuable to record as a positive one, and is not evidence of wasted effort
Two of three completed experiments (EXP-002's original hypothesis, EXP-003's naive and parsimony-regularized selection) were falsified before a working variant was found. This is treated as the methodology functioning correctly, not as failure — see DEC-005 and `docs/06_experiments/Completed.md`.

---

*Prior placeholder text (superseded, not deleted): "This document is a placeholder for assumptions explicitly accepted by the Council." Under the council-driven methodology, no assumption had been explicitly ratified by the Council as a body (only proposed by individual roles, e.g. the Research Theorist's Sprint 1 and Sprint 3A working assumptions in `council/knowledge-foundation/responses/`). Those remain on record there and are not restated here, since they belong to the now-secondary council methodology rather than the current build-experiment-validate line.*

---

**Purpose:** Track assumptions relied upon by current research so they remain visible and challengeable.
**Current Status:** Active
**Historical Context:** Populated 2026-07-18 per DEC-005; previously a placeholder synced to the (now superseded) Knowledge Foundation Council methodology.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** Whether A1's synthetic-to-real transfer assumption holds — this is exactly what EXP-004 and later integration work will test.
**References:** `docs/06_experiments/Completed.md`, `docs/05_research/Decisions.md` (DEC-005)
