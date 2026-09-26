# PAARTHA-RESET-001: Recovering the Original Vision and Re-Deriving the Core AI Architecture

**Author:** Antigravity AI & Paartha Research Team  
**Date:** September 2026  
**Status:** Foundational Research Reset & Epistemic Trajectory Audit  
**Target Document:** `docs/12_cognition/PAARTHA-RESET-001.md`  
**Prior Milestone Context:** [EXP-037](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ADVERSARIAL-001.md), [DECISIVE-001](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-DECISIVE-RESULTS-001.md), [ABLATION-001](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-MECHANISM-ABLATION-001.md), [TRANSFER-001](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ABSTRACTION-TRANSFER-001.md)

---

## 1. Executive Overview & The Reason for the Reset

The Paartha research program has reached a critical juncture. 

Over the past experimental sequence (EXP-032 through EXP-037, followed by the Decisive Benchmark, Mechanism Ablation, and Genuine Abstraction Transfer trials), the project produced valuable, rigorously verified empirical results:
1. It proved that a frontier LLM alone collapses on multi-step state transformations (33.3% accuracy) due to compounding calculation drift.
2. It proved that an external execution harness providing **State Checkpointing and Rollback (SET-CR)** dramatically elevates multi-step agent reliability to **83.3%** by recovering from single-step execution exceptions.
3. It proved that typed capability contracts provide formal compile-time safety without hurting solve rates.
4. It proved that heuristic parameter re-grounding (RESOLVE) on structured schemas silently distorts intent and degrades accuracy.
5. It proved that autonomous macro abstraction discovery via frequent motif mining and anti-unification **fails to transfer across genuinely independent, non-co-designed domains**, collapsing the cross-domain transfer ratio to $1.00\times$.

However, these findings reveal a profound methodological drift:

> **The research trajectory has drifted from inventing a fundamentally new AI model architecture into engineering an external LLM agent and tool-execution runtime.**

The original Paartha vision was never to build a Python wrapper around a commercial Large Language Model. The original vision was:

> **Design an AI computational architecture in which intelligence, knowledge representation, reasoning, and computation are not forced through the same token-based neural computation for every problem, with the goal of building models that are efficient, capable of complex reasoning, brainstorming, planning, coding, and agentic behavior.**

This document executes a complete **Research Reset**. It recovers the foundational research trajectory from day one, diagnoses the exact causes of architectural drift, studies the state-of-the-art literature in adaptive computation and neuro-symbolic learning, analyzes the representational bottlenecks of modern Transformers, re-derives what a genuine Paartha model would be, and evaluates whether the program should **Continue**, **Reframe**, or **Abandon**.

---

## 2. Historical Trajectory & The Anatomy of Drift

To understand where the research currently stands, we must reconstruct the chronological evolution of the program across its major phases:

```
                               THE EVOLUTION OF PAARTHA
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: The Design Model Initiative                                                  │
│ Objective: Invent a new foundation model for web design generation.                    │
│ Finding: Tokenizing spatial and aesthetic layouts failed. Led to Council review.      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: Cognitive Computational Architecture (CCA v0.1)                               │
│ Objective: Rigid cognitive pipeline (Observation -> Difference -> Pattern -> Concept). │
│ Finding: Static pipelines cannot adapt to structurally diverse problem spaces.        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: The Adaptive Pivot                                                            │
│ The Core Question: "Whether intelligence should be implemented through one universal   │
│ computational framework, or through multiple fundamentally different computational    │
│ mechanisms dynamically selected according to the nature of the problem."              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 5: Build-Experiment-Validate Loop                                                │
│ • EXP-001: Surprise-gated memory allocation validated for static distributions.        │
│ • EXP-002 / EXP-020: Structure-matched composition on SCAN achieved 100% vs 0.71%      │
│   for standard Transformers (proving invariant structural constraints work).           │
│ • EXP-018: Competence-gated memory failed under sequential continual learning.        │
│ • EXP-019: Working context is a reserved partition in episodic memory, not a 4th sub.  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 6 / INTEGRATION: ACA v1.0, JEv-001, and ARCH-001                                │
│ • CTX-002: Formalized Three-Tier State (Semantic, Episodic, Invariants).               │
│ • JEV-001: Studied non-autoregressive calibrated decision models (System 1).          │
│ • ARCH-001: Proposed tripartite model (encoder, calibrated router, surface generator). │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 7: The Cognitive Drift (EXP-032 through EXP-037 & Decisive Benchmarks)           │
│ • EXP-032..037: Replaced model training with frozen LLM prompting + Python tool calls. │
│ • RESOLVE, Contracts, SET-CR, and Macro Discovery were implemented as external Python  │
│   harnesses around commercial frontier models (Sarvam-105B).                           │
│ • The system became an agent framework rather than a model architecture.              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### The Seven Crucial Trajectory Dimensions

#### A. Original Problem
How to natively represent and compute structured, relational, spatial, and algorithmic problems without forcing them into a 1D sequence of autoregressive text tokens.

#### B. Original Hypothesis
Intelligence requires heterogeneous computational mechanisms (neural representations, explicit relational structures, discrete symbolic operations, and invariant constraints) dynamically selected according to the problem, rather than a monolithic next-token predictor.

#### C. Subsequent Hypotheses
* *Hypothesis 2 (JEv / System 1):* Non-autoregressive decision models can replace conversational token generation for intent, routing, and risk estimation.
* *Hypothesis 3 (Non-Gradient Competence Acquisition):* An AI system can accumulate reusable competence without weight updates ($\Delta \Theta = 0$) by registering verified procedural compositions into a discrete library $\mathcal{L}$.
* *Hypothesis 4 (Autonomous Abstraction Discovery):* Anti-unification and Minimum Description Length (MDL) compression can autonomously discover reusable computational macros that transfer across novel domains.

#### D. The Exact Point of Research Drift
The drift occurred during **EXP-032**. Instead of training or modifying a model's internal computational substrate, the experiment introduced an external Python search wrapper that prompted an external frontier LLM to propose names from a dictionary of 12 deterministic Python functions (`FilterByThreshold`, `SortByColumn`, etc.). From that moment onward, every subsequent experiment (EXP-033 through EXP-037, DECISIVE-001) was optimizing **external prompt-and-tool middleware**, completely abandoning internal model architecture.

#### E. Valuable Discoveries (What Remains True)
1. **SET-CR Checkpoint Rollback is essential for multi-step agentic execution:** When sequential actions are non-deterministic, having an explicit state rollback stack prevents catastrophic unrecoverable errors (83.3% success in A6).
2. **Structural Symmetries Guarantee Exact Composition:** When an operator is constrained to its true algebraic symmetry family (EXP-002, EXP-020), it achieves 100% out-of-distribution compositional generalization where a standard Transformer achieves 0.71%.
3. **External Contracts Prevent Schema Hallucination:** Hiding ASTs and exposing typed contracts prevents model confusion.
4. **MDL Correctly Rejects Superficial Macros:** Information-theoretic compression successfully prevents library bloat by penalizing parameter overhead.

#### F. Dead Ends (What Was Falsified or Weakened)
1. **Autonomous Cross-Domain Macro Transfer:** Discovered macro abstractions do **not** transfer across independent domains ($D / B_1 = 1.00\times$).
2. **RESOLVE as an Irreducible Cognitive Primitive:** Heuristic column fallbacks in RESOLVE actively degraded frontier model accuracy from 75% to 50% by silently mutating user intent.
3. **Competence-Gated Memory Alone for Continual Learning:** EXP-018 decisively falsified the claim that entropy-gated episodic memory prevents catastrophic forgetting in real neural weights.
4. **Composition Caching:** Caching un-parameterized execution traces yielded 0% held-out generalization (EXP-033).
5. **Static Cognitive Pipelines:** Rigid multi-faculty pipelines (Observation $\to$ Concept $\to$ Decision) collapse when problem modalities vary.

#### G. Open Questions (Completely Unanswered)
* What does an actual neural network look like if its internal computation graph dynamically changes per problem?
* How does credit assignment work when backpropagating through dynamic computational choices without collapsing into intractable reinforcement learning?
* Can knowledge and procedures be stored in a form that is both natively differentiable and structurally inspectable?

---

## 3. The Fundamental Problem Restated

We must move past the superficial framing of "LLM + tools". The true architectural question is:

> **Can an AI model have a computational architecture in which the internal representation, computational structure, memory access, and reasoning depth dynamically adapt to the problem being solved, rather than executing a fixed number of uniform matrix multiplications over a 1D sequence of tokens?**

### The Computational Pathology of the Modern Transformer

To design an alternative, we must dissect the exact mechanics of a standard autoregressive Transformer across the entire inference pipeline:

```
INPUT
  ↓
Tokenization (1D discrete integers via BPE)
  ↓
Static Embedding Lookup ($x_0 = W_e[t] + W_p[i]$)
  ↓
Repeated Uniform Layers ($L$ identical blocks of Attention + MLP)
  ↓
  ├── Layer 1: Self-Attention $O(N^2 \cdot d)$ + Dense FFN ($2 \cdot d \cdot 4d$)
  ├── Layer 2: Self-Attention $O(N^2 \cdot d)$ + Dense FFN ($2 \cdot d \cdot 4d$)
  │   ...
  └── Layer L: Self-Attention $O(N^2 \cdot d)$ + Dense FFN ($2 \cdot d \cdot 4d$)
  ↓
Next-Token Unembedding ($P(w_{t+1}) = \text{softmax}(W_u \cdot x_L)$)
```

### Critical Bottleneck Analysis:

1. **Uniform Computation for Non-Uniform Problems:**  
   The token `"the"` in an easy sentence executes the exact same number of floating-point operations ($2 \cdot L \cdot N_{\text{params}}$ FLOPs) as a token representing the critical step in a complex mathematical proof.
2. **1D Sequence Bottleneck:**  
   Every complex structure—relational tables, molecular graphs, spatial geometries, syntax trees, ASTs, and planning DAGs—must be serialized into a flat string of characters, forcing attention layers to spend quadratic capacity merely reconstructing basic topological relationships.
3. **Implicit, Entangled Knowledge Storage:**  
   Factual knowledge, linguistic grammar, logical reasoning, and procedural algorithms are all compressed into the same dense weight matrices ($W_k, W_v, W_{\text{gate}}, W_{\text{up}}$). Because knowledge is stored implicitly across millions of distributed parameters:
   * It cannot be updated without catastrophic forgetting.
   * It cannot be inspected or verified without speculative probing.
   * It hallucinating facts when statistical associations decouple from ground truth.
4. **Ephemerality of Intermediate Reasoning:**  
   The rich intermediate latent states calculated across the $L$ layers are discarded immediately after predicting a token. To "think", modern frontier models (OpenAI o1/o3, DeepSeek-R1) must emit physical tokens into the context window ("Let me think... wait, that's wrong..."), converting internal reasoning into an astronomically expensive sequence of autoregressive forward passes.
5. **No Dynamic Computational Construction:**  
   A standard Transformer cannot decide: *"This problem is a shortest-path graph search; I will instantiate a priority queue and a relaxation loop."* It can only simulate the execution of a graph algorithm through statistical pattern matching across attention heads.

---

## 4. Deep Study of Adaptive Computation & Competing Approaches

To avoid reinventing existing ideas under new names, we conducted a comprehensive survey of modern adaptive computation, modular architectures, and neural-symbolic systems:

```
                                  TAXONOMY OF ADAPTIVE AI
┌─────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Paradigm                        │ Core Mechanism & Foundational Literature               │
├─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Dynamic Depth / Halting      │ Adaptive Computation Time (Graves 2016), PonderNet     │
│                                 │ (Banino et al. 2021), Universal Transformers (2018)    │
│ 2. Conditional Parameter Routing│ Sparse Mixture of Experts (Shazeer 2017, Switch 2022,  │
│                                 │ DeepSeek-V3), Mixture of Depths (Raposo et al. 2024)   │
│ 3. Memory-Augmented Networks    │ Neural Turing Machines (2014), Differentiable Neural   │
│                                 │ Computers (Graves 2016), Recurrent Memory Transformer │
│ 4. Neural Algorithmic Reasoning │ GNN Algorithmic Execution (Veličković et al. 2020-2022)│
│                                 │ Neural GPU (Kaiser & Sutskever 2015)                   │
│ 5. Program Synthesis / Induction│ DreamCoder (Ellis et al. 2021), Neuro-Symbolic Concept │
│                                 │ Learner (Mao et al. 2019), DeepProbLog (2018)          │
│ 6. Test-Time Compute Scaling    │ Tree-of-Thoughts (Yao 2023), STaR (Zelikman 2022),     │
│                                 │ Process Supervision (Lightman 2023), o1 / DeepSeek-R1  │
│ 7. State-Space Models (SSMs)    │ Mamba (Gu & Dao 2023), S4 (Gu et al. 2021)             │
└─────────────────────────────────┴────────────────────────────────────────────────────────┘
```

### Detailed Deconstruction of Key Approaches

#### 1. Adaptive Computation Time (ACT) & PonderNet
* **What is represented:** Standard recurrent or transformer hidden states $h_t \in \mathbb{R}^d$.
* **What is learned:** A scalar halting unit $p_n = \sigma(w_h \cdot h_n + b_h)$ trained with a prior (geometric distribution in PonderNet) penalizing excessive steps.
* **What is dynamically selected:** The number of recurrent layer iterations per token.
* **Limitations:** ACT only scales depth **within the same fixed neural operation**. It cannot change the *nature* of the computation. Applying a transformer layer 10 times does not turn it into a constraint solver or a database join.

#### 2. Sparse Mixture of Experts (MoE) & Mixture of Depths (MoD)
* **What is represented:** Token embeddings in a standard transformer backbone.
* **What is learned:** Softmax routing gates $G(x) = \text{TopK}(\text{Softmax}(W_g \cdot x))$.
* **What is dynamically selected:** Which subset of feedforward MLP parameter blocks are activated per token.
* **Limitations:** Experts are simply unconstrained MLP weight matrices. They do not represent distinct algorithms or data structures. Furthermore, routing is token-level, causing expert specialization to fragment across grammatical and syntactic features rather than cohesive problem-solving procedures.

#### 3. Neural Algorithmic Reasoning (CLRS Benchmark / Veličković)
* **What is represented:** Graphs where nodes and edges hold high-dimensional latent vectors representing data structures (pointers, distances, visited flags).
* **What is learned:** Message-passing weight matrices trained to match the intermediate execution steps of classic algorithms (Bellman-Ford, Kruskal, BFS).
* **Limitations:** Requires processor networks to be supervised on step-by-step algorithmic traces. Fails on open-domain natural language inputs where the graph topology is not explicitly provided.

#### 4. Program Induction & Neuro-Symbolic Synthesis (DreamCoder)
* **What is represented:** LISP-like AST expressions over domain-specific primitives.
* **What is learned:** A neural recognition model (predicts search probabilities over primitives) and an expanding library of discovered functions via anti-unification.
* **Limitations:** **The Combinatorial Search Cliff.** Program search in discrete syntax trees scales exponentially with depth ($O(b^d)$). It struggles with continuous perceptual inputs and cannot handle noisy, ill-posed tasks without hand-crafted domain DSLs.

#### 5. Autoregressive Test-Time Compute (OpenAI o1 / DeepSeek-R1)
* **What is represented:** Flat natural language text strings.
* **What is learned:** An autoregressive policy fine-tuned via RL with rule-based or verifier rewards to emit extended chains of reasoning ("thinking tokens").
* **What is dynamically selected:** Number of thinking tokens generated before emitting the final answer.
* **Limitations:** **Astronomical FLOP waste.** To explore a hypothetical branch, the model must sample hundreds of tokens. To backtrack, it must emit natural language sentences acknowledging its error. The search and verification mechanisms are entirely simulated through sequential autoregressive matrix multiplications.

---

## 5. The Central Question of Representation: Beyond Pure Tokens

One of Paartha’s foundational motivations was:
> **Is tokenization really the right universal representation for intelligent computation?**

The answer from cognitive science and computational complexity is an emphatic **NO**. 

Forcing all cognitive faculties into a 1D token sequence creates severe representational friction:

```
                            REPRESENTATIONAL HIERARCHY
┌───────────────────────┬───────────────────────────────┬──────────────────────────────┐
│ Modality / Structure  │ Pathology in Token Form       │ Native Computational Form    │
├───────────────────────┼───────────────────────────────┼──────────────────────────────┤
│ Discrete Entities     │ Split across subword tokens   │ Unique typed entity IDs      │
│ Relational Graphs     │ Serialized flat adjacency list│ Topological edge matrix / DAG│
│ Precise Numbers       │ BPE fragmentation ('3', '41') │ IEEE 754 float / BigInt      │
│ Spatial / Geometric   │ Markdown ASCII or text tokens │ Coordinate tensor / mesh     │
│ Procedural Logic      │ Autoregressive code strings   │ Executable syntax tree (AST) │
│ State Invariants      │ Implicit in attention weights │ First-order logic predicates │
│ Epistemic Uncertainty │ Overconfident logits          │ Calibrated confidence vector │
└───────────────────────┴───────────────────────────────┴──────────────────────────────┘
```

### The Heterogeneous Representation Hypothesis:
A true post-transformer architecture must support **Co-Representational Substrates**:
$$\mathcal{R} = \langle \mathbf{e}_{\text{dense}}, \mathcal{G}_{\text{relational}}, \mathcal{T}_{\text{symbolic}}, \mathbf{c}_{\text{epistemic}} \rangle$$
1. **$\mathbf{e}_{\text{dense}} \in \mathbb{R}^d$**: High-dimensional continuous embeddings for fuzzy semantic context, perceptual patterns, and linguistic nuance.
2. **$\mathcal{G}_{\text{relational}}$**: Explicit entity-relation graph nodes for factual grounding, preventing hallucination.
3. **$\mathcal{T}_{\text{symbolic}}$**: Structured syntax trees and executable code blocks for exact arithmetic, sorting, and algorithmic procedures.
4. **$\mathbf{c}_{\text{epistemic}}$**: Calibrated uncertainty distributions indicating what the model knows, suspects, or does not know.

---

## 6. Computation as a First-Class Object

In a conventional model, computation is a **side effect of parameter evaluation**:
$$\text{Input Tokens} \xrightarrow{W_1, \dots, W_L} \text{Output Tokens}$$

In Paartha's original conception, computation is a **dynamically constructed artifact**:
$$\text{Problem Representation} \xrightarrow{\text{Synthesis / Routing}} \text{Computational Graph } \mathcal{C} \xrightarrow{\text{Execution}} \text{Verified State}$$

```
CONVENTIONAL DEEP LEARNING:
Input ──> [Fixed Dense Neural Network (L Layers, D Dimensions)] ──> Output
(Computation is static; every input flows through the exact same circuit)

PAARTHA DYNAMIC COMPUTATION:
Input ──> Problem Representation ──> Graph Selector
                                           │
         ┌─────────────────────────────────┴────────────────────────────────┐
         ▼                                 ▼                                ▼
   [Neural Subgraph]              [Symbolic Subgraph]             [Algorithmic Subgraph]
   (Semantic Embeddings)          (Constraint Solver / SQL)       (Search / Sorting / Loop)
         │                                 │                                │
         └─────────────────────────────────┬────────────────────────────────┘
                                           ▼
                              Execution & State Transition
                                           ▼
                                 Invariant Verification
                                           ▼
                                         Output
```

### Why Has This Been Difficult Historically?
The fundamental reason why dynamic computation graphs have not replaced Transformers is **The Differentiability & Credit Assignment Dilemma**:
1. **If the graph construction is discrete** (selecting Python tools, SQL queries, or distinct modules), gradients $\frac{\partial \mathcal{L}}{\partial \text{Graph}}$ cannot flow backwards. Training requires reinforcement learning (policy gradients) over combinatorial graph topologies, which suffers from extreme variance, sparse rewards, and sample inefficiency.
2. **If the graph construction is continuous** (like DARTS / Neural Architecture Search or soft Mixture of Experts), the model must evaluate all candidate branches simultaneously to compute weighted averages, destroying the computational efficiency that dynamic selection was supposed to provide!

**The Core Scientific Question for Paartha:**  
Can an architecture select discrete computational subgraphs efficiently without succumbing to the sample-inefficiency collapse of combinatorial RL?

---

## 7. Re-Examining "Weights" and Parameters

Our earlier research frequently asserted:
> *"Intelligence changes via topological growth of the capability library $\mathcal{L}$, while the neural substrate remains fixed ($\Delta \Theta = 0$)".*

We must evaluate this assertion with ruthless honesty.

If $\Delta \Theta = 0$ and the entire "learning" process consists of adding Python function definitions to a dictionary in a JSON file, **we have not built a new AI model—we have built an automated macro recording script.**

### What Parameters Should Actually Represent:

```
                            PARAMETER TAXONOMY
┌───────────────────────────┬──────────────┬───────────────┬───────────────────────────────┐
│ Parameter Substrate       │ Form         │ Timescale     │ Representation                │
├───────────────────────────┼──────────────┼───────────────┼───────────────────────────────┤
│ $\Theta_{\text{percept}}$ │ Dense Tensor │ Slow (Pretrain│ Sensory & linguistic grounding│
│ $\Theta_{\text{decision}}$│ Calibrated   │ Medium (RLCD) │ Fast non-autoregressive       │
│                           │ Head Weights │               │ routing & computational choice│
│ $\mathcal{K}_{\text{rel}}$│ Relational   │ Rapid (Online)│ Explicit entity-relation edges│
│                           │ Graph Nodes  │               │ & verified facts              │
│ $\mathcal{P}_{\text{proc}}$│ Parametric  │ Dynamic       │ Reusable computational sub-   │
│                           │ Subgraphs    │ (Consolidation│ graphs with bound weights     │
└───────────────────────────┴──────────────┴───────────────┴───────────────────────────────┘
```

A true model architecture cannot be static weights plus an external script. It must have **modular parametric capacity**:
When a new computational procedure is learned, it must either:
1. Update the **routing parameters** $\Theta_{\text{decision}}$ so that the model reliably dispatches to the new procedure, or
2. Allocate a **differentiable neural module** with specialized weights that integrate into the model's forward execution pass.

---

## 8. Re-Evaluating the Teacher $\to$ Student Paradigm

Our earlier intended learning paradigm was:
$$\text{Frontier Teacher} \xrightarrow{\text{Demonstrations}} \text{Paartha Learner} \xrightarrow{\text{Consolidation}} \text{Independent Execution}$$

In EXP-032 through EXP-037, this collapsed into:
* Teacher generates tool call $\to$ Python executes tool call $\to$ Save trace $\to$ Mine trace $\to$ Add macro to library.

### What MUST Change in Teacher $\to$ Student Distillation:
For distillation to produce a new model, the teacher must teach **internal computational policies**, not just text answers:
1. **Teaching Problem Representation:** Distilling how to compress a complex problem into an explicit entity-relation graph $\mathcal{G}$.
2. **Teaching Computational Routing:** Training Paartha's fast decision heads ($\Theta_{\text{decision}}$) to predict the correct computational subgraph in a single non-autoregressive pass.
3. **Teaching Verification Invariants:** Learning what invariant predicates $\phi(S)$ must hold for a state transition to be valid.

---

## 9. Reassessing JEv & SET-CR

### 9.1 Reassessing JEv: The Fast Decision Substrate
In [JEV-001](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/JEV-001.md), we studied TypeSafe AI's Jev model (a non-autoregressive, calibrated decision model trained via RLCD).

* **What was valuable about JEv:**  
  The realization that **decisions should not be generated as text tokens**. Evaluating intent, routing, risk, and categorical choices is naturally a non-autoregressive classification/regression problem over bounded output spaces ($k \le 255$, Boolean, scalar), executable in 50–100ms for fractions of a cent.
* **Where JEv was misused:**  
  In EXP-036, JEv was reduced to a scalar confidence threshold ($\Delta < \tau$) for natural-language clarification.
* **The Deep Architectural Role of a JEv-like Substrate:**  
  In a dynamic computational architecture, a JEv-like substrate is the **Computation Router**. It inspects the input representation and outputs a discrete probability distribution over which computational subgraph to instantiate, without producing conversational tokens.

### 9.2 Reclassifying SET-CR: Execution Harness, Not Cognitive Engine
In [ABLATION-001](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-MECHANISM-ABLATION-001.md), Condition A6 (SET-CR Search & Rollback) achieved 83.3% success.

* **We must classify SET-CR correctly:**
  * SET-CR is **NOT** a new theory of intelligence.
  * SET-CR is **NOT** a fundamental cognitive primitive.
  * SET-CR **IS** an **exception-safe state execution harness with checkpoint rollback** (essentially transactions with `TRY/EXCEPT` and `ROLLBACK` applied to agent state).
* **Verdict:** Retain SET-CR as an execution substrate for stateful tasks, but stop treating it as the core definition of Paartha.

---

## 10. Precise Definition: What a "Paartha Model" Actually Is

We now formalize the exact computational anatomy of a genuine Paartha model:

```
                            PAARTHA MODEL ANATOMY
┌───────────────────────────┬───────────────────────────────────────────────────────────┐
│ Dimension                 │ Formal Mathematical & Architectural Specification         │
├───────────────────────────┼───────────────────────────────────────────────────────────┤
│ 1. Inputs                 │ Multimodal context $X = \langle \text{text}, \text{data},│
│                           │ \text{constraints} \rangle$.                             │
│ 2. Internal Representation│ Heterogeneous State Tuple:                                │
│                           │ $S = \langle \mathbf{z}_{\text{dense}}, \mathcal{G}_{rel},│
│                           │ \mathbf{c}_{epistemic} \rangle$.                          │
│ 3. Computation Selector   │ Calibrated Non-Autoregressive Policy Substrate:           │
│                           │ $\pi_\theta(C_k \mid S) \to \text{Categorical Distribution│
│                           │ over Computational Subgraphs}$.                           │
│ 4. Dynamic Computation    │ Instantiated Computational Graph $\mathcal{G}_C$:         │
│                           │ Composed of Neural Blocks, Symbolic Solvers, Algorithmic  │
│                           │ Iterators, and Relational Database Lookups.               │
│ 5. Execution Substrate    │ Sandboxed state transition with checkpoint stack:         │
│                           │ $S_{t+1} = \text{Execute}(\mathcal{G}_C, S_t)$.           │
│ 6. Invariant Verification │ Explicit symbolic invariant predicates $\Phi(S_{t+1})$:    │
│                           │ If $\Phi$ holds, commit state; else rollback and branch.  │
│ 7. Memory & Persistence   │ Dual-speed memory:                                        │
│                           │ • Fast: Overwritten working slot partition ($S_{working}$).│
│                           │ • Slow: Relational Knowledge Graph ($\mathcal{K}$) and    │
│                           │   Episodic Experience Store ($S_{episodic}$).             │
│ 8. Learned Parameters     │ • $\Theta_{\text{enc}}$: Multimodal representation encoder│
│                           │ • $\Theta_{\text{select}}$: RLCD-calibrated router        │
│                           │ • $\Theta_{\text{proc}}$: Neural algorithmic processors   │
│                           │ • $\Theta_{\text{gen}}$: Constrained surface realizer     │
│ 9. Growth Mechanism       │ Modular addition of specialized computational subgraphs   │
│                           │ accompanied by routing parameter updates ($\Delta \Theta$).│
│ 10. Output                │ Verified state projection or natural language dialogue    │
│                           │ synthesized strictly from verified state transitions.     │
└───────────────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 11. Minimal Architecture Hypothesis

To make this research scientifically tractable and falsifiable, we must specify the **smallest possible system** that embodies this computational divergence from a Transformer:

```
                          MINIMAL PAARTHA ARCHITECTURE (MPA)
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. INPUT: Relational / Algorithmic Query (e.g. Graph Pathfinding / Tabular Reasoning) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. ENCODER (Dense): Maps input into problem vector z in R^d                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. COMPUTATION ROUTER (Calibrated System 1 Head):                                     │
│    Evaluates z in a single forward pass -> outputs Choice among:                      │
│    • Circuit 1: Direct Neural Feedforward (for simple associative queries)            │
│    • Circuit 2: Iterative Latent Recurrent Loop (for multi-step relational search)    │
│    • Circuit 3: Deterministic Algorithmic Solver (for exact numerical/sort execution) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. DYNAMIC EXECUTION: Executes the chosen circuit over the structured state.          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. INVARIANT CHECKER: Verifies output against schema invariants.                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 6. OUTPUT: Final state or natural language response.                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### What MPA Computes Differently from a Standard Transformer:
* If given an associative factual query, MPA routes to Circuit 1, executing a small, fast 50M parameter feedforward pass ($O(1)$ compute).
* If given a complex algorithmic sorting/filtering query, MPA routes to Circuit 3, invoking an exact execution operator with zero hallucination and zero token-by-token matrix multiplies ($O(N \log N)$ exact compute).
* If given a multi-step reasoning deduction, MPA routes to Circuit 2, iterating a recurrent latent state with dynamic halting ($O(T)$ adaptive compute).
* **A standard Transformer forces all three tasks through the exact same $L$-layer sequence of dense attention multiplications.**

---

## 12. Computational Economics & Efficiency Analysis

A core pillar of the original vision was computational efficiency. We formalize this through **Computational Economics**:

$$\text{Efficiency Ratio } \eta = \frac{\text{Intrinsic Problem Complexity } \mathcal{H}(X)}{\text{Actual Incurred FLOPs } \mathcal{F}(X)}$$

```
                            COMPUTATIONAL ECONOMICS PROFILES
┌───────────────────────┬───────────────────────────────┬──────────────────────────────┐
│ Problem Class         │ Standard Transformer / LLM    │ Minimal Paartha Architecture │
├───────────────────────┼───────────────────────────────┼──────────────────────────────┤
│ Simple Fact Recall    │ 70B FLOPs (Full dense pass)   │ 100M FLOPs (Direct routing)  │
│ Arithmetic Operation  │ 70B FLOPs/token * 20 tokens   │ 1,000 FLOPs (Exact ALU call) │
│ Long-Chain Reasoning  │ 70B FLOPs * 2,000 o1 tokens   │ Iterative Latent Loop / Search│
│ Wasted Computation    │ ~80% of FLOPs spent on syntax │ < 10% (compute matched to    │
│                       │ and static layer overhead     │ problem complexity)          │
└───────────────────────┴───────────────────────────────┴──────────────────────────────┘
```

The fundamental metric of success for Paartha is **Compute-Quality Pareto Dominance**:
Can Paartha achieve equal or superior reasoning accuracy while using $\ge 5\times$ fewer inference FLOPs on heterogeneous problem distributions?

---

## 13. Adversarial Falsification: Trying to Kill the Idea

To maintain strict scientific integrity, we mount the strongest possible counterarguments against the proposed architecture:

### Critique 1: "Could an existing Sparse MoE with Mixture-of-Depths already do this?"
* **The Attack:** DeepSeek-V3 and Mixture-of-Depths (MoD) already route tokens to different expert MLPs and skip layers dynamically. Why do we need Paartha?
* **The Defense:** MoE and MoD route individual tokens across identical mathematical structures (dense matrix multiplications). They cannot route a problem to an exact symbolic solver, a graph relaxation loop, or a state checkpoint stack. They remain trapped in the tokenization bottleneck.

### Critique 2: "Does dynamic discrete computation create an impossible credit-assignment problem?"
* **The Attack:** If Circuit 3 is non-differentiable (e.g. an algorithmic solver), gradients cannot flow back into the Encoder. Training the Router requires RL over discrete choices, which collapses or requires millions of trials.
* **The Defense:** This is a real risk. However, it can be resolved by **Decoupled Training**:
  * The Encoder and Router are trained using RLCD on labeled problem-type distributions and verified trace rewards (similar to AlphaGo training policy heads on MCTS rollouts).
  * Neural circuits are trained on their respective domain embeddings.
  * The architecture does not attempt end-to-end backpropagation through discrete solvers.

### Critique 3: "Doesn't this require hand-crafting symbolic modules, losing neural generality?"
* **The Attack:** If Paartha relies on pre-programmed circuits (Circuit 1, 2, 3), it is just old-fashioned GOFAI (Good Old-Fashioned AI) dressed up with an embedding router.
* **The Defense:** The circuits are not brittle expert systems. Circuit 1 is a general neural representation; Circuit 2 is an algorithmic GNN / latent recurrent block; Circuit 3 is a typed tool library. The intelligence lies in the **calibrated non-autoregressive routing and state verification**, not in hardcoded rule trees.

---

## 14. Novelty Assessment & Comparative Literature Table

| Approach | Representation | Computation | Dynamic Selection? | Persistent Memory | Learning Paradigm | Critical Limitation | Paartha Difference |
|:---|:---|:---|:---:|:---|:---|:---|:---|
| **Standard Transformer** | 1D Token sequence | Fixed $L$-layer dense Attention + MLP | None (Uniform FLOPs) | KV Cache (transient) | End-to-end SGD on next-token loss | Compute is static and uncalibrated; hallucination prone | Heterogeneous representation + dynamic circuit routing |
| **Sparse MoE (DeepSeek / Switch)** | 1D Token sequence | Dynamic expert MLPs | Token-level MLP selection | KV Cache (transient) | End-to-end SGD with load-balancing loss | Experts are identical dense MLPs; no symbolic or algorithmic tools | Routes entire problem to heterogeneous computational modalities |
| **Adaptive Compute (ACT / PonderNet)** | 1D Token sequence | Recurrent depth iterations | Scalar halting probability | Transient hidden state | SGD with geometric halting prior | Scales depth only; cannot change the computational operator | Selects different computational operators (symbolic, neural, loop) |
| **Tool-Augmented LLMs (ReAct / Toolformer)** | 1D Token sequence | Autoregressive text $\to$ API call $\to$ text | LLM token prediction | Context window text string | In-context prompting or SFT on tool traces | Extremely high latency; unverified argument hallucination | Native non-autoregressive routing + SET-CR state rollback |
| **Neuro-Symbolic (DreamCoder)** | Symbolic LISP AST | Discrete program execution | Neural recognition guide | Evolving LISP library | Wake-sleep discrete search + compression | Combinatorial search explosion; cannot handle fuzzy text | Hybrid neural-symbolic: neural for semantics, symbolic for execution |
| **Test-Time Search (o1 / R1)** | 1D Token sequence | Millions of autoregressive thinking tokens | Number of tokens sampled | Context window string | RL with rule-based / verifier reward | Massive FLOP waste simulating search via natural language text | Search occurs in state/graph space, not token generation space |
| **Minimal Paartha Architecture (Proposed)** | $\langle \mathbf{e}_{\text{dense}}, \mathcal{G}_{\text{rel}}, \mathbf{c}_{\text{epistemic}} \rangle$ | Heterogeneous circuits (Neural, Latent Loop, Symbolic) | Single-pass calibrated router ($\Theta_{\text{select}}$) | Three-tier state ($S_{working}, S_{episodic}, \mathcal{K}$) | RLCD router training + modular circuit optimization | Must prove decoupled training converges without end-to-end SGD | Replaces token simulation of thought with native computational execution |

---

## 15. The Minimal Falsifiable Experiment: EXP-RESET-001

To test this architecture without building a massive system, we design a minimal, definitive falsification experiment:

```
                            EXPERIMENT EXP-RESET-001
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ The Benchmark: Heterogeneous Algorithmic & Semantic Problem Suite (HASP-100)          │
│ Composed of 100 mixed problems across three distinct computational regimes:            │
│ 1. Regime A: Semantic Associative Inquiries (Factual queries, paraphrasing, synthesis)│
│ 2. Regime B: Relational Algorithmic Tasks (Shortest path, cycle detection, topological)│
│ 3. Regime C: Exact Numerical / Transformation Tasks (Multi-table joins, sort, filters) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ The Competitors (Equal Model Parameter Scale ~ 500M - 1B parameters):                 │
│ • Baseline 1: Standard Autoregressive Transformer (1B dense parameters)               │
│ • Baseline 2: Transformer + Chain-of-Thought (o1-style test-time compute)              │
│ • Baseline 3: Transformer + ReAct Tool Calling                                        │
│ • Paartha MPA: Minimal Paartha Architecture (Encoder + Calibrated Router + 3 Circuits) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Pre-Registered Falsification Criteria:                                                │
│ Paartha MPA is FALSIFIED if:                                                          │
│ 1. Accuracy on Regime B/C does not exceed Baseline 1 by at least 20 percentage points. │
│ 2. Total FLOPs consumed by MPA exceed 50% of Baseline 2 (Compute efficiency failure). │
│ 3. Calibrated Router accuracy fails to achieve >= 85% correct circuit dispatch.        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 16. Final Scientific Verdict & Recommendation

In accordance with Section 23 of the reset mandate, we evaluate the three possible outcomes:

* **OUTCOME A — CONTINUE:** A genuinely differentiated architecture has been identified with a plausible mechanism and minimal falsifiable experiment.
* **OUTCOME B — REFRAME:** The original idea is valuable, but existing research already provides most of the mechanism. Paartha should focus on a narrower unsolved problem.
* **OUTCOME C — ABANDON:** No defensible architectural distinction or tractable research hypothesis remains.

### The Decisive Verdict: **OUTCOME B — REFRAME**

#### Scientific Justification:
1. **Why NOT Outcome A (Continue as previously conceived)?**  
   The previous conception claimed that Paartha could discover generalizable cross-domain computational abstractions without parameter updates ($\Delta \Theta = 0$). That claim was **empirically falsified** in TRANSFER-001 ($1.00\times$ transfer ratio). Continuing to treat offline macro discovery as the core of intelligence is scientifically indefensible. Furthermore, building an end-to-end foundation model from scratch without massive compute is intractable.
2. **Why NOT Outcome C (Abandon)?**  
   The empirical evidence from ABLATION-001 and CTX-002 demonstrated that **SET-CR state rollback, typed capability contracts, and non-autoregressive decision routing solve fundamental failure modes of modern LLMs** (raising multi-step task success from 33% to 83% and cutting latency by 43%). Abandoning the research would discard genuine, highly valuable computational mechanisms.
3. **The Reframed Focus:**  
   Paartha must officially reframe from:
   > *"An autonomous cognitive architecture that discovers universal abstractions without weight updates"*  
   to:
   > **"A Heterogeneous Adaptive Inference Architecture that dynamically routes problems to specialized computational circuits (neural, latent recurrent, symbolic) using a calibrated System 1 decision substrate and verified state-checkpoint execution."**

### Immediate Prescriptions for the Next Phase:
1. **Halt Agent Scaffolding:** Cease treating prompt wrappers and ReAct loops as model architecture.
2. **Freeze Macro Discovery:** Archive the frequent motif / anti-unification pipeline until structural graph isomorphism routing is theoretically resolved.
3. **Focus on the Compute-Selection Interface:** Develop and train the calibrated non-autoregressive router ($\Theta_{\text{select}}$) that predicts computational graphs from problem representations.
4. **Implement EXP-RESET-001:** Build the Minimal Paartha Architecture on the HASP-100 benchmark to measure whether dynamic circuit execution achieves compute-quality Pareto dominance over standard Transformers.
