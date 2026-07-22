**Status: Active**

# Completed Experiments

---

## EXP-001: Surprise-Gated Capacity-Constrained Episodic Memory vs. Naive Caching

**Epistemic Status:** Working Hypothesis — CONFIRMED under toy-task conditions (see Limitations). Not yet tested at language-model scale or with a real training corpus.

### Objective
Test whether a specific, non-obvious design choice for episodic memory in a memory-typed architecture — writing only what the parametric backbone still gets wrong, and evicting whatever it has since mastered — outperforms the naive alternative (write on first sight, evict at random) at a fixed, limited memory capacity. This is not a test of "does external memory help recall" (already well-established by kNN-LM/RETRO) — it isolates the value of the *allocation policy* specifically.

### Research Question
Under a memory budget too small to store every fact, does competence-aware (surprise-gated) write/eviction beat naive caching on rare/long-tail fact recall, at equal capacity?

### Hypothesis
A surprise-gated policy — write when current parametric loss on a fact exceeds a threshold, evict the currently-stored fact the backbone now predicts best when capacity is full — achieves higher tail-fact recall accuracy than naive caching at the same memory capacity, because it avoids wasting slots on facts the backbone has already learned.

### Methodology
Synthetic associative-recall task: 1000 facts, each a fixed random near-orthogonal key vector mapped to a unique value id (no cross-fact structure, so recall requires either genuine memorization or storage — no generalization is possible, isolating memorization capability specifically). Facts sampled during training via a Zipfian distribution (exponent 1.3) over 1250 steps x batch 32 (40,000 samples), producing 434 "tail" facts (≤3 expected exposures) and 96 "head" facts (≥30 expected exposures) out of 1000. Three conditions, same backbone architecture (2-hidden-layer MLP) and identical per-seed backbone initialization and sampled-fact sequence (so only the memory policy differs):
1. **no_memory_baseline** — pure parametric model, no external memory.
2. **naive_cache** — fixed-capacity (200 slots) memory, write on first sight, evict a uniformly random slot when full.
3. **surprise_gated** — same 200-slot capacity, write only if current loss > 2.0 nats, evict the stored fact with lowest current loss (most "mastered") when full and no slot is safely evictable otherwise skip the write.
Run across 5 seeds (identical world/fact-distribution across seeds; seed varies backbone init + sample order + eviction randomness).

### Variables
* **Independent:** memory write/eviction policy (none / naive / surprise-gated).
* **Dependent:** final tail-fact recall accuracy (with memory applied at inference), final head-fact recall accuracy, memory composition (fraction of capacity spent on tail vs. head facts).
* **Controlled:** backbone architecture and size, memory capacity (200 slots in all memory conditions), training steps, data distribution, per-seed initialization and sample order.

### Expected Outcome
Surprise-gated should show meaningfully higher tail recall than naive_cache at the same capacity, driven by a lower fraction of memory spent on head facts.

### Results (mean ± std over 5 seeds)

| Condition | Tail recall (with memory) | Tail memory coverage | Head memory coverage |
|---|---|---|---|
| no_memory_baseline | 0.050 ± 0.019 | 0.000 | 0.000 |
| naive_cache | 0.098 ± 0.017 | 0.059 | **0.733** |
| surprise_gated | **0.182 ± 0.025** | 0.146 | 0.019 |

Full per-seed data: `experiments/exp001_surprise_gated_memory/results.json`. Code: `experiments/exp001_surprise_gated_memory/run.py`.

### Conclusion
**Hypothesis confirmed under these toy-task conditions, consistently across all 5 seeds.** Surprise-gated allocation achieves roughly **2x** the tail recall of naive caching at the identical memory budget (18.2% vs 9.8%), and roughly **3.6x** the no-memory baseline. The mechanism is directly visible in the coverage breakdown: naive caching wastes **73.3%** of its 200-slot budget on head facts the backbone already predicts perfectly (zero marginal value from storing them), while surprise-gating spends only **1.9%** of capacity there and allocates the rest to facts the backbone genuinely cannot yet handle. This validates the specific claim under test: at a fixed memory budget, *what* you choose to store matters as much as *whether* you have external memory at all — a naive "cache everything you've seen" policy actively self-sabotages under capacity pressure because high-frequency facts (which the parametric backbone learns fine on its own) get written first and occupy slots indefinitely unless evicted by luck.

### Limitations (read before generalizing this result)
- **Retrieval is exact-match by construction.** Keys are near-orthogonal random vectors, so there is no ambiguity/interference in lookup. A harder, more realistic test would use correlated/similar keys where retrieval itself can misfire — this experiment says nothing about that failure mode yet.
- **Toy scale.** ~1000-parameter-class task, 1000 facts, a 2-layer MLP backbone. This has not been tested integrated into an actual language-model backbone, on real text, or at any scale approaching an SLM.
- **No cost accounting yet.** This measures accuracy only, not the actual training/inference compute cost of running the eviction-scan step (which requires a forward pass over all stored facts whenever eviction is needed) — at larger memory capacities this could become a real overhead that needs its own efficiency measurement.
- **Single architecture family for the backbone.** Not yet tested whether this holds with a transformer-shaped backbone instead of an MLP, or with real (non-uniform, non-independent) key structure.

### Follow-up Research
1. Repeat with correlated/similar keys (e.g. keys clustered so some facts are genuinely confusable) to test retrieval robustness, not just allocation policy.
2. Integrate this memory mechanism into an actual small transformer/language-model backbone and test on a real (or semi-real) long-tail factual corpus, not a synthetic id-mapping task.
3. Measure the compute overhead of the eviction-scan step as memory capacity scales, to check the efficiency story actually holds in practice, not just the accuracy story.
4. Test sensitivity to `SURPRISE_WRITE_THRESHOLD` and `MASTERED_THRESHOLD` — current values were reasonable guesses, not tuned; a sweep would show how robust the effect is to these choices.

---

## EXP-002: Factorized Rule Module for Compositional Generalization — a Three-Stage Failure Chain That Converges on the Real Mechanism

**Epistemic Status:** Working Hypothesis — the *original* proposal (generic factorized linear rule module) is FALSIFIED. A specific, much more constrained revision is CONFIRMED under toy-task conditions, with an honest, mechanistically-understood negative control (see below). Not yet tested at any scale beyond a 40-example synthetic task, and the central open problem this experiment surfaces (see "What this actually means for the architecture") is unresolved.

### Objective
Test whether an architecture that structurally factors "which operator" from "which operand" generalizes to (operator, operand) combinations never seen jointly during training, as the compositional-generalization literature (Fodor & Pylyshyn; SCAN) and our own quarantined RP-001 material both predicted it should, in principle, be able to.

### Research Question
Does factoring operator from operand, by itself, produce compositional generalization — and if not, what specifically is missing?

### Hypothesis (original, as stated before running anything)
A model with a shared operand-embedding pathway and a per-operator linear "rule" applied on top will correctly compute held-out (operator, operand) combinations that a black-box model (given the same information as one joint input) will not.

### Methodology
4 fixed arithmetic operators mod 10 (`op0: x+1`, `op1: x*2`, `op2: 9-x`, `op3: x+5`) applied to operands 0–9. 8 of 40 (operator, operand) pairs held out entirely from training (2 per operator), such that every operand is still seen under most operators and every operator is still seen with most operands — held-out-combination recovery is possible in principle from compositional structure alone. Three successive model variants tested, 5 seeds each:
1. **black_box_mlp** — one-hot(op) concatenated with one-hot(x) → 2-layer MLP → logits. No architectural bias toward factorization.
2. **factorized_rule_module** — shared learned operand embedding (`nn.Embedding`) → per-operator learned linear readout (~30 free parameters per operator).
3. **fixed-feature variant** — same per-operator linear readout, but the learned embedding replaced with a FIXED, non-learned sin/cos encoding of the operand's position on a 10-point circle, to remove the "free lookup table" degree of freedom.
4. **weight-decay sweep** on variant 3 (0 to 1.0), testing whether pushing toward a minimal-norm solution recovers generalization.
5. **group-action-constrained variant** — the per-operator transform constrained to a single learned rotation angle + reflection sign (2 parameters per operator, not ~30), i.e. the operator can only represent a rotation/reflection of the circle, not an arbitrary linear map.

### Variables
* **Independent:** model architecture / operator parameterization (steps 1–3, 5 above); regularization strength (step 4).
* **Dependent:** held-out-combination accuracy, overall and per-operator; training-set accuracy (to check the model isn't simply failing to fit at all).
* **Controlled:** task, held-out split, training steps, optimizer, seeds.

### Results

| Stage | Variant | Train acc | Held-out acc | Per-operator held-out |
|---|---|---|---|---|
| 1 | black_box_mlp | 1.000 | 0.050 ± 0.061 | — |
| 2 | factorized_rule_module (learned embedding) | 1.000 | **0.000 ± 0.000** | all 0% |
| 3 | fixed sin/cos feature, free per-op linear layer | 0.863 ± 0.025 | **0.000 ± 0.000** | all 4 operators 0%, including op0/op2/op3 which are theoretically linear in this feature space |
| 4 | weight-decay sweep (0 → 1.0) on stage 3 | degrades monotonically (0.863 → 0.369) | **0.000 at every setting** | regularization never recovers generalization |
| 5 | group-action-constrained (rotation angle + reflection, 2 params/op) | 0.781 | **0.750 ± 0.000** | op0: **1.000**, op2: **1.000**, op3: **1.000**, op1: **0.000** |

In stage 5, the learned parameters recovered the exact ground truth: op0's rotation angle converged to 0.6283 rad (= 2π/10, exactly correct for `+1`); op3's converged to 3.1416 rad (= π, exactly correct for `+5`, a half-turn); op2 recovered a reflection (learned sign ≈ −0.997). op1 (`x*2 mod 10`) — which is quadratic in circle coordinates, not linear, and additionally not a bijection — stayed at exactly 0%, not a partial or lucky score.

Full data: `experiments/exp002_factorized_rule_module/results.json`, `results_fix_attempt.json`. Code: `run.py`, `run_fix_attempt.py`, and the two inline follow-up scripts referenced in this session's tool history (weight-decay sweep, group-action-constrained model).

### Conclusion
**The original hypothesis, as stated, is false.** Merely factoring operator from operand — with either a learned or a fixed operand encoding, and regardless of L2 regularization strength — does not produce compositional generalization. The generic factorized layer has enough free parameters (~30 per operator) that gradient descent reliably finds *a* solution that fits the training pairs without finding the *specific* solution that also generalizes, and no amount of weight decay nudges it there, because "small weights" and "the generalizing solution" are not the same target in this parameterization.

**A corrected, much narrower hypothesis is confirmed:** compositional generalization becomes reliable and exact — not just improved, but 100% and parameter-exact — once the operator is constrained to belong to the *actual symmetry family the true function belongs to* (here: rotations/reflections of a cyclic group), reducing the operator's free parameters from ~30 to 2. This is a real, mechanistically-understood, positive result, not a lucky fit: the model recovered the literal correct rotation angles, and correctly, honestly failed on the one operator (op1) that doesn't belong to that family, rather than producing a spuriously-plausible wrong answer.

### What this actually means for the architecture (the important, unresolved part)
This result is good news and a serious warning at the same time. The good news: when the inductive bias is *correctly matched* to the task's true structure, compositional generalization is not just possible but easy and exact, with a tiny number of parameters. The warning: **we only got this result because we, the experiment designers, already knew in advance that the true operators were rotations/reflections**, and hand-built the model to only be capable of representing that family. A "rule module" in a real architecture will not have a human pre-telling it the correct symmetry group for every domain it encounters. The actual open research problem this experiment surfaces is: **how does a rule module discover or select the right constrained hypothesis family for an unknown domain, rather than requiring it to be hand-designed per task?** That is a much harder and more central question than "can factorized architectures generalize compositionally" (answered here: yes, but only under a correctly-matched constraint), and it is now the most important next step for this line of the architecture, not a side detail.

### Follow-up Research
1. **The central open problem:** test whether a small library of candidate constrained transform families (e.g., rotation/reflection, permutation, affine, a shallow generic MLP as fallback) with a *learned, differentiable selection mechanism* over which family applies per operator can recover the right structure without being told in advance — this is the actual test of whether a "rule module" can be built without hand-designing the symmetry per task.
2. Test whether this finding transfers beyond cyclic-group arithmetic — e.g. permutation groups, affine transforms on other domains — to check "match the constraint family to the true structure" generalizes as a design principle, or is an artifact of this specific toy task's clean group structure.
3. Investigate why op1 could not be solved by ANY of the more general (unconstrained) parameterizations either (stages 2–4) despite having more raw expressive power than the constrained rotation model — i.e. confirm that generic over-parameterized models don't accidentally solve the harder case just because they have more capacity (current evidence: they don't, but this wasn't the focus of the experiment and deserves a dedicated check).

**Follow-up 1 above was executed as EXP-003 (below), immediately following this experiment in the same research session.**

---

## EXP-003: Can Family Selection Be Learned Automatically, Instead of Hand-Picked?

**Epistemic Status:** Working Hypothesis — CONFIRMED for the validation-driven mechanism, with an honest caveat on interpretability (see below). Two of three candidate mechanisms were tested and cleanly falsified. Small library (2 families), small task — not yet tested with a richer family library or at any real scale.

### Objective
EXP-002 showed constraining a rule module to the *correct* transform family (rotation/reflection) gives perfect, exact compositional generalization — but only because the correct family was hand-picked by the experiment designer. This experiment tests whether a model can instead **discover** which of a small library of candidate families applies to each operator, without being told.

### Research Question
Given a library of two candidate operator families — Family A ("simple": rotation/reflection, 2 parameters/operator) and Family B ("expressive": generic free linear map, ~30 parameters/operator) — can a model correctly learn which family applies to each of the 4 operators from EXP-002, using only the training data?

### Hypothesis (stated before running)
1. **Naive joint selection** (train both families' parameters and a learned per-operator mixture gate together, via ordinary cross-entropy on training pairs) will FAIL to prefer the simple family even where it's correct, because Family B fits training data at least as well as Family A (strictly more capacity) and nothing in a standard training loss rewards a family for generalizing to points it hasn't seen. Expected: gate drifts toward the expressive family everywhere.
2. **Parsimony-regularized selection** (add a penalty encouraging the simple family unless the expressive one measurably reduces training loss) might partially help, but the penalty strength is an arbitrary hyperparameter with no principled setting — expected to be fragile.
3. **Validation-driven hard selection** (fit both families on a fit-split, choose per-operator whichever generalizes better to a disjoint selection-split never used for fitting, evaluate on a further-disjoint final test split) should correctly recover the right family, because it's the only mechanism that measures generalization rather than training fit before choosing.

### Methodology
Same 4-operator task and final held-out test pairs as EXP-002 (8 pairs, 2/operator, untouched by any of the three mechanisms). Training pairs (32) further split for condition (iii) into a 24-pair fit split and an 8-pair (2/operator) selection split, reserved purely for choosing between families — the final test pairs are never used for fitting OR selection. 5 seeds per condition.

### Results

| Condition | Held-out acc | Learned gate on simple family (mean per operator: op0, op1, op2, op3 — true label: simple, EXPRESSIVE, simple, simple) |
|---|---|---|
| (i) naive joint | **0.000 ± 0.000** | [0.00, 0.01, 0.00, 0.00] — collapsed to the expressive family for *every* operator, including the 3 that are truly simple |
| (ii) parsimony λ=0.1 | **0.000 ± 0.000** | [0.00, 0.02, 0.00, 0.01] — regularization too weak to move the gate at all |
| (ii) parsimony λ=0.5 | **0.000 ± 0.000** | [0.24, 0.59, 0.25, 0.22] — gate moved, but **backwards**: op1 (the one operator that should NOT use the simple family) got the *highest* simple-family weight of all four, while the 3 truly-simple operators got lower, near-identical weights around 0.24 |
| (iii) validation-driven | **0.750 ± 0.000** | Hard selection: family A chosen for all 4 operators (op0 ✓, op1 ✗, op2 ✓, op3 ✓) — 3/4 correct, exactly matching EXP-002's oracle held-out accuracy (0.750) |

Full data: `experiments/exp003_family_selection/results.json`. Code: `experiments/exp003_family_selection/run.py`.

### Conclusion
**Hypotheses 1 and 2 confirmed exactly, including the specific failure mode predicted for hypothesis 1** (training-loss-driven selection always prefers the more expressive family, regardless of whether it generalizes). **Hypothesis 3 confirmed**: validation-driven selection — the only mechanism of the three that actually measures generalization before choosing — matches the oracle (hand-picked) accuracy from EXP-002.

**A genuinely surprising result within the falsified conditions:** at λ=0.5, the parsimony penalty pushed hardest toward the simple family on op1 — the one operator where that's wrong — while barely moving the gate for the 3 operators where the simple family is actually correct. This wasn't predicted and deserves honest flagging rather than being smoothed over: penalizing model complexity in the loss does not reliably track which operators the simple family is actually *right* about; it interacts with something else (likely how confidently/easily the expressive family fits each operator's training points, which may be least confident precisely on the non-bijective, harder-to-interpolate op1).

**An important caveat on the validation-driven success:** the mechanism selected Family A for op1 too — technically the wrong choice (op1 is the one operator that is NOT a rotation). But this didn't hurt the final accuracy, because Family B does not generalize op1 either (confirmed in EXP-002 — no parameterization tested anywhere in this line has solved op1). The validation split correctly detected "these two options are equally unable to handle op1" and defaulted to A on the tie, which is a fine practical outcome here but is not the same as correctly diagnosing "op1 needs a different family we don't have." **A cleaner test of the mechanism would require a family library where every operator has at least one family that actually works for it** — something this experiment's 2-family library doesn't provide for op1.

### What this means for the architecture
This validates a specific, actionable design rule for a real rule module: **family/structure selection must be driven by held-out generalization performance on a reserved split, not by training loss or by a fixed-strength complexity penalty.** Naive end-to-end training will always relax toward the most expressive available option regardless of correctness, and ad hoc regularization doesn't reliably fix that (and can misfire in non-obvious directions, as seen at λ=0.5). This is now a validated constraint on how any future "does this domain need a constrained rule vs. a generic learned function" decision should be implemented in the real architecture, not a design guess.

### Follow-up Research
1. Expand the family library to include a structure that actually *can* represent op1 (e.g. an explicit "doubling/multiplicative map" family), and re-test whether validation-driven selection correctly picks it — this is the real test of whether the mechanism diagnoses correctly rather than merely tying on mutual failure.
2. Test validation-driven selection with a much larger family library (5–10 candidate structures) and more operators, to see whether the approach still cleanly separates correct families as the search space grows, or whether the small selection-split (2 points/operator here) becomes a reliability bottleneck.
3. Investigate the λ=0.5 "backwards" pattern directly — is it something specific to op1's non-bijectivity, or a more general property of how parsimony penalties interact with per-operator training-fit confidence? This could itself be an important (and currently unexplained) finding.
4. Integration test: combine the validated pieces from EXP-001 (surprise-gated episodic memory) and EXP-002/003 (validation-selected rule module) into a single small end-to-end toy model with both a memory pathway and a rule pathway, to check the two validated mechanisms compose without interfering with each other — neither has been tested alongside the other yet.

**Follow-up 4 above was executed as EXP-004 (below), immediately following this experiment in the same research effort.**

---

## EXP-004: Integration Test — Do the Memory and Rule Pathways Compose?

**Epistemic Status:** Working Hypothesis — CONFIRMED at the engineering-composability level tested here. Explicitly does not test the harder question of a shared substrate (shared embeddings, learned routing) — see scope note below.

### Objective
EXP-001 (episodic memory allocation) and EXP-002/003 (constrained, validation-selected rule module) were each validated in isolation, on separate toy tasks, by separate model classes. Determine whether combining both into one model, trained jointly via one optimizer and one training loop, causes either mechanism to degrade relative to its own isolated-training performance.

### Research Question
Does joint training of two disjoint-parameter, structurally different pathways (a memory allocator and a rule module) in a single model produce any interference, or does each pathway perform as if trained alone?

### Design Decision Worth Flagging
The two pathways were kept with **fully disjoint parameters** — critically, the rule pathway kept its validated fixed (non-learned) sin/cos operand encoding rather than being given a learned embedding shared with the recall pathway. Sharing a learned embedding would have reintroduced exactly the free-embedding degree of freedom EXP-002 falsified, undermining the mechanism under test. This means EXP-004 tests **engineering composability** (can one training loop and one optimizer correctly carry both mechanisms without bugs, loss-scale imbalance, or optimizer-state issues) — it does **not** test the harder question of whether the two mechanisms could share a real substrate (e.g. a common token embedding space in an actual language model), which remains open.

### Hypothesis (stated before running)
Since the two pathways share no parameters, joint training should closely match each isolated baseline — Adam updates each parameter independently based on its own gradient, so there is no principled mathematical reason for disjoint pathways to interfere. A meaningful gap would indicate a real engineering interaction (e.g. a bug, or an unexpected effect of shared optimizer state) worth diagnosing.

### Methodology
Same worlds as EXP-001 (1000-fact Zipfian recall task, 200-slot competence-aware memory) and EXP-002 stage 5 (4-operator rotation/reflection task, 8 held-out combinations). Three conditions, 5 seeds each: **recall_isolated** (memory pathway trained alone, re-run here for an apples-to-apples comparison under identical code), **rule_isolated** (rule pathway trained alone), **joint** (both pathways in one model, one Adam optimizer with per-pathway parameter groups at each pathway's validated learning rate, mixed batches every step — a recall sub-batch and a rule sub-batch each step, losses summed, one `backward()`/`step()` call).

### Results (mean ± std over 5 seeds)

| Metric | Isolated | Joint |
|---|---|---|
| Recall tail-fact accuracy (with memory) | 0.444 ± 0.021 | 0.480 ± 0.017 |
| Rule held-out accuracy | 0.750 ± 0.000 | 0.750 ± 0.000 |

Full data: `experiments/exp004_integration_test/results.json`. Code: `experiments/exp004_integration_test/run.py`.

*(Note: the isolated recall tail accuracy here, ~0.44, is higher than EXP-001's originally-reported ~0.18 — this is because EXP-004 runs recall training for 2000 steps rather than EXP-001's 1250, to match the rule pathway's step count for a fair joint-training schedule, giving the memory backbone more total exposure and more opportunity for the surprise-gated write policy to populate useful slots. This is an artifact of the step-count choice, not a contradiction of EXP-001 — the isolated and joint conditions here both use the same 2000-step budget, so the isolated-vs-joint comparison is still apples-to-apples.)*

### Conclusion
**Hypothesis confirmed.** The rule pathway's held-out accuracy is bit-for-bit identical between isolated and joint training (0.750 ± 0.000 in both conditions, every seed). The recall pathway's tail accuracy shows no degradation under joint training — if anything, joint training slightly outperformed isolated training (0.480 vs 0.444), though this difference is well within normal seed-to-seed noise and should not be read as joint training being *better*, only as clear evidence of no interference. Two independently-validated, structurally different mechanisms can be trained together in one model, with one optimizer, without either one's validated behavior degrading — at least under the disjoint-parameter design tested here.

### What This Does and Doesn't Establish
**Establishes:** a real architecture can plausibly contain both a memory-allocation component and a rule/family-selection component without them stepping on each other during training, as long as they don't share the parameters whose constraints made them work in isolation.

**Does not establish:** whether the two mechanisms can share a common substrate (e.g. one token embedding space serving both a memory lookup and a rule operand role) without interference — this is a harder, more realistic integration question deferred to future work, since sharing a learned embedding would specifically threaten the rule pathway's validated constraint (see EXP-002). Also does not establish anything about a learned *routing* mechanism between the two pathways — this experiment used an explicit, non-learned dispatch (recall examples always go to the recall pathway, rule examples always go to the rule pathway), which is a simpler problem than the dynamic scheduling question tracked in `docs/04_architecture/Dynamic_Computation.md`.

### Follow-up Research
1. Test a version where the two pathways share a real substrate (e.g. a common embedding space), to see whether the interference risk EXP-002's design specifically avoided actually materializes when forced.
2. Replace the explicit non-learned dispatch with a learned router, applying EXP-003's validation-driven-selection constraint, as the first real test of `docs/04_architecture/Dynamic_Computation.md`'s open scheduling question.
3. Move beyond synthetic toy tasks entirely — integrate a version of these validated mechanisms into a small real transformer backbone on real (or semi-real) data, per `docs/03_foundations/OPEN.md`'s standing open question on scale transfer.

---

## EXP-009: Does a Single EVALUATE Function Unify Across All Its Downstream Consumers?

**Epistemic Status:** The unified-EVALUATE hypothesis is **FALSIFIED**. A specific, mechanistically-understood fracture point was found and is documented below, revising `docs/08_requirements/ARS-001.md` and `docs/04_architecture/ACA_v0.4_Architecture.md` accordingly (both preserved with the original hypothesis intact, per their own stated revision policies — nothing rewritten, a new section added).

### Objective
ARS-001's functional decomposition (Section 5.7) identified EVALUATE as the single most load-bearing function in the entire specification — a dependency of memory gating (ME-03), computation selection (RC-02), self-regulation (SR-01/SR-02), planning termination (RC-04), and deployment readiness (DP-03) — but explicitly flagged that whether *one* signal can serve all these consumers, versus requiring fundamentally different signals, had never been tested. This experiment tests that specific claim directly, before any further architecture implementation proceeds on top of it.

### Research Question
Can a single label-free (no-ground-truth-at-decision-time) EVALUATE realization serve memory-gating, computation-family-selection, and wrongness-detection/self-regulation equally well — or does it fracture into task-specific signals?

### Hypothesis (stated before running)
Three candidate label-free realizations were tested — entropy, ensemble disagreement, and a learned self-assessment head predicting the backbone's own loss (Yoo & Kweon, "Learning Loss for Active Learning," 2019) — each compared against the true-label oracle (exactly what EXP-001 and EXP-002/003 already validated) across three structurally different consumers, reusing those experiments' own validated testbeds rather than new ones. **Falsification criterion, fixed in advance:** if the same candidate ranks best across all three consumers, EVALUATE unifies; if the ranking differs, that is a real fracture, to be documented precisely, not averaged away.

### Methodology
**Stage 1 (memory-gating, EXP-001's task):** substitute each candidate for the oracle's write/evict gate (adaptive running-median threshold, scale-agnostic across signal types), measure tail-fact recall accuracy. **Stage 2 (family-selection, EXP-002/003's task):** substitute each candidate, computed *without* the selection-split's true labels, for EXP-003's held-out-accuracy-driven selection; measure final held-out test accuracy and correctness of family choice per operator. **Stage 3 (wrongness-detection, EXP-001's task):** measure how well each candidate's ranking separates inputs the model gets right from inputs it gets wrong (AUC), without using the label. 5 seeds throughout. Code: `experiments/exp009_unified_evaluate/` (`recall_stage.py`, `rule_stage.py`).

### Results (mean over 5 seeds)

| Signal | Stage 1: gating (tail acc) | Stage 3: wrongness-detection (AUC) | Stage 2: family selection (held-out acc) |
|---|---|---|---|
| Oracle (true label) | 0.082 ± 0.008 | — (is ground truth) | **0.750** (reference, EXP-003) |
| Entropy | 0.083 ± 0.008 (tied) | **0.990 ± 0.001** | **0.000 ± 0.000** (every seed) |
| Ensemble disagreement | 0.082 ± 0.008 (tied) | 0.990 ± 0.001 | 0.250 ± 0.158 (unreliable) |
| Self-assessment head | 0.083 ± 0.010 (tied) | 0.925 ± 0.005 | **0.000 ± 0.000** (every seed) |
| No-memory baseline (Stage 1 only) | 0.031 ± 0.013 | — | — |

### Conclusion
**Falsified, cleanly, with an identified mechanism.** Every candidate is statistically indistinguishable from the oracle at memory-gating. Entropy and ensemble disagreement are both excellent at wrongness-detection (0.990 AUC). But at family-selection — the one consumer whose entire purpose is distinguishing "fits what I've seen" from "will generalize to what I haven't" — entropy and the self-assessment head **fail completely, in every one of 5 seeds**, always selecting the more expressive, non-generalizing family. This is not noise; it is the identical failure mode EXP-003 already proved for raw training loss, recurring one layer down: the over-parameterized family achieves *lower entropy and lower predicted loss* on the selection split specifically *because* it is overfit to data resembling it, not because it is correct. A signal built to measure "how sharply does the model fit what it's looking at right now" is systematically fooled by the exact thing family-selection exists to catch. Ensemble disagreement partially escapes this (it measures cross-instance variance, not single-instance sharpness — an over-parameterized family's independently-trained instances genuinely disagree with each other more), but remains noisy (±0.158) and far below the validated oracle (0.750).

**EVALUATE does not reduce to one function.** It splits into at least two:
- **EVALUATE-LOCAL** (per-instance confidence/discrepancy) — entropy, ensemble, and the self-assessment head are all viable, interchangeable substitutes for the true-label oracle here. Serves ME-03 (memory gating) and, by direct test, wrongness-detection (the empirical proxy used for SR-01/SR-02 self-regulation).
- **EVALUATE-GENERALIZATION** (does this actually generalize, or does it merely fit what's been seen) — no label-free candidate tested here substitutes for genuine held-out evaluation. Serves RC-02 (computation selection) and, by the same structural reasoning (not directly tested), likely DP-03 (deployment readiness, which is explicitly about performance on novel compositions — the same problem shape as family-selection).

**Explicitly not tested:** RC-04 (planning termination) was not directly run in this experiment. Whether it behaves like EVALUATE-LOCAL (a per-step "is this good enough" judgment, plausibly local) or EVALUATE-GENERALIZATION (if "good enough" implicitly means "will this generalize") is a reasoned open question, not a result — flagged as such, not guessed at as if tested.

### What This Means for ARS-001 and ACA v0.4
Both documents are revised, not rewritten — the original unified-EVALUATE hypothesis (ARS-001 §5, ACA v0.4 §2.2) is preserved as the tested-and-falsified starting point, with a new section in each documenting the split and its evidence. See `docs/08_requirements/ARS-001.md` Section 6 and `docs/04_architecture/ACA_v0.4_Architecture.md`'s revised Section 2.2.

### Follow-up Research
1. **EXP-013: Does anything substitute for EVALUATE-GENERALIZATION without labels?** Ensemble disagreement partially works but is unreliable — is there a better label-free proxy (e.g. sharpness-aware measures, PAC-Bayes-style bounds, disagreement under input perturbation rather than across independently-trained instances), or does structure/family selection fundamentally require real held-out labeled data, full stop?
2. Directly test RC-04 (planning termination) and DP-03 (deployment readiness) rather than extrapolating their classification from this experiment's mechanistic pattern.
3. Test whether the fracture pattern holds with larger, more realistic over-parameterization gaps (this experiment's Family B was only ~15x larger than Family A) — does the entropy/self-assessment failure get worse, better, or stay the same as the capacity gap grows?

---

## EXP-018: ACA-MVP-001 Benchmark A — Competence-Gated Memory Under Staged, Non-Rehearsed Continual Training (First Real-Transformer Result)

**Epistemic Status:** The MVP-001 pre-registered success criterion (≥2x baseline tail-recall retention) is **FAILED, cleanly, across all 5 seeds**. A precise mechanism is identified and confirmed directly from logged data, not just inferred. This is the first experiment in this research program to use a real multi-head self-attention Transformer rather than an MLP, and the first to test EXP-001's validated memory-allocation policy outside a single static distribution.

### Objective
ACA-MVP-001 (`docs/11_mvp/ACA-MVP-001.md`) committed in advance to testing whether competence-gated episodic memory (ME-01/ME-03, validated at toy scale by EXP-001) retains its tail-recall advantage over naive caching and over no memory at all, once embedded in a real Transformer backbone under a harsher, staged continual-learning task than EXP-001 ever tested. The threshold was fixed before running: **at least 2x the baseline's rare-fact accuracy after staged continual training**, mirroring EXP-001's own already-observed margin.

### Research Question
Does competence-gated write/eviction (EXP-001's validated policy) protect the oldest facts from catastrophic forgetting when a real Transformer is trained sequentially on three disjoint, non-rehearsed stages of facts — or does something about moving from a static distribution to a staged one break the mechanism?

### Hypothesis (stated before running, per `docs/11_mvp/ACA-MVP-001.md` §5)
Competence-gated memory retains at least 2x naive-cache's and no-memory's Stage-1 (oldest facts) recall accuracy, measured after all three stages complete. A relative improvement under ~20–30% was pre-committed to be reported as **not** justifying the architecture's added complexity, regardless of how that looks after the fact.

### Methodology
Real causal Transformer (`nn.TransformerEncoder` + causal mask, 4 layers, 4 heads, d_model=128, 619,352 parameters — `CausalTransformerLM` in `experiments/exp_mvp001_continual_recall/run.py`), word-level tokenizer, 6-token template sentences ("NAME was born in CITY."). 300 distinct (name, city) facts introduced across 3 **sequential, non-rehearsed** stages of 100 facts each (800 training steps/stage, batch 32) — Stage 2 and Stage 3 never re-show Stage 1's names. Three conditions, 5 seeds each:
1. **no_memory** — backbone only.
2. **naive_cache_memory** — write every name on first sight, evict a uniformly random slot at capacity (EXP-001's naive baseline).
3. **competence_gated_memory** — write only when the backbone's own city-token entropy exceeds a running median (EXP-001/009's validated gate), evict the lowest-entropy ("most mastered") stored entry at capacity; stored entries' entropy is explicitly **refreshed against the current model at every stage boundary** (`refresh_gated_confidences`), mirroring EXP-001's live re-check design rather than using stale write-time values.

Memory capacity fixed at 60 slots — deliberately smaller than any single stage's 100 facts, and far smaller than the 300 facts introduced in total, to force real, sustained eviction pressure (EXP-001 used a 200-slot memory against 1000 facts under a single static Zipfian distribution — a different, non-staged, non-adversarial-to-recency pressure).

### Variables
* **Independent:** memory policy (none / naive / competence-gated).
* **Dependent:** Stage-1 recall accuracy after all 3 stages (primary), Stage-3 recall accuracy after all 3 stages (sanity check that the task is learnable at all), memory coverage of Stage-1 facts at evaluation time (diagnostic).
* **Controlled:** backbone architecture/size, memory capacity, training steps, optimizer, per-seed initialization and batch sampling.

### Results (mean ± std over 5 seeds)

| Condition | Stage-1 acc (after 3 stages) | Stage-1 = param-only acc? | Stage-1 memory coverage at eval | Stage-3 acc |
|---|---|---|---|---|
| no_memory | 0.158 ± 0.039 | n/a (no memory) | n/a | 1.000 ± 0.000 |
| naive_cache_memory | 0.150 ± 0.023 | **Yes, exactly, every seed** | **0.0, every seed** | 1.000 ± 0.000 |
| competence_gated_memory | 0.158 ± 0.027 | **Yes, exactly, every seed** | **0.0, every seed** | 1.000 ± 0.000 |

Full per-seed data: `experiments/exp_mvp001_continual_recall/results.json` (`raw.*.stage1.coverage` field, confirmed 0.0 for both memory conditions across all 5 seeds — checked directly, not inferred from the console summary, which did not print it). Code: `experiments/exp_mvp001_continual_recall/run.py`.

### Conclusion
**Pre-registered success criterion failed cleanly.** All three conditions are statistically indistinguishable (~0.15–0.16), a ~0% relative improvement against a required 2x threshold. Per §5 and §7's own pre-committed publication roadmap, this is reported as a genuine negative result, not a qualified success.

**The mechanism is fully identified, not just hypothesized — confirmed directly from the `coverage` field, which is exactly 0.0 for both memory conditions in every seed.** Neither memory policy retains a single Stage-1 entry by the time evaluation runs. Tracing this through the code (`gated_write`, `refresh_gated_confidences`, `naive_write`):

- **Stage-3 accuracy of 1.000 in every condition confirms the task itself is fully learnable** — the backbone masters each stage's 100 facts completely within 800 steps. This is what makes Stage-1's collapse to ~0.16 a genuine, cleanly-induced catastrophic-forgetting effect, not a confound from an under-capacity model or an unlearnable task.
- **`naive_cache_memory`:** with 300 total distinct names competing for 60 slots across 3 stages of unrehearsed writes, and eviction chosen uniformly at random, no mechanism protects any particular stage's entries — by the time Stage 3 finishes, the accumulated random churn has almost surely cleared every Stage-1 entry. Confirmed: coverage 0.0.
- **`competence_gated_memory`:** the failure is more specific and more informative than naive's. `refresh_gated_confidences` is called once at each stage boundary and recomputes every stored entry's entropy **under the model as it stands at that exact moment**. Because Stage 1 trains for a full 800 steps on only Stage 1's 100 facts, by the Stage-1/Stage-2 boundary the backbone has already mastered them — so the refresh correctly marks essentially every stored Stage-1 entry as low-entropy ("mastered"). `gated_write`'s eviction rule always evicts the *lowest*-entropy stored entry when a new, high-entropy (novel) name needs a slot. Since Stage 2 introduces 100 new names against a memory already full of just-marked-"mastered" Stage-1 entries, Stage-1 content is evicted first and fastest — precisely at the moment it is about to become vulnerable to being forgotten by training on unrelated data, not after. The same happens again at the Stage-2/Stage-3 boundary to whatever Stage-2 remnants remain. Confirmed: coverage 0.0.

**This is not a bug.** The code does exactly what its design specifies. It is a real, previously-untested limitation of the policy itself: **EXP-001 validated "evict what's currently mastered" against a single static distribution, where "mastered now" and "mastered permanently" are the same fact.** Under sequential, non-rehearsed training on *new* data, they are not — a point-in-time mastery reading says nothing about whether that competence survives the training that happens after the reading is taken. The policy has no way to distinguish "safely redundant" from "about to be overwritten by what comes next," because at eviction time, the future training that will cause forgetting hasn't happened yet.

### Relationship to Existing Predicted Risks (Important Precision, Not Overclaiming)
- **This is not EXP-016.** EXP-016 (`docs/09_validation/IVS-001.md` §6, rank 1) asks whether EVALUATE-LOCAL's entropy *signal* stays calibrated (correlated with true correctness) under concurrent learning. Here, the entropy signal was **accurate at the moment it was read** — the backbone genuinely had low loss on Stage-1 facts right at the Stage-1/2 boundary. The failure is not a miscalibrated signal; it is that the *eviction policy* treats an accurate point-in-time reading as a license for permanent removal. EXP-016 remains open and untested; this experiment does not resolve or substitute for it.
- **This directly confirms and generalizes a mechanism `docs/09_validation/IVS-001.md` §2 already predicted — for a different component.** The "Routing ↔ Learning (UPDATE)" risk row states: *"A routing entry could be evicted as 'mastered' (low current discrepancy) while still being the only record of which family handles a class — silent regression... indistinguishable from normal fact eviction under the current shared policy."* That row scoped this failure mode to routing entries specifically. **EXP-018 shows the identical mechanism afflicts ordinary factual content too** — it is a general property of point-in-time-mastery-based eviction under sequential training, not a routing-specific concern. IVS-001 §2's risk matrix under-scoped this risk; it is broader than originally written.

### What This Does and Doesn't Establish
**Establishes:** at real Transformer scale, under staged non-rehearsed training, EXP-001's validated eviction policy — applied with no modification — provides no measurable protection against catastrophic forgetting, because it structurally evicts exactly the content most at risk right when that risk is created. This is a genuine, mechanistically-confirmed limitation of the mechanism as currently specified in ACA v1.0 (ME-03), not of "external memory" as a general idea.

**Does not establish:** that memory-augmented recall is unsalvageable under continual training. Untested here: (a) whether a much larger capacity (approaching the total fact count) trivially fixes this — plausible but uninteresting, since it defeats the point of a bounded memory; (b) whether **active consolidation before eviction** (replaying a "mastered" entry into the backbone's own training a few times before dropping it from external memory — EXP-010, previously unvalidated) closes the gap, since that would mean the backbone, not just the memory, retains the competence being evicted; (c) whether a policy that protects recently-written entries for a minimum number of steps regardless of apparent mastery helps — though this is expected to only delay, not fix, the mechanism, since mastery legitimately does occur before the risk period begins.

### Follow-up Research
1. **Highest priority, and already in scope as the pre-registered stretch ablation (`docs/11_mvp/ACA-MVP-001.md` §4):** test active consolidation-via-replay at each stage boundary (EXP-010) on this exact task, at the same constrained capacity (60), to isolate whether consolidation — not merely more capacity — rescues Stage-1 retention.
2. Explicitly re-rank `docs/09_validation/IVS-001.md` §6: EXP-010 was ranked lowest (#6 of 7) on the stated grounds that it "does not affect correctness of anything already validated." EXP-018 shows this is no longer accurate — EXP-010 (or an equivalent fix) may be a prerequisite for ME-03 to deliver any benefit at all outside a static distribution, not an optional refinement.
3. A control not yet run: repeat with memory capacity increased to ≥300 (able to hold every fact across all stages) to confirm the naive-cache condition trivially recovers full retention once eviction pressure is removed — a cheap, uninteresting-but-necessary sanity check that the harness itself isn't broken in some other way.
4. Test whether a smaller, non-adversarial stage transition (e.g., partial rehearsal — a small fraction of earlier-stage facts mixed into later stages) changes the picture, to separate "sequential" from "zero rehearsal" as the operative harshness factor.

---

## EXP-010: Consolidation-via-Replay — Does a Stage-Boundary Reinforcement Burst Rescue What EXP-018 Falsified?

**Epistemic Status:** **FALSIFIED** for the specific, minimal operationalization tested here. This closes out EXP-010 as a previously-reserved but unrun roadmap item (`docs/07_future/Roadmap.md`, `docs/09_validation/IVS-001.md` §6) — now run, with a negative result, immediately following EXP-018 in the same research session. **Numbering note:** this entry appears after EXP-018 in this log despite its lower number, because EXP-010's ID was reserved at architecture-design time (before EXP-018 existed) but not actually executed until now, directly motivated by EXP-018's result. Logged in true completion order, not renumbered.

### Objective
EXP-018 found that competence-gated memory (ME-03) provides no measurable protection against catastrophic forgetting under staged, non-rehearsed continual training, because evicting a "mastered" entry treats a point-in-time reading as permanent safety. The most direct candidate fix, already named in this architecture's own roadmap and pre-scoped as `docs/11_mvp/ACA-MVP-001.md` §4's stretch ablation, is consolidation: reinforce a fact into the backbone's own weights before its external memory copy is evicted, so competence survives even after the copy is gone.

### Research Question
Does a stage-boundary replay burst — extra gradient steps on everything currently in memory, run immediately before the eviction pressure of the next stage begins — measurably improve Stage-1 recall after all 3 stages, relative to EXP-018's un-consolidated competence-gated result?

### Hypothesis (stated before running)
Reinforcing stored facts into the backbone via direct gradient steps, independent of whether their external memory copy later gets evicted, should raise Stage-1 param-only accuracy above EXP-018's 0.158 baseline — since the mechanism targets the backbone's own retention, not memory coverage (which was expected to remain near 0, unchanged, since eviction logic itself was deliberately left untouched to isolate consolidation as the only new variable).

### Methodology
Identical model, task, seeds (0–4), and 60-slot memory capacity to EXP-018. One new condition, `consolidated_gated_memory`: at each stage boundary except the last, every entry currently in memory receives 20 extra gradient steps (batch 32, sampled with replacement from whatever is currently stored — up to 60 facts, so roughly 10–11 expected exposures per fact) before the usual entropy-refresh/eviction bookkeeping proceeds. REPLAY_STEPS=20 and REPLAY_BATCH=32 are stated as a reasonable first choice, not tuned, exactly like EXP-001's original threshold constants. Code: `experiments/exp_mvp001_continual_recall/run_consolidation_ablation.py`. Compared directly against EXP-018's already-logged `competence_gated_memory` and `no_memory` numbers (same code path, same seeds, nothing else changed) rather than re-running them.

### Results (mean ± std over 5 seeds)

| Condition | Stage-1 acc (after 3 stages) | Stage-1 memory coverage at eval |
|---|---|---|
| no_memory (EXP-018) | 0.158 ± 0.039 | n/a |
| competence_gated_memory, no consolidation (EXP-018) | 0.158 ± 0.027 | 0.0, every seed |
| **consolidated_gated_memory (this experiment)** | **0.160 ± 0.028** | **0.0, every seed** |

Per-seed Stage-1 param-only accuracy: 0.11, 0.15, 0.19, 0.18, 0.17 — same range and spread as EXP-018's baseline, not a shifted distribution. Full data: `experiments/exp_mvp001_continual_recall/results_consolidation_ablation.json`.

### Conclusion
**Hypothesis falsified.** A 20-step replay burst at each of 2 stage boundaries (40 extra gradient steps total per seed) produced no detectable improvement in Stage-1 retention — 0.160 vs. 0.158 is well within seed-to-seed noise (std ≈ 0.03), not a shifted result. Memory coverage remained exactly 0.0 in every seed, as expected (eviction logic was deliberately unchanged), confirming the test correctly isolated backbone-side reinforcement as the only variable — and that variable, at this dose, did nothing measurable.

**Why, mechanistically, a plausible reason to expect this:** each stage boundary's 40 total replay steps face 800 steps of the *next* stage's unrelated training immediately afterward — a 20x disadvantage in step count, with nothing in the optimizer (plain Adam, no explicit weight-importance protection) anchoring the reinforced weights back toward Stage-1-good regions once that subsequent training begins. A one-time burst, however real the gradient update, is not defended against what comes right after it; ordinary gradient descent on 800 steps of new, disjoint data has no reason to preserve a state it was never continuously pulled back toward.

### What This Does and Doesn't Establish
**Establishes:** the specific, minimal, "one-time burst at the boundary" operationalization of consolidation-via-replay tested here does not rescue ME-03 under staged non-rehearsed training. This narrows, not closes, the space of viable fixes.

**Does not establish:** that consolidation-via-replay as a general strategy cannot work. Two meaningfully different, untested variants remain: (a) **sustained/interleaved rehearsal** — mixing a small amount of old-stage data into *every* training step of the following stage, not just a burst at the boundary, so old competence is continuously defended rather than reinforced once and abandoned; (b) **explicit weight-importance protection** (e.g., EWC/synaptic-intelligence-style penalties keeping parameters estimated important for old facts from moving freely), which changes the optimizer's objective rather than adding extra data exposure. Both are larger, more invasive changes than what this experiment tested, and both are now the most informative next steps — sharper, more specific candidates than "try consolidation" was before this result.

### Follow-up Research
1. **Highest priority:** test interleaved rehearsal (a small fixed fraction of every subsequent-stage batch drawn from currently/recently-stored memory content, not a one-time boundary burst) on this same task — the natural next, sharper hypothesis given this result.
2. Test whether simply scaling up REPLAY_STEPS substantially (e.g., 200 instead of 20) recovers any effect, to check whether this was a dose problem rather than a mechanism problem — cheap to run, worth ruling out explicitly before moving to a larger design change.
3. Test an explicit weight-protection mechanism (EWC-style) as a structurally different candidate, since it targets the optimizer's treatment of "important" parameters directly rather than adding more data exposure.
4. Update `docs/04_architecture/ACA_v1.0_Architecture.md` Section 11/18 and `docs/09_validation/IVS-001.md` Section 9 to record that the "candidate fix" they named is now itself falsified in its simplest form, not merely untested.

---

## EXP-020: ACA-MVP-001 Benchmark B — Structure-Matched COMPOSE vs. Generic Seq2Seq on Real SCAN (addprim_jump)

**Epistemic Status:** **CONFIRMED**, decisively, on a real, standard, cited benchmark — not an in-house toy task. This directly extends EXP-002/003's toy-scale finding (structure-matched constrained computation beats generic computation when the structure is correctly specified) to real published data, with a real published baseline number to compare against. Grammar used by the structure-matched model was verified, not assumed — see "Grammar Verification" below.

### Objective
ACA-MVP-001 (`docs/11_mvp/ACA-MVP-001.md` §3, Benchmark B) committed to testing EXP-002's compositional-generalization claim against the actual SCAN benchmark (Lake & Baroni, 2018) rather than repeating this program's own synthetic 4-operator task at larger scale, specifically because SCAN has small-enough data for a single consumer GPU and published baseline numbers in the literature to compare against.

### Research Question
Does a COMPOSE module built from a fixed, hand-specified compositional grammar (structure-matched, per RC-01/EXP-002) outperform a generic Transformer that must discover the same compositional structure purely from training data, on SCAN's addprim_jump split — the split specifically designed so "jump" is seen only in isolation during training and must be correctly composed with modifiers never seen jointly with it?

### Grammar Verification (done before writing any model, not assumed from a secondary source)
The SCAN grammar was reverse-engineered from real data, not taken on trust from a paper summary. Real, complete `tasks_train_addprim_jump.txt` (14,670 examples) and `tasks_test_addprim_jump.txt` (7,706 examples) were downloaded directly from `github.com/brendenlake/SCAN`. The composition rules (`U`, `U D`, `U opposite D`, `U around D`, `X twice/thrice`, `X and/after Y`, and the special-cased `turn` primitive whose action *is* the direction-change, with no separate action token appended) were derived by hand-tracing real examples, then a self-check script (`scan_common.py`, run standalone) parsed and re-evaluated **all 22,376 real train+test examples** with the resulting interpreter and an oracle primitive mapping: **exact match on every single example, both files, confirmed before any model was trained.** Also confirmed directly against the data: "jump" appears only as the isolated fact "jump → I_JUMP" in training (1467 occurrences, zero composed forms), and no command in either file chains more than one "and"/"after" connective (0 of 22,376).

### Hypothesis (stated before running)
A structure-matched model (fixed parser + interpreter implementing the verified grammar, with only a small classifier mapping each of the 4 non-"turn" primitives to its action token left to learn from data) generalizes correctly to held-out compositions of "jump" with modifiers never seen jointly with it during training. A generic Transformer, lacking this structural knowledge, does not — consistent with Lake & Baroni's own published finding of near-zero exact-match accuracy for vanilla seq2seq models on this exact split.

### Methodology
**Generic baseline:** a real encoder-decoder Transformer (`nn.TransformerEncoder` + `nn.TransformerDecoder`, 2+2 layers, 4 heads, d_model=128, 681,481 parameters), trained end-to-end via teacher forcing, evaluated via greedy autoregressive generation, standard SCAN exact-full-sequence-match accuracy. 25 epochs, batch 128, 5 seeds. Code: `experiments/exp_mvp001_scan_compositional/run_generic_seq2seq.py`.

**Structure-matched model:** the verified fixed grammar (`scan_common.py`) supplies 100% of the compositional structure (turn-token insertion, repetition, and/after ordering) — the interpreter is called with a sentinel function for the 4 learnable primitives (walk/look/run/jump; "turn" is never a learned slot, per the verified grammar), which is expanded into a differentiable logit vector at composition time, so gradients flow through the fixed structural operations into a tiny classifier (embedding(4) → linear(6), 326 parameters). Trained end-to-end on the same real training data and the same cross-entropy loss as the generic baseline — not pre-fit on hand-extracted labels. Every example's compiled slot-list length was asserted equal to its true action-sequence length before training (a correctness self-check). Code: `experiments/exp_mvp001_scan_compositional/run_structure_matched.py`.

Both models trained and evaluated on the identical, real, downloaded addprim_jump split — no synthetic re-creation.

### Results (mean ± std over 5 seeds, exact-sequence-match accuracy on all 7,706 real held-out test examples)

| Model | Parameters | Train acc | Test acc (exact match) |
|---|---|---|---|
| Generic seq2seq Transformer | 681,481 | 0.998 ± 0.001 (subsample) | **0.0071 ± 0.0039** |
| Structure-matched (fixed grammar + learned primitive lookup) | 326 | 1.000 ± 0.000 | **1.0000 ± 0.0000** |

Relative improvement: **~141x**. Parameter reduction: **~2090x fewer parameters, better accuracy.** Full data: `experiments/exp_mvp001_scan_compositional/results_generic_seq2seq.json`, `results_structure_matched.json`.

**Sanity check against the literature:** the generic baseline's 0.71% ± 0.39% is closely consistent with Lake & Baroni (2018)'s own published ~1% for vanilla seq2seq models on this exact split, despite 99.8%+ training accuracy in both — confirming this baseline is a real, literature-consistent result, not an artificially weakened strawman.

### Conclusion
**Pre-registered success criterion (`docs/11_mvp/ACA-MVP-001.md` §5, ≥2x improvement) exceeded overwhelmingly, not marginally.** The structure-matched model's 100.000% is not a lucky fit or a leak — every element of the true grammar was verified against real data before training, the only free parameter is a 4-class lookup extracted from 1467 genuine training exposures of "jump" in isolation (the same mechanism read off `walk`/`look`/`run` from their own many training occurrences), and the fixed composition rules apply that lookup identically to seen and unseen combinations by construction. Given a correctly and fully verified compositional structure, correct generalization to novel compositions follows deterministically — this is the expected, correct behavior of a correctly-matched constrained family, not a surprising result, exactly mirroring EXP-002's own stage-5 finding (100% on true rotations) at real benchmark scale instead of an in-house 40-example task.

### What This Does and Doesn't Establish — the Same Caveat EXP-002 Already Raised, Recurring at Scale
**Establishes:** structure-matched COMPOSE (RC-01), when the structure is correctly and completely specified, generalizes compositionally where a generic Transformer of ~2000x more parameters does not — now demonstrated on a real, standard, cited benchmark with a real published number to compare against, not only on this program's own 40-example synthetic task.

**Does not establish:** how a system would discover or construct the correct grammar without a human hand-specifying it in advance — **the identical unresolved problem EXP-002 flagged as "the central open problem," recurring here at real benchmark scale, not newly introduced.** `docs/11_mvp/ACA-MVP-001.md` §2 explicitly excluded automatic/learned routing (RC-02) from this benchmark for exactly this reason; this result says nothing about that harder question. Also does not establish that hand-specified grammars are commonly available for real-world domains — SCAN's grammar is unusually small and clean; most real compositional domains will not hand this program a fully-verifiable 13-word grammar to exploit.

### Follow-up Research
1. **Unchanged central open problem (still the most important next step, first flagged by EXP-002):** test whether a family-discovery mechanism (EXP-005, still not run) can recover a grammar like SCAN's from data alone, without it being hand-specified — the actual test of whether this result's mechanism could ever operate autonomously.
2. Test on SCAN's other published splits (e.g., `addprim_turn_left`, length generalization, the simple random split as a non-compositional control) to check whether the 141x margin is specific to `addprim_jump` or general across SCAN's splits.
3. Investigate whether the generic Transformer's near-zero accuracy is concentrated on `jump`-composed examples specifically (expected) or spread more broadly (would indicate a training issue unrelated to the compositional generalization question) — not yet checked at the per-example level.
