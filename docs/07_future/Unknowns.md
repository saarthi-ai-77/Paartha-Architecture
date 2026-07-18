**Status: Active** (populated 2026-07-18 per DEC-005; file was previously empty)

# Outstanding Unknowns

This file tracks unknowns specific to forward planning (distinct from `docs/03_foundations/OPEN.md`, which tracks open *research* questions). See that file for the research-question version of several items below.

## Technical Unknowns
* Whether EXP-001's and EXP-002/003's validated mechanisms compose without interference (EXP-004 will answer this directly).
* Whether any of the validated toy-task findings survive integration into a real transformer/language-model backbone and real data — nothing has been tested beyond small synthetic tasks yet.
* How to discover or construct a correct constrained transform family for an unfamiliar domain, rather than selecting among a pre-supplied library (the central open problem from EXP-002/003).
* What the actual dynamic-scheduling/routing mechanism should be, and whether it can satisfy the validation-driven-selection constraint established by EXP-003 at the scale of routing individual inputs rather than whole operators.

## Planning Unknowns
* Timeline for reaching a small trainable SLM proof of concept — depends on experimental results, not fixed by a schedule.
* Compute budget required for the SLM POC phase, and how it fits within currently available GPU resources versus what would require the India AI compute grant.
* Whether the Arch-Ops tooling effort (`tooling/architecture_test_harness/PROMPT.md`), being built in parallel, will be ready by the time a scheduler/integration experiment needs automated training infrastructure.

## Research-Program Unknowns
* Whether the Normative Foundation Council should begin once the architecture line has something concrete to evaluate for safety/corrigibility properties, or whether that remains premature until further along (currently: still gated, not yet commenced — see `research/normative_foundation_council/README.md`).
* Whether the quarantined `council/main` RP-001 material (`docs/03_foundations/OPEN.md`) will ever be provenance-resolved, or should eventually be formally retired.

---

**Purpose:** Track forward-looking unknowns distinct from active research questions.
**Current Status:** Active
**Historical Context:** File was empty prior to 2026-07-18; populated alongside the DEC-005 documentation update.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** All items above, by definition.
**References:** `docs/03_foundations/OPEN.md`, `docs/07_future/Roadmap.md`, `docs/07_future/Milestones.md`
