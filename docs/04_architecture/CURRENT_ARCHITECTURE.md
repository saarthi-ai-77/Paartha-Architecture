**Status: Active**

# Conceptual Architecture

## Current Architecture Thinking
The architecture is currently in a conceptual phase, transitioning away from monolithic structures toward an adaptive, multi-primitive framework. The core premise is that the system must possess a repertoire of distinct computational mechanisms and a dynamic scheduling layer capable of routing execution based on the specific structural requirements of the problem space.

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
* **v0.2 (Current):** Conceptual stage of dynamic adaptive computation. Defining primitives and scheduler mechanism.

## Current Unknowns
* The specific architectural mechanism for the dynamic scheduler.
* The communication substrate allowing different primitives to share intermediate representations.
* The exact, minimal set of necessary primitives.

---

**Purpose:** Describe the current conceptual state of the architecture.
**Current Status:** Conceptual Research
**Historical Context:** Evolved from the limitations of the CCA v0.1 pipeline.
**Known Facts:** N/A
**Hypotheses:** Dynamic scheduling of distinct primitives is superior to fixed pipelines.
**Unknowns:** Implementation details of the scheduler and communication substrate.
**References:** `archive/CCA_v0.1.md`, `docs/03_foundations/OPEN.md`

