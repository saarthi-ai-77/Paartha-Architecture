**Status: Active — Scientific Prototype Specification**

# ACA-MVP-001: Minimal Scientific Prototype

**Role note:** produced as ACA's Chief Experimental Scientist, not its architect. Default assumption throughout: ACA is wrong until an experiment says otherwise. This is not a product or a demo — it is the smallest implementation capable of producing evidence that ACA is either genuinely useful or fundamentally unnecessary.

---

## 1. The Smallest Implementation Possible

Two of ACA v1.0's three validated-at-toy-scale components are included; everything still-hypothetical is excluded. Real Transformer backbone (necessary baseline capability, not itself an ACA claim), competence-gated episodic memory (ME-01/ME-03, EXP-001 — the single most validated, most distinctive claim), and a structure-matched COMPOSE module (RC-01, EXP-002) with **family assignment fixed by hand, not auto-routed**.

## 2. Component Justification — Why Must This Exist, What Hypothesis Disappears Without It

| Component | Included? | Why | Hypothesis lost if removed |
|---|---|---|---|
| Transformer backbone (S_semantic) | Yes | Baseline capability; without one there is nothing to compare against | All of them |
| Episodic memory, competence-gated write/evict (ME-01/ME-03) | Yes | The core, most-validated, most distinctive claim | "Allocation policy matters, not just having memory" (EXP-001) — untestable at real scale otherwise |
| EVALUATE-LOCAL, entropy only | Yes, minimal form | Must gate memory writes; entropy already validated equal to costlier alternatives (EXP-009) | Memory gating has no signal to act on |
| COMPOSE library, ≥2 structure-matched families | Yes, **fixed assignment** | Tests EXP-002's compositional-generalization claim at real scale | "Structure-matched constrained computation beats generic" untestable at scale |
| RC-02 automatic/learned routing | **Excluded** | Depends on EVALUATE-GENERALIZATION, which is labels-only (EXP-009) or unvalidated (EXP-015 not yet run) — including it now would confound two unresolved questions at once | Nothing — not what MVP-001 tests; deferred to MVP-002 pending EXP-015 |
| EVALUATE-STRUCTURAL / S_invariants | **Excluded** | Untested (EXP-015 pending); testing it simultaneously with memory/compose would muddy causal attribution of any result | Nothing — explicitly out of scope until EXP-015 resolves in isolation |
| Consolidation (replay) | **Excluded from core; optional stretch ablation** | EXP-010 untested; the primary hypothesis (memory prevents forgetting) is testable via write/evict alone | Nothing for the primary hypothesis |
| RC-04 planning/multi-step | **Excluded** | Unclassified (EXP-014 pending); no MVP hypothesis needs it | Nothing |
| DP-01/02/03 deployment/versioning | **Excluded** | This is a training+eval scientific prototype, not a deployment exercise | Nothing |

## 3. Benchmark Design — Real Tasks, Not More Synthetic Toys

Two benchmarks, each targeting a specific already-toy-validated claim, each chosen so a plain Transformer is a genuinely strong, standard baseline (not a strawman):

**Benchmark A — Continual factual recall with staged introduction (new, more realistic than EXP-001).** Real natural-language template sentences ("[NAME] was born in [CITY]."), a fixed small vocabulary, a real word-level tokenizer. Facts introduced in **stages**, not one static distribution: Stage 1 trains heavily on facts 1–100, Stage 2 shifts to facts 101–200 (facts 1–100 now rare/absent), Stage 3 shifts to 201–300. This directly stresses catastrophic forgetting — EXP-001 measured a static long-tail at one point in time; this measures whether *earlier* rare knowledge survives *later* training, the actual continual-learning question IVS-001's EXP-016 was designed around, now at real-Transformer scale instead of an MLP.

**Benchmark B — Compositional generalization, SCAN (Lake & Baroni), not a hand-built task.** Switching from this program's own small synthetic 4-operator task to the actual, standard, citable SCAN benchmark — small enough to train on a single consumer GPU, with published baseline numbers in the literature to compare against, making this a genuinely stronger, more credible test of EXP-002's claim than repeating the in-house task at larger scale would be.

**Benchmark C — Joint test.** Both benchmarks' data combined in one model (fixed routing: recall-shaped inputs to the memory-augmented pathway, SCAN-shaped inputs to the compose pathway), extending EXP-004's disjoint-parameter composability finding to real backbones and real tasks.

## 4. Ablation Studies

Each mechanism removed one at a time, isolating exactly one architectural claim per run:

- **Full ACA-MVP** (Transformer + competence-gated memory + structure-matched compose) vs.
- **No memory** (Transformer + compose, memory removed) — isolates memory's contribution.
- **Naive-cache memory** (write-on-first-sight, random eviction, replacing the competence-gated policy) — isolates whether the *policy*, not just the presence of memory, matters (directly re-testing EXP-001's core finding at real scale, not assuming it transfers).
- **Generic compose** (an unconstrained module replacing the structure-matched one, on Benchmark B only) — isolates whether structure-matching matters at this scale (re-testing EXP-002).
- **[Stretch] + consolidation** — isolates EXP-010's still-untested claim, added only if the core ablations complete with time remaining.

## 5. Success Criteria

Stated in advance, per this program's own standing discipline of committing to a threshold before running, not after: **ACA-MVP must retain at least 2x the baseline's rare-fact accuracy after staged continual training to justify its added complexity** — chosen because it mirrors EXP-001's own already-observed margin over naive caching, not an arbitrary new number invented for this test. **A relative improvement under ~20–30% (within plausible seed-to-seed noise at this scale) should be reported as not justifying the architecture's added complexity**, explicitly, not spun as a qualified success.

## 6. Computational Cost

Measured directly, not estimated: parameter count (exact), wall-clock latency per forward pass with vs. without the memory lookup, peak GPU memory (`torch.cuda.max_memory_allocated`). **Energy is not rigorously measurable in this environment** (a laptop GPU with no power instrumentation) and is not reported as a precise figure — stated honestly rather than fabricated, unlike the other four metrics.

## 7. Publication-Quality Experimental Design

5 seeds minimum per condition (this program's standing practice), pre-registered success criteria (Section 5, not adjusted post hoc), honest negative-result reporting if the criteria aren't met. **Publication roadmap, scoped honestly to current maturity:** if Benchmark A/B/C succeed, this is a workshop-paper-shaped result ("does competence-gated memory and structure-matched composition survive integration with a real Transformer backbone") — not a claim of state-of-the-art capability. A full paper would additionally need: comparison against an actual published memory-augmented baseline (kNN-LM/RETRO), statistical significance testing across more seeds, and the scale-transfer step this program has flagged as open since EXP-001. If the criteria are *not* met, the honest, still-publishable result is the negative one: a real-Transformer-scale attempt to test the memory-allocation-policy hypothesis and what specifically broke it — following this program's own precedent (EXP-002's own falsification-then-narrower-confirmation was more valuable than a premature positive claim would have been).

## Implementation Order

1. Benchmark A (continual recall) — highest priority, directly extends IVS-001's #1-ranked EXP-016.
2. Benchmark B (SCAN) — second, independent of A, can run in parallel if resources allow.
3. Benchmark C (joint) — only after A and B each independently clear their own ablations.
4. Consolidation stretch ablation — only if time remains.

## Expected Failure Modes

- Memory's advantage could shrink or vanish at real-Transformer scale — the backbone itself may absorb rare facts better than the toy MLP did, given more capacity and richer representations (a real, stated possibility, not assumed away).
- SCAN's structure-matched module requires knowing SCAN's actual compositional structure in advance — a real instance of the still-open family-*discovery* problem (EXP-005/012), sidestepped here by hand-specifying it, exactly as Section 2 states.
- Staged continual training could interact with the Transformer's own optimizer state (Adam moments, learning-rate schedule) in ways a toy MLP's simpler training never exposed — a genuine new risk specific to using a real architecture for the first time.

---

## 8. Benchmark A Result (Appended, Not Edited Into Sections 1–7's Pre-Registered Design)

**Result: the §5 success criterion (≥2x baseline Stage-1 retention) FAILED, cleanly, across all 5 seeds.** All three conditions (no_memory, naive_cache_memory, competence_gated_memory) scored statistically indistinguishable Stage-1 recall (0.150–0.158) after staged, non-rehearsed continual training — a ~0% relative improvement against the pre-committed 2x threshold. Full write-up, mechanism, and data: `docs/06_experiments/Completed.md` (EXP-018).

**Why this is reported as a clean negative result, not a qualified success, per §5's own pre-commitment:** memory coverage of Stage-1 facts at evaluation time is exactly 0.0 in both memory conditions, every seed — neither policy retained a single old fact by the time it was needed. The mechanism is fully traced in EXP-018: competence-gated eviction (validated by EXP-001 against a *static* distribution) evicts whatever currently reads as "mastered," but under sequential non-rehearsed training, "mastered now" does not imply "safe to forget" — it is evicted at precisely the moment it becomes vulnerable to the next stage's training, not after. This is a real limitation of ME-03 as specified in ACA v1.0, confirmed at real scale for the first time, not a harness bug (Stage-3 accuracy of 1.000 in every condition confirms the task and model capacity are fine).

**Effect on Implementation Order (§ above):** the core Benchmark A ablations are complete, but the §4 stretch ablation ("+consolidation," isolating EXP-010) is now the immediately motivated next step, not an optional extension — it directly tests the one candidate mechanism (replay-based consolidation before eviction) that could plausibly rescue ME-03 under staged training. This is run before Benchmark B per this document's own §5 discipline: an honest negative result on the highest-priority benchmark warrants a motivated follow-up test before moving to an independent benchmark, not silent progression to B as if A had cleared its ablations.

---

**Purpose:** Determine whether ACA demonstrates measurable, real-scale advantages over a standard Transformer baseline, or whether its added complexity is unjustified — not to extend ACA's design further.
**Current Status:** Benchmark A complete — pre-registered success criterion failed, mechanism identified (EXP-018). Stretch ablation (consolidation) motivated and next. Benchmarks B/C not yet started.
**Historical Context:** Produced 2026-07-18 under a Chief Experimental Scientist role, following DAS-001, in response to a directive that further conceptual architecture work was producing diminishing returns without implementation evidence. Benchmark A executed and logged the same day.
**Known Facts:** Every included component traces to EXP-001, EXP-002, or EXP-009; every excluded component traces to an explicitly still-unvalidated hypothesis (EXP-005/010/012/014/015). Benchmark A's actual result: EXP-018, `docs/06_experiments/Completed.md`.
**Hypotheses:** Sections 3–5 as originally stated for Benchmarks B/C, not yet tested. Benchmark A's hypothesis (§5) has been tested and failed — see Section 8.
**Unknowns:** Section "Expected Failure Modes" for B/C. For A: whether consolidation (EXP-010) rescues the result — open, motivated, not yet run.
**References:** `docs/04_architecture/ACA_v1.0_Architecture.md`, `docs/09_validation/IVS-001.md`, `docs/10_deployment/DAS-001.md`, `docs/06_experiments/Completed.md` (EXP-001, EXP-002, EXP-009, EXP-018)
