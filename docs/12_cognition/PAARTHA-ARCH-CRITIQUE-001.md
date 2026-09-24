**Status: Active — Adversarial Red-Team Audit & Architectural Falsification**

# PAARTHA-ARCH-CRITIQUE-001: Adversarial Tear-Down of the Paartha Architecture & Training Strategy

**Role note:** Produced under the hostile reviewer mandate. This document is explicitly designed to **tear down, invalidate, expose, and red-team** the architecture, state model, IR, parameter claims, and training strategies recently proposed in [`PAARTHA-ARCH-001.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ARCH-001.md) and [`JEV-001.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/JEV-001.md).

**Core Rule:** Do NOT protect previous proposals. Do NOT defend ideas because they sound elegant. Every major claim is labeled under its strict epistemic status:
- **SUPPORTED**: Directly verified by completed multi-seed empirical experiments in this repository.
- **HYPOTHESIS**: A plausible theoretical conjecture lacking empirical demonstration.
- **UNDEFINED**: An abstraction, term, or quantity used without formal, measurable specification.
- **CONTRADICTED**: Directly falsified or challenged by repository experiments or fundamental computer science literature.

---

## 1. What Is a “Parameter” in Paartha? (Deconstructing the Category Error)

The recent proposals repeatedly mix neural weights, discrete state, knowledge graphs, and execution engines under vague descriptions of "a small model" or "a 1.2B system." This is a severe conceptual category error.

### 1.1 The Strict Ontological Boundary
We must disentangle the six distinct concepts that have been conflated:

| Category | Strict Definition | Physical Implementation in Paartha | Differentiable? | Persistent? |
|---|---|---|---|---|
| **A. Weights / Parameters ($\Theta$)** | Dense or sparse floating-point tensors optimized via gradient descent. | PyTorch `nn.Parameter` tensors ($\theta_{enc}, \theta_{decide}, \theta_{gen}$). | **YES** | **YES** |
| **B. State ($\mathcal{S}$)** | The dynamic, mutable runtime configuration of the system at step $t$. | `WorkingStateStore` slots, search stack, active goals. | **NO** | **EPHEMERAL** |
| **C. Knowledge ($\mathcal{K}$)** | Explicit declarative relations and invariant assertions about the world. | KRS-001 graph ($\mathcal{V}_E, \mathcal{E}_R$) and $S_{episodic}$ key-value entries. | **NO** | **YES** |
| **D. Capabilities ($\mathcal{L}$)** | Discrete executable routines, tools, algorithms, and AST transformations. | Python callables, sandboxed scripts, symbolic transforms. | **NO** (except neural adapters) | **YES** |
| **E. Representations** | Geometric vectors or discrete symbolic structures carrying meaning between steps. | Latent vectors $\mathbf{z}_x$, discrete IR frames, token IDs. | **HYBRID** | **TRANSIENT** |
| **F. Runtime Mechanisms** | The execution engine, search loop, and memory access logic. | SET-CR search VM, graph traversal algorithms, indexing logic. | **NO** | **STATIC CODE** |

### 1.2 The "500M Parameters" Challenge
In [`PAARTHA-ARCH-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ARCH-001.md), we proposed that the surface realizer $\theta_{gen}$ would be "~500M parameters."

**Hostile Attack**: What are those 500,000,000 floating-point numbers actually encoding?
- If world knowledge lives in $\mathcal{K}$,
- If reasoning lives in invariant deduction and SET-CR,
- If decision logic lives in $\theta_{decide}$,
- If working context lives in `WorkingStateStore`,

then $\theta_{gen}$ is doing nothing other than mapping a structured proof trace into grammatical natural language. 
- Why does turning `is_a(whale, mammal) & rule(...) => breathes(whale, air)` into English, Telugu, or Hindi require 500 million numbers? 
- Conversely, if $\theta_{gen}$ is 500M parameters, it has sufficient statistical capacity to memorize and hallucinate facts independently of the proof trace, directly violating our non-hallucination guarantee!
- **Verdict**: **UNDEFINED & ARBITRARY**. We have zero empirical data proving what parameter capacity is required for proof-trace realization. Specifying "500M" or "1.2B" is engineering fiction. All explicit parameter counts are hereby **STRICKEN** until empirically measured via scaling curves.

---

## 2. Challenging the Fixed Parameter Count Assumption

The architectural proposal casually assumed a fixed-capacity model ($\Theta_{core} \le 1.2\text{B}$).

```
FIXED-CAPACITY PARADOX:
If Paartha's parameters are fixed at initialization, then as Paartha sequentially learns:
English -> Telugu -> Hindi -> Coding -> Geometry -> Agentic Tool Use
all new representations MUST compress into the original fixed tensor space.
```

### The Inevitable Collision with EXP-018:
- In [EXP-018](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-018), Paartha directly proved that updating fixed transformer parameters under continual, staged distributions causes **immediate catastrophic forgetting** (memory coverage collapsed to 0.0%).
- If Paartha has a fixed parameter backbone, teaching it Telugu after English will degrade its English representations unless it rehearses everything.
- **Verdict**: **CONTRADICTED**. A fixed parameter count is structurally incompatible with Paartha's continual learning objective.

### The Alternatives Evaluated:
1. **Fixed-capacity Paartha**: **REJECTED** (Falsified by EXP-018).
2. **Capability-Scaled Modular Parameter Spaces**: **SUPPORTED by EXP-004 & EXP-021**. The core backbone must remain frozen or slow-updating, while each new language, domain, or capability attaches its own **modular, isolated parameter block** in $\mathcal{L}$ (e.g. localized adapter weights or distinct primitive classifiers).

---

## 3. What Does “Learning” Actually Mean in Paartha?

We have used the word "learning" as an undisciplined umbrella term. We must formally define the exact physical changes that occur during learning events:

```
+──────────────────────────+───────────────────────────────────────+──────────────────────────+
| Event                    | What Actually Changes?                | What Does NOT Change?    |
+──────────────────────────+───────────────────────────────────────+──────────────────────────+
| Learning a Fact:         | 1. S_episodic gains namespaced KV     | theta (NO gradient step) |
| "Neptune is a planet"    | 2. K gains edge: (Neptune, is_a,      | L (No new capability)    |
|                          |    Planet) via EXP-022 write rule     | S_working                |
+──────────────────────────+───────────────────────────────────────+──────────────────────────+
| Learning a Language:     | 1. theta_enc gains new tokenizer/vocab| K (Concepts unchanged)   |
| (e.g., Telugu)           | 2. Dedicated modular language adapter | C_I (Logic unchanged)    |
|                          |    in L trained via distillation      | S_episodic               |
+──────────────────────────+───────────────────────────────────────+──────────────────────────+
| Learning a Capability:   | 1. L registers new executable routine | K (Knowledge unchanged)  |
| (e.g., Quicksort / Tool) | 2. theta_decide updates candidate set | theta_enc (Ingress same) |
|                          | 3. C_I registers pre/post conditions  |                          |
+──────────────────────────+───────────────────────────────────────+──────────────────────────+
| Conversational Learning: | 1. S_working updates slots in-place   | theta (No weight update) |
| (Multi-turn dialogue)    | 2. s_hist appends turn record         | K (No global fact added) |
+──────────────────────────+───────────────────────────────────────+──────────────────────────+
```

**Takeaway**: In Paartha, **90% of learning events involve ZERO backpropagation into neural weights**. Learning is primarily the accumulation of verified symbolic edges ($\mathcal{K}$), executable routines ($\mathcal{L}$), and episodic entries ($S_{episodic}$). Gradient descent is reserved strictly for training representation bridges and decision calibration.

---

## 4. Critical Attack on the Proposed Paartha IR

[`PAARTHA-ARCH-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ARCH-001.md) proposed a simple semantic frame IR:
```json
{"speech_act": "...", "intent": "...", "frame": {"predicate": "...", "roles": {...}}}
```

This toy schema collapses immediately when exposed to real-world cognitive and communicative demands:

```
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| Linguistic / Cognitive   | Concrete Real-World Example             | Why the Proposed IR      |
| Phenomenon               |                                         | Completely Fails         |
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 1. Anaphora / Ellipsis   | "What about the second one?"            | Cannot resolve referents |
|                          |                                         | without discourse stack. |
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 2. Temporal Reasoning    | "What happened before the server died?" | Has no temporal ordering,|
|                          |                                         | tense, or interval logic.|
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 3. Negation Scope        | "Not all mammals live on land."         | Frame predicates cannot  |
|                          |                                         | represent quantifier neg.|
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 4. Epistemic Modality    | "He might have forgotten his keys."     | Truth is binary; cannot  |
|                          |                                         | express modal possibility|
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 5. Propositional Attitude| "She believes John is lying."           | Cannot embed a full frame|
|                          |                                         | as an argument of belief.|
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 6. Hypotheticals         | "If it rains tomorrow, cancel the trip."| No conditional branch    |
|                          |                                         | representation.          |
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 7. Generalized Quantifier| "Most students passed the exam."        | First-order logic fails  |
|                          |                                         | on non-first-order "most"|
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 8. Social Intent / Irony | "Oh, brilliant job crashing the build!" | Speech-act enum treats   |
|                          |                                         | praise literally.        |
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 9. Program / Code Patch  | "Refactor this function to O(N log N)." | Code ASTs cannot fit     |
|                          |                                         | into semantic role frames|
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 10. Multi-Step Planning  | "Book flights, then reserve a cab."     | Relational frames have no|
|                          |                                         | dependency scheduling.   |
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
```

### The Symbolic Over-Expansion Trap:
If we patch the IR by adding schemas for temporal logic, epistemic logic, modal logic, causal DAGs, discourse anaphora, ASTs, and planning primitives, **the IR ceases to be a lightweight representation and becomes an uncomputable, bloated programming language**.
- **Verdict**: **CONTRADICTED & GROSSLY UNDERSPECIFIED**. A single monolithic JSON schema cannot bridge dialogue, code, planning, and formal logic without collapsing under its own complexity.

---

## 5. Is Paartha IR Actually a “Language”?

We have carelessly called this "Paartha Language" while describing it as a JSON Schema.
- A **serialization format** (JSON) is not a language.
- A **grammar** (BNF) is not a cognitive representation.
- A **relational tuple** is not a mental state.

### The Resolution:
- JSON is merely an external debugging and serialization wire-format.
- Inside Paartha, the internal representation is an **in-memory typed graph and tensor state**:
  $$\text{Internal State} \ne \text{JSON string}$$
- Using JSON strings inside the execution loop would impose massive string serialization, parsing overhead, and syntax vulnerability. All internal communication between components must occur via **compiled in-memory data structures** (e.g. pointer-based graph nodes and tensor embeddings), not text-based JSON parsing!
- **Verdict**: **UNDEFINED**. Calling JSON "Paartha Language" was sloppy terminology.

---

## 6. Attacking the “Language-Neutral Reasoning” Claim

The claim that Telugu, Hindi, and English can all map to a single, identical language-neutral IR without information loss is the classical **Interlingua Fallacy** (which collapsed 1980s machine translation efforts like Eurotra and KANT).

### Devastating Counterexamples in Indian Languages:

1. **Evidentials in Telugu**:
   - Telugu: *"అతను వచ్చాడట"* (*Atanu vaccāḍaṭa*).
   - Meaning: *"He arrived, reportedly / so I heard."* The morpheme `-aṭa` is a grammaticalized hearsay evidential.
   - English has no grammatical evidential. If the IR is language-neutral, it must either:
     - Discard `-aṭa` (causing semantic loss and epistemic blindness), or
     - Force every English sentence to declare an evidential tag (bloating the IR unnaturally).
2. **Untranslatable Cultural Pragmatics**:
   - Telugu: *"అయ్యో!"* (*Ayyō!*). Depending on context, tone, and pause, this expresses empathy, acute sorrow, mild embarrassment, or shock. It has no predicate, no agent, and no patient. Mapping it to `{"predicate": "grief", "roles": {}}` destroys its communicative function.
3. **Grammaticalized Social Distance**:
   - Telugu (*నువ్వు* / *మీరు*), Hindi (*तू* / *तुम* / *आप*). Social hierarchy and politeness are encoded directly into pronoun and verb morphology. English uses lexical hedges ("Would you mind...").
   - If the IR strips honorifics, surface realization into Telugu or Hindi will produce socially offensive, robotic speech.

### Verdict:
- **HYPOTHESIS — PARTIALLY CONTRADICTED BY LINGUISTICS**. 
- A 100% language-neutral semantic representation is impossible without either losing pragmatics or bloating into absurdity.
- **Architectural Correction**: Paartha must use a **Universal Conceptual Core** (for physical, logical, and factual relations) PLUS a **Pragmatic & Cultural Extension Layer** (retaining language-specific honorifics, evidentials, and discourse markers).

---

## 7. Destroying the “500M Model Can Easily Learn It” Claim

[`PAARTHA-ARCH-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ARCH-001.md) casually asserted: *"A compact 300M–500M parameter model can easily learn text $\leftrightarrow$ IR translation with ~50,000 examples."*

### Why This Claim Is Baseless:
1. **Sample Complexity is Untested**: Why 50,000? Why not 5,000? Why not 5,000,000? In the semantic parsing literature (Spider, AMR, GeoQuery), 50,000 synthetic examples are notoriously insufficient for out-of-distribution systematic generalization.
2. **Memorization vs. Compositionality**: Lake & Baroni (SCAN) and our own [EXP-020](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-020) proved that generic neural seq2seq models achieve **0.71% accuracy** on compositional generalization because they memorize lexical combinations rather than learning the generative grammar.
3. **The Multilingual Multiplier**: Learning systematic semantic parsing across Telugu, Hindi, and English simultaneously with distinct scripts, morphologically rich agglutination (Telugu), and non-concatenative morphology requires significant capacity and cross-lingual alignment data.
- **Verdict**: **UNSUPPORTED GUESS**. The sample complexity and parameter requirements for text $\to$ IR mapping are completely unknown.

---

## 8. Attacking Teacher Distillation & the Hallucination Propagation Risk

The proposed training strategy assumes:
$$\text{Frontier Model (Teacher)} \longrightarrow \text{Generates IR} \longrightarrow \text{Trains Paartha}$$

### The Fatal Vulnerability: Permanent Structured Hallucinations
- Frontier models (Llama-3-70B, GPT-4o) hallucinate constantly. They state false facts with high confidence and invent plausible-sounding causal explanations.
- When an LLM hallucinates during a chat session, the error is ephemeral and disappears in the next conversation.
- **In Paartha, if the teacher outputs a hallucinated relation**:
  $$\text{Teacher: "Whales are fish."} \longrightarrow \text{Compiled into IR} \longrightarrow \text{Permanently written into } \mathcal{K}$$
  **The hallucination becomes immutable structural ground truth inside Paartha’s Knowledge Graph!**

```
HALLUCINATION PROPAGATION TRAP:
Frontier LLM Hallucination
           │
           ▼
    Valid JSON Schema
           │
           ▼
    Compiler Passes
           │
           ▼
Permanent Corrupted Edge in Paartha's Knowledge Graph K
```

### The Circularity Trap:
If we ask the *same* frontier teacher to verify the IR it just produced, it will confirm its own hallucination with near-100% confidence.
- **Verdict**: **CRITICAL UNMITIGATED FLAW**. Distilling teacher outputs directly into persistent knowledge without external ground-truth verification or human supervision is fatal to system reliability.

---

## 9. Attacking the “Zero Noisy Data” Claim

[`PAARTHA-ARCH-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ARCH-001.md) claimed: *"Every piece of training data... is run through Paartha’s deterministic compiler... Zero noisy or hallucinated data enters Paartha’s weights."*

This claim conflates **Syntactic Form** with **Empirical Truth**.

```
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| Level of Verification    | What Can Actually Be Verified?          | Can a Compiler Detect?   |
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
| 1. Syntactic Validity    | Is the string well-formed JSON?         | **YES**                  |
| 2. Schema Validity       | Are required fields present?            | **YES**                  |
| 3. Type Validity         | Are fields of correct datatype?         | **YES**                  |
| 4. Logical Consistency   | Does assertion violate A & !A?          | **YES** (partially)      |
| 5. Factual Correctness   | Is the assertion true in reality?       | **NO — IMPOSSIBLE**      |
| 6. Empirical Truth       | Does the code run without side-effects? | **ONLY IN SANDBOX**      |
+──────────────────────────+─────────────────────────────────────────+──────────────────────────+
```

A compiler can confirm that `whale is_a fish` is syntactically flawless and satisfies the schema. It cannot know that whales are mammals.
- **Verdict**: **FALSIFIED / ERRONEOUS CLAIM**. The claim of "zero noisy data" is false and must be permanently retracted.

---

## 10. Attacking Knowledge Graphs as "Reasoning"

The architecture relies heavily on KRS-001 relational graphs ($\mathcal{K} = \langle \mathcal{V}_E, \mathcal{E}_R, \mathcal{C}_I \rangle$) for deduction.

Knowledge graphs are effective for taxonomic syllogisms (`Whale is_a Mammal => breathes Air`). **They fail catastrophically across almost all other cognitive domains**:
1. **Arithmetic**: You cannot store the sum of all numbers as edges in a graph.
2. **Continuous Physics / Spatial Reasoning**: Trajectory calculation and collision detection cannot be expressed as static relations.
3. **Code Execution**: Dynamic memory pointers, loops, and stack frames cannot be simulated via static graph queries.
4. **Probabilistic Reasoning**: Bayesian belief updating under continuous noise breaks standard relational logic.
- **Verdict**: **ESTABLISHED BOUNDARY**. Knowledge graphs solve taxonomic recall, not general reasoning.

---

## 11. Complete Information-Flow Model: What Does the Teacher Actually Teach?

To prevent dumping all teacher outputs into a single training soup, we map each teacher output to its exact destination in Paartha:

```
+─────────────────────────────────+────────────────────────────────────────────────────────────+
| Teacher Output Stream           | Physical Destination in Paartha Architecture               |
+─────────────────────────────────+────────────────────────────────────────────────────────────+
| 1. Language Pairs (Text <-> IR) | Transient dataset training theta_enc and theta_gen         |
| 2. Decision Scenarios (RLCD)    | Calibration dataset training theta_decide                  |
| 3. Declarative Facts (Triples)  | Relational Graph K and Episodic Memory S_episodic          |
| 4. Formal Domain Invariants     | S_invariants (C_I) — REQUIRES FORMAL VERIFICATION          |
| 5. Code & Algorithmic Primitives| Capability Library L — REQUIRES SANDBOX TEST PASS          |
| 6. Search Trajectories          | Offline compilation into macro-primitives in L             |
| 7. Heuristic Priors             | Search policy weights pi(a | s) in theta_decide            |
+─────────────────────────────────+────────────────────────────────────────────────────────────+
```

---

## 12. What Makes Paartha a "Model"? (Resolving the Identity Crisis)

Is Paartha a "model"?

```
Is Paartha:
  (A) The neural weights (theta_enc, theta_decide, theta_gen)?
  (B) The neural weights + Knowledge Graph?
  (C) The complete computational system including runtime and sandboxes?
```

- If Paartha is just (A), then Paartha cannot reason, retain state, or verify anything.
- If Paartha is (C), then **calling Paartha a "model" is a category error**.
- **Formal Resolution**: Paartha is an **Adaptive Computational Cognitive Architecture**. The neural networks inside Paartha ($\Theta$) are merely **perceptual and decision transducers**. Treating Paartha as "a model" encourages thinking in terms of monolithic weights and training runs, which directly undermines our entire architectural foundation.

---

## 13. What Is the Unit of Capacity in Paartha?

LLMs measure capacity via **parameter count** (e.g. 7B, 70B). In Paartha, parameter count is almost meaningless because 90% of competence resides outside neural weights.

Paartha requires a **Vector of Capacity Metrics**:

$$\mathbf{C}_{\text{Paartha}} = \langle C_{\text{neural}}, C_{\text{facts}}, C_{\text{rules}}, C_{\text{primitives}}, C_{\text{context}}, C_{\text{search}} \rangle$$

```
1. C_neural:      Floating-point parameter count in encoders/decoders/decision heads.
2. C_facts:       Number of verified relational edges in K and S_episodic.
3. C_rules:       Number of active logical invariants in C_I.
4. C_primitives:  Number of verified executable routines in Capability Library L.
5. C_context:     Slot capacity of WorkingStateStore.
6. C_search:      Maximum search depth and branch budget in SET-CR VM.
```

---

## 14. Steelmanning the Opposition: The Case Against Paartha

To maintain intellectual honesty, we state the strongest possible argument against our entire research project:

### The Hostile Counter-Thesis (The Modern Deep Learning Argument):
> *"Paartha is a doomed attempt to resurrect Good Old-Fashioned AI (GOFAI). History has repeatedly proven (Rich Sutton’s 'The Bitter Lesson') that hand-crafted representations, knowledge graphs, symbolic IRs, and modular cognitive architectures always lose to general methods leveraging massive search and end-to-end learning over large compute.*
> 
> *A standard 70B transformer with fine-tuned tool calling, RAG, and an inference-time reasoning loop (like o1/CoT) already handles dialogue, code, planning, and tool execution without requiring hand-engineered IR schemas, fragile graph parsers, or rigid write policies. Paartha is taking on immense architectural complexity to solve problems that scale and post-training alignment will solve naturally."*

### Paartha’s Counter-Defense (Where Paartha Must Win to Survive):
The Bitter Lesson applies when engineers try to hand-code knowledge. Paartha does **not** hand-code knowledge; it uses teachers and search to learn. 

Paartha's existence is justified **only if it empirically outperforms monolithic LLMs on five specific failure modes that gradient descent cannot fix**:
1. **Catastrophic Forgetting**: Proved in EXP-018; monolithic weights cannot learn continually without rehearsal.
2. **Compositional Generalization**: Proved in EXP-020; transformers score 0.71% on SCAN compositions where modular structures score 100%.
3. **Deceptive Subgoal Collapse**: Proved in EXP-CCS-0; greedy autoregression collapses (0%) where sandboxed search with rollback succeeds (100%).
4. **Epistemic Boundaries**: Monolithic LLMs cannot reliably know what they do not know.
5. **Token Cost / Inference Economics**: Multi-turn quadratic attention over large token buffers is fundamentally unsustainable compared to $O(1)$ in-place state slots.

---

## 15. What Must Remain Neural vs. Symbolic vs. Either

```
+──────────────────────────────+──────────────────────────────+──────────────────────────────+
| MUST REMAIN NEURAL           | MUST REMAIN SYMBOLIC / CODE  | CAN BE HYBRID (EITHER)       |
+──────────────────────────────+──────────────────────────────+──────────────────────────────+
| • Surface Speech Parsing     | • Formal Invariant Checking  | • Decision Heuristics        |
| • Acoustic / Text Encoding   | • State Rollback & Sandbox   | • Concept Clustering         |
| • Surface Realization Fluency| • Relational Proof Chaining  | • Macro-Primitive Induction  |
| • Perceptual Pattern Match   | • Epistemic Slot Reservation | • Discourse Topic Tracking   |
| • Calibrated Confidence RLCD | • Memory Key Namespacing     | • Capability Routing Cache   |
+──────────────────────────────+──────────────────────────────+──────────────────────────────+
```

---

## 16. Hostile Reviewer Summary: The Audit Scorecard

```
===================================================================================================
                                PAARTHA ARCHITECTURAL SCORECARD
===================================================================================================

[CLAIM 1] "Paartha is a 1.2B parameter model"
          Status: CONTRADICTED & ARBITRARY. Retracted immediately.

[CLAIM 2] "A fixed parameter backbone can support continual multi-language learning"
          Status: CONTRADICTED by EXP-018. Modular parameter expansion in L required.

[CLAIM 3] "Paartha IR handles universal reasoning across Telugu, Hindi, and English"
          Status: HYPOTHESIS / PARTIALLY CONTRADICTED by linguistic evidentials and pragmatics.

[CLAIM 4] "Compiler + Invariant Verifier guarantees Zero Noisy Data"
          Status: FALSIFIED. Compilers verify syntax/schema, not empirical truth.

[CLAIM 5] "A 500M parameter model easily learns Text <-> IR with 50,000 examples"
          Status: UNDEFINED & UNSUPPORTED GUESS. Sample complexity is completely unknown.

[CLAIM 6] "Knowledge Graphs provide general reasoning"
          Status: CONTRADICTED. KGs fail at arithmetic, code, physics, and continuous dynamics.

[CLAIM 7] "Teacher distillation yields reliable persistent knowledge"
          Status: CRITICAL UNMITIGATED FLAW. Teacher hallucinations become permanent corruptions.
===================================================================================================
```

---

## 17. Decisions That MUST Be Made Before Any Training Begins

1. **Retract All Explicit Parameter Targets**: Stop saying "100M encoder", "20M decision head", or "500M realizer". Parameterize only after measuring validation loss curves on real tasks.
2. **Abandon the Single Universal JSON IR**: Split the internal representation into a **Universal Relational Core** (first-order relations) and a **Domain-Specific Execution Extension** (ASTs for code, causal graphs for physics, pragmatics for Indic languages).
3. **Establish External Ground-Truth Verification for Teachers**: Teacher-generated facts must NEVER enter $\mathcal{K}$ permanently without passing an empirical verifier, multi-teacher consensus check, or human mentor sign-off.
4. **Define Modular Parameter Expansion**: Build the architecture around **frozen core representations + modular capability adapters in $\mathcal{L}$** to prevent EXP-018 catastrophic forgetting during continual multilingual expansion.
5. **Execute EXP-SPEAK-0 Before Architectural Scaling**: Measure empirical sample complexity and compositional generalization on a small, honest benchmark before committing to any training pipeline.
