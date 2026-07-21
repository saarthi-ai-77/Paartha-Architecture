**Status: Active — designed, not yet built or tested** (updated 2026-07-18: ACA v0.4 now specifies this component)

# Dynamic Computation

## Current State: Designed in ACA v0.4, Not Yet Implemented or Tested

`docs/04_architecture/ACA_v0.4_Architecture.md` (Section 3) now specifies routing concretely: EVALUATE scores each candidate COMPOSE family against routing entries stored in S_episodic, SELECT chooses (hard argmax, per EXP-003's validated approach), with an explicit (but unvalidated — Reasoned hypothesis) fallback for novel input classes with no existing routing entry. This is a design, not an implementation — no experiment has yet built or tested it. The reasoning below (predating that design) is preserved as the rationale the design was built to satisfy.

## What EXP-003 Already Tells Us About This Problem

Dynamic computation routing is structurally the same problem as EXP-003's family-selection question, one level up: instead of choosing which constrained transform family handles an operator, a scheduler must choose which computational component (memory lookup, rule execution, or eventually other mechanisms) handles a given input. EXP-003's central, empirically-confirmed finding therefore applies directly and should be treated as a hard constraint on any future scheduler design:

**A scheduler that is trained to minimize task loss end-to-end, with no separate signal for generalization, should be expected to fail the same way EXP-003's naive and parsimony-regularized selectors failed** — collapsing toward whichever component fits the training distribution best, regardless of whether that's the component that will actually generalize on inputs it hasn't seen. Any scheduler design should build in a validation-driven selection signal from the start, rather than discovering this failure mode the way EXP-003 had to.

## Open Questions (now scoped by ACA v0.4's design)
* Does EXP-003's validation-driven principle transfer to routing decisions stored and updated via S_episodic's general write/evict mechanism (ACA v0.4's proposal), rather than via a bespoke selection apparatus like EXP-003 actually used? This is EXP-011 in `ACA_v0.4_Architecture.md` Section 7 — currently unvalidated.
* Is the novel-input fallback (generic-module dispatch + low-confidence flagging, ACA v0.4 Section 3) adequate, or does it silently fail in ways EXP-002/003's clean synthetic tasks never exposed? This is EXP-012.
* What is the communication substrate allowing the memory component and rule module to share intermediate representations, if a scheduler needs to combine their outputs rather than pick exactly one? Not addressed by ACA v0.4 — still open.

---

**Purpose:** Track the dynamic scheduling component of the architecture — now designed (ACA v0.4), not yet implemented or tested.
**Current Status:** Active — designed, not yet built
**Historical Context:** Previously fully open; ACA v0.4 (2026-07-18) gave it a concrete design derived from ARS-001's SELECT function and EXP-003's validated constraint.
**Known Facts:** N/A — the design exists; no implementation has been built or tested.
**Hypotheses:** See `ACA_v0.4_Architecture.md` Section 3 and Section 7 (EXP-011, EXP-012).
**Unknowns:** Whether the design as specified actually works when implemented.
**References:** `docs/04_architecture/ACA_v0.4_Architecture.md`, `docs/06_experiments/Completed.md` (EXP-003), `docs/04_architecture/Scheduler.md`, `docs/03_foundations/OPEN.md`
