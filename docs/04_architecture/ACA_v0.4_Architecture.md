**Status: Active — First Concrete Architecture (v0.4)**

# ACA v0.4: The Function-Substrate Architecture

**Design principle:** every component below is derived from the four functions (EVALUATE, SELECT, UPDATE, COMPOSE) and the state substrates identified in `docs/08_requirements/ARS-001.md` — not from Transformers, MoE, RNNs, memory networks, or cognitive architectures. Those are used only as **reference implementations**: places to borrow a specific mechanism once a function's requirement is already established, never as templates whose overall shape gets reproduced. Every decision below states which function(s) it realizes, what state it operates on, which ARS-001 requirement(s) it satisfies, and what evidence (experimental or literature) supports it, using ARS-001's four-tier scale (Validated by ACA experiments / Supported by external literature / Reasoned hypothesis / Speculative). Where a tempting component has no such trace, it is named and explicitly excluded (Section 5) rather than silently omitted.

---

## 1. State Substrates

### 1.1 S_episodic

A finite-capacity (`C`), content-addressable key-value store: `insert(key, value)`, `evict(criterion)`, `query(key) → nearest matches`.

*Traces to:* ME-01. *Evidence:* **Validated by ACA experiments** — EXP-001 built and tested exactly this, achieving ~2x the tail-fact recall of naive caching at equal capacity via competence-gated write/eviction.

**Design decision — one substrate, multiple content kinds, not three substrates.** ARS-001 identified routing decisions (which COMPOSE family handles which input class) and self-model/competence summaries (aggregate EVALUATE scores per domain) as necessary state, alongside episodic facts. Rather than introducing two more substrate types, this architecture stores all three as different *content schemas* within the same S_episodic mechanism:

| Content kind | Key | Value | Write trigger | Evict trigger |
|---|---|---|---|---|
| Fact/correction | input representation | correct output | EVALUATE finds current S_semantic prediction wrong (EXP-001, Validated) | EVALUATE finds S_semantic now predicts it correctly (EXP-001, Validated) |
| Routing decision | input-class signature | chosen COMPOSE family ID | EVALUATE (held-out performance) prefers one family over the currently-assumed default (Reasoned hypothesis — extends EXP-003's validated *selection* logic to this *storage* location, not itself tested) | EVALUATE shows the routing choice no longer holds under new evidence (Reasoned hypothesis) |
| Self-model entry | domain/skill identifier | aggregated EVALUATE score over recent probes | Periodic, driven by DP-03's probe cycle (Speculative) | Superseded by a newer aggregate (Speculative) |

This is a deliberate unification, not an assumption: all three content kinds follow the identical write-on-high-discrepancy / evict-on-mastery dynamic that EXP-001 validated for facts specifically. Extending that *mechanism* to routing and self-model *content* is a genuine, flagged extrapolation — **Reasoned hypothesis**, not validated — and is named as a concrete next experiment (EXP-011, Section 7).

### 1.2 S_semantic

Slowly-updating trainable parameters, hosting (a) a general associative/pattern-completion backbone and (b) the parameters of each COMPOSE module in the library (Section 2.1).

*Traces to:* ME-02. *Evidence:* **Supported by external literature** — this is standard deep learning practice; included for completeness of its required pairing with S_episodic (the pairing itself, not this substrate in isolation, is what CLS theory and EXP-001 jointly motivate).

### 1.3 Explicitly not a separate substrate

Routing state and self-model state were considered as candidates for their own dedicated storage mechanisms (as EXP-003 in fact used — a bespoke fit/selection-split apparatus, separate from EXP-001's memory). They are **not** given separate substrates here, because nothing in ARS-001 identifies a functional reason they need different write/read dynamics than episodic facts already have. If EXP-011 (Section 7) finds that reusing S_episodic for routing degrades EXP-003's validated selection accuracy, this decision should be reversed, not defended.

---

## 2. The Four Functions, Concretely Realized

### 2.1 COMPOSE

**Concrete design:** a typed library of parametric transform modules, `compose_i: (Representation, Params_i) → Representation`, where `Params_i ⊂ S_semantic`. Each module declares its structural constraint as explicit, inspectable metadata (e.g. "rotation/reflection-constrained," "permutation-equivariant," "unconstrained-generic," "discrete rule-execution") — not left implicit in its weights.

*Traces to:* RC-01. *Evidence:* **Validated by ACA experiments** — EXP-002 directly falsified a single generic/unconstrained module (0% held-out accuracy across three attempts) and validated a module constrained to the true symmetry family (100% held-out accuracy, exact parameter recovery).

**Reference implementations drawn from, and what's explicitly rejected from each:**
- *Attention (Transformers)* — borrowed as one library member: a flexible, content-based, relatively unconstrained transform, useful where a domain's structure genuinely doesn't warrant a tighter constraint. **Rejected:** using attention as the *sole* or *default* composition mechanism for all domains — this is precisely what EXP-002 falsified.
- *Equivariant/symmetry-constrained layers (Geometric Deep Learning)* — borrowed as the reference class for structure-matched modules; EXP-002's validated rotation/reflection module is a member of this class. **Rejected:** nothing — this reference is adopted directly, as evidence-backed.
- *Discrete rule execution (cognitive architectures — Soar, ACT-R production rules)* — borrowed as the reference for a module type needed when a domain requires exact, discrete computation rather than any continuous transform (e.g. arithmetic beyond a single group operation, program execution). **Rejected:** the surrounding cognitive-architecture apparatus (fixed pipeline stages, working-memory-as-a-separate-named-system) — only the rule-execution mechanism itself is borrowed, not the architecture it came from.

### 2.2 EVALUATE

**Concrete design, two realizations with different evidence status:**

**(a) Supervised/labeled-target EVALUATE** — `evaluate(output, known_target) → discrepancy_score`. *Traces to:* ME-03's write-gating half, RC-02's family-selection signal. *Evidence:* **Validated by ACA experiments** — this is exactly EXP-001's surprise-threshold and EXP-002/003's held-out accuracy computation.

**(b) Unsupervised/self-consistency EVALUATE** — required because SR-01 and DP-03 both need an evaluation signal in contexts with no ground truth (open-ended deployment, self-generated probes). Candidate designs: ensemble disagreement across multiple COMPOSE pathways processing the same input; a learned calibration head trained to predict the system's own error rate; cross-consistency between a module's forward and (if invertible) reverse computation. *Traces to:* SR-01 (the general form), DP-03. *Evidence:* **Reasoned hypothesis, supported by external literature** (calibration and uncertainty-estimation research broadly) — **not validated by any ACA experiment.** This is included because SR-01/DP-03 clearly require some realization of it (they pass the "traceable to a requirement" bar) and external literature supports its plausibility, but it must not be mistaken for something ACA has actually tested. EXP-009 (Section 7) is the concrete next step to close this gap before relying on it in any real deployment decision.

**Reference implementations:** the broader calibration/uncertainty-estimation literature (ensembling, temperature scaling, learned confidence heads) — no single existing architecture is being reproduced here; these are cited as evidence the general approach is plausible, not as a template.

### 2.3 SELECT

**Concrete design:** `select(scored_candidates) → choice`, where scores must come from EVALUATE run against a held-out/generalization-oriented probe, never from raw training loss (this specific constraint is itself evidence-backed, not a stylistic preference — see below). Hard argmax selection is the validated default; soft/weighted-mixture selection is a plausible variant with no ACA test behind it.

*Traces to:* RC-02 (family choice: **Validated by ACA experiments**, EXP-003; compute-amount choice: **Reasoned hypothesis**, untested), SR-02 (**Reasoned hypothesis**), ME-03's write/evict decision (**Validated**, EXP-001), DP-03 (**Speculative**, a degenerate two-option case of this function).

**Reference implementations drawn from, and what's explicitly rejected:**
- *Mixture-of-Experts gating mechanics* — the mechanical shape (a gate producing a distribution or hard choice over a set of modules) is borrowed. **Explicitly rejected: the typical MoE training objective**, which optimizes the gate via training loss. EXP-003 directly falsified loss-driven and parsimony-regularized gating (both measured at exactly 0% held-out accuracy) and validated a held-out-performance-driven alternative. This is the clearest case in this document of taking a mechanism from an existing architecture while rejecting the objective that architecture normally pairs it with, because ACA has direct evidence that pairing fails.

### 2.4 UPDATE

**Concrete design, two regimes:**

**(a) Episodic write/eviction** — `update(S_episodic, new_info, gate) → S_episodic'`, where `gate` comes from EVALUATE (2.2a). This is exactly EXP-001's mechanism, applied uniformly across all three content schemas in Section 1.1 (facts, routing, self-model). *Traces to:* ME-01, ME-03. *Evidence:* **Validated by ACA experiments** for the fact-content schema; **Reasoned hypothesis** for the routing and self-model schemas (see Section 1.1's flagged extrapolation).

**(b) Semantic consolidation** — periodic, not per-input: sample entries from S_episodic (weighted toward those with low current EVALUATE-discrepancy, i.e. "mastered," or those reinforced many times) and feed them into S_semantic's ordinary gradient-based training as additional data (replay), then evict consolidated entries. *Traces to:* ME-03's consolidation half, LN-02. *Evidence:* **Reasoned hypothesis** — EXP-001 only validated *eviction* (freeing a slot once the backbone independently, passively learns a fact); it never tested *actively transferring* episodic content into semantic weights via replay. This is a real, named gap, not a validated mechanism — flagged explicitly, with EXP-010 (Section 7) as the concrete test.

**LN-02 (stability-plasticity), realized as a constraint on 2.4b, not a separate function:** consolidation should never directly overwrite S_semantic parameters from a single episodic entry; it should only ever contribute one sample among many in an ordinary training batch, so no single correction can destabilize previously-consolidated competence. This is a design constraint on how (b) is implemented, not new machinery — consistent with ARS-001's own finding that LN-02 is a property of UPDATE, not a fifth function.

**RC-03 (sequential state-carrying), realized as a specific *usage pattern* of 2.4a, not new machinery:** a multi-step composition chain carries intermediate results by writing them to S_episodic with a short-horizon-appropriate eviction policy (evict once the chain terminates), rather than requiring any separate working-memory mechanism. *Evidence:* **Reasoned hypothesis** — this reduction was proposed in ARS-001 and is repeated here as an architectural commitment, not newly validated.

**Reference implementations drawn from, and what's explicitly rejected:**
- *Neural Turing Machine / Differentiable Neural Computer* — the addressable-write *mechanics* are a reasonable reference. **Rejected:** neither prescribes a competence-gated write/eviction *policy*; adopting their mechanics without EXP-001's policy would be adopting the least-validated part of this architecture's own prior work and discarding the most-validated part.
- *kNN-LM / RETRO (retrieval-augmented generation)* — reference for the general "smaller parametric model + retrieval can match a larger pure-parametric one" result, which motivated EXP-001 in the first place. **Rejected:** their typical policy of indexing *all* available data unconditionally, which EXP-001 directly outperformed with competence-gated writing (73% vs. 2% of capacity wasted on already-known content).

---

## 3. Assembled Architecture — Computational Flow

This section describes how the functions and substrates above compose into one processing loop. No new components are introduced here — everything below is a *use* of Sections 1–2, not additional machinery.

```
Input arrives (already encoded — see Section 4, out of scope)
        │
        ▼
ROUTING: EVALUATE(input, routing entries in S_episodic)
        │  → SELECT chosen COMPOSE family
        │  → if no routing entry exists (novel input class): fall back to the
        │     most general/unconstrained library member, flag low confidence
        │     via EVALUATE(b), and mark as a candidate for a new routing entry
        │     [Reasoned hypothesis — no fallback/discovery policy is validated;
        │      this is EXP-005/EXP-012's open problem, not solved here]
        ▼
COMPOSE (selected family processes the input)
        │
        ├─ if multi-step (RC-03/RC-04): write intermediate result to
        │  S_episodic (short-horizon schema) → COMPOSE again → repeat until
        │  EVALUATE(b) signals sufficient confidence or a step limit is hit
        ▼
EVALUATE the output
        │  (a) against a known target, if available (training/correction mode)
        │  (b) via self-consistency, if not (open-ended/deployment mode —
        │      Reasoned hypothesis, not validated)
        ▼
UPDATE
        │  high discrepancy against known target → write correction to
        │    S_episodic (Validated, EXP-001) + SELECT an SR-02 action
        │    (proceed / ask / flag) [Reasoned hypothesis]
        │  low discrepancy → reinforce the routing entry that produced this
        │    result [Reasoned hypothesis]
        ▼
(periodic, not per-input) CONSOLIDATION
        │  sample mastered/reinforced S_episodic entries → replay into
        │  S_semantic's ordinary training → evict consolidated entries
        │  [Reasoned hypothesis — EXP-010]
        ▼
(periodic) GRADUATION / READINESS CHECK
        COMPOSE generates novel probe compositions → EVALUATE against them,
        aggregated → SELECT (threshold-crossing) → readiness signal
        [Speculative — DP-03]
```

---

## 4. Out of Scope (Unchanged from ARS-001)

Encoding — mapping raw external input into a representation usable by the functions above — remains a boundary assumption, not designed here, per ARS-001 §5.4: no requirement or experiment addresses it, and nothing in this architecture depends on a specific encoding scheme.

---

## 5. Explicitly Rejected Components

Named and excluded because no requirement or evidence traces to them, even though each is common in reference architectures:

- **A single monolithic "world model" module.** Common in planning-oriented RL architectures. Rejected: RC-04's planning need is already satisfied by COMPOSE (used generatively) + EVALUATE + SELECT working together (Section 3's flow); no requirement calls for a separate, unified world-model component, and adding one would be unjustified by this specification.
- **A language-shaped scratchpad as the mandatory mechanism for multi-step state-carrying.** Common in current LLM "chain-of-thought" designs. Rejected as a *global requirement*: RC-03 reduces to S_episodic used for short-horizon state (Section 2.4), which was never shown to need a natural-language format. A specific COMPOSE module handling a language-generation task may still use language-shaped intermediate state internally — that is a per-module choice (Section 2.1), not an architecture-wide commitment.
- **Global fixed positional encoding / sequence-order assumptions.** A Transformer-specific default. Rejected as an architecture-wide commitment: ordering matters only for COMPOSE modules whose domain genuinely has sequential structure, so it belongs as a per-module property (declared alongside each module's structural-constraint metadata, Section 2.1), not a global assumption every input representation must carry.
- **A single global next-token-prediction training objective.** Rejected as a mandatory, architecture-wide default: LN-01 requires support for a non-stationary, trajectory-dependent signal, which a fixed generative objective does not provide by default. A specific COMPOSE module may still use a token-prediction-style internal objective where appropriate — again a per-module choice, not a global commitment.
- **A single, architecture-wide critic/reward model (RLHF-style).** Rejected as a separate, additional component: SELECT already consumes EVALUATE's output per decision context (Section 2.3) everywhere a "critic" would otherwise be needed (family choice, action choice, write/evict, readiness). Adding a second, global critic on top would duplicate machinery already justified by RC-02/SR-02/ME-03/DP-03, without new requirement coverage to justify the duplication.

---

## 6. Full Traceability Table

| Design decision | Function(s) | State | Requirement(s) | Evidence |
|---|---|---|---|---|
| S_episodic (capacity-constrained KV store) | — (substrate) | S_episodic | ME-01 | Validated (EXP-001) |
| S_semantic (slow parameters) | — (substrate) | S_semantic | ME-02 | Supported by literature |
| Routing/self-model as S_episodic content, not new substrates | UPDATE, EVALUATE | S_episodic | ME-01, ME-03, RC-02, SR-01 | Reasoned hypothesis |
| Typed COMPOSE library, structure-matched per module | COMPOSE | S_semantic (params) | RC-01 | Validated (EXP-002) |
| Supervised EVALUATE (known target) | EVALUATE | — | ME-03, RC-02 | Validated (EXP-001, EXP-002/003) |
| Unsupervised/self-consistency EVALUATE | EVALUATE | — | SR-01, DP-03 | Reasoned hypothesis / literature |
| Held-out-driven, hard-argmax family SELECT | SELECT | S_episodic (routing) | RC-02 | Validated (EXP-003) |
| Variable compute-amount SELECT | SELECT | — | RC-02 | Reasoned hypothesis |
| Confidence-conditioned action SELECT | SELECT | — | SR-02 | Reasoned hypothesis |
| Competence-gated episodic write/evict | UPDATE | S_episodic | ME-01, ME-03 | Validated (EXP-001) |
| Replay-based semantic consolidation | UPDATE | S_semantic | ME-03, LN-02 | Reasoned hypothesis |
| Short-horizon state-carrying via S_episodic | UPDATE | S_episodic | RC-03 | Reasoned hypothesis |
| Generative COMPOSE + EVALUATE + SELECT for planning | COMPOSE, EVALUATE, SELECT | S_episodic (working) | RC-04 | Reasoned hypothesis (literature: classical search) |
| Periodic probe-based graduation signal | EVALUATE, SELECT | S_episodic (self-model) | DP-03 | Speculative |
| Novel-input fallback to generic COMPOSE member | COMPOSE, EVALUATE | S_episodic (routing) | RC-01, RC-02 | Reasoned hypothesis (unresolved — EXP-005/012) |

---

## 7. What Remains Unvalidated — Concrete Next Experiments

- **EXP-009: General-purpose EVALUATE.** Does any of the candidate unsupervised/self-consistency designs (Section 2.2b) produce a usable, calibrated signal outside a labeled-target setting? Currently the least-validated, most load-bearing piece of the entire architecture (per ARS-001 §5.7).
- **EXP-010: Explicit consolidation via replay.** Does actively sampling mastered S_episodic entries into S_semantic's training (rather than relying on the backbone to passively catch up, as EXP-001 did) measurably transfer competence, and does it respect LN-02's stability constraint?
- **EXP-011: Routing-as-episodic-content.** Does storing routing decisions in S_episodic under the same write/evict policy as facts (Section 1.1) match EXP-003's dedicated-mechanism accuracy, or does reusing the substrate degrade selection quality?
- **EXP-012 (refines EXP-005): Novel-input fallback and family discovery.** What should actually happen when an input class has no routing entry — is generic-module fallback plus low-confidence flagging (Section 3) adequate, or does it silently fail in a way EXP-002/003's clean synthetic tasks never exposed?

---

## 8. Versioning

- **v0.1** — CCA static pipeline (archived, `archive/CCA_v0.1.md`).
- **v0.2** — Council-driven conceptual stage; superseded by DEC-005 without producing a validated primitive.
- **v0.3** — Build-experiment-validate; two components validated in isolation (EXP-001, EXP-002/003) plus their composability (EXP-004); no architecture yet.
- **v0.4 (this document)** — First concrete architecture, derived from ARS-001's requirements and functional decomposition rather than from any existing AI architecture's overall shape. Not yet implemented as an integrated system beyond the isolated/paired validations already completed (EXP-001–004); Section 7's four experiments are the next validation steps before any claim of end-to-end viability.

---

**Purpose:** The first concrete ACA architecture, built exclusively from the four functions and state substrates identified in ARS-001, with every component traced to a specific requirement and evidence tier.
**Current Status:** Active — v0.4, designed but not yet implemented or tested as an integrated system.
**Historical Context:** Produced 2026-07-18, immediately following ARS-001's completion (both reduction passes) — the first architecture-design phase this research program has entered, after four prior phases (design-generation origin, CCA v0.1, council-driven v0.2, build-experiment-validate v0.3) that each stopped short of one.
**Known Facts:** See Section 6's traceability table for exactly what is and isn't validated per component.
**Hypotheses:** Every component tagged "Reasoned hypothesis" or "Speculative" in Sections 1–3 and 6.
**Unknowns:** Section 7's four experiments; whether the assembled flow (Section 3) behaves coherently as an integrated system at all, which has not been tested even where individual components are validated.
**References:** `docs/08_requirements/ARS-001.md`, `docs/06_experiments/Completed.md` (EXP-001–004), `docs/04_architecture/Memory.md`, `docs/04_architecture/Cognitive_Primitives.md`, `docs/04_architecture/Dynamic_Computation.md`, `docs/04_architecture/Scheduler.md`
