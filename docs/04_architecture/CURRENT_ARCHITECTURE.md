**Status: Active** (revised 2026-07-18 per DEC-005 — this document now describes empirically-validated components, not conceptual speculation)

# Current Architecture

## Current Architecture Thinking
As of DEC-005, this document distinguishes between **validated components** (backed by reproducible, multi-seed experiments) and **open design questions** (not yet built or tested). The core premise is unchanged from earlier phases — the system should possess a repertoire of distinct computational mechanisms rather than one uniform process — but the confidence behind each piece is now tied to specific experimental evidence rather than argument alone.

## Validated Components (see `docs/06_experiments/Completed.md` for full results)

**Episodic memory allocator (EXP-001).** A fixed-capacity key-value memory that writes a fact only when the parametric backbone's current prediction loss for it is high (i.e. the backbone doesn't know it yet), and evicts, under capacity pressure, whichever stored fact the backbone now predicts best (i.e. has since mastered). Achieves ~2x the tail-fact recall of naive caching at equal capacity. See `docs/04_architecture/Memory.md`.

**Rule/family-selection module (EXP-002, EXP-003).** A component whose operator representation is deliberately constrained to a small hypothesis-class family matching the true structure of its domain (e.g. a 2-parameter rotation/reflection, not a generic ~30-parameter linear layer), with the correct family chosen per-operator via a held-out validation split rather than training loss. Gives exact compositional generalization on in-family operators. See `docs/04_architecture/Cognitive_Primitives.md`.

**Not yet validated:** how these two components would compose in a single model (EXP-004, in progress), and the dynamic scheduler that would route between them and any future components — see `docs/04_architecture/Dynamic_Computation.md` and `Scheduler.md`, both still open.

## Fixed Pipelines vs. Adaptive Computation
* **Fixed Pipelines (Conventional AI):** Data flows through a predetermined, uniform sequence of operations (e.g., layers of attention). All problems are treated as fundamentally identical structural tasks.
* **Adaptive Computation (Current Architecture):** The system evaluates the nature of the cognitive task and dynamically invokes the most appropriate computational primitive. The path of execution is determined at runtime, varying significantly between different types of cognitive loads.

## Current Understanding of Computational Primitives
Computational primitives are envisioned as discrete, highly specialized operations. While the exact taxonomy is actively being researched, conceptually, a primitive might be dedicated purely to spatial manipulation, another to temporal prediction, and another to logical deduction. They are not simply layers in a neural network; they are fundamentally different computational mechanisms.

## Relationship to the Archived CCA Architecture
The earlier Cognitive Computational Architecture (CCA v0.1) introduced a static sequence of cognitive steps (Observation -> Difference -> Pattern -> Concept -> Memory -> Composition -> World Model -> Prediction -> Planning). 

While the new architecture inherits many of these conceptual categories, it rejects the fixed pipeline approach of CCA v0.1. In the current framework, operations like "Planning" or "Pattern extraction" are treated as primitives that the dynamic scheduler can call upon in any arbitrary order as required by the task.

## Architecture Evolution
* **v0.1:** Static pipeline CCA model. (Archived)
* **v0.2:** Conceptual stage of dynamic adaptive computation, pursued via council-driven first-principles derivation (Knowledge Foundation Council). Superseded by DEC-005 without ever producing a validated primitive.
* **v0.3 (Current):** Build-experiment-validate. Two components empirically validated in isolation (episodic memory allocator, rule/family-selection module); dynamic scheduler and inter-component communication substrate still open.

## Current Unknowns
* The specific architectural mechanism for the dynamic scheduler — still entirely open; no experiment has built or tested one yet.
* The communication substrate allowing different validated components (memory, rule module) to share intermediate representations — targeted by EXP-004.
* Whether the validated components' benefits (EXP-001, EXP-002, EXP-003) survive integration into a real backbone on real data, rather than isolated synthetic toy tasks.

---

**Purpose:** Describe the current, empirically-grounded state of the architecture.
**Current Status:** Active — partially validated
**Historical Context:** Evolved from the limitations of the CCA v0.1 pipeline, then from the council-driven v0.2 phase (superseded by DEC-005).
**Known Facts:** Two architectural components (episodic memory allocation, rule/family selection) are validated by reproducible experiment — see `docs/06_experiments/Completed.md`.
**Hypotheses:** Dynamic scheduling of distinct, validated components will outperform a uniform architecture — not yet tested.
**Unknowns:** Implementation details of the scheduler and communication substrate; scale transfer of validated toy-task results.
**References:** `archive/CCA_v0.1.md`, `docs/03_foundations/OPEN.md`, `docs/06_experiments/Completed.md`, `docs/05_research/Decisions.md` (DEC-005)

