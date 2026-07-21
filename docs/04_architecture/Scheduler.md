**Status: Active — genuinely open** (updated 2026-07-18 per DEC-005; prior placeholder superseded)

# Scheduler

## Current State: Partially Addressed by ACA v0.4, Execution Details Still Open

`docs/04_architecture/ACA_v0.4_Architecture.md` (Section 3) specifies the overall computational flow — routing, compose (possibly iterated), evaluate, update, periodic consolidation, periodic graduation check — as a sequence, but does not specify execution order guarantees, resource allocation, or concurrency behavior when multiple components must run per input. This file tracks that remaining, still-open engineering concern, distinct from the routing *logic* now designed in `Dynamic_Computation.md`.

## Relationship to the Arch-Ops Tooling Effort

A separate, parallel effort (`tooling/architecture_test_harness/PROMPT.md`) specifies infrastructure for automatically training and testing architecture candidates — this is tooling to support *experimenting on* scheduler designs once one exists, not the scheduler itself. Do not conflate the two: Arch-Ops runs experiments; the Scheduler would be part of the architecture being experimented on.

## Open Questions
* Execution order and resource allocation once more than one component must run per input (e.g. memory lookup and rule execution both contributing to one prediction).
* Whether scheduling decisions need to be differentiable (trainable end-to-end) or can be a separate, non-differentiable control mechanism.
* How this interacts with the routing-logic constraint already established in `Dynamic_Computation.md` (validation-driven, not loss-driven selection).

This remains fully open pending EXP-004 (composability of the two validated components) and the dynamic-routing work that would follow it.

---

**Purpose:** Track the (still open) execution/scheduling layer of the architecture.
**Current Status:** Active — open, not yet built
**Historical Context:** Previously a placeholder stating "architecture research has not yet begun"; updated 2026-07-18 for terminology clarity against the new Arch-Ops tooling effort.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** Everything about the actual mechanism.
**References:** `docs/04_architecture/ACA_v0.4_Architecture.md`, `docs/04_architecture/Dynamic_Computation.md`, `tooling/architecture_test_harness/PROMPT.md`, `docs/03_foundations/OPEN.md`
