**Status: Active** (populated 2026-07-18 per DEC-005; prior placeholder superseded)

# Memory

## Validated: Competence-Aware Episodic Memory Allocation (EXP-001)

A fixed-capacity key-value memory component with a specific write/eviction policy: it writes a fact only when the parametric backbone's current prediction loss for that fact exceeds a threshold (i.e. the backbone does not yet know it), and — when capacity is full — evicts whichever currently-stored fact the backbone now predicts best (i.e. has since been learned parametrically, making its memory slot redundant).

**Result:** at identical memory capacity, this policy achieves roughly 2x the tail (rare-fact) recall accuracy of naive caching (write on first sight, evict at random) — 18.2% vs 9.8% across 5 seeds — because naive caching wastes the large majority of its capacity (measured at 73%) on facts the backbone already predicts correctly, while the competence-aware policy spends only ~2% of capacity there.

Full methodology, code, and honest limitations: `docs/06_experiments/Completed.md` (EXP-001); code at `experiments/exp001_surprise_gated_memory/`.

## What This Validates and What It Doesn't

**Validates:** the *allocation policy* matters as much as *having* external memory at all — a naive "cache everything you've seen" approach actively self-sabotages under a fixed capacity budget.

**Does not yet validate:** retrieval robustness under realistic, non-orthogonal (confusable) keys — the toy task used near-orthogonal random keys, making retrieval effectively exact-match; integration into a real transformer/language-model backbone; behavior at any scale beyond a small synthetic task; the compute cost of the eviction-scan step at larger capacities.

## Relationship to Prior (Council-Era) Memory Concepts

The CCA v0.1 "Memory Engine" concept (`archive/CCA_v0.1.md`) described memory in prose, with no implementation or test. This validated mechanism is a specific, narrow instantiation of that broader idea — it should not be read as validating the full CCA v0.1 Memory Engine vision (concept storage, consolidation, relationship maintenance), only the specific write/eviction policy tested.

---

**Purpose:** Document the architecture's memory component, distinguishing validated mechanism from open design questions.
**Current Status:** Active — one mechanism validated
**Historical Context:** Populated 2026-07-18 per DEC-005; previously a placeholder stating "architecture research has not yet begun."
**Known Facts:** Competence-aware allocation beats naive caching at equal capacity (EXP-001, 5 seeds, reproducible).
**Hypotheses:** This mechanism will retain its advantage when integrated with a rule module (EXP-004) and when retrieval is no longer exact-match.
**Unknowns:** Scale transfer, retrieval robustness, integration cost.
**References:** `docs/06_experiments/Completed.md`, `docs/03_foundations/ACCEPTED.md` (FP-1), `docs/04_architecture/CURRENT_ARCHITECTURE.md`
