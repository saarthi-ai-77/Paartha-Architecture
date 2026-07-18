**Status: Active** (populated 2026-07-18 per DEC-005; prior placeholder superseded)

# ACA Overview

This is a short entry point into the architecture documentation; `CURRENT_ARCHITECTURE.md` is the canonical, detailed statement referenced in the repository's reading order (`README.md`). This page exists to summarize how the sub-topic documents in this directory relate to each other.

## The Picture as of DEC-005

ACA is not, at this point, a single architecture — it is a small set of independently-validated components plus a set of open questions about how to combine them:

| Component | Status | Document |
|---|---|---|
| Episodic memory allocation | **Validated** (EXP-001) | `Memory.md` |
| Rule/family-selection module | **Validated, narrow** (EXP-002, EXP-003) | `Cognitive_Primitives.md` |
| Component composition | **In progress** (EXP-004) | `docs/06_experiments/Completed.md` (once EXP-004 lands) |
| Routing logic between components | **Open** | `Dynamic_Computation.md` |
| Execution/scheduling layer | **Open** | `Scheduler.md` |

Each validated component's confidence comes from a specific, reproducible, multi-seed experiment with code preserved in `experiments/`, not from architectural argument alone — this is the direct consequence of DEC-005's build-experiment-validate methodology. Read `docs/06_experiments/Completed.md` for the actual evidence behind the "Validated" rows above; the per-topic files in this directory summarize and link back to it rather than duplicating it.

---

**Purpose:** Give a one-page orientation to the architecture documentation for a new reader.
**Current Status:** Active
**Historical Context:** Previously a placeholder stating "architecture research has not yet begun"; populated 2026-07-18 once two components had been empirically validated.
**Known Facts:** See the table above and its linked documents.
**Hypotheses:** N/A — this page only summarizes, it does not introduce new claims.
**Unknowns:** See `docs/03_foundations/OPEN.md`.
**References:** `docs/04_architecture/CURRENT_ARCHITECTURE.md`, `docs/06_experiments/Completed.md`
