**Status: Active — Foundational Architectural Specification**

# PAARTHA-ARCH-001: The Computational Architecture of Paartha

**Role note:** Produced under the foundational research directive to move from conceptual research toward defining a **proper computational architecture for Paartha**. 
This document defines:
> **The smallest coherent computational architecture that can make Paartha “Speak” (Stage 1) while establishing the exact computational primitives that scale across the 7-stage capability ladder:**
$$\text{Stage 1: Speak} \longrightarrow \text{Stage 2: Understand} \longrightarrow \text{Stage 3: Brainstorm} \longrightarrow \text{Stage 4: Plan} \longrightarrow \text{Stage 5: Code} \longrightarrow \text{Stage 6: Act} \longrightarrow \text{Stage 7: General Problem Solving}$$

This specification builds directly on:
- [`docs/12_cognition/CTX-002.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/CTX-002.md) *(State, Memory, Weights, and Inference Archaeology)*
- [`docs/12_cognition/JEV-001.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/JEV-001.md) *(Calibrated Decision Substrates & RLCD)*
- [`docs/12_cognition/GDR-003.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/GDR-003.md) *(SET-CR: Search over Transformations with Rollback)*
- [`docs/13_state_model/SOS-001.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/13_state_model/SOS-001.md) *(State Ownership & Write Disciplines)*
- [`docs/17_knowledge/KRS-001.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/17_knowledge/KRS-001.md) *(Computational Knowledge Graph & Deductive Engine)*

Every major architectural claim is explicitly labeled with its epistemic status:
`Established`, `Observed experimentally`, `Derived from previous Paartha experiments`, `Inferred from JEv`, `Architectural hypothesis`, or `Unknown`.

---

## 1. First Principles: What Does “Speak” Actually Require?

Mainstream AI reduces "Speak" to an autoregressive language model sampling tokens from next-token probabilities: $P(w_t \mid w_{<t})$. This formulation conflates understanding, intent determination, memory retrieval, epistemic self-assessment, reasoning, and phonological/syntactic realization into a single unconstrained stochastic process.

From first principles (drawing on computational linguistics, speech act theory, and grounding models), for an intelligent computational agent to receive a human utterance and produce an appropriate response, it must execute **seven strictly distinct functional transformations**:

```
+───────────────────────────────────────────────────────────────────────────────────────────+
|                                COMPUTATIONAL ANATOMY OF "SPEAK"                           |
|                                                                                           |
|  1. Ingress & Grounding:      Map surface utterance into structured discourse frame       |
|  2. Context Resolution:       Bind referents & resolve anaphora against working state     |
|  3. Epistemic Assessment:     Query knowledge graph to detect known vs. missing facts     |
|  4. Pragmatic Decision:       Select speech act (Direct Answer | Clarify | Explain | N/A) |
|  5. Semantic Formulation:     Construct verified semantic proof trace or slot query       |
|  6. Surface Realization:      Render verified semantic object into fluent language tokens |
|  7. State & Memory Update:    Record interaction episode & commit newly taught assertions  |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### Analysis: Can Any of These Be Unified or Collapsed?
1. **Can Ingress Grounding and Pragmatic Decision be collapsed?**
   - **YES** *(Inferred from JEv / Derived from EXP-003)*. A calibrated decision model (System 1) can take the raw utterance together with the active working state and directly output the discrete speech act (`Choice`), identify missing slots (`Noul`), and route to the appropriate capability domain without producing intermediate text.
2. **Can Semantic Formulation and Surface Realization be collapsed?**
   - **NO — STRUCTURALLY FORBIDDEN** *(Derived from previous Paartha experiments: EXP-009, EXP-026)*. If the language generator simultaneously invents the semantic fact while predicting tokens, it is statistically prone to hallucination. Semantic truth must be established by structural deduction or explicit memory retrieval **before** the surface realization engine formats it into natural language.
3. **Can Context Resolution be eliminated in favor of full-context attention?**
   - **NO — FALSIFIED** *(CTX-001, EXP-019)*. Bounded working memory requires an in-place overwritten state representation (`WorkingStateStore`) to avoid write-starvation and catastrophic recency degradation.

---

## 2. Paartha’s Fundamental State Model

Paartha replaces the conventional LLM state representation (monolithic weights + activations + token context buffer + KV cache) with a **rigorous, multi-tier state model**:

$$\mathcal{S}_t = \langle \Theta, \mathcal{L}, \mathcal{K}, S_{episodic}, S_{working}, s^{hist}, S_{decision} \rangle$$

```
                                  PAARTHA COMPLETE STATE MODEL
  =================================================================================================
  
  [A] PERSISTENT LEARNED PARAMETERS (Theta)
      - theta_enc:    Compact linguistic/state encoder (~50M - 100M parameters)
      - theta_decide: Calibrated System 1 decision heads (RLCD-trained, ~10M - 50M parameters)
      - theta_gen:    Constrained surface realization decoder (~300M - 1B parameters)
  
  [B] CAPABILITY STATE (L)
      - Registry of discrete executable primitives: L = { p_1, p_2, ..., p_K }
      - Each primitive p_i = < Signature, Invariants, ExecutionSandbox, Pre/PostConditions >
  
  [C] RELATIONAL KNOWLEDGE STATE (K)
      - Formal KRS-001 3-tuple: K = < V_E, E_R, C_I >
      - V_E: Entities | E_R: Relational Edges | C_I: Structural Invariants & Logic Rules
  
  [D] EPISODIC EXPERIENCE STATE (S_episodic)
      - Bounded key-value memory with namespaced schemas: fact, unknown, routing
      - Governed by SOS-001 write disciplines (unconditional first-exposure write - EXP-022)
  
  [E] WORKING CONTEXT STATE (S_working)
      - Fixed-slot partition overwritten unconditionally on each turn (EXP-019)
      - Slots: { current_topic, active_speaker, active_goal, focus_entity, pending_slot }
  
  [F] INTERACTION & EXECUTION HISTORY (s_hist)
      - Immutable sequential append-only log of interaction turns and search episodes
  
  [G] TRANSIENT DECISION STATE (S_decision)
      - Ephemeral search frontier, active candidate probabilities, rollback checkpoint stack
```

### Epistemic Status of State Components:
- $S_{episodic}$ & $S_{working}$: **Established & Observed Experimentally** ([EXP-001](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-001), [EXP-019](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-019), [EXP-022](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-022)).
- $\mathcal{K}$ & $\mathcal{C}_I$: **Established & Observed Experimentally** ([EXP-020](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-020), [EXP-026](file:///d:/Paartha/adaptive-computational-architecture/docs/06_experiments/Completed.md#exp-026)).
- $\mathcal{L}$ & Sandboxed Rollback: **Observed Experimentally** ([EXP-CCS-0](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/GDR-003.md)).
- $\Theta$ decomposition ($\theta_{enc}, \theta_{decide}, \theta_{gen}$): **Architectural Hypothesis** (synthesized from [JEV-001](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/JEV-001.md) and [CTX-002](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/CTX-002.md)).

---

## 3. Definition of “Inference” in Paartha

Inference is NOT autoregressive next-token sampling. In Paartha, inference is a **discrete, verified state-transition cycle**:

$$(\mathcal{S}_t, X_{t+1}) \xrightarrow{\quad \text{INFERENCE} \quad} (\mathcal{S}_{t+1}, Y_{t+1})$$

The complete inference computation comprises five formal operators:

```
  Observation X_{t+1}
          │
          ▼
   1. INGRESS & RESOLUTION:      tau_ingress: (S_working, X) -> S_working'
          │
          ▼
   2. SYSTEM 1 DECISION:         tau_decide: (S_working', L) -> < a_comm, c_target, u_conf >
          │
          ▼
   3. DELIBERATION / DEDUCTION:  tau_exec: (S_working', K, L, a_comm) -> SemanticMessage M
          │                      (Direct graph query OR SET-CR tree search with rollback)
          ▼
   4. INVARIANT VERIFICATION:    tau_verify: (M, C_I) -> { Pass, Fail }
          │
          ▼
   5. SURFACE REALIZATION:       tau_realize: (M, S_working') -> Natural Language Output Y
```

### Characterization of Operations:
- **Learned vs. Deterministic**:
  - $\tau_{ingress}$ and $\tau_{decide}$ are **learned neural operations** ($\theta_{enc}, \theta_{decide}$).
  - $\tau_{verify}$ is **purely deterministic and formal** (evaluated over logical invariants $\mathcal{C}_I$ in $S_{invariants}$).
  - $\tau_{exec}$ is **hybrid**: deterministic rule deduction (in $\mathcal{K}$) or heuristic tree search (guided by $\theta_{decide}$ over $\mathcal{L}$).
  - $\tau_{realize}$ is **learned constrained generation** ($\theta_{gen}$).
- **Continuous vs. Discrete**:
  - Continuous: Text encoding and intermediate representations in $\theta_{enc}$ and $\theta_{gen}$.
  - Discrete: Speech act classification, capability selection, graph proof-trace synthesis, and invariant audits.
- **Where Uncertainty Exists**: Exclusively inside $\tau_{decide}$ (calibrated probability distribution via RLCD) and missing-knowledge boundary checks.
- **Where Search Occurs**: Exclusively inside $\tau_{exec}$ when a goal cannot be answered by direct relational recall.

---

## 4. The Exact Architectural Role of JEv

Building on [`docs/12_cognition/JEV-001.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/JEV-001.md), we specify the precise contract for the JEv-style Calibrated Decision Substrate ($\theta_{decide}$):

```
+───────────────────────────────────────────────────────────────────────────────────────────+
|                           JEV-STYLE DECISION CONTRACT IN PAARTHA                          |
|                                                                                           |
|  1. Input:                                                                                |
|     - State Vector z_s = Enc(S_working, context)                                          |
|     - Candidate Space C = { c_1, c_2, ..., c_k } (where k <= 255)                         |
|     - Typed Query q (SpeechAct | MissingInfo | PruneBranch | ToolChoice)                 |
|                                                                                           |
|  2. Output:                                                                               |
|     - Discrete selection c* in C                                                          |
|     - Normalized posterior distribution P(c_i | z_s, q)                                   |
|     - Calibrated confidence metric gamma in [0, 1]                                        |
|                                                                                           |
|  3. Inference Mode:                                                                       |
|     - Single-pass non-autoregressive forward pass (latency: 70ms - 200ms)                 |
|     - Evaluates all parallel queries q_1, ..., q_m in one forward pass                    |
|                                                                                           |
|  4. State Mutated:                                                                        |
|     - Updates S_decision only (ephemeral deliberation frame)                              |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### Specific Roles Across the 7 Capabilities:
1. **Linguistic Ingress & Speech-Act Selection (Stage 1 Speak)**:
   - Output: `Choice` $\in$ `[DIRECT_ANSWER, EXPLAIN, CLARIFY, UNKNOWN, EXECUTE]`.
   - Output: `Noul` (Is information missing from the query?).
2. **Ambiguity & Unknown Detection (Stage 2 Understand)**:
   - Output: `Noul` (Does this assertion contradict existing invariants in $\mathcal{C}_I$?).
3. **Branch Prioritization in SET-CR (Stages 3 & 4 Brainstorm & Plan)**:
   - Output: `Choice` over candidate transformation primitives in $\mathcal{L}$, acting as the heuristic policy $\pi(a \mid s)$ in $f(n) = g(n) + h(n)$.
   - Output: `Noul` (Prune branch if $P(\text{dead}) > 0.95$).
4. **Tool & Action Selection (Stages 5 & 6 Code & Act)**:
   - Output: `Choice` over available tool/API signatures in $\mathcal{L}$.
   - Output: `Score` (Expected risk / test-failure severity).

---

## 5. The Smallest Reusable Computational Primitive: The Paartha Hexagon

To prevent building fragmented, ad-hoc architectures for each capability stage, we isolate the **single universal computational primitive** that executes across all 7 stages:

$$\mathcal{P}_{\text{universal}} = \langle \text{PERCEIVE} \longrightarrow \text{RESOLVE} \longrightarrow \text{DECIDE} \longrightarrow \text{TRANSFORM} \longrightarrow \text{VERIFY} \longrightarrow \text{UPDATE} \rangle$$

```
+───────────────────────────────────────────────────────────────────────────────────────────+
|                            THE PAARTHA HEXAGONAL PRIMITIVE                                |
|                                                                                           |
|       PERCEIVE   ──> Map external observation X into state representation z_x             |
|          │                                                                                |
|          ▼                                                                                |
|       RESOLVE    ──> Bind z_x to WorkingState slots & resolve referents                   |
|          │                                                                                |
|          ▼                                                                                |
|       DECIDE     ──> JEv-style System 1 calibrated choice over candidate actions          |
|          │                                                                                |
|          ▼                                                                                |
|      TRANSFORM   ──> Execute selected primitive p in L (Deduction, Search step, Tool)     |
|          │                                                                                |
|          ▼                                                                                |
|       VERIFY     ──> Check structural invariants C_I (EVALUATE-STRUCTURAL)                |
|          │                                                                                |
|          ▼                                                                                |
|       UPDATE     ──> Realize output Y, append to s_hist, commit persistent memory          |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### Demonstrating Invariance Across the Entire Ladder:

| Stage | PERCEIVE | RESOLVE | DECIDE | TRANSFORM | VERIFY | UPDATE |
|---|---|---|---|---|---|---|
| **1. Speak** | User question $X$ | Bind referents to $S_{working}$ | Select speech act (`Choice`) | Deduce proof trace in $\mathcal{K}$ | Verify proof trace against $\mathcal{C}_I$ | Realize text $Y$; log to $s^{hist}$ |
| **2. Understand** | User assertion $X$ | Extract entities & predicate | Select assertion schema | Construct relation edge $\mathcal{E}_R$ | Audit invariants for contradiction | Commit edge to $\mathcal{K}$ and $S_{episodic}$ |
| **3. Brainstorm** | Problem goal $G$ | Bind goal constraints | Rank candidate solution strategies | Expand hypothesis set $\{H_1..H_k\}$ | Filter strategies violating invariants | Commit candidate set to search frontier |
| **4. Plan** | Goal & strategy $H^*$ | Map state $s_0 \to s^*$ | Order subgoals via heuristic score | Sequence primitives into a DAG | Verify causal preconditions of DAG | Store plan DAG in $S_{working}$ |
| **5. Code** | Algorithm sub-step | Bind variable types & signatures | Select AST template / syntax rule | Synthesize executable code | Run compiler, lint, and unit tests | If pass: commit artifact; else: rollback |
| **6. Act** | Tool output / env state | Update world state in $S_{working}$ | Select next tool call from $\mathcal{L}$ | Execute action in sandbox | Audit return code & security guardrails | Record action in $s^{hist}$; advance state |
| **7. General Problem Solving** | Arbitrary complex goal | Dynamic task decomposition | Hierarchical action selection | Iterated SET-CR search execution | Invariant & goal satisfaction audit | Consolidate learned macro into $\mathcal{L}$ |

---

## 6. Architectural Allocation of SET-CR

In [`docs/12_cognition/GDR-003.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/GDR-003.md), SET-CR proved that pure greedy discrepancy reduction fails, while heuristic tree search with rollback succeeds (100%).

We now formally decouple what belongs in the **Core Architecture** from what belongs in the **Higher-Level Search Subsystem**:

```
+───────────────────────────────────────────────────────────────────────────────────────────+
| CORE ARCHITECTURAL ENGINE (Primitive Substrate)                                           |
|   1. Isolated Execution Sandbox: Prevents speculative actions from corrupting K or S_episodic |
|   2. Checkpoint & Rollback Mechanism: Reversible state deltas on S_working and L          |
|   3. Structural Invariant Audit: EVALUATE-STRUCTURAL enforcing hard physical/logic rules  |
+───────────────────────────────────────────────────────────────────────────────────────────+
                                             ▲
                                             │  Exposed Interface
                                             ▼
+───────────────────────────────────────────────────────────────────────────────────────────+
| HIGHER-LEVEL DELIBERATION SUBSYSTEM (SET-CR Search Algorithm)                              |
|   1. Search Policy: Heuristic scoring f(n) = g(n) + h(n) provided by JEv decision head    |
|   2. Frontier Management: Priority queue of candidate search branches                     |
|   3. Macro Compilation: Sleeper consolidation compiling repeated search paths into L      |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 7. The Role of Language: Core Computation vs. I/O Modality

A fundamental flaw of foundation models is treating natural language as the substrate of thought. Natural language is ambiguous, serial, redundant, and underspecified. 

In Paartha, **natural language is strictly an I/O modality**, never the internal reasoning substrate:

```
Human Utterance (Natural Language)
              │
              ▼  [Ingress Encoder theta_enc]
Structured Semantic Representation (Discourse Frame, Entity Nodes, Intent)
              │
              ▼  [Paartha Core Computation: K, L, JEv, SET-CR, C_I]
Verified Conceptual Proof Trace / Execution Artifact
              │
              ▼  [Surface Realizer theta_gen]
Natural Language Response (English Output)
```

### The Internal Semantic State:
The intermediate representation passed from Core Computation to Surface Realization is a **Semantic Message $M$**:
$$M = \langle \text{SpeechAct}, \text{ProofTrace}, \text{EntityBindings}, \text{Confidence} \rangle$$
For example:
$$M = \langle \text{EXPLAIN}, \ [\text{Whale} \xrightarrow{\text{is\_a}} \text{Mammal}, \ \forall x: \text{Mammal}(x) \implies \text{BreathesAir}(x)], \ \{\text{Whale}, \text{Air}\}, \ 1.0 \rangle$$
The surface realizer $\theta_{gen}$ receives $M$ and simply synthesizes fluent phrasing ("Whales breathe air because they are mammals, and all mammals breathe air"). $\theta_{gen}$ is never permitted to alter the facts in $M$.

---

## 8. What Must Be Learned vs. Deterministic

To guarantee that Paartha remains compact, verifiable, and trainable on modest compute, we strictly limit what is parameterized by neural weights:

```
+──────────────────────────+────────────────────+──────────────────────────────────────────+
| Component                | Nature             | Scale / Implementation                   |
+──────────────────────────+────────────────────+──────────────────────────────────────────+
| Ingress Encoder          | Neural (Learned)   | ~50M - 100M params (Bidirectional)      |
| JEv Decision Substrate   | Neural (Learned)   | ~10M - 50M params (RLCD calibrated heads)|
| Surface Realizer         | Neural (Learned)   | ~300M - 1B params (Conditional Decoder)  |
| Relational Graph K       | Symbolic / Formal  | ZERO weights (Explicit graph in memory)  |
| Invariant Rules C_I      | Symbolic / Formal  | ZERO weights (First-order logic rules)   |
| WorkingStateStore        | Deterministic      | ZERO weights (Typed slot records)        |
| EpisodicMemory           | Deterministic Store| ZERO weights (Content-addressable KV)    |
| SET-CR Search Sandbox    | Deterministic VM   | ZERO weights (Stack / Checkpoint engine) |
+──────────────────────────+────────────────────+──────────────────────────────────────────+
```

**Total Learned Weight Footprint for Stage 1**: **$\le 1.2$ Billion parameters** (orders of magnitude smaller than 70B+ LLMs, trainable on a single GPU).

---

## 9. Computational Graphs: Architecture A vs. Architecture B

### Architecture A: Minimum Viable Paartha for "Speak" (MVP-Speak)

```
                       USER NATURAL LANGUAGE UTTERANCE
                                      │
                                      ▼
                        INGRESS ENCODER (theta_enc)
                                      │
                                      ▼
                      CONTEXT RESOLUTION (WorkingState)
                 [Updates active topic, focus entity, speaker]
                                      │
                                      ▼
                    JEV-STYLE CALIBRATED DECISION HEAD
                 [Evaluates in parallel non-autoregressively]
                 - Q1: Speech Act (ANSWER | CLARIFY | EXPLAIN | UNKNOWN)
                 - Q2: Target Relational Query / Domain
                 - Q3: Ambiguity / Missing Slot Flag
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             [DIRECT / EXPLAIN]   [CLARIFY]         [UNKNOWN]
                    │                 │                 │
                    ▼                 ▼                 ▼
             KRS-001 Graph       Extract Missing    Log to S_episodic
             Deduction Engine    Slot Definition    Unknown Partition
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
                          SEMANTIC MESSAGE M (Proof)
                                      │
                                      ▼
                    SURFACE REALIZER DECODER (theta_gen)
                                      │
                                      ▼
                          FINAL LANGUAGE RESPONSE
```

---

### Architecture B: Generalized Paartha Architecture (Stages 1 through 7)

```
                            ENVIRONMENT / USER
                                     │
                                     ▼
                    MULTIMODAL INGRESS & PERCEPTION
                                     │
                                     ▼
                      ACTIVE WORKING STATE RESOLVER
              (WorkingStateStore: Goals, Slots, Sandboxes)
                                     │
                                     ▼
                   SYSTEM 1 CALIBRATED DECISION ENGINE
             (Speech Acts, Intent, Branch Heuristics, Pruning)
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
         [Direct Verbal Response]         [Complex Goal / Search]
                    │                                 │
                    ▼                                 ▼
             KRS-001 Graph                SYSTEM 2 SET-CR SEARCH
            Deductive Engine              - Primitive Tree Search
                    │                     - Checkpoint Rollback Stack
                    │                     - Modular Capability Library L
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                      EVALUATE-STRUCTURAL (C_I Rules)
                       [Invariant Verification Gate]
                                     │
                                     ▼
                        OUTPUT GENERATION / ACTION
               ┌─────────────────────┴─────────────────────┐
               ▼                                           ▼
       Surface Realizer                             Sandboxed Action
    (Natural Language Text)                      (Tool / Code Execution)
```

---

## 10. Formal Execution Model of Paartha

We define Paartha formally as a 7-tuple:

$$\mathcal{P} = \langle \mathcal{S}, \mathcal{X}, \mathcal{Y}, \mathcal{L}, \mathcal{K}, \Theta, \mathcal{T} \rangle$$

where:
- $\mathcal{S}$ is the state space $\mathcal{S} = S_{working} \times S_{episodic} \times s^{hist} \times S_{decision}$.
- $\mathcal{X}$ is the input space (text, observations).
- $\mathcal{Y}$ is the output space (language responses, tool commands).
- $\mathcal{L}$ is the capability library.
- $\mathcal{K} = \langle \mathcal{V}_E, \mathcal{E}_R, \mathcal{C}_I \rangle$ is the relational knowledge graph and invariants.
- $\Theta = \{\theta_{enc}, \theta_{decide}, \theta_{gen}\}$ is the learned parameter vector.
- $\mathcal{T}$ is the set of transition operators.

### Execution Cycle:
For each input $X \in \mathcal{X}$:
1. **Ingress**: $\mathbf{z}_x = f_{\theta_{enc}}(X)$.
2. **Context Resolution**: $s_{work}' = \text{update\_slots}(s_{work}, \mathbf{z}_x)$.
3. **Decision Step**:
   $$\mathbf{d} = \text{softmax}(g_{\theta_{decide}}(s_{work}', \mathbf{z}_x)) \longrightarrow \langle a_{comm}, c^*, \gamma \rangle$$
   where $\gamma \in [0, 1]$ is the calibrated confidence.
4. **Execution Step**:
   $$M = \begin{cases} 
   \text{Deduce}(\mathcal{K}, c^*), & \text{if } a_{comm} \in \{\text{ANSWER}, \text{EXPLAIN}\} \\ 
   \text{QuerySlot}(s_{work}'), & \text{if } a_{comm} = \text{CLARIFY} \\ 
   \text{UnknownToken}, & \text{if } a_{comm} = \text{UNKNOWN} \\ 
   \text{SET-CR-Search}(s_{work}', \mathcal{L}, \mathcal{C}_I), & \text{if } a_{comm} = \text{EXECUTE} 
   \end{cases}$$
5. **Invariant Check**:
   $$\text{Assert } \mathcal{C}_I(M) = \top. \quad \text{If } \bot \implies \text{Rollback and fallback to CLARIFY}.$$
6. **Realization**:
   $$Y = h_{\theta_{gen}}(M, s_{work}').$$
7. **Trace Logging**:
   $$s^{hist} \leftarrow s^{hist} \cup \langle X, s_{work}', \mathbf{d}, M, Y \rangle.$$

---

## 11. The “Weights” Equivalent in Paartha

Paartha explicitly rejects a single, monolithic 100B parameter space where all knowledge, logic, and tools are blended.

Instead, Paartha establishes **Three Parameter Tiers**:

```
+───────────────────────────────────────────────────────────────────────────────────────────+
| 1. SHARED CORE BACKBONE PARAMETERS (Theta_core: ~1.2B Parameters)                         |
|    - Language Ingress Encoder (theta_enc)                                                 |
|    - System 1 Calibrated Decision Heads (theta_decide)                                   |
|    - Surface Realization Decoder (theta_gen)                                              |
|    * Training Cadence: Slow, curated multi-task pretraining & RLCD calibration.           |
+───────────────────────────────────────────────────────────────────────────────────────────+
                                             ▲
                                             │ Interacts With
                                             ▼
+───────────────────────────────────────────────────────────────────────────────────────────+
| 2. MODULAR CAPABILITY PARAMETERS (L: Isolated Primitive Weights)                           |
|    - Independent parameter vectors per capability (e.g. 326-param classifier from EXP-020)|
|    - LoRA-style adapters or AST rewrite operators                                         |
|    * Training Cadence: Fast, local optimization without modifying Theta_core.             |
+───────────────────────────────────────────────────────────────────────────────────────────+
                                             ▲
                                             │ Bound By
                                             ▼
+───────────────────────────────────────────────────────────────────────────────────────────+
| 3. STRUCTURAL INVARIANTS & KNOWLEDGE GRAPH (Zero Parameters)                              |
|    - Explicit relational graph edges E_R                                                  |
|    - First-order logic rules C_I                                                          |
|    * Modification Cadence: Single-exposure unconditional assertion write (EXP-022).       |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 12. Architecture Falsification: Red-Teaming the Candidate Architecture

We subject this candidate architecture to adversarial red-teaming:

1. **Can it actually Speak?**
   - *Verdict*: **YES**. Given an input, it resolves context, determines the speech act via $\theta_{decide}$, retrieves the verified proof from $\mathcal{K}$, and verbalizes it via $\theta_{gen}$.
2. **Can it retain conversational state?**
   - *Verdict*: **YES**. Validated by EXP-019 (`WorkingStateStore` achieves $1.000$ recall across extended turns via unconditional overwrite).
3. **Can it say “I don't know”?**
   - *Verdict*: **YES**. Validated by EXP-009 and EXP-026 Stage 5. When confidence $\gamma < \tau$ or a required relational edge is missing in $\mathcal{K}$, it deterministically emits `UNKNOWN` or triggers `CLARIFICATION_REQUIRED`.
4. **Can it learn a new capability?**
   - *Verdict*: **YES**. A new primitive is added directly to $\mathcal{L}$ without retraining $\Theta_{core}$ (validated in EXP-004 and EXP-021).
5. **Can it perform search?**
   - *Verdict*: **YES**. SET-CR tree search runs over sandboxed checkpoints (validated in EXP-CCS-0).
6. **Can it verify its own result?**
   - *Verdict*: **YES**. Evaluated formally against $\mathcal{C}_I$ via `EVALUATE-STRUCTURAL` (validated in EXP-020 and EXP-026).
7. **Where does the architecture risk collapsing back into “just an LLM”?**
   - *Failure Mode*: If the surface realization decoder $\theta_{gen}$ is allowed to generate unconditioned text, it will hallucinate.
   - *Mitigation*: $\theta_{gen}$ must receive the fully instantiated semantic proof trace $M$ as a hard conditioning constraint; decoding without proof tokens is structurally blocked.
8. **Where does it risk becoming unnecessarily symbolic?**
   - *Failure Mode*: Attempting to hand-code every English grammar rule or real-world relation symbolically.
   - *Mitigation*: The linguistic front-end ($\theta_{enc}$) and back-end ($\theta_{gen}$) are statistical neural models. Only domain invariants and relational knowledge reside in $\mathcal{K}$.

---

## 13. The Next Experiment: EXP-SPEAK-0

To falsify the central architectural hypothesis of this document before writing full runtime code:

### Core Hypothesis:
> **Decoupling System 1 speech-act decision ($\theta_{decide}$) and factual proof deduction ($\mathcal{K}$) from surface realization ($\theta_{gen}$) eliminates factual hallucinations and false clarification loops while reducing latency by $\ge 3\times$ compared to a monolithic autoregressive language model on multi-turn dialogue with missing information.**

### Experimental Design (EXP-SPEAK-0):
- **Task**: Multi-Turn Grounded Dialogue Benchmark with Deliberate Knowledge Gaps (100 dialogue sessions across 5 random seeds).
- **Conditions**:
  1. *Condition A (Monolithic LLM Baseline)*: 8B autoregressive instruction-tuned model prompted to manage dialogue, detect missing info, and answer.
  2. *Condition B (Paartha Architecture A)*: Compact encoder + RLCD-calibrated decision head + KRS-001 knowledge graph + conditioned surface realizer.
- **Metrics**:
  - **Factual Hallucination Rate**: Percentage of answers containing fabricated facts on missing-knowledge questions (Target: $0.0\%$ in Paartha).
  - **Clarification Precision**: Correctly triggering `CLARIFY` only when user query is underspecified.
  - **Inference Latency**: Total milliseconds per conversational turn.
  - **Calibration Error (ECE)**: Calibration of reported confidence vs. true correctness.
- **Falsification Criteria**:
  - If Condition B exhibits $\ge 5\%$ factual hallucinations, the semantic conditioning boundary is falsified.
  - If Condition B's speech-act decision accuracy falls below Condition A, the decoupled System 1 decision hypothesis is rejected.

---

## 14. Deliverable Summary: The Minimum Viable Paartha System

Answering the directive’s final question precisely:

> **If we had to build Paartha tomorrow, with Stage 1 = Speak, what are the minimum computational components we would build, what information flows between them, what state does each maintain, what is learned versus computed, and which of those components are fundamental enough to survive all the way to Stage 7?**

```
+───────────────────────────────────────────────────────────────────────────────────────────+
| MINIMUM COMPONENTS TO BUILD TOMORROW:                                                     |
|                                                                                           |
|  1. Linguistic Ingress Encoder (theta_enc):                                               |
|     - Learned (~100M params). Maps utterance into embedding vector z_x.                   |
|                                                                                           |
|  2. Working State Store (WorkingStateStore):                                              |
|     - Computed (Zero weights). Overwritten unconditionally each turn (EXP-019).           |
|                                                                                           |
|  3. Calibrated System 1 Decision Head (theta_decide):                                     |
|     - Learned (~20M params). Non-autoregressively outputs speech act & ambiguity flags.   |
|                                                                                           |
|  4. Relational Knowledge Graph Engine (runtime/aca0/krs.py):                              |
|     - Computed (Zero weights). Executes deductive proofs over invariants (EXP-026).       |
|                                                                                           |
|  5. Grounded Surface Realizer (theta_gen):                                                |
|     - Learned (~500M params). Renders proof trace M into fluent English.                  |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### Which Components Survive All the Way to Stage 7?
- **`WorkingStateStore`**: Survives to Stage 7 as the local execution context and sandbox stack.
- **Calibrated Decision Head ($\theta_{decide}$)**: Survives to Stage 7 as the heuristic search policy $\pi(a \mid s)$ and tool dispatcher.
- **Relational Graph & Invariants ($\mathcal{K}, \mathcal{C}_I$)**: Survives to Stage 7 as the non-negotiable formal verification gate (`EVALUATE-STRUCTURAL`).
- **Surface Realizer ($\theta_{gen}$)**: Survives as the explanatory communication interface.
- **SET-CR Engine**: Plugs directly between $\theta_{decide}$ and $\mathcal{C}_I$ to enable multi-step planning, coding, and agentic tool execution without altering the base architecture!
