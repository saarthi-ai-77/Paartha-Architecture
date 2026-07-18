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
