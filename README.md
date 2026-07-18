# Adaptive Computational Architecture Research

## Research Objective

The current research investigates whether intelligence should be implemented through one universal computational framework, or through multiple fundamentally different computational mechanisms dynamically selected according to the nature of the problem. Instead of asking "How can we improve the Transformer?", this research asks "Should every form of cognition use the same computational process?" The long-term objective is discovering the computational foundations of adaptive intelligence.

## Current Status

**Status:** Active Research
**Current Milestone:** EXP-004 complete — the two independently-validated mechanisms (competence-aware episodic memory allocator; validation-driven rule/family-selection module) compose in one model without interfering, under a disjoint-parameter design. Next: EXP-006, testing whether they can share a real substrate (e.g. one token embedding space), which EXP-004 deliberately did not test.
**Current Architecture Status:** Empirically-validated components exist for two of the architecture's pieces, and their composability (in isolation from shared-substrate and learned-routing questions) is now also validated (see `docs/06_experiments/Completed.md`, EXP-001 through EXP-004). The dynamic-scheduling layer and shared-substrate integration are not yet built or tested.
**Latest Research Direction:** As of DEC-005 (2026-07-18), ACA's primary methodology shifted from council-driven first-principles derivation to build-experiment-validate-iterate: propose a small, concrete, trainable mechanism; test it against an honest baseline with multiple seeds; report the result — including falsification — before generalizing. See `docs/05_research/Decisions.md` (DEC-005) and `docs/01_background/HISTORY.md` (Phase 5) for the full rationale and what changed.

## Repository Overview

This repository serves as the official historical record and technical archive for the research program. It maintains a strict chronological evolution of ideas, ensuring that any researcher can understand the trajectory from the project's inception (design generation foundation models) to its current broader philosophical scope.

## Repository Structure

* `README.md` - Project homepage and overview.
* `RESEARCH_MANIFESTO.md` - Core mission, motivations, and scientific principles.
* `RESEARCH_PHILOSOPHY.md` - Evolution of research worldview and philosophical stances.
* `TERMINOLOGY.md` - Canonical glossary of concepts and primitives.
* `docs/01_background/` - Chronological narrative of the project's history and evolution.
* `docs/02_vision/` - Mission, vision, objectives, and success criteria.
* `docs/03_foundations/` - Explicitly categorized research foundations (Accepted, Rejected, Open, Archived).
* `docs/04_architecture/` - Current conceptual understanding of the architecture.
* `docs/05_research/` - Research logs, council decisions, and hypothesis registers.
* `docs/06_experiments/` - Templates, planned experiments, and the completed-experiment record (real code-based results, not prose hypotheses).
* `docs/07_future/` - Roadmaps, milestones, and outstanding unknowns.
* `archive/` - Deprecated and historical documentation (e.g., CCA v0.1).
* `experiments/` - Actual runnable code for each completed/in-progress experiment (`expNNN_name/`), with results data alongside the write-up in `docs/06_experiments/Completed.md`.
* `tooling/` - Supporting engineering tools for the research process (e.g. the Architecture Test Harness spec), separate from the research documentation itself.

## Reading Order for New Researchers

To fully understand the context, progression, and current state of this research, new researchers are advised to read the repository in the following order:

1. `README.md` (You are here)
2. `RESEARCH_MANIFESTO.md`
3. `RESEARCH_PHILOSOPHY.md`
4. `TERMINOLOGY.md`
5. `docs/01_background/HISTORY.md`
6. `docs/02_vision/VISION.md`
7. `docs/04_architecture/CURRENT_ARCHITECTURE.md`
8. `docs/05_research/Decisions.md` (see DEC-005 for the current methodology)
9. `docs/06_experiments/Completed.md` (the actual validated results this program currently stands on)

## Contribution Philosophy

We are maintaining the official research repository for a long-term investigation into the computational foundations of adaptive artificial intelligence. Contributions must protect the project's institutional memory with scientific discipline, clarity, consistency, and historical accuracy. Never overwrite history, preserve chronology, and always maintain clear separation between philosophy, architecture, and hypotheses.

## Research Methodology

**As of DEC-005, ACA's primary methodology is build-experiment-validate-iterate:** propose a small, concrete, trainable architectural mechanism; implement it in code; test it against an honest baseline across multiple seeds; report the result — including outright falsification — before generalizing anything. Negative results are reported as prominently as positive ones (`docs/06_experiments/Completed.md`). Findings are only promoted to `docs/03_foundations/ACCEPTED.md` after they've actually been observed to work in a reproducible experiment, not after surviving argument alone.

The prior methodology — rigorous discussion within a hierarchical, modular council system, with domain councils (e.g., Knowledge Foundation Council) feeding a Main Council — is retained as a **secondary, diagnostic tool**: used to root-cause an experiment's failure and propose a revised mechanism, not as the primary way new claims get established. See `council/README.md` for its current role, and `docs/01_background/HISTORY.md` (Phase 5) for why this changed. Hypotheses must still be separated from accepted facts, and all decisions must still be tracked chronologically, under either methodology.

---

**Purpose:** Provide a clear, structured introduction to the research repository.
**Current Status:** Active
**Historical Context:** Day 0 of the newly structured documentation repository.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `RESEARCH_MANIFESTO.md`, `RESEARCH_PHILOSOPHY.md`, `TERMINOLOGY.md`
