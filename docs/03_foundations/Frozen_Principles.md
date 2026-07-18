**Status: Active** (populated 2026-07-18 per DEC-005; prior placeholder preserved below)

# Frozen Principles

Design constraints that have survived empirical, reproducible, multi-seed testing (per DEC-005's build-experiment-validate methodology) and should not be re-litigated by argument alone — only by new experimental evidence.

## FP-1: Episodic memory capacity must be allocated by backbone competence, not recency or arrival order
Validated by EXP-001. A write/eviction policy that stores only what the parametric backbone currently gets wrong, and evicts what it has since mastered, achieves ~2x the tail-fact recall of naive caching at identical memory capacity. Any future memory-module design in this architecture should default to a competence-aware allocation policy, not naive caching, unless a specific reason to deviate is documented and tested.

## FP-2: A rule/operator module's hypothesis class must be constrained to the true structure of its domain, not left as a generic high-parameter factorization
Validated by EXP-002. Generic factorization (learned or fixed operand encoding, ~30 free parameters per operator) failed to generalize compositionally under three separate attempts, including a full weight-decay sweep. Constraining the operator to a 2-parameter rotation/reflection family — matching the true symmetry of the domain — gave exact, parameter-correct generalization. This does not mean "always use a rotation family" (that was specific to this task's true structure) — it means: identify or provide the correct constrained family for the domain; do not rely on a generic, over-parameterized layer to discover it via regularization alone (regularization was tested and does not work — see EXP-002's weight-decay sweep).

## FP-3: Structure/family selection must be driven by measured held-out generalization, not by training loss or a fixed complexity penalty
Validated by EXP-003. Any mechanism that decides between candidate hypothesis-class families using ordinary training loss (with or without a fixed-strength parsimony penalty) reliably fails, because training loss cannot distinguish "fits the data" from "will generalize." A mechanism that reserves a held-out selection split and chooses based on performance there works, matching oracle (hand-picked) accuracy. Any future automatic structure-selection mechanism in this architecture must be built around this principle.

---

*Prior placeholder text (superseded, not deleted): "This document is a placeholder for principles frozen by the Council." The Sprint 3A draft research standard referenced by that placeholder (`council/knowledge-foundation/responses/Research_Theorist(res).md`) was never completed through Scientific Reviewer/Reductionist review to a frozen state, and is no longer the active methodology per DEC-005 — it remains on record in the council directory as historical work, not restated here.*

---

**Purpose:** Track design constraints locked in by empirical validation, to prevent re-litigating settled findings without new evidence.
**Current Status:** Active
**Historical Context:** Populated 2026-07-18 per DEC-005; previously a placeholder synced to the (now superseded) Knowledge Foundation Council's unfinished Sprint 3A standard.
**Known Facts:** FP-1 through FP-3 are each backed by reproducible code and multi-seed results in `experiments/` and `docs/06_experiments/Completed.md`.
**Hypotheses:** N/A — these are the validated results, not hypotheses.
**Unknowns:** Whether FP-1–FP-3 hold at scale beyond the toy tasks they were validated on (see `docs/03_foundations/OPEN.md`).
**References:** `docs/06_experiments/Completed.md`, `docs/03_foundations/ACCEPTED.md`, `docs/05_research/Decisions.md` (DEC-005)
