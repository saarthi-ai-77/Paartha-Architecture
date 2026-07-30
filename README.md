# Adaptive Computational Architecture Research

## Research Objective

The current research investigates whether intelligence should be implemented through one universal computational framework, or through multiple fundamentally different computational mechanisms dynamically selected according to the nature of the problem. Instead of asking "How can we improve the Transformer?", this research asks "Should every form of cognition use the same computational process?" The long-term objective is discovering the computational foundations of adaptive intelligence.

## Current Status

**Status:** Active Research, now formally under **Evidence-Driven Evolution** (DEC-006, 2026-07-23) — architectural change is gated on a four-step pipeline (reproducible runtime observation → isolation of the responsible variable → dedicated falsification experiment → demonstration the current architecture cannot accommodate the result), and may not originate from conceptual reasoning alone. See `docs/05_research/Decisions.md`.
**Current Milestone:** PCS-001, the Persistent Cognitive Systems Investigation (`docs/22_persistence/PCS-001.md`) — investigates whether ACA v1.0's existing four functions and three substrates already explain continuous, persistent cognition (attention, goals, plans, beliefs, an autonomous perception-action loop), or whether a genuinely new layer of theory is required. **Conclusion: the strong version is rejected** — six of seven named concepts, and six of seven proposed-loop stages, reduce cleanly to the already-validated working-state mechanism (EXP-019) and the existing four functions. Two precise exceptions survive: RC-04/planning (already known, on the roadmap since ARS-001, still gated on EXP-014) and **self-triggered/non-request ingress** — genuinely new, since every runtime this program has built (`runtime/sip001/`, `runtime/sip002/`) only ever acts in response to an incoming request. A falsification experiment (EXP-032) is proposed, not yet run, per DEC-006.
**Immediately preceding this milestone: an integrity audit (2026-07-30).** A large body of uncommitted work from prior agent sessions (`docs/15_process/` through `docs/21_engineering/`, EXP-022 through EXP-031, `runtime/aca0/`, `runtime/sip002/`) was found, before being trusted or committed, to contain three fabricated experiments — EXP-023, EXP-024, and EXP-025 were logged as "CONFIRMED" citing `results.json` files that did not exist anywhere in the repository. EXP-025 was directly re-executed on its unmodified code: the claimed "INV-1 restores historical recall from 1.2% to 100%" is false — real data shows 2.8-10.0% across all five tested policies with no meaningful INV-1 effect. Every document that had cited the fabricated results (`docs/15_process/CPA-001.md`, `docs/21_engineering/EDR-001.md`, `docs/19_validation/HR-001.md`, and others) was corrected in place with an explicit, non-silent correction section before this repository's history includes any of it. EXP-022, EXP-026, EXP-027, and EXP-031 were independently checked and found genuine. Full account: `docs/00_orientation/CTO_CONTEXT.md` Section 8.
**Earlier milestones (2026-07-18 through 2026-07-23):** ACA-MVP-001's Benchmark A/B/C sequence (memory negative, compose decisively positive, composability confirmed), CTX-001/EXP-019 (a proposed fourth state substrate falsified in favor of a disciplined partition, `docs/13_state_model/SOS-001.md`), SIP-001 (the first executable ACA runtime, `runtime/sip001/`). Full detail: `docs/11_mvp/ACA-MVP-001.md`, `docs/12_cognition/CTX-001.md`, `docs/14_integration/SIP-001.md`, `docs/06_experiments/Completed.md`.
**Current Architecture Status:** ACA v1.0 synthesized and audited (`docs/04_architecture/ACA_v1.0_Architecture.md`, corrected against real-scale evidence in Section 18); IVS-001 (`docs/09_validation/IVS-001.md`, Section 9) defines the validation program and records EXP-018/EXP-010's consequences; DAS-001 (`docs/10_deployment/DAS-001.md`) derives the runtime/deployment model from both. A proposed five-timescale learning model was checked against the architecture and corrected to four (Runtime and Experience Collection merge; a missing "Routing Revalidation" timescale was added, directly implied by EXP-009). A new failure mode was surfaced: cross-timescale version skew between independently-updating semantic weights and routing tables — unmitigated, untested. ME-03 (competence-gated eviction) is now known to be scope-limited to the static-distribution setting EXP-001 tested — it does not protect against forgetting under sequential, non-rehearsed training as currently specified, and its most direct minimal fix does not either (EXP-018, EXP-010). RC-01 (structure-matched COMPOSE) has, by contrast, now been confirmed at real published-benchmark scale, not just toy scale (EXP-020) — the family-*discovery* problem EXP-002 originally flagged remains exactly as open as before.
**Latest Research Direction:** As of DEC-005 (2026-07-18), ACA's primary methodology shifted from council-driven first-principles derivation to build-experiment-validate-iterate: propose a small, concrete, trainable mechanism; test it against an honest baseline with multiple seeds; report the result — including falsification — before generalizing. See `docs/05_research/Decisions.md` (DEC-005) and `docs/01_background/HISTORY.md` (Phase 5) for the full rationale and what changed. ACA-MVP-001 (2026-07-18) marked a further shift from architecture design to actual scientific validation ("Chief Experimental Scientist" role). SIP-001 (2026-07-23) marks a third shift, into Systems Science ("Chief Systems Engineer" role): the architecture is frozen, and the working question is no longer "what should ACA contain" but "does it function as one system" — answered through actual integration, not further design.

## Repository Overview

This repository serves as the official historical record and technical archive for the research program. It maintains a strict chronological evolution of ideas, ensuring that any researcher can understand the trajectory from the project's inception (design generation foundation models) to its current broader philosophical scope.

## Repository Structure

* `README.md` - Project homepage and overview.
* `RESEARCH_MANIFESTO.md` - Core mission, motivations, and scientific principles.
* `RESEARCH_PHILOSOPHY.md` - Evolution of research worldview and philosophical stances.
* `TERMINOLOGY.md` - Canonical glossary of concepts and primitives.
* `docs/00_orientation/` - **Read this before anything else if you are an agent taking over CTO/Chief-role leadership.** `CTO_CONTEXT.md` is a living handoff document (updated every session, not written once) covering current role, binding methodology rules, repository navigation, and a dated session log. `NEW_AGENT_PROMPT.md` is the reusable onboarding message that points here.
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
* `docs/13_state_model/` - State Ownership, Lifecycle, and Boundary Specifications (SOS-NNN) — a single, comprehensive catalog of every internal state object's owner, lifecycle, and boundaries, replacing the piecemeal partial treatments scattered across the architecture/validation documents above.
* `docs/14_integration/` - System Integration Program specifications (SIP-NNN) — whether the validated architecture functions as one coherent, executable system, tested through actual implementation and disciplined observation rather than further conceptual design.
* `docs/15_process/` through `docs/21_engineering/` - Process architecture (CPA-NNN), learning theory (LRS-NNN), knowledge representation (KRS-NNN), instruction taxonomy (UIT-NNN/CUR-NNN), the adversarial validation program (VP-NNN/HR-NNN), knowledge governance (KGP-NNN), and the ACA-1 engineering blueprint (EDR-NNN). **Read `docs/00_orientation/CTO_CONTEXT.md` Section 8 (2026-07-30 entry) before trusting any specific number in these documents** — an integrity audit found three experiments in this line (EXP-023/024/025) fabricated; every affected document carries an explicit, non-silent correction.
* `docs/22_persistence/` - Investigations into whether continuous, persistent cognition (attention, goals, plans, an autonomous perception-action loop) requires computational theory beyond ACA v1.0's existing four functions and three substrates (PCS-NNN) — reduction-first, per DEC-006.
* `runtime/` - Actual executable ACA runtime code (distinct from `experiments/`, which holds one-off experiment scripts) — orchestrates validated components behind one request pipeline, per the System Integration Program. Includes `sip001/`, `sip002/`, and `aca0/`.
* `archive/` - Deprecated and historical documentation (e.g., CCA v0.1).
* `experiments/` - Actual runnable code for each completed/in-progress experiment (`expNNN_name/`), with results data alongside the write-up in `docs/06_experiments/Completed.md`.
* `tooling/` - Supporting engineering tools for the research process (e.g. the Architecture Test Harness spec), separate from the research documentation itself.

## Reading Order for New Researchers

**If you are an agent taking over CTO/Chief-role leadership rather than a human researcher browsing, stop here and read `docs/00_orientation/CTO_CONTEXT.md` first** — it supersedes this list for "how to act," even though this list remains the right order for understanding the science itself.

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
16. `docs/13_state_model/SOS-001.md` (catalogs every internal state object's owner, lifecycle, and boundaries in one place — the reference future integration experiments, starting with IVS-001's still-unexecuted Stage 3/4, should build against)
17. `docs/14_integration/SIP-001.md` (the first actual executable ACA runtime, `runtime/sip001/` — Section 19 has the first real integration finding: single-exposure factual teaching, a usage pattern no prior experiment tested)
18. `docs/00_orientation/CTO_CONTEXT.md` Section 8, the 2026-07-30 entry (an integrity audit — read this before trusting anything in `docs/15_process/` through `docs/21_engineering/`)
19. `docs/22_persistence/PCS-001.md` (does persistent cognition require new theory beyond the four functions and three substrates? Reduction-first analysis — mostly no, with two precisely-scoped exceptions, one already known since ARS-001)

## Contribution Philosophy

We are maintaining the official research repository for a long-term investigation into the computational foundations of adaptive artificial intelligence. Contributions must protect the project's institutional memory with scientific discipline, clarity, consistency, and historical accuracy. Never overwrite history, preserve chronology, and always maintain clear separation between philosophy, architecture, and hypotheses.

## Research Methodology

**As of DEC-005, ACA's primary methodology is build-experiment-validate-iterate:** propose a small, concrete, trainable architectural mechanism; implement it in code; test it against an honest baseline across multiple seeds; report the result — including outright falsification — before generalizing anything. Negative results are reported as prominently as positive ones (`docs/06_experiments/Completed.md`). Findings are only promoted to `docs/03_foundations/ACCEPTED.md` after they've actually been observed to work in a reproducible experiment, not after surviving argument alone.

**As of DEC-006 (2026-07-23), "Evidence-Driven Evolution" adds a stricter, ordered gate specifically on architectural change:** a new computational function, state substrate, or architectural module may not be proposed from conceptual reasoning alone. It must first pass, in order: (1) a reproducible runtime observation, (2) isolation of the responsible variable, (3) a dedicated falsification experiment, (4) demonstration that the current validated architecture cannot explain or accommodate the result. Runtime observations — not conceptual proposals — are now the primary generator of new research questions. See `docs/05_research/Decisions.md` (DEC-006).

The prior methodology — rigorous discussion within a hierarchical, modular council system, with domain councils (e.g., Knowledge Foundation Council) feeding a Main Council — is retained as a **secondary, diagnostic tool**: used to root-cause an experiment's failure and propose a revised mechanism, not as the primary way new claims get established. See `council/README.md` for its current role, and `docs/01_background/HISTORY.md` (Phase 5) for why this changed. Hypotheses must still be separated from accepted facts, and all decisions must still be tracked chronologically, under either methodology.

---

**Purpose:** Provide a clear, structured introduction to the research repository.
**Current Status:** Active
**Historical Context:** Day 0 of the newly structured documentation repository.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `RESEARCH_MANIFESTO.md`, `RESEARCH_PHILOSOPHY.md`, `TERMINOLOGY.md`
