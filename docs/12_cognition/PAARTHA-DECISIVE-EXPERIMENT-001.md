# PAARTHA-DECISIVE-EXPERIMENT-001: Controlled Benchmark for Testing Competence Acquisition Beyond Frontier LLM + Tools

**Author:** Antigravity AI & Paartha Research  
**Date:** September 2026  
**Status:** Pre-Registration Experiment Specification & Protocol  
**Target Directory:** `experiments/decisive_paartha/`  
**Execution Script:** `experiments/decisive_paartha/run_experiment.py`  
**Results Report:** `docs/12_cognition/PAARTHA-DECISIVE-RESULTS-001.md`  

---

## 1. Scientific Objective & Problem Formulation

The overarching goal of the Paartha research project is to investigate whether intelligence can acquire, retain, and reuse generalizable competence through structured representation, explicit executable capabilities, proposal-guided search, and verified abstraction discovery, without requiring end-to-end backpropagation across a monolithic neural network.

While previous experiments ([EXP-032](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-COMPETENCE-001.md) through [EXP-036](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-COMM-001.md)) showed positive indications, the adversarial audit in [EXP-037](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ADVERSARIAL-001.md) demonstrated that benchmark co-design and procedural leakage can easily mask architectural stagnation. Furthermore, a foundational critique remains unaddressed:

> **The Fundamental Critique:** The observed competence of Paartha may simply be an artifact of sophisticated symbolic scaffolding surrounding a frontier Large Language Model (LLM), rather than a computational mechanism that produces genuinely emergent, generalizable capability beyond what the same frontier LLM can achieve when given the exact same tools and contracts.

### The Central Question
> **Does the Paartha computational architecture allow a system to acquire and reuse generalizable competence through experience and abstraction discovery, beyond what the same frontier LLM can achieve alone or with the same tools/contracts?**

---

## 2. Hypotheses & Null Hypotheses

### Primary Experimental Hypothesis ($H_1$)
The Paartha computational architecture (incorporating typed capability contracts, joint CSP parameter resolution, sandboxed invariant verification, and autonomous abstraction discovery via anti-unification and MDL selection) produces a statistically significant improvement in task completion rate, verification reliability, and cross-domain transfer on unseen tasks compared to the identical frontier LLM operating with identical primitive tools.
$$\text{Performance}(D) > \text{Performance}(B_2) > \text{Performance}(B_1) > \text{Performance}(A)$$

### The Null Hypothesis ($H_0$)
The Paartha computational architecture provides no statistically significant capability improvement over the frontier LLM equipped with the same tools and discovered abstractions. Any apparent performance gain in Paartha is entirely attributable to the information content of the discovered programs or prompt framing, rather than the Paartha runtime mechanisms.
$$\text{Performance}(D) \approx \text{Performance}(B_2)$$

### Falsification Conditions
The Paartha core hypothesis will be considered **FALSIFIED** if any of the following empirical criteria are met:
1. **Tool Equivalence Failure ($B_1 \approx C$):** System C (Paartha without discovered abstractions) achieves no higher accuracy or safety than System B1 (LLM + Tools) on held-out tasks.
2. **Abstraction Explanation Failure ($B_2 \approx D$):** When discovered abstractions are provided to the baseline LLM as tools ($B_2$), System D exhibits no performance or reliability advantage over $B_2$. (Indicates Paartha is merely an offline macro discovery script, not an active cognitive runtime).
3. **Cross-Domain Transfer Collapse ($D_{Domain B} \le B_{1, Domain B}$):** Abstractions discovered in Domain A fail to transfer to independently authored Domain B, collapsing to baseline levels.
4. **Leakage Dependence:** Any performance advantage disappears once hardcoded keywords, entity lists, or prompt mappings are stripped.

---

## 3. The Four Primary Experimental Systems & Controls

All systems utilize the **exact same frontier LLM** via a unified API client wrapper (configurable via `SARVAM_API_KEY` and `SARVAM_MODEL`, with standard fallback support).

```
                                SYSTEM TAXONOMY
┌─────────────────────────────────────────────────────────────────────────────┐
│ SYSTEM A: Frontier LLM Alone                                                │
│ • Input: Task description + schema + input data.                            │
│ • Substrate: Frontier LLM zero-shot / few-shot reasoning.                   │
│ • Output: Direct textual answer / calculated state.                         │
│ • No external tools, no contracts, no verification, no Paartha runtime.     │
├─────────────────────────────────────────────────────────────────────────────┤
│ SYSTEM B1: Frontier LLM + Primitive Tools (Strong Agent Baseline)           │
│ • Input: Task description + schema + input data.                            │
│ • Substrate: Frontier LLM + standard iterative ReAct tool-use loop.         │
│ • Tools: Exact same 12 primitive tools and contracts as Paartha.            │
│ • No Paartha-specific search (SET-CR), no JEv decision routing, no memory.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ SYSTEM B2: Frontier LLM + Tools + Discovered Abstractions (Critical Control)│
│ • Identical to System B1, but equipped with both the primitive tools AND   │
│   the exact parameterized abstractions discovered by System D.              │
│ • Critical Test: Tests whether abstractions alone explain Paartha's gains.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ SYSTEM C: Paartha Runtime Without Discovered Abstractions                   │
│ • Input: Task description + schema + input data.                            │
│ • Architecture: Goal extraction → Epistemic Decision → Capability Selection │
│   → RESOLVE (CSP binding) → Sandboxed Verification → State Delta.           │
│ • Library: 12 primitive capabilities only ($\mathcal{L}_0$).               │
├─────────────────────────────────────────────────────────────────────────────┤
│ SYSTEM D: Paartha + Experience + Abstraction Discovery                      │
│ • Initial state identical to System C.                                      │
│ • Experience Phase: Solves training tasks, logs verified execution traces.  │
│ • Consolidation Phase: Motif Miner → Plotkin Anti-Unifier → MDL Engine      │
│   → Contract Synthesis & Test → Capability Registration into $\mathcal{L}$. │
│ • Freeze Phase: All weights, contracts, and libraries frozen.               │
│ • Evaluation Phase: Evaluated on unseen Level 2 and Level 3 transfer tasks. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. The 12 Primitive Tools & Typed Contracts

Both System B and Paartha (Systems C & D) have access to the exact same 12 deterministic primitive tools:

```
                            PRIMITIVE TOOL REGISTRY
┌──────┬──────────────────────┬────────────────────────┬──────────────────────────────────┐
│ #    │ Tool Name            │ Abstract Signature     │ Semantic Description             │
├──────┼──────────────────────┼────────────────────────┼──────────────────────────────────┤
│ 1    │ FilterByThreshold    │ (col, val, op) → S'    │ Rows matching comparison op      │
│ 2    │ FilterEquals         │ (col, val) → S'        │ Rows where col == val            │
│ 3    │ SortByColumn         │ (col, ascending) → S'  │ Deterministic row sort           │
│ 4    │ TopK                 │ (k) → S'               │ First k rows of state            │
│ 5    │ TailK                │ (k) → S'               │ Last k rows of state             │
│ 6    │ GroupBy              │ (group_col) → S_grp    │ Partition state into groups      │
│ 7    │ AggregateSum         │ (num_col, out) → S'    │ Sum reduction over group/table   │
│ 8    │ AggregateMean        │ (num_col, out) → S'    │ Mean reduction over group/table  │
│ 9    │ ProjectColumns       │ (cols) → S'            │ Column projection / slice        │
│ 10   │ ScaleColumn          │ (col, factor) → S'     │ Multiply column by scalar factor │
│ 11   │ Deduplicate          │ (key_col) → S'         │ Distinct rows by key column      │
│ 12   │ DropNull             │ (col) → S'             │ Drop rows where col is None      │
└──────┴──────────────────────┴────────────────────────┴──────────────────────────────────┘
```

Each tool exposes an explicit typed contract containing:
* `name`: Unique identifier.
* `description`: Natural language description of functionality.
* `input_schema`: Typed parameters (column names, numeric values, operators, lists).
* `output_schema`: Return data shape (`FLAT` vs `GROUPED`).
* `preconditions`: Symbolic checks (e.g. `col in state.columns`, `k > 0`).
* `effects`: State transformation specification.
* `invariants`: Preserved properties (e.g. non-negative row count).

---

## 5. Task Design & Three-Level Benchmark Methodology

To eliminate benchmark co-design, tasks are structured across three hierarchical levels:

### Level 1: Familiar Composition (Sanity & Calibration)
* **Domain:** Logistics & Warehouse Operations (Domain A).
* **Characteristics:** Simple 2-3 step sequences directly composing primitive operations (e.g. `FilterEquals` followed by `SortByColumn`).
* **Purpose:** Verify that all systems, API integrations, tool runners, and evaluators execute without syntax errors.

### Level 2: Held-Out Tasks (Unfamiliar Composition)
* **Domain:** Logistics & Warehouse Operations (Domain A).
* **Characteristics:** Complex 4-6 step compositions requiring multi-branch reasoning, nested group aggregations, and unfamiliar parameter relationships that were never present during initial tool implementation.
* **Purpose:** Measure whether Paartha's runtime (RESOLVE, verification, capability selection) provides advantages on unseen problems in the same domain.

### Level 3: Independently Authored Cross-Domain Transfer (The Decisive Test)
* **Experience Domain (Domain A):** Supply Chain Logistics & Fleet Warehousing (Entities: shipments, routes, bin locations, carrying capacity, fuel consumption).
* **Transfer Domain (Domain B):** Molecular Spectroscopy & Sensor Telemetry (Entities: photodetectors, optical absorbance, wavelengths, nanometers, cryogenic temperature, quantum noise).
* **Leakage Safeguards:**
  * Zero shared column names.
  * Zero shared entity names.
  * Zero shared domain vocabulary.
  * Zero shared prompts or task templates.
* **Purpose:** Test whether abstractions discovered in Domain A (e.g., `RankedHighPerformers` or `RankedGroupTotals`) can transfer to Domain B purely through structural isomorphism, or whether they collapse.

---

## 6. Strict Benchmark Leakage Controls & Pre-Execution Audit

To prevent recurrence of the flaws exposed in EXP-037, the harness incorporates an automated static analysis scanner (`leakage_audit.py`) that executes before any benchmark run:

1. **No Keyword Ingress:** The system must not inspect fixed keywords (e.g. searching for `"wavelength"` or `"shipment"` to route actions).
2. **No Hardcoded Entity Lists:** System code must not contain lists of valid values (e.g. `['HQ', 'Branch']` or `['Sensor_A', 'Sensor_B']`).
3. **No Exact Prompt Matching:** Routing cannot match against benchmark scenario strings.
4. **No Pre-Wired Capability Mappings:** Hand-written dictionaries mapping `task_id -> capability` are strictly prohibited.
5. **No Solution Peek:** Evaluator test assertions are isolated in separate files and cannot be imported by the systems.

---

## 7. Metrics & Measurement Framework

### 1. Capability Metrics
* **Task Success Rate ($SR$):** Percentage of tasks where the final output state matches the ground truth oracle exactly.
* **Partial Correctness Score ($PC$):** F1-score over returned records/columns when exact match fails.
* **Held-Out Generalization ($HOG$):** Success rate on Level 2 held-out tasks.
* **Cross-Domain Transfer Ratio ($CDTR$):** $\frac{SR_{Level 3}(D)}{SR_{Level 3}(B_1)}$.

### 2. Reliability Metrics
* **Crash Rate ($CR$):** Percentage of tasks terminating in uncaught runtime exceptions.
* **Invalid Tool Call Rate ($ITCR$):** Tool calls rejected by type check or precondition failure.
* **Safety & Invariant Violations ($SV$):** Executions violating contract pre/post conditions.
* **Self-Recovery Rate ($SRR$):** Percentage of initially failed tool calls recovered on retry.

### 3. Efficiency Metrics
* **Tool Invocation Count:** Total primitive/composite calls executed per task.
* **Search Node Expansions:** Number of candidate capability paths explored.
* **Execution Latency:** Wall-clock runtime in milliseconds.
* **API Calls & Tokens:** External model invocations required per task.

### 4. Learning & Abstraction Metrics (System D)
* **Abstractions Discovered ($N_{disc}$):** Total candidate motifs identified.
* **MDL Acceptance Ratio ($AR$):** $\frac{N_{accepted}}{N_{disc}}$.
* **Compression Gain ($\Delta \text{MDL}$):** Net description length bits saved across the corpus.
* **Abstraction Reuse Frequency ($RF$):** Percentage of held-out tasks where discovered abstractions were invoked.

---

## 8. Pre-Defined Failure Attribution Taxonomy

To ensure objective failure analysis without retrospective storytelling, every failure is deterministically categorized into one of 12 mutually exclusive bottlenecks:

```
                          FAILURE TAXONOMY TABLE
┌────┬──────────────────────────┬──────────────────────────────────────────────────────┐
│ #  │ Category Code            │ Precise Definition                                   │
├────┼──────────────────────────┼──────────────────────────────────────────────────────┤
│ 1  │ REPRESENTATION           │ State cannot express input/output data relations     │
│ 2  │ UNDERSTANDING            │ Goal extractor misidentifies intent or modality      │
│ 3  │ CAPABILITY_SELECTION     │ System fails to retrieve relevant tool/contract      │
│ 4  │ PARAMETER_BINDING        │ RESOLVE / agent generates illegal or ungrounded args │
│ 5  │ EXECUTION                │ Tool fails internal computation on valid parameters  │
│ 6  │ VERIFICATION             │ Contract invariant checker falsely accepts/rejects   │
│ 7  │ SEARCH                   │ Plan search exceeds branch budget or hits local min  │
│ 8  │ ABSTRACTION              │ Anti-unification or MDL produces malformed macro     │
│ 9  │ MEMORY                   │ Multi-step state context lost across iterations      │
│ 10 │ GENERATION               │ Surface answer generation hallucinates or corrupts   │
│ 11 │ MODEL_LIMITATION         │ LLM context truncation or reasoning breakdown       │
│ 12 │ TOOL_LIMITATION          │ Required primitive operation does not exist in reg   │
└────┴──────────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 9. Experimental Phases

```text
PHASE 0: Calibration & Leakage Audit
  ├── Run automated static leakage audit
  ├── Verify Sarvam API / provider connectivity and fallback runner
  └── Run single calibration task across Systems A, B1, C, D

PHASE 1: Baseline Evaluation (Held-Out Level 2)
  ├── Run System A (Frontier LLM Alone)
  ├── Run System B1 (Frontier LLM + Tools)
  └── Run System C (Paartha Runtime without Abstractions)

PHASE 2: Experience & Abstraction Discovery
  ├── Run System D through Domain A Experience Tasks
  ├── Log all verified execution traces
  ├── Execute MotifMiner (frequent subgraphs, support ≥ 2)
  ├── Execute Plotkin Anti-Unifier (lift constants to $params)
  ├── Execute MDL Compression Engine (reject if ΔMDL ≤ 0)
  ├── Synthesize typed contracts & execute verification probes
  └── Register accepted abstractions into Library L_D

PHASE 3: System Freeze
  ├── Freeze LLM parameters (ΔΘ = 0)
  ├── Freeze Capability Library L_D
  └── Lock all routing calibrations

PHASE 4: Held-Out Evaluation (Level 2)
  └── Evaluate A, B1, C, and D on held-out tasks

PHASE 5: Abstraction Control Evaluation
  ├── Construct System B2 (LLM + Tools + Discovered Abstractions)
  └── Compare B1 vs B2 vs D

PHASE 6: Cross-Domain Transfer Evaluation (Level 3)
  ├── Load independently authored Domain B (Spectroscopy)
  ├── Deploy B1, B2, C, and D without retraining or modification
  └── Measure cross-domain transfer ratio and abstraction reuse
```

---

## 10. Statistical Methodology & Rigor

1. **Multiple Trials:** Each task is evaluated over $N = 3$ independent runs with varied random seeds for stochastic LLM generation.
2. **Confidence Intervals:** 95% Clopper-Pearson binomial confidence intervals reported for task success rates.
3. **Hypothesis Testing:** Two-sided McNemar's test for paired categorical outcomes between System D and System B2.
4. **Blinded Evaluation:** Scoring oracles evaluate the final state representations independently from the system logs.

---

## 11. Expected Outcomes & Scientific Interpretations

```
                          OUTCOME DECISION MATRIX
┌──────────────────────┬───────────────────────────────────────────────────────────────┐
│ Observed Outcome     │ Scientific Interpretation                                     │
├──────────────────────┼───────────────────────────────────────────────────────────────┤
│ Case 1:              │ STRONG POSITIVE: Paartha provides genuine computational       │
│ D > B2 > B1 > A      │ advantage. Abstractions help, and Paartha's runtime          │
│                      │ (RESOLVE + verification) uses them more effectively than LLM. │
├──────────────────────┼───────────────────────────────────────────────────────────────┤
│ Case 2:              │ REFRAMING RESULT: Paartha is an Abstraction Discovery Engine. │
│ D ≈ B2 > B1 > A      │ The runtime adds little value during execution, but the       │
│                      │ offline mining/MDL process creates genuinely valuable tools.  │
├──────────────────────┼───────────────────────────────────────────────────────────────┤
│ Case 3:              │ RUNTIME-ONLY RESULT: Abstractions do not transfer, but        │
│ D ≈ C > B2 ≈ B1      │ Paartha's verification/CSP runtime prevents agent errors.     │
├──────────────────────┼───────────────────────────────────────────────────────────────┤
│ Case 4:              │ STRONG NEGATIVE (FALSIFICATION): Neither the runtime nor the  │
│ B1 ≈ B2 ≈ C ≈ D      │ discovered abstractions provide advantage over standard tool  │
│                      │ use with a frontier model. Paartha hypothesis is dead.        │
└──────────────────────┴───────────────────────────────────────────────────────────────┘
```

---

## 12. Limitations & Scope Constraints

1. **DSL Expressivity:** The experiment evaluates relational-functional data processing. While representative of symbolic transformations, it does not evaluate continuous robotics or visual perception.
2. **Fixed Primitive Vocabulary:** Primitive capabilities are provided; the experiment tests abstraction discovery *over* primitives, not primitive invention from raw machine code.
3. **Model Dependence:** Results reflect the reasoning capacity of the chosen frontier model family (Sarvam / frontier LLM).
