**Status: Active — ACA v1.0 Architecture Specification**

# ACA v1.0: Architecture Specification

**Role note:** this document is produced under a changed responsibility. Prior documents (ARS-001, ACA v0.4) were produced in a research role — searching for and validating abstractions. This document is produced in an architecture-synthesis role: transforming validated knowledge into a coherent engineering blueprint. Research continues only where architecture cannot yet proceed (Section 12, the experimental roadmap) — it is no longer the primary activity.

**What changed from ACA v0.4:** v0.4 established the four functions and two state substrates and traced every component to a requirement and evidence tier. Two things happened since: EXP-009 falsified the assumption that EVALUATE is a single function (it splits into LOCAL and GENERALIZATION), and a required theoretical clarification (`docs/08_requirements/ARS-001.md` Section 7) identified a third category, STRUCTURAL evaluation. v1.0 is v0.4 matured to reflect both, with the full lifecycle, risk, and roadmap detail a synthesis-stage document requires. v0.4 is preserved in place, not deleted — this document supersedes it as ACA's current architecture.

**Non-negotiable rule, carried forward from v0.4 and restated because it now governs eleven deliverables instead of eight sections:** every component below must trace through Component → Computational Function → Requirement ID → Evidence. If that chain cannot be written, the component is not included. Every component is tagged **Validated / Supported by literature / Reasoned hypothesis / Speculative**. Falsified beliefs are preserved with what replaced them, not erased.

---

## 1. State Model

Three substrates, not two — the third is new in this document, derived (not assumed) from Section 2's structural evaluation requirement.

### 1.1 S_episodic
Fixed-capacity, content-addressable key-value store; `insert`, `evict`, `query`. Hosts three content schemas under one write/evict mechanism (facts, routing decisions, self-model entries) — see ACA v0.4 §1.1 for the full schema table, unchanged here.
*Function:* target of UPDATE, read by EVALUATE-LOCAL/SELECT. *Requirement:* ME-01. *Evidence:* **Validated** (EXP-001).

### 1.2 S_semantic
Slow-updating trainable parameters: the general associative backbone and each COMPOSE module's structural parameters.
*Function:* target of UPDATE (consolidation), read by COMPOSE. *Requirement:* ME-02. *Evidence:* **Supported by literature**.

### 1.3 S_invariants — new in v1.0
A **read-only**, externally-supplied store of domain invariants (symmetries, closure properties, logical/causal consistency constraints) — e.g., "this operator family is a group action; closure and identity must hold." Unlike S_episodic and S_semantic, nothing in the architecture *writes* to S_invariants through ordinary operation; it is populated by whoever specifies the domain, the same way RC-01's family library itself must currently be hand-specified (EXP-005/012's still-open family-*discovery* problem).
*Function:* the second input to STRUCTURAL evaluation (`evaluate_structural(representation, invariant)`), which no other function or substrate provides. *Requirement:* traces to RC-02, RC-04, SR-01/SR-02 per ARS-001 §7.3's derivation. *Evidence:* **Reasoned hypothesis** — this substrate does not exist in any validated experiment; it is included because Section 2.2c's function requires an input source for known invariants, and nothing else in the state model supplies one. If EXP-015 (Section 12) fails to show structural evaluation adds value, this substrate's justification collapses with it — it is not included speculatively beyond that dependency.

**Why three, not two, and why not folded into S_semantic:** S_invariants is neither fast-adaptive (S_episodic) nor slow-adaptive (S_semantic) — it is *non-adaptive*, supplied rather than learned. Folding it into S_semantic would misrepresent it as something the system updates through training, which it explicitly must not (an invariant a system could train itself out of respecting is not serving its purpose as an external check).

---

## 2. Computational Functions

### 2.1 COMPOSE
Typed library of structure-matched transform modules, each declaring its constraint as inspectable metadata. *Requirement:* RC-01. *Evidence:* **Validated** (EXP-002). Reference implementations: attention (generic/flexible member), equivariant layers (structure-matched member, EXP-002's validated design), discrete rule execution from cognitive architectures (exact-computation member). Rejected: any of these as the sole/default mechanism (EXP-002 falsified this directly).

### 2.2 EVALUATE — three realizations, not one

**(a) EVALUATE-LOCAL** — `(output, known_target | self) → discrepancy_score`. *Requirement:* ME-03, SR-01/SR-02. *Evidence:* **Validated** — supervised form (EXP-001), label-free form via entropy/ensemble/self-assessment (EXP-009). This is the one EVALUATE realization ready for direct implementation.

**(b) EVALUATE-GENERALIZATION** — `(output, held-out reference) → discrepancy_score`, semantically distinct from (a): must distinguish overfitting from correctness. *Requirement:* RC-02, DP-03 (by analogy). *Evidence:* **Validated only with real labels** (EXP-002/003); **label-free realizations falsified** (EXP-009 — entropy and self-assessment fail completely, ensemble partially and unreliably). **No architecture should assume this function can run without real held-out labels** until EXP-013 (Section 12) says otherwise.

**(c) EVALUATE-STRUCTURAL — new in v1.0** — `(representation, invariant from S_invariants) → consistency_score`. *Requirement:* RC-02 (family-type verification), RC-04 (plan constraint-satisfaction), SR-01/SR-02 (complementary trigger). *Evidence:* **Reasoned hypothesis** (`docs/08_requirements/ARS-001.md` §7) — theoretically well-motivated, mechanistically targeted at exactly what broke (b), but **not yet tested**. Included because it passes the traceability bar (a real requirement, a real theoretical argument) — not because it is proven.

### 2.3 SELECT
`(scored candidates) → choice`. Held-out-driven, hard argmax is validated (EXP-003) for family choice — **and, per (b) above, still requires real labels as its score source; it is not yet label-free**. *Requirement:* RC-02, SR-02, ME-03, DP-03. Reference: MoE gating mechanics adopted, MoE's loss-driven training objective explicitly rejected (EXP-003).

### 2.4 UPDATE
Episodic write/eviction: **Validated** (EXP-001). Semantic consolidation via replay: **Reasoned hypothesis**, untested (EXP-010). RC-03's state-carrying is a usage pattern of this function over S_episodic, not new machinery.

---

## 3. Component Dependency Graph

```
S_invariants (external, read-only)
      │
      ▼
EVALUATE-STRUCTURAL ──────────────┐
      │                           │
      ▼                           ▼
   RC-02 family verification   RC-04 plan constraint-checking
      │                           │
      ▼                           ▼
EVALUATE-GENERALIZATION ◄── (still needs real labels) ──► SELECT (family/plan choice)
      │
      ▼
COMPOSE library (S_semantic params) ◄─────────────────────┐
      │                                                    │
      ▼                                                    │
EVALUATE-LOCAL (entropy / ensemble / self-assessment) ─────┘
      │
      ▼
UPDATE (S_episodic write/evict; S_semantic consolidation)
      │
      ▼
SR-02 action policy (proceed / ask / flag) ◄── EVALUATE-STRUCTURAL (complementary trigger)
```

**Foundational nodes (no upstream dependency):** COMPOSE, EVALUATE-LOCAL, EVALUATE-STRUCTURAL (given S_invariants), S_invariants itself (externally supplied). **Everything downstream of EVALUATE-GENERALIZATION is gated on real labels being available** — this is stated as a hard dependency, not softened, because EXP-009 demonstrated what happens when it's treated as optional.

---

## 4. Execution Pipeline (Inference)

Extends ACA v0.4 §3 with structural evaluation inserted at the routing and planning steps:

```
Input arrives (encoding out of scope, per ARS-001 §5.4)
        │
        ▼
ROUTING: EVALUATE-STRUCTURAL(candidate families, S_invariants)
         → families failing a known invariant are excluded first (cheap, label-free filter)
         │  then EVALUATE-GENERALIZATION on survivors (requires labels; if unavailable,
         │  fall back to the structural-only filter's top candidate, flagged low-confidence)
         → SELECT chosen family
        ▼
COMPOSE (selected family processes the input)
        │  if multi-step: write intermediate state to S_episodic, repeat COMPOSE,
        │  check termination via EVALUATE-STRUCTURAL (constraint satisfaction of the
        │  partial result -- primary) + EVALUATE-LOCAL (confidence heuristic -- secondary)
        ▼
EVALUATE-LOCAL the output (labeled if available, label-free otherwise -- both validated)
        ▼
UPDATE: high discrepancy -> write correction (S_episodic) + SELECT an SR-02 action
        low discrepancy -> reinforce routing entry
        EVALUATE-STRUCTURAL flags invariant violation regardless of confidence
        -> independent trigger for SR-02, even if EVALUATE-LOCAL was confident
```

**What is new relative to v0.4:** structural evaluation gives routing a cheap, label-free *pre-filter* (exclude families that violate known invariants) before falling back to the label-requiring GENERALIZATION check — this reduces, but does not eliminate, v0.4's dependency on labels at routing time. Planning termination now has a primary (structural) and secondary (local) signal rather than one unclassified signal.

---

## 5. Learning Pipeline (Training)

1. **COMPOSE module fitting:** ordinary supervised training per family on its FIT-equivalent split, exactly as EXP-002 validated. **Validated.**
2. **EVALUATE-LOCAL calibration:** entropy needs no training; ensemble requires training K independent backbones; the self-assessment head trains jointly via a regression auxiliary loss against realized loss. **Validated** (EXP-009).
3. **EVALUATE-GENERALIZATION (family selection):** requires a reserved, labeled selection split, held out from FIT — exactly EXP-003's mechanism. **Validated, requires labels.**
4. **EVALUATE-STRUCTURAL setup:** S_invariants populated by whoever specifies the domain (not learned); no training step exists for this today — it is checked, not fit. **Reasoned hypothesis** for whether checking alone (without any fitting) is sufficient, pending EXP-015.
5. **Consolidation:** periodic replay of mastered S_episodic entries into S_semantic's ordinary training batches. **Reasoned hypothesis**, untested (EXP-010).

---

## 6. Memory Pipeline

Unchanged from ACA v0.4 §1.1/2.4: competence-gated write (**Validated**, EXP-001), competence-gated eviction (**Validated**, EXP-001), replay-based consolidation (**Reasoned hypothesis**, EXP-010), routing/self-model content sharing the same substrate and policy (**Reasoned hypothesis**, EXP-011).

---

## 7. Evaluation Pipeline — the Three-Way Dispatch

| Consumer | Primary | Secondary | Status |
|---|---|---|---|
| ME-03 (memory gating) | LOCAL | — | Validated |
| RC-02 (family selection) | STRUCTURAL (cheap pre-filter) | GENERALIZATION (requires labels) | STRUCTURAL: Reasoned hypothesis. GENERALIZATION: Validated-with-labels only |
| RC-04 (planning termination) | STRUCTURAL | LOCAL (heuristic) | Both Reasoned hypothesis |
| SR-01/SR-02 (self-regulation) | LOCAL | STRUCTURAL (independent trigger) | LOCAL: Validated. STRUCTURAL: Reasoned hypothesis |
| DP-03 (deployment readiness) | All three, aggregated | — | Mixed — see Section 10 |

No consumer relies on GENERALIZATION alone without a labeled fallback path. This is a deliberate architectural constraint, not an oversight — it is the direct, load-bearing consequence of EXP-009.

---

## 8. Routing and Planning

Routing (RC-02): structural pre-filter → labeled selection (Section 4). Planning (RC-04): COMPOSE generates candidate sequences → structural constraint-check (primary termination signal) → local-confidence heuristic (secondary, for search ordering, not correctness) → SELECT best surviving sequence. Neither is implemented; both are specified precisely enough to build against, per the "originally believed / replacement" discipline in Section 11.

---

## 9. Failure Handling

Three independent ways a wrong output can occur, and what currently catches (or doesn't catch) each:

1. **Statistically confident but structurally invalid** (e.g., output violates a known invariant despite low entropy) — caught by EVALUATE-STRUCTURAL, a genuinely new capability relative to v0.4, where this failure mode was invisible.
2. **Structurally valid but wrong parameters** (e.g., a valid rotation, wrong angle) — not caught by STRUCTURAL by design (Section 2.2c's stated limit); caught only by GENERALIZATION with real labels, or not caught at all if labels are unavailable. **This is an acknowledged, currently-unclosed gap, not a solved case.**
3. **No known invariant exists for the domain** — STRUCTURAL evaluation is unavailable entirely; the architecture falls back to LOCAL (which EXP-009 shows is unreliable for exactly this kind of question) plus GENERALIZATION-with-labels if available. **If neither is available, the architecture has no validated way to catch this failure mode.** This is stated plainly rather than implied to be handled.

---

## 10. Continual Learning, Version Evolution, and Deployment

**Continual learning:** governed by UPDATE's consolidation behavior (Section 6) and the stability-plasticity constraint (LN-02) — consolidation must contribute one sample among many to an ordinary training batch, never directly overwrite S_semantic from a single entry. **Reasoned hypothesis.**

**DP-01 (deployment artifact):** must package S_episodic, S_semantic, S_invariants (read-only, so simplest to package — no versioning concern of its own), and routing/self-model state coherently. **Speculative** (unchanged from v0.4 — this remains the least-resolved requirement in the entire specification).

**DP-02 (versioned checkpoints):** unchanged from v0.4. **Reasoned hypothesis.**

**DP-03 (deployment readiness):** now explicitly a three-signal aggregate (Section 7's last row) rather than a single probe-based score as in v0.4 — this is the clearest concrete change v1.0 makes to a DP requirement. **Speculative overall** (the aggregation itself is untested), built from two Validated and one Reasoned-hypothesis component.

**Training / Inference / Deployment lifecycles, explicitly:**
- **Training lifecycle:** Section 5, steps 1–5, in that order — COMPOSE fitting must precede EVALUATE-GENERALIZATION's selection step (you need trained candidates before selecting among them); EVALUATE-LOCAL calibration can proceed in parallel with COMPOSE fitting since it doesn't depend on family selection being resolved.
- **Inference lifecycle:** Section 4's pipeline, per input.
- **Deployment lifecycle:** DP-03's readiness aggregate must clear a threshold (unspecified — **Speculative**, matching DP-03's own tag) before DP-01's artifact is packaged and DP-02 records a checkpoint.

---

## 11. Falsified Beliefs and Their Replacements

| Originally believed | Why it failed | Evidence | Current replacement |
|---|---|---|---|
| A single EVALUATE function can serve all consumers (ARS-001 §5) | Entropy and a self-assessment head are proxies for output sharpness; an overfit hypothesis is sharper on training-like data precisely because it overfit, not because it's correct — indistinguishable from correctness by any function of the sharpness signal alone | EXP-009: 0% held-out accuracy, every seed, for entropy and self-assessment at family-selection, despite both matching the oracle at memory-gating | EVALUATE splits into LOCAL (validated label-free) and GENERALIZATION (requires real labels) |
| Loss-driven or parsimony-regularized family selection can discover correct structure automatically | Training loss (and, later, statistical confidence) cannot distinguish "fits the data" from "will generalize" | EXP-003: 0% held-out accuracy at every tested penalty strength, with an unpredicted "backwards" pattern at higher penalty | Validation-driven (labeled) selection; now supplemented by a structural pre-filter, itself unvalidated |
| A generic, sufficiently expressive computation module can learn any structure given enough data | Excess free parameters admit many training-consistent solutions, only some of which generalize; nothing in ordinary training selects the generalizing one | EXP-002: 0% held-out accuracy across three attempts (learned embedding, fixed features, weight-decay sweep 0–1.0) | Structure-matched, constrained COMPOSE modules (RC-01) |
| The council-driven, first-principles methodology would converge on a validated architecture (pre-DEC-005) | Four sprints produced progressively refined methodology for evaluating claims, never a validated primitive or contact with data | Absence of any validated result across Sprints 1–3A | Build-experiment-validate-iterate (DEC-005), which produced EXP-001 through 009 in comparable time |
| Competence-gated eviction (ME-03, Section 6) protects valuable memory content in general, not just under the static distribution EXP-001 tested | Point-in-time "mastered" (low current entropy/loss) is treated as permanently safe to evict; under sequential, non-rehearsed training this is false — an entry is evicted for being mastered right at the moment it becomes vulnerable to the next stage's training overwriting that mastery | EXP-018: Stage-1 memory coverage exactly 0.0 at evaluation, every seed, both memory conditions; Stage-1 recall statistically indistinguishable from no-memory baseline (real Transformer, real staged continual task) | Unresolved. A one-time consolidation-via-replay burst at stage boundaries does **not** fix it either (EXP-010: 0.160 ± 0.028 vs. 0.158 ± 0.027 baseline — no improvement); interleaved rehearsal or explicit weight-importance protection (EWC-style) are the next untested candidates. See Section 18 |

---

## 12. Experimental Roadmap — Dependency-Aware, Prioritized by Architectural Impact

| ID | Purpose | Architectural dependency | Risk if false | Fallback modification | Expected impact |
|---|---|---|---|---|---|
| **EXP-015** | Test structural (algebraic-consistency) evaluation on EXP-002/003's own task: does it correctly reject Family B without labels? | Section 2.2c, Section 4's routing pre-filter, Section 7's whole STRUCTURAL row | If it fails: STRUCTURAL is not a real escape from GENERALIZATION's limit; S_invariants (Section 1.3) loses its justification and should be removed, not kept as decoration | Revert to labels-only GENERALIZATION for RC-02; remove the structural pre-filter from Section 4 | **Highest** — determines whether any part of RC-02/RC-04 can ever be label-free |
| **EXP-013** | Search harder for any label-free GENERALIZATION proxy beyond the three already-falsified candidates (sharpness/flatness measures, perturbation-based disagreement) | Section 2.2b, Section 4's fallback path | If all fail: GENERALIZATION is confirmed labels-only for the foreseeable future | Architect RC-02/DP-03 permanently around requiring labeled data; stop searching for a label-free substitute | High — but lower than EXP-015, since EXP-015 tests a *qualitatively different* mechanism, not a variant of what already failed |
| **EXP-014** | Directly test where RC-04 (planning termination) falls, rather than the reasoned classification in Section 7.3 | Section 8's planning design | If STRUCTURAL doesn't actually serve termination well: Section 8 needs a different primary signal, likely falling back to labeled GENERALIZATION per-step, which is expensive | Use LOCAL as primary with STRUCTURAL as a secondary sanity check instead of the reverse | Medium-high — reshapes Section 8 specifically |
| **EXP-010** | Explicit consolidation via replay | Section 5 step 5, Section 6 | If replay doesn't measurably transfer competence: consolidation stays passive (backbone catch-up only, as in EXP-001), S_semantic never actively absorbs episodic content | Drop active replay; keep only passive eviction | Medium — affects long-run memory capacity management, not correctness |
| **EXP-011** | Routing-as-episodic-content | Section 1.1's schema-sharing design | If reuse degrades EXP-003's selection accuracy: routing needs its own substrate after all | Give routing decisions a dedicated store, breaking the "one substrate, three schemas" economy | Medium — a state-model simplification, not a correctness-critical path |
| **EXP-012** | Novel-input fallback / family discovery | Section 4's routing fallback | If generic-fallback-plus-flagging is inadequate: routing silently fails on genuinely new input classes | Requires a dedicated family-discovery mechanism, currently unspecified | Medium — matters more as domain coverage grows, less urgent for a narrow first deployment |

**Priority order and why:** EXP-015 first, because it tests the one idea (Section 7) that could change what's *architecturally possible*, not just how well an already-accepted approach performs. EXP-013 second, because if it also fails, GENERALIZATION's labels-only status becomes a permanent design constraint rather than a temporary gap — worth knowing before investing further in Section 4's fallback machinery. EXP-014 third: it doesn't change whether structural evaluation works, only where it applies. EXP-010–012 are real but lower-stakes refinements to already-functioning designs.

---

## 13. Architecture Risk Register

| Risk | Severity | Likelihood | Mitigation status |
|---|---|---|---|
| EVALUATE-GENERALIZATION remains labels-only indefinitely | High — limits RC-02/DP-03 to settings with available labeled data, foreclosing fully autonomous deployment | Moderate-high, given EXP-009's clean falsification and NFL's theoretical backing | Architecturally acknowledged (Section 7's table), not hidden; EXP-013/015 are the direct response |
| Structural evaluation (S_invariants) requires hand-specified domain knowledge that doesn't scale | High if it does not scale — reproduces the "human must supply the correct family" problem one level up, at the invariant level | Unknown until EXP-015 and broader domain testing | Not yet mitigated; explicitly named as a risk rather than assumed away |
| DP-01 (deployment artifact) remains Speculative across two architecture versions (v0.4 and v1.0) | High — the architecture has no validated notion of what actually deploys | High, given zero progress since v0.4 | Unaddressed; flagged as a standing gap, not deprioritized by omission |
| Consolidation-via-replay (UPDATE, Section 6) never gets validated | Medium — long-run memory capacity growth without bound if consolidation stays passive-only | Moderate | EXP-010 named, not yet run |
| The whole architecture has never been tested as one integrated system beyond EXP-004's narrow, disjoint-parameter composability test | High — every component's validation is isolated; nothing confirms the *assembled* Section 4 pipeline behaves coherently | High, by construction — this has never been attempted | Named explicitly; the single largest scale/integration risk in the document |

---

## 14. Open Assumptions Register

- Encoding of raw input into a usable representation (ARS-001 §5.4) — presupposed throughout, never designed.
- One EVALUATE-LOCAL signal suffices for all its consumers (ARS-001 §5's original assumption, narrowed but not eliminated by EXP-009 — EXP-009 tested memory-gating and wrongness-detection specifically, not every possible LOCAL use).
- S_invariants can be populated correctly and completely enough to be useful — untested; a wrong or incomplete invariant set could make STRUCTURAL evaluation actively misleading, not just unhelpful.
- The disjoint-parameter design validated in EXP-004 will still hold once routing (Section 4) and consolidation (Section 6) are both live simultaneously — untested combination.
- Compute cost of running structural checks, ensembles, and self-assessment heads together, at any scale beyond toy tasks, is unknown and unmeasured.

---

## 15. Future Revision Policy

Following ARS-001's own precedent (§5.8, §6, §7): revisions are added as new sections or new table rows, never by editing a prior claim's text. A component's evidence tag changes only when a specific experiment changes it, cited by ID. Falsified beliefs move to Section 11 with their replacement, not deleted. This document's own Section 11 should, in turn, be extended (not edited) if any of its "current replacements" are themselves later falsified — there is no principled reason to expect this architecture is exempt from the same fate as its predecessors, and the document should not be written as if it were.

---

## 16. Versioning

v0.1 (CCA, archived) → v0.2 (council-driven, superseded) → v0.3 (validated components, no architecture) → v0.4 (first architecture, EVALUATE later revised in place) → **v1.0 (this document): EVALUATE formalized as three realizations, S_invariants added, full lifecycle/risk/roadmap detail, superseding v0.4 as current.** Not yet implemented as an integrated system; Section 13's last risk item is the standing reminder of exactly how much remains unintegrated.

---

## 17. Corrections from IVS-001's Prerequisite Audit (Appended, Not Edited In-Place)

`docs/09_validation/IVS-001.md` was required to audit this document for redundant or unjustified components before designing a validation strategy against it. Its findings are recorded here as an addition, per Section 15's own policy (revisions are appended, not silently rewritten into prior text):

- **RC-03 has no separate identity.** Everywhere above that appears to treat it as distinct machinery (Sections 2.4, 3, 4, 7) should be read as: S_episodic (ME-01) used with a short-horizon eviction policy, not a separate component.
- **EVALUATE-LOCAL's required default is entropy alone**, not all three EXP-009-validated candidates. Ensemble disagreement and the self-assessment head are documented fallbacks, not co-required components — they cost more (K× training; an extra head) for no measured benefit over entropy on either tested use.
- **Variable compute-amount SELECT (part of Section 2.3/RC-02) is excluded from any near-term implementation** — no experiment has ever shown hard-argmax-only is insufficient. It remains a documented possibility, not a current requirement.
- **S_episodic's shared content schemas (Section 1.1's original design, carried from ACA v0.4) require key-namespacing by schema** — a specification gap, not an experimental question, patched directly rather than deferred.
- **A contingency to watch, not yet resolved:** if EXP-015 (Section 12) shows structural pre-filtering fully resolves family selection in tested cases, the labeled EVALUATE-GENERALIZATION step for that specific decision becomes redundant and should be removed then, not retained by default.

---

## 18. Corrections from ACA-MVP-001 Benchmark A / EXP-018 (Appended, Not Edited In-Place)

The first real-Transformer, real-scale test of ME-03 (competence-gated memory, Section 6) produced a falsifying result for a claim this document previously stated without qualification. Recorded here per Section 15's own policy:

- **Section 6's "competence-gated eviction (Validated, EXP-001)" must be read as scope-limited to EXP-001's tested setting: a single static distribution.** Under sequential, non-rehearsed staged training, EXP-018 shows the identical policy provides no measurable protection against forgetting — Stage-1 memory coverage was exactly 0.0 at evaluation time, every seed. This does not reverse EXP-001's original result (which stands, under the conditions it tested); it narrows the claim's generality, which Section 6 previously implied was unrestricted.
- **The mechanism generalizes a risk Section 13/IVS-001 §2 had already named for a different component.** IVS-001's "Routing ↔ Learning (UPDATE)" risk row predicted that a routing entry could be evicted as "mastered" while still load-bearing, calling this a risk specific to routing content. EXP-018 shows the same mechanism afflicts ordinary factual content under S_episodic's shared write/evict policy — the risk was under-scoped, not wrong.
- **This is not a failure of EVALUATE-LOCAL's calibration (Section 7, EXP-016's still-open question).** The entropy signal read correctly at the moment it was taken — the backbone genuinely had mastered Stage-1 by the Stage-1/2 boundary. The failure is in treating a correct point-in-time reading as license for permanent eviction, a policy-design gap, not a signal-accuracy gap. Kept explicitly distinct to avoid conflating two different open questions under one label.
- **Consequence for Section 12/IVS-001 §6's roadmap ranking:** EXP-010 (consolidation via replay) was ranked lowest (rank 6 of 7) on the stated grounds that it "does not affect correctness of anything already validated." EXP-018 shows this rationale no longer holds — EXP-010 (or an equivalent fix) may be a precondition for ME-03 to deliver any real-world benefit outside a static distribution, not a lower-stakes refinement. The ranking itself is not rewritten here (per Section 15, that revision belongs in IVS-001 directly); this section only records why it needs revisiting.
- **EXP-010 has since been run (same day, immediately following EXP-018) and is itself falsified in its minimal form:** a one-time replay burst (20 steps/boundary) reinforcing memory's contents into the backbone before eviction produced no measurable improvement (0.160 ± 0.028 vs. 0.158 ± 0.027 baseline). Reasoned mechanism: a brief burst is not defended against the 800 steps of unrelated training that immediately follow it, with plain Adam providing no explicit protection for parameters the burst just reinforced. ME-03's general-case status therefore remains genuinely open, not pending-a-known-fix — the next candidates (interleaved rehearsal throughout subsequent training; explicit weight-importance protection) are structurally different and larger changes, not variations on what was just falsified. Full detail: `docs/06_experiments/Completed.md` (EXP-010).
- **Not every real-scale test this section records is negative.** Section 2.1's COMPOSE (RC-01, tagged Validated by EXP-002 at toy scale) has since been confirmed at real published-benchmark scale: ACA-MVP-001 Benchmark B (EXP-020, `docs/06_experiments/Completed.md`) shows a fixed, real-data-verified grammar plus a 326-parameter learned lookup scoring 100.000% ± 0.000% exact-match on SCAN's `addprim_jump` held-out compositional test set, against 0.71% ± 0.39% for a 681,481-parameter generic Transformer trained identically — a ~141x margin, consistent with Lake & Baroni (2018)'s own published baseline for this split. This does not change RC-01's evidence tag (already Validated) but extends its evidentiary base from a 40-example synthetic task to a real, cited one. **The caveat EXP-002 already raised is unchanged, not resolved by scale:** the grammar was hand-specified and verified by the experimenter, not discovered by the system — RC-02's automatic family-discovery problem (EXP-005) remains exactly as open as it was.
- **A candidate fourth state substrate was considered and resolved before adoption, not added.** `docs/12_cognition/CTX-001.md` proposed "S_working," a structurally separate substrate for conversation/reasoning context, as a Reasoned Hypothesis. EXP-019 (`docs/06_experiments/Completed.md`) falsified the need for it directly: a reserved capacity partition within the existing S_episodic mechanism, written unconditionally rather than surprise-gated, performs identically (1.000 ± 0.000 recall) to full structural separation, while naive schema-tagging without this discipline collapses (0.200 ± 0.100, zero coverage) via a newly-identified **write-starvation** mechanism distinct from EXP-018's eviction-based one. Section 1 is therefore unchanged — three substrates, not four — with the reserved-partition discipline now catalogued in `docs/13_state_model/SOS-001.md` rather than added here as new architecture.

Full experimental detail: `docs/06_experiments/Completed.md` (EXP-018, EXP-010, EXP-020, EXP-019), `docs/11_mvp/ACA-MVP-001.md` Sections 8-9, `docs/12_cognition/CTX-001.md` §10, `docs/13_state_model/SOS-001.md`.

---

**Purpose:** ACA's architecture specification — the engineering blueprint synthesized from validated requirements (ARS-001), with complete Component → Function → Requirement → Evidence traceability throughout, audited for redundancy before validation planning proceeded against it.
**Current Status:** Active — v1.0, synthesized, partially implemented (ME-01/ME-03 and RC-01 both tested at real scale by ACA-MVP-001 Benchmarks A and B respectively), audited once (Section 17), corrected/extended four times against real-scale evidence (Section 18: EXP-018 negative, EXP-010 negative, EXP-020 decisively positive, EXP-019 resolves a candidate fourth substrate without adopting one).
**Historical Context:** Produced 2026-07-18 under a changed role (architecture synthesis rather than research), immediately following ARS-001 Section 7's required theoretical clarification on structural evaluation. Audited the same day per `docs/09_validation/IVS-001.md`'s prerequisite requirement. Section 18 added 2026-07-22 following ACA-MVP-001 Benchmark A's completion, extended same day with EXP-010, extended again 2026-07-23 with EXP-020 (Benchmark B) and EXP-019 (S_working resolution).
**Known Facts:** See Section 2's per-function evidence tags and Section 11's falsification table (now including EXP-018's ME-03 scope-narrowing and EXP-010's falsified minimal fix). RC-01/COMPOSE's real-scale confirmation (EXP-020) does not change its evidence tag (already Validated) but substantially extends its evidentiary base. The state model (Section 1) remains three substrates, not four — EXP-019 resolved the candidate fourth (S_working) via a disciplined S_episodic partition instead, catalogued in `docs/13_state_model/SOS-001.md`.
**Hypotheses:** Every component tagged Reasoned hypothesis or Speculative throughout, most consequentially S_invariants (1.3) and EVALUATE-STRUCTURAL (2.2c), both contingent on EXP-015. ME-03's general-case status is genuinely open — its most direct candidate fix (one-time consolidation replay) is now also falsified; interleaved rehearsal and explicit weight-protection are the next, untested, structurally larger candidates. RC-01's confirmation at scale does not touch RC-02's still-fully-open automatic family-discovery problem (EXP-005).
**Unknowns:** Section 12's six experiments (now superseded in priority order by IVS-001 §6's blast-radius ranking, itself due for revision per Section 18); Section 13's five named risks, especially whole-system integration, never yet attempted even in miniature. Whether EXP-019's write-starvation mechanism also affects the routing or self-model schemas — untested, flagged as follow-up in EXP-019 and `docs/13_state_model/SOS-001.md`.
**References:** `docs/08_requirements/ARS-001.md` (Sections 2, 5, 6, 7), `docs/06_experiments/Completed.md` (EXP-001–004, EXP-009, EXP-018, EXP-010, EXP-020, EXP-019), `docs/04_architecture/ACA_v0.4_Architecture.md` (superseded, preserved), `docs/09_validation/IVS-001.md`, `docs/11_mvp/ACA-MVP-001.md`, `docs/12_cognition/CTX-001.md`, `docs/13_state_model/SOS-001.md`, `docs/03_foundations/{ACCEPTED,REJECTED,OPEN}.md`
