# Adaptive Computational Architecture Research

## Research Objective

The current research investigates whether intelligence should be implemented through one universal computational framework, or through multiple fundamentally different computational mechanisms dynamically selected according to the nature of the problem. Instead of asking "How can we improve the Transformer?", this research asks "Should every form of cognition use the same computational process?" The long-term objective is discovering the computational foundations of adaptive intelligence.

## Current Status

**Status:** Active Research
**Current Milestone:** Two parallel tracks, per CTO directive (2026-07-23). **Track A** continues ACA-MVP-001 (`docs/11_mvp/ACA-MVP-001.md`) — the first experiments in this program to use a real Transformer rather than an MLP. Benchmark A (memory/ME-03), complete including its stretch ablation (Section 8): EXP-018 found competence-gated memory (validated at toy scale by EXP-001) gives **zero measurable protection** against catastrophic forgetting under staged, non-rehearsed continual training — memory coverage of the oldest facts was exactly 0.0 at evaluation time, every seed. EXP-010 then tested the most direct candidate fix (a one-time consolidation-replay burst) — **also failed** (0.160 ± 0.028 vs. 0.158 ± 0.027 baseline). Benchmark B (compose/RC-01), complete (Section 9): tested on the real, published SCAN `addprim_jump` split (grammar verified against all 22,376 real examples first) — a 326-parameter structure-matched model scored **100.000% ± 0.000%** exact-match, against **0.71% ± 0.39%** for a 681,481-parameter generic Transformer (closely matching Lake & Baroni's own published ~1% baseline) — a **~141x margin**, decisively clearing the pre-registered 2x threshold. Memory and compose now have genuinely different, independently-earned outcomes: one clean negative result, one clean, decisive positive result, both reported as such. Full mechanisms: `docs/06_experiments/Completed.md` (EXP-018, EXP-010, EXP-020). **Track B** produced CTX-001 (`docs/12_cognition/CTX-001.md`): investigates whether EXP-018/010, conversation-context representation, and "known unknown" tracking share a root cause. Rejects the strong version of that idea (relabeling "information" as "cognitive state" doesn't fix EXP-018's failure) but finds a narrower, defensible version — conversation/reasoning context is the one candidate that doesn't cleanly reduce to the existing three substrates, tentatively named S_working, Reasoned Hypothesis only, falsification test (EXP-019) proposed but not run.
**Current Architecture Status:** ACA v1.0 synthesized and audited (`docs/04_architecture/ACA_v1.0_Architecture.md`, corrected against real-scale evidence in Section 18); IVS-001 (`docs/09_validation/IVS-001.md`, Section 9) defines the validation program and records EXP-018/EXP-010's consequences; DAS-001 (`docs/10_deployment/DAS-001.md`) derives the runtime/deployment model from both. A proposed five-timescale learning model was checked against the architecture and corrected to four (Runtime and Experience Collection merge; a missing "Routing Revalidation" timescale was added, directly implied by EXP-009). A new failure mode was surfaced: cross-timescale version skew between independently-updating semantic weights and routing tables — unmitigated, untested. ME-03 (competence-gated eviction) is now known to be scope-limited to the static-distribution setting EXP-001 tested — it does not protect against forgetting under sequential, non-rehearsed training as currently specified, and its most direct minimal fix does not either (EXP-018, EXP-010). RC-01 (structure-matched COMPOSE) has, by contrast, now been confirmed at real published-benchmark scale, not just toy scale (EXP-020) — the family-*discovery* problem EXP-002 originally flagged remains exactly as open as before.
**Latest Research Direction:** As of DEC-005 (2026-07-18), ACA's primary methodology shifted from council-driven first-principles derivation to build-experiment-validate-iterate: propose a small, concrete, trainable mechanism; test it against an honest baseline with multiple seeds; report the result — including falsification — before generalizing. See `docs/05_research/Decisions.md` (DEC-005) and `docs/01_background/HISTORY.md` (Phase 5) for the full rationale and what changed. ACA-MVP-001 (2026-07-18) marked a further shift from architecture design to actual scientific validation ("Chief Experimental Scientist" role) — Benchmark A and its stretch ablation (2026-07-22) are the first results under that role, and both are clean negative results, reported as such.

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
* `docs/08_requirements/` - Implementation-independent Architecture Requirement Specifications (ARS-NNN) — the bridge between validated research and eventual architecture design. Deliberately kept separate from `docs/04_architecture/`, which is reserved for actual architecture content once it exists.
* `docs/09_validation/` - Integrated Validation Strategies (IVS-NNN) — the bridge between an architecture specification and evidence that it works as one system, not just as a set of independently-validated components. Deliberately kept separate from `docs/04_architecture/`.
* `docs/10_deployment/` - Deployment & Runtime Architecture Specifications (DAS-NNN) — what the architecture implies about its own deployable artifact and runtime, derived from (not invented independently of) the architecture itself.
* `docs/11_mvp/` - Minimal Scientific Prototype specifications (ACA-MVP-NNN) — the transition from architecture research to actual implementation and empirical validation ("does ACA deserve to exist experimentally"), including real benchmark results as they complete.
* `docs/12_cognition/` - Foundational investigations into candidate abstractions at the same level as the four computational functions or the EVALUATE three-way split (CTX-NNN) — reduction-first analysis of whether a new primitive is actually needed, not architecture proposals.
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
10. `docs/08_requirements/ARS-001.md` (the requirements bridge between validated research and architecture design)
11. `docs/04_architecture/ACA_v1.0_Architecture.md` (the current architecture itself, derived from ARS-001, with full function/requirement/evidence traceability)
12. `docs/09_validation/IVS-001.md` (the validation program now determining whether that architecture actually works as one system)
13. `docs/10_deployment/DAS-001.md` (what that architecture implies about its own runtime and deployable artifact)
14. `docs/11_mvp/ACA-MVP-001.md` (the transition to actual implementation — Section 8 has Benchmark A's real, negative result; `docs/06_experiments/Completed.md`'s EXP-018 has the full mechanism)
15. `docs/12_cognition/CTX-001.md` (investigates whether memory, context, and unknown-tracking share a root cause — a narrower, evidenced conclusion than the appealing version of that question, with a falsification test proposed but not yet run)

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
