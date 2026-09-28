# PAARTHA-PRIMITIVES-001: Autonomous Primitive Formation and Evolving Representations

**Author:** Antigravity AI & Paartha Research Team  
**Date:** September 2026  
**Status:** Foundational Research Specification & Experimental Design  
**Target Document:** `docs/12_cognition/PAARTHA-PRIMITIVES-001.md`  
**Foundational Precursors:** [`PAARTHA-RESET-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-RESET-001.md), [`CTX-002`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/CTX-002.md), [`KRS-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/17_knowledge/KRS-001.md), [`LRS-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/16_learning/LRS-001.md), [`EXP-020`](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-020)

---

## 01 — Research Synthesis: What Existing Science Already Tells Us

To determine whether the concept of autonomous primitive formation provides a genuine architectural opening for Paartha, we first synthesize foundational findings across cognitive developmental science, representation learning, neuro-symbolic systems, and algorithmic reasoning.

```
                              TAXONOMY OF REPRESENTATIONAL SCIENCE
┌──────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Discipline                   │ Core Scientific Principle & Literature Baseline                        │
├──────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 1. Developmental Psychology  │ Core Knowledge Systems (Spelke & Kinzler 2007; Carey 2009): Infants    │
│    & Genetic Epistemology    │ possess innate foundational priors (objects, agency, space, number).   │
│                              │ Assimilation vs. Accommodation (Piaget 1952): Schema accommodation     │
│                              │ triggers when observation creates unresolvable cognitive dissonance.  │
├──────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 2. Causal Representation     │ Independent Causal Mechanisms (Schölkopf et al. 2021): True components │
│    Learning                  │ factorize into autonomous mechanisms that remain invariant under local │
│                              │ interventions. Autoregressive tokens entangle these mechanisms.        │
├──────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 3. Object-Centric Learning   │ Slot Attention & IODINE (Locatello et al. 2020; Greff et al. 2019):    │
│    & Disentanglement         │ Binds continuous sensory streams into permutation-invariant slots.     │
│                              │ Limitation: Discovers *instances*, not reusable abstract *primitives*. │
├──────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 4. Program Induction & DSLs  │ DreamCoder (Ellis et al. 2021): Synthesizes LISP ASTs, mines motifs,   │
│                              │ and refactors DSLs via wake-sleep. Limitation: Requires fixed, hand-   │
│                              │ crafted initial DSLs; discrete search collapses under perceptual noise.│
├──────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 5. Neural Algorithmic        │ Algorithmic Alignment (Veličković et al. 2020-2022; Xu et al. 2020):   │
│    Reasoning                 │ Neural networks generalize out-of-distribution only when their internal│
│                              │ computational steps align with the underlying algorithmic structure.   │
├──────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 6. Bayesian Concept Learning │ Theory-Theory & Probabilistic Programs (Gopnik & Tenenbaum 2007;       │
│                              │ Lake et al. 2015): Concepts are generative programs evaluated by       │
│                              │ Bayesian Occam's Razor: Tradeoff between likelihood and complexity.    │
└──────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

### The Ten Critical Questions on Prior Art

1. **What problem does prior art solve?**  
   Prior art either learns continuous representations of static perceptual data (VAEs, Slot Attention) or synthesizes discrete programs over rigid, pre-existing primitive sets (ILP, DreamCoder).
2. **What representation is learned?**  
   Dense latent vectors $\mathbf{z} \in \mathbb{R}^d$ or symbolic expression trees in fixed DSLs.
3. **Can representations be added after training?**  
   In deep learning: **NO**. Latent dimensionality $d$ and token vocabulary $|V|$ are fixed at initialization. Adding a new dimension or token requires expanding projection matrices and retraining. In DreamCoder: **YES**, but only as compositions of pre-existing primitive operators.
4. **Is the ontology fixed or expandable?**  
   Mainstream foundation models have a **fixed, static ontology** determined entirely by pre-training tokenizer vocabularies and embedding dimensions.
5. **Can genuinely new concepts emerge?**  
   In standard neural models, "emergence" is merely statistical interpolation within a fixed high-dimensional manifold. No new computational operators or structural graph types are created.
6. **How are concepts validated?**  
   Via end-to-end task loss (cross-entropy or MSE). There is no explicit invariant testing or verification firewall.
7. **How does credit assignment work?**  
   Continuous backpropagation via SGD. In discrete program synthesis, credit assignment is mediated by reinforcement learning or combinatorial tree search.
8. **Does learning require gradient descent?**  
   Yes, almost exclusively. In neuro-symbolic systems, gradient updates optimize recognition models while discrete enumeration handles program search.
9. **Does the approach scale?**  
   Dense neural models scale exceptionally well with compute ($O(N)$ FLOPs per parameter), but suffer from catastrophic forgetting and sample inefficiency. Discrete program induction scales poorly ($O(b^d)$ combinatorial explosion).
10. **What critical limitations remain?**  
    **The Representation-Computation Decoupling:** Deep learning learns representations without discrete computational affordances. Symbolic AI has computational affordances without continuous perceptual grounding.

---

## 02 — The Paartha Research Hypothesis

We formulate the core hypothesis of this research mission with mathematical and empirical precision:

> **Primary Hypothesis ($H_1$):**  
> An artificial intelligence system initialized with an irreducible seed substrate of perceptual differentiating operators can autonomously expand its internal representational vocabulary by forming typed, reusable primitives whenever its existing vocabulary incurs persistent predictive residual error, and that these newly formed primitives enable out-of-distribution compositional generalization and reduce test-time inference FLOPs compared to a monolithic neural network of equal parameter capacity.

### The Null Hypothesis ($H_0$):
> Explicit primitive formation provides no measurable advantage over an unconstrained Transformer with equivalent total compute and memory. Any apparent compositional or sample-efficiency gains are artifacts of manually provided seed priors, teacher leakage, or task-specific inductive biases.

---

## 03 — Rigorous Computational Definition of a "Primitive"

To prevent philosophical vagueness, we establish precise boundaries separating Labels, Representations, Concepts, and Primitives:

```
                            THE ONTOLOGICAL LADDER
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. LABEL: A surface communication token (e.g. "gravity", "red", "container").          │
│    • Role: External linguistic interface for mentor/human interaction.                 │
│    • Nature: Arbitrary discrete symbol; carries zero intrinsic computational dynamics. │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. REPRESENTATION: A point or trajectory in latent space: z = f_theta(x).              │
│    • Role: Encodes sensory observation x into a differentiable manifold.               │
│    • Nature: Continuous vector z in R^d; epiphenomenal, un-factored, transient.        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. CONCEPT: A categorical density or equivalence class over representations: p(z | C). │
│    • Role: Recognizes semantic invariants across varied sensory presentations.         │
│    • Nature: Statistical distribution, clustering centroid, or convex region.         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. PRIMITIVE: A typed, reusable computational building block:                          │
│    pi = < Id, Type, w_anchor, R_affordances, Phi_invariants >                         │
│    • Role: Participates actively as an operator or bound argument in state transitions. │
│    • Nature: Co-representational tuple combining continuous grounding and computation. │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Mathematical Definition of a Primitive
Formally, a **Paartha Primitive** $\pi$ is defined as a 5-tuple:

$$\pi = \langle \text{Id}, \mathcal{T}_{\text{type}}, \mathbf{w}_{\text{anchor}}, \mathcal{A}_{\text{affordance}}, \Phi_{\text{invariants}} \rangle$$

1. **Identifier ($\text{Id} \in \mathbb{N}$):** A unique, discrete global identifier within the agent's growing substrate $\Pi$.
2. **Ontological Type ($\mathcal{T}_{\text{type}}$):** Explicit structural type governing legal compositional syntax:
   $$\mathcal{T}_{\text{type}} \in \{\text{ENTITY\_CLASS}, \text{RELATIONAL\_PREDICATE}, \text{CONTINUOUS\_PROPERTY}, \text{STATE\_OPERATOR}\}$$
3. **Perceptual Grounding Anchor ($\mathbf{w}_{\text{anchor}} \in \mathbb{R}^d$):** A continuous prototype embedding in sensory feature space. Enables differentiable recognition, fuzzy similarity matching, and distance-based gating:
   $$P(\pi \text{ active} \mid \mathbf{z}) = \sigma\left(\frac{\mathbf{z} \cdot \mathbf{w}_{\text{anchor}}}{\tau}\right)$$
4. **Computational Affordance ($\mathcal{A}_{\text{affordance}}$):** A concrete execution operator or state transformation rule associated with the primitive:
   $$\mathcal{A}_{\text{affordance}}: \mathcal{S} \times \text{Args} \longrightarrow \mathcal{S}'$$
   *Example:* If $\pi$ represents the spatial relation `INSIDE`, $\mathcal{A}_{\text{affordance}}$ computes topological bounding-box or containment intersection tests. If $\pi$ represents `PUSH`, it executes coordinate translation subject to collision physics.
5. **Invariant Invariants ($\Phi_{\text{invariants}}$):** A set of logical constraints that must hold across all states where $\pi$ is bound:
   $$\forall s \in \mathcal{S}, \quad \Phi_{\text{invariants}}(s, \pi) = \text{True}$$
   *Example:* Non-co-location: $\forall e_1, e_2, \quad \text{CoLocated}(e_1, e_2) \implies e_1 = e_2 \lor \text{Permeable}(e_1, e_2)$.

---

## 04 — The Core Learning Model: Continuous vs. Discrete Duality

The central design of Paartha's learning model is the separation of **Continuous Perceptual Calibration** from **Discrete Structural Growth**:

```
                       PAARTHA DUAL-LOOP LEARNING MODEL
  ===================================================================================
  FAST / CONTINUOUS LOOP (Within-Episode Gradient Dynamics, Delta Theta)
    Sensory Input x_t ──> Encoder ──> Latent z_t
                             │
                             ▼
    Grounding Projection: Match z_t against Anchor Prototypes { w_anchor^(i) }
                             │
                             ▼
    Formulate Structured Working State: S_t = ( Entities, Active Relations, Goals )
                             │
                             ▼
    Execute Selected Affordance / Operator: S_{t+1} = A_pi(S_t)
                             │
                             ▼
    Compute Predictive & Sensor Loss: L_fast = || z_{t+1} - Encoder(x_{t+1}) ||^2
                             │
                             ▼
    Backpropagate Gradients: Update ONLY Encoder & Anchor Weights (Delta Theta)
  ===================================================================================
  SLOW / DISCRETE LOOP (Post-Episode Consolidation & Structural Growth, Delta Pi)
    Inspect Episode Residual Buffer: R = { (x_t, z_t, L_fast) | L_fast > Threshold }
                             │
                             ▼
    Recurring Residual Motif Mining: Cluster unexplained feature trajectories
                             │
                             ▼
    Synthesize Candidate Primitive: pi^* = < Id_new, Type, w_cand, A_cand, Phi_cand >
                             │
                             ▼
    MDL / Compression & Predictive Audit: Evaluate Delta J(pi^*) over validation history
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
      Delta J > 0                       Delta J <= 0
    Commit pi^* to Library Pi        Discard Candidate
```

### Detailed Learning Mechanisms:
* **What receives gradient updates?**  
  The continuous perceptual encoder $\theta_{\text{enc}}$ and the primitive grounding anchor vectors $\{\mathbf{w}_{\text{anchor}}\}$.
* **What does NOT receive gradient updates?**  
  The discrete primitive registry $\Pi$, the ontological type definitions $\mathcal{T}_{\text{type}}$, the invariant constraints $\Phi_{\text{invariants}}$, and the state execution logic.
* **Credit Assignment:**  
  * Continuous credit assignment (within-primitive tuning) is solved via local standard backpropagation on state prediction error.
  * Discrete credit assignment (whether to form, retain, or evict a primitive) is governed by **Validation Information Gain (MDL)** computed over historical replay episodes.

---

## 05 — Innate vs. Learned: The Minimum Seed Substrate

A foundational flaw in symbolic AI is hand-crafting a massive domain ontology (e.g. Cyc), while a foundational flaw in deep learning is assuming tabula rasa with zero structure.

Paartha starts with **Five Irreducible Meta-Operators (The Core Seed Substrate)**:

```
                            THE 5 SEED META-OPERATORS
┌────┬──────────────────────┬────────────────────────────────────────────────────────┐
│ #  │ Seed Meta-Operator   │ Computational Function                                 │
├────┼──────────────────────┼────────────────────────────────────────────────────────┤
│ 1  │ METRIC_DIFF (Delta)  │ Distance metric in continuous latent space to compute  │
│    │                      │ whether two representations are distinct: ||z_1 - z_2||│
│ 2  │ OBJECT_PERSISTENCE   │ Temporal continuity prior: clusters that move together │
│    │ (O)                  │ preserve identity across consecutive time slices.       │
│ 3  │ TEMPORAL_TRANSITION  │ The concept of time evolution: S_t -> S_{t+1}.         │
│    │ (tau)                │ Distinguishes cause from effect via temporal sequence. │
│ 4  │ RELATIONAL_BINDING   │ Structural operator that binds two entity tokens via a │
│    │ (otimes)             │ directed edge: Edge = (Subject, Predicate, Object).    │
│ 5  │ RESIDUAL_MONITOR     │ Quantifies unexplained variance: e_t = ||z_t - z^_t||. │
│    │ (E_res)              │ Triggers primitive candidate synthesis when non-zero.  │
└────┴──────────────────────┴────────────────────────────────────────────────────────┘
```

**Everything else must be learned from experience.**  
The system is **NOT** given seed primitives for "gravity", "container", "velocity", "mammal", or "tool". It is given only the machinery to detect persistent entities, measure differences, link entities, observe time transitions, and detect prediction errors.

---

## 06 — Teacher $\to$ Learner Grounded Bootstrap Protocol

How can a teacher communicate a new concept to an agent that does not yet possess the representational vocabulary required to understand the words?

We design a **Four-Stage Developmental Progression**:

```
                         THE DEVELOPMENTAL PROGRESSION
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Ostensive Grounding & Joint Attention                                         │
│ • Teacher does not use complex sentences.                                              │
│ • Teacher provides positive and negative sensory exemplars: (x+, x-).                  │
│ • Learner's METRIC_DIFF identifies the separating hyperplane in continuous latent      │
│   space, anchoring a new primitive prototype w_anchor.                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STAGE 2: Symbolic Label Binding                                                        │
│ • Once prototype w_anchor achieves stable recognition, teacher emits surface label L.  │
│ • Learner binds L as an external alias to the internal primitive ID.                  │
│ • Language is anchored in sensory perception, eliminating Chinese Room hallucinations. │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STAGE 3: Relational Composition via Grounded Vocabulary                                │
│ • Teacher introduces higher-order concepts using previously grounded labels.           │
│ • Example: "Support = Contact(A, B) AND Above(A, B) AND ResistsGravity(B)".           │
│ • Learner uses RELATIONAL_BINDING to compose existing primitives into a new composite. │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STAGE 4: Abstract Instruction & Counterfactual Reasoning                               │
│ • Teacher provides ungrounded hypothetical scenarios and rule constraints.             │
│ • Learner simulates transitions across internal relational graphs without physical act.│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 07 — The Autonomous Primitive Formation Engine

When grounded experience reveals recurring structure that the existing vocabulary cannot represent, the system executes an autonomous 5-step lifecycle:

```text
Continuous Sensorimotor Stream
              ↓
[1. Prediction & Residual Monitoring]
  -> S^_t+1 = Predict(S_t, a_t)
  -> Compute Residual: r_t = x_t+1 - Decode(S^_t+1)
  -> If r_t > Threshold persistently -> Route to Residual Experience Buffer
              ↓
[2. Topological & Manifold Motif Mining]
  -> Run density-based spectral clustering over residual buffer { r_t }
  -> Extract recurring state transition patterns across multiple episodes
              ↓
[3. Parameter Lifting & Affordance Synthesis]
  -> Assign candidate prototype: w_cand = Centroid(cluster)
  -> Infer affordance: fit a localized transformation mapping S -> S'
  -> Infer invariant: find invariants that hold across all cluster instances
              ↓
[4. Information-Theoretic Optimization Filter (Anti-Explosion)]
  -> Evaluate candidate primitive pi^* under MDL Objective:
     Delta J(pi^*) = PredictiveGain(D_val) + lambda * Compression(D_val) - Cost(pi^*)
              ↓
[5. Registration & Freeze]
  -> If Delta J > 0: Register pi^* into Primitive Substrate Pi
  -> Else: Discard candidate as ad-hoc noise
```

---

## 08 — Preventing Primitive Explosion: The Objective Function

To prevent the catastrophic trap of creating a dedicated primitive for every idiosyncratic experience, primitive creation is formalized as a constrained **Minimum Description Length (MDL) optimization problem**:

$$\max_{\pi^*} \Delta \mathcal{J}(\pi^*) = \Delta \mathcal{L}_{\text{predictive}}(\mathcal{D}_{\text{eval}}) + \alpha \cdot \Delta \text{Bits}(\mathcal{D}_{\text{eval}}) - \beta \cdot \mathcal{K}(\pi^*)$$

Where:
* **$\Delta \mathcal{L}_{\text{predictive}}(\mathcal{D}_{\text{eval}})$**: Reduction in multi-step state transition prediction error on held-out experiences when using the new primitive.
* **$\Delta \text{Bits}(\mathcal{D}_{\text{eval}})$**: Reduction in description length (compression gain) achieved by encoding recurring state graphs using $\pi^*$ rather than raw entity-level assertions.
* **$\mathcal{K}(\pi^*)$**: Structural complexity penalty of the primitive itself (number of parameters in $\mathbf{w}_{\text{anchor}}$ plus formal complexity of its affordance and invariant contracts).
* **$\beta$**: Regularization hyperparameter enforcing parsimony.

A candidate primitive is minted **if and only if $\Delta \mathcal{J}(\pi^*) > 0$**.

---

## 09 — Operational Definition of "Understanding"

In Paartha, "understanding" is never attributed based on fluent conversational generation. Understanding is defined as passing **Eight Operational Verification Tests**:

```
                            THE 8 TESTS OF UNDERSTANDING
┌────┬─────────────────────────────┬────────────────────────────────────────────────────┐
│ #  │ Dimension                   │ Operational Test & Empirical Metric                │
├────┼─────────────────────────────┼────────────────────────────────────────────────────┤
│ 1  │ Predictive Accuracy         │ Predicts future states S_{t+k} with lower error    │
│    │                             │ than a model lacking the primitive: L(pi) < L_base │
│ 2  │ Out-of-Distribution Transfer│ Correctly applies primitive in novel environments  │
│    │                             │ with unfamiliar background textures / entities.    │
│ 3  │ Combinatorial Composition   │ Combines with at least 2 other primitives to solve │
│    │                             │ a composite task never seen during formation.      │
│ 4  │ Counterfactual Robustness   │ Accurately predicts outcome under hypothetical     │
│    │                             │ premise mutations: S' = Mutate(S).                 │
│ 5  │ Invariant Falsification     │ Detects and rejects invalid environmental states   │
│    │                             │ that violate Phi_invariants.                       │
│ 6  │ Algorithmic Efficiency      │ Replaces O(N^2) token simulation with O(1) or      │
│    │                             │ O(N log N) structured computational affordance.    │
│ 7  │ Information Compression     │ Compresses state description length (MDL gain > 0).│
│ 8  │ Retention Stability         │ Primitive remains functional after 1,000 subsequent│
│    │                             │ unrelated tasks without catastrophic forgetting.   │
└────┴─────────────────────────────┴────────────────────────────────────────────────────┘
```

---

## 10 — Primitive Compositionality & Computational Affordances

Primitives do not simply sit in an encyclopedia; they compose into **Hierarchical Computational Circuits**:

```text
Level 0: Seed Meta-Operators
  [OBJECT_PERSISTENCE] + [TEMPORAL_TRANSITION]
          ↓ (Grounded Experience in 2D Grid)
Level 1: Learned Spatial Primitives
  pi_1 = LOCATION(x, y)
  pi_2 = CONTACT(e_1, e_2)
          ↓ (Grounded Motion Experience)
Level 2: Learned Dynamic Primitives
  pi_3 = VELOCITY(dx/dt, dy/dt) = Delta(LOCATION) / Delta(TIME)
  pi_4 = OBSTACLE(e) = Solid object that halts VELOCITY upon CONTACT
          ↓ (Task Interaction)
Level 3: Composite Behavioral Affordances
  pi_5 = PATH_CLEAR(from, to) = Forall e in Line(from, to), NOT OBSTACLE(e)
          ↓ (Complex Planning)
Level 4: Autonomous Problem-Solving Circuit
  Executes A* or Dijkstra search using PATH_CLEAR as an exact computational test!
```

### The Crucial Coupling:
Notice that as representations grow from `CONTACT` $\to$ `OBSTACLE` $\to$ `PATH_CLEAR`, **the computational mechanism shifts from continuous distance checking to exact topological graph search.**  
The representation dictates the computation!

---

## 11 — Adversarial Falsification: Twelve Attacks on the Hypothesis

To ensure scientific honesty, we subject this hypothesis to twelve adversarial critiques:

```
                            THE 12 ADVERSARIAL ATTACKS
┌────┬────────────────────────────────────┬────────────────────────────────────────────┐
│ #  │ Adversarial Critique               │ Rigorous Architectural Defense             │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 1  │ Primitive formation is just latent │ False. A cluster is a passive centroid in  │
│    │ clustering (e.g. k-means, VQ-VAE). │ R^d. A primitive possesses typed afford-   │
│    │                                    │ ances, invariants, and composition rules.  │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 2  │ It is just external key-value      │ False. External memory stores verbatim past│
│    │ memory (e.g. episodic retrieval).  │ states. Primitives are generalizable oper- │
│    │                                    │ ators applied to unseen states.            │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 3  │ It is just program synthesis       │ False. Program synthesis searches discrete │
│    │ (DreamCoder).                      │ trees over fixed DSLs. Paartha anchors     │
│    │                                    │ primitives in continuous latent embeddings.│
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 4  │ A standard Transformer learns the  │ It learns them implicitly, but cannot:     │
│    │ same structure implicitly.         │ (a) prevent catastrophic forgetting,       │
│    │                                    │ (b) guarantee invariant compliance,        │
│    │                                    │ (c) execute in O(1) FLOPs without tokens.  │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 5  │ Seed primitives leak the solution  │ Falsified by designing tasks whose solution│
│    │ to the evaluation tasks.           │ requires concepts orthogonal to seeds.     │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 6  │ Teacher communication leaks the    │ Enforced by Teacher Blindness Protocol:    │
│    │ concept directly in natural text.  │ Teacher only provides ostensive examples.  │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 7  │ Primitive creation only works on   │ Must be evaluated on noisy, partially-     │
│    │ synthetic clean grid worlds.       │ observable environments with pixel noise.  │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 8  │ Primitive library explodes into an │ Controlled mathematically by the MDL Occam│
│    │ unmanageable dictionary.           │ filter: Delta J > 0 threshold.             │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 9  │ Newly formed primitives cannot     │ Evaluated explicitly by Level 3 & 4        │
│    │ compose with existing ones.        │ compositional benchmark tasks.             │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 10 │ New primitives do not improve      │ Tracked via FLOP counters and search       │
│    │ downstream computational efficiency│ expansion depth on complex reasoning.      │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 11 │ Primitive formation requires as    │ Measured via sample-efficiency curves:     │
│    │ many samples as end-to-end SGD.    │ Primitives must form within <= 50 traces.  │
├────┼────────────────────────────────────┼────────────────────────────────────────────┤
│ 12 │ The architecture is secretly just  │ Proved by running the entire model         │
│    │ a wrapper around a commercial LLM. │ locally with zero external API calls.      │
└────┴────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 12 — The Minimal Plausible Architecture: Paartha-Core-v0

We define the concrete, minimal architecture capable of executing this learning model:

```
                            PAARTHA-CORE-v0 TOPOLOGY
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. SENSORY ENCODER (theta_enc, ~2M parameters):                                        │
│    Small convolutional/MLP backbone mapping sensory grid/state x_t to z_t in R^64.     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. SEED OPERATOR KERNEL (Non-Parametric Invariant Core):                               │
│    Implements METRIC_DIFF, OBJECT_PERSISTENCE, TEMPORAL_TRANSITION, RELATIONAL_BINDING. │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. EVOLVING PRIMITIVE REGISTRY (Pi):                                                   │
│    Dynamic list of active primitives: pi_i = < Id_i, Type_i, w_anchor^(i), A_i, Phi_i >│
│    • Initially populated ONLY with 2 basic seeds: ENTITY_ID and SPATIAL_COORD.         │
│    • Expands via Residual Consolidation.                                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. PREDICTIVE TRANSITION CORE (theta_trans, ~3M parameters):                           │
│    GNN processor predicting state deltas over active entity-relation graphs.           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. RESIDUAL CONSOLIDATION ENGINE (Offline Sleep Phase):                                │
│    Buffers high-residual episodes, runs clustering, evaluates Delta J, updates Pi.     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

Total Parameter Scale: **$\approx 5\text{ Million Parameters}$**.  
No multi-billion parameter LLMs. No commercial API wrappers. Completely self-contained, trainable locally, and mathematically inspectable.

---

## 13 — Minimal Falsifiable Experiment: The "PhysWorld-Genesis" Benchmark

We specify the exact experimental protocol to test whether Paartha-Core-v0 can autonomously discover and utilize a new primitive:

### The Environment: PhysWorld-Genesis
A 2D continuous grid world containing moving particles, walls, and energy zones.
* **Seed Primitives Given:** `ENTITY` (particles), `POSITION` ($x, y$), `MOTION` ($\Delta x, \Delta y$).
* **The Hidden Physical Law (The Target Primitive):**  
  A hidden "Magnetic Barrier" zone exists. When a particle enters the zone, if its velocity exceeds $v_{\text{crit}}$, it is reflected; if below $v_{\text{crit}}$, it is absorbed and transformed into a static obstacle.
* **The Task:**  
  Predict particle trajectories 20 steps into the future, and plan paths for a designated agent particle to reach target goals without getting absorbed or reflected.
* **Zero Leakage:** The agent is never given the word "barrier", "magnetism", "reflection", or "absorption".

---

## 14 — Required Baselines & Control Systems

To eliminate alternative explanations, Paartha-Core-v0 is benchmarked against **Seven Strictly Controlled Baselines**:

```
                              THE SEVEN BASELINES
┌─────┬──────────────────────────┬─────────────────────────────────────────────────────┐
│ ID  │ Baseline Name            │ Controlled Independent Variable                     │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_A │ Standard Neural Learner  │ Equal-parameter MLP/Transformer (5M params) trained │
│     │                          │ end-to-end with SGD on state prediction.            │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_B │ Transformer + Teacher    │ Standard Transformer trained with teacher guidance  │
│     │                          │ providing identical ostensive demonstrations.       │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_C │ Transformer + Ext Memory │ Transformer equipped with episodic key-value memory │
│     │                          │ buffer to test if memory alone explains performance.│
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_D │ Fixed-Primitive Paartha  │ Has the initial seed primitives but CANNOT mint new │
│     │                          │ primitives (ablation of consolidation engine).      │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_E │ Primitive-Forming Paartha│ The full Paartha-Core-v0 architecture (can form     │
│     │                          │ new primitives via Residual Consolidation).         │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_F │ Random-Primitive Paartha │ Mints random/arbitrary primitives without MDL or    │
│     │                          │ residual clustering (tests if growth is ad-hoc).    │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_G │ Teacher-Leaked Paartha   │ Teacher explicitly injects the ground-truth target  │
│     │                          │ primitive into the library (ceiling baseline).      │
└─────┴──────────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 15 — Quantitative Metrics & Falsification Criteria

```
                              EVALUATION METRICS TABLE
┌──────────────────────────────┬────────────────────────────────────────────────────────┐
│ Metric                       │ Formal Measurement & Target Threshold                  │
├──────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Sample Efficiency         │ Training episodes required to reach 80% trajectory     │
│                              │ prediction accuracy (Target: Paartha <= 0.2x Baseline A│
├──────────────────────────────┼────────────────────────────────────────────────────────┤
│ 2. OOD Compositional Acc     │ Accuracy on multi-barrier compound mazes never seen    │
│                              │ during training (Target: Paartha >= 75%, Baselines <30%│
├──────────────────────────────┼────────────────────────────────────────────────────────┤
│ 3. Primitive Parsimony       │ Number of primitives formed (Target: exactly 1-2 new   │
│                              │ primitives; reject if library explodes to > 10).       │
├──────────────────────────────┼────────────────────────────────────────────────────────┤
│ 4. Inference Compute Ratio   │ FLOPs per inference step (Target: Paartha <= 0.3x      │
│                              │ of Baseline B / C due to structured affordance bypass).│
├──────────────────────────────┼────────────────────────────────────────────────────────┤
│ 5. Catastrophic Retention    │ Trajectory prediction accuracy on original tasks after │
│                              │ learning barrier mechanics (Target: >= 95% retention). │
└──────────────────────────────┴────────────────────────────────────────────────────────┘
```

### Pre-Registered Falsification Conditions
Paartha's primitive formation hypothesis is declared **FALSIFIED** if:
1. **The Structural Parity Failure:** Baseline A or Baseline C matches Paartha's OOD compositional accuracy within 10 percentage points.
2. **The Growth Failure:** Baseline D (Fixed Primitives) matches Paartha's accuracy on the barrier environment.
3. **The Primitive Explosion Failure:** Paartha mints $> 10$ primitives on the toy environment, failing the MDL parsimony objective.
4. **The Sample Inefficiency Failure:** Paartha requires equal or greater training episodes than the standard neural baseline.

---

## 16 — What "Evolving AI" Actually Means Technically

We banish marketing rhetoric and establish the strict technical definition:

> **A system qualifies as an "Evolving AI" if and only if:**
> 1. Its **representational vocabulary** $\Pi$ grows by adding discrete, typed primitives with continuous anchors: $|\Pi_{t+1}| > |\Pi_t|$.
> 2. Its **computational repertoire** expands by binding new affordance operators $\mathcal{A}_{\text{affordance}}$ that execute in sub-linear complexity relative to token simulation.
> 3. Its **knowledge invariants** $\Phi$ accumulate verified structural constraints that prevent catastrophic forgetting without requiring complete retraining of existing weights.
> 4. It achieves this growth **without increasing the parameter size of its sensory encoder or retraining from scratch**.

---

## 17 — The Research Roadmap: Next Steps

```
                           THE PRIMITIVE RESEARCH ROADMAP
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Theoretical & Architectural Freezing (COMPLETED via PAARTHA-PRIMITIVES-001)   │
│ • Formalize primitive mathematics, learning duality, and anti-explosion criteria.     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STAGE 2: Implementation of Minimal Benchmark Environment (PhysWorld-Genesis)           │
│ • Build lightweight 2D continuous simulator with particles, walls, and barrier physics.│
│ • Build automated Blinded Evaluator and metric logging harness.                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STAGE 3: Build Paartha-Core-v0 & Baselines                                             │
│ • Implement 5M-parameter PyTorch neural baseline (Baseline A).                         │
│ • Implement Transformer + Memory baseline (Baseline C).                                │
│ • Implement Paartha-Core-v0 with Seed Kernels and Residual Consolidation.              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STAGE 4: Execute the Controlled Falsification Benchmark                                │
│ • Run 5 random seeds across Baselines A through G.                                     │
│ • Audit primitive formation, parsimony, sample efficiency, and OOD generalization.     │
│ • Issue definitive empirical verdict.                                                  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 18 — Final Decision Classification

In accordance with Section 23 of the research mission directive, we evaluate the status of the hypothesis:

### **VERDICT: E — UNDERDETERMINED (RATIONALLY JUSTIFIED FOR CONTROLLED EMPIRICAL PROBE)**

#### Scientific Justification:
* **Why NOT A (Strongly Supported)?**  
  We do not yet have empirical benchmark data proving that Paartha-Core-v0 autonomously forms primitives in code without leakage. Claiming strong support prior to running the experiment would violate scientific discipline.
* **Why NOT C (Existing Technology)?**  
  No existing literature provides an architecture that combines continuous perceptual anchoring, discrete typed primitives, invariant verification guards, and computational affordances in a self-expanding, non-retrained local model.
* **Why NOT D (Falsified)?**  
  What was falsified in our previous Decisive Experiment was *un-grounded macro discovery in an external LLM agent wrapper*. The core hypothesis—that grounded sensorimotor residual monitoring can mint reusable primitives in a small local architecture—has never been tested and remains theoretically sound.
* **The Verdict:**  
  The hypothesis is **Underdetermined** pending the execution of the minimal falsifiable experiment (**PhysWorld-Genesis**). The research is authorized to proceed to Stage 2 of the roadmap.
