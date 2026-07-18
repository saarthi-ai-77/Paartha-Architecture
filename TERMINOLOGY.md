# Terminology

This document serves as the canonical glossary for the research program. Every definition here must remain consistent across the entire repository.

### Adaptive Computation
The ability of an intelligent system to alter its computational process or mechanism in real-time based on the structural requirements of the problem it is attempting to solve.

### Architecture Version
A discrete, chronological milestone in the design of the system (e.g., CCA v0.1). Every major architectural change results in a new version to preserve historical continuity.

### Cognitive Architecture
The overarching structural blueprint that defines how various computational primitives and memory systems interact to produce intelligent behavior.

### Composition
The cognitive process of combining distinct concepts, patterns, or primitives to form a novel, coherent whole or a more complex concept.

### Constrained Transform Family
A hypothesis class for a "rule module" component that is deliberately restricted to a small number of degrees of freedom matching a specific structural pattern (e.g. rotation/reflection of a cyclic group), rather than a generic linear or MLP layer with many free parameters. Validated in EXP-002 (`docs/06_experiments/Completed.md`): matching the family to the true structure of the underlying function gives exact compositional generalization; a generic, over-parameterized factorization does not, regardless of regularization.

### Family Selection / Validation-Driven Selection
The mechanism by which a model chooses which constrained transform family (see above) applies to a given operator or sub-task. Validated in EXP-003: selection must be driven by measured generalization on a held-out split, not by training loss or a fixed-strength complexity penalty — training-loss-driven selection reliably prefers the more expressive, non-generalizing option even where a simpler family is correct.

### Computational Primitive
A fundamental, indivisible mechanism of computation designed to handle a specific class of cognitive task (e.g., spatial reasoning, temporal sequence matching). 

### Concept
An abstracted representation of a specific entity, idea, or pattern that the system can hold in memory, manipulate, and compose with other concepts.

### Council System
The rigorous review methodology and modular governing hierarchy that guides the research program. It is composed of a Main Council (for validating mature research and architecture) and several specialized domain councils (e.g., Knowledge Foundation Council) that independently discover foundations. These bodies comprise specific AI roles (e.g., Architect, Reviewer, Research Theorist) tasked with enforcing first principles.

### Difference
A core computational mechanism from the CCA v0.1 architecture focused on computing the delta or variance between observations, expected outcomes, or patterns.

### Dynamic Computation
The execution framework in which the scheduler actively routes processing through different computational primitives rather than following a static pipeline.

### Pattern
A recognizable regularity or structure identified within observations or data, which can be extracted and formalized as a concept.

### Planning
The process of utilizing the world model to simulate multiple future states, evaluate their outcomes, and formulate a sequence of actions to achieve a specific goal.

### Prediction
The cognitive function of anticipating future states or observations based on the current world model, historical memory, and identified patterns.

### Reasoning
The deliberate, step-by-step application of computational primitives to navigate a problem space, resolve unknowns, or synthesize new conclusions. 

### Research Freeze
A designated period during which no new architectural changes or foundational shifts are accepted, allowing for stabilization, deep review, or focused experimentation.

### Surprise-Gated Write
An episodic-memory write policy that stores a fact only when the parametric backbone's current prediction loss for it exceeds a threshold (i.e. the backbone doesn't yet know it), and evicts, under capacity pressure, whichever stored fact the backbone now predicts best (i.e. has since "mastered"). Validated in EXP-001: this achieves roughly 2x the tail-fact recall of naive caching (write on first sight, evict at random) at the same fixed memory capacity, because naive caching wastes most of its budget on facts the backbone already knows.

### World Model
An internal, dynamically updated representation of the environment, its rules, and entities, used by the system to simulate outcomes and perform planning.

---

**Purpose:** Establish a consistent, centralized dictionary for all technical terms.
**Current Status:** Active
**Historical Context:** Includes terms carried over from CCA v0.1 (Difference, Pattern), terms from the adaptive computation phase, and terms introduced by the DEC-005 build-experiment-validate methodology (Surprise-Gated Write, Constrained Transform Family, Family Selection).
**Known Facts:** Consistent terminology is required to prevent conceptual drift.
**Hypotheses:** N/A
**Unknowns:** New primitives that may require definition in future architectural versions.
**References:** `docs/04_architecture/CURRENT_ARCHITECTURE.md`, `archive/CCA_v0.1.md`, `docs/06_experiments/Completed.md`
