**Status: Active — genuinely open** (updated 2026-07-18 per DEC-005; prior placeholder superseded)

# Dynamic Computation

## Current State: Not Yet Built or Tested

Unlike Memory (`Memory.md`) and Cognitive Primitives / rule modules (`Cognitive_Primitives.md`), no experiment has yet built or tested a mechanism that dynamically routes execution across multiple heterogeneous computation types at runtime. This remains an open architectural question, not a validated component.

## What EXP-003 Already Tells Us About This Problem

Dynamic computation routing is structurally the same problem as EXP-003's family-selection question, one level up: instead of choosing which constrained transform family handles an operator, a scheduler must choose which computational component (memory lookup, rule execution, or eventually other mechanisms) handles a given input. EXP-003's central, empirically-confirmed finding therefore applies directly and should be treated as a hard constraint on any future scheduler design:

**A scheduler that is trained to minimize task loss end-to-end, with no separate signal for generalization, should be expected to fail the same way EXP-003's naive and parsimony-regularized selectors failed** — collapsing toward whichever component fits the training distribution best, regardless of whether that's the component that will actually generalize on inputs it hasn't seen. Any scheduler design should build in a validation-driven selection signal from the start, rather than discovering this failure mode the way EXP-003 had to.

## Open Questions
* What is the actual routing mechanism — a learned classifier, a Gumbel-softmax gate, something else — and does EXP-003's validation-driven principle transfer to a routing decision made per-input rather than per-operator (a much larger, more dynamic decision space)?
* What is the communication substrate allowing the memory component and rule module to share intermediate representations, if a scheduler needs to combine their outputs rather than pick exactly one?
* Is this even the right next component to build, or should EXP-004 (a simpler, fixed combination of the two validated components, no learned routing yet) come first? Current plan: EXP-004 first, dynamic scheduling only after composability itself is confirmed.

---

**Purpose:** Track the (still open) dynamic scheduling component of the architecture.
**Current Status:** Active — open, not yet built
**Historical Context:** Previously a placeholder stating "architecture research has not yet begun"; updated 2026-07-18 to reflect that other components have since been validated and to record the EXP-003 constraint this component must satisfy.
**Known Facts:** N/A — no scheduler has been built or tested.
**Hypotheses:** A validation-driven routing signal will be necessary here for the same reason it was necessary in EXP-003.
**Unknowns:** Everything about the actual mechanism.
**References:** `docs/06_experiments/Completed.md` (EXP-003), `docs/04_architecture/Scheduler.md`, `docs/03_foundations/OPEN.md`
