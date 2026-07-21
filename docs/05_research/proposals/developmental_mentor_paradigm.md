**Status: Evaluated — Requires Prerequisite Research** (not an accepted ACA direction)

# Research Proposal Evaluation: Developmental / Mentor-Society Training Paradigm

**Date:** 2026-07-18
**Evaluated by:** CTO role, against the build-experiment-validate methodology (DEC-005), with literature verification via web search rather than recall alone.
**Epistemic status of this document:** This is a **Provisional Assessment** — a scientific evaluation of a proposed research direction, not a validated ACA finding. Nothing in this document is a Working Hypothesis of ACA's own until (and unless) the experimental roadmap below is actually run.

---

## 1. The Proposal, As Submitted

Instead of building capability primarily through massive-scale pretraining (next-token prediction over internet-scale data, followed by instruction tuning/alignment), an architecture could acquire its capability primarily through a developmental process: an "Innate Architecture" with little domain knowledge but mechanisms for learning, educated via a "Mentor Society" of AI teacher systems that explain, question, correct, adapt difficulty, and progressively fade assistance — with the explicit goal of producing independent reasoning capability (mentors becoming unnecessary after "graduation"), and an open question about what computational artifact should actually be deployed if not frozen weights.

Full original proposal text is preserved in the conversational record that produced this evaluation; it is not restated here in full to avoid duplicating content, per the repository's "one canonical source" rule — this file is the canonical, structured evaluation.

## 2. Scientific Background

The proposal separates into two claims with very different evidentiary status:

- **Claim A (mechanism-level):** an adaptive, feedback-giving "teacher" process (progressive difficulty, explanation, correction, fading assistance) produces better or more compute-efficient capability than static imitation on a fixed corpus.
- **Claim B (framing-level):** the deployment artifact need not be frozen weights; "what graduates" is an open architectural question.

Claim A is **not speculative** — components of it are already implemented and measured in the literature (see below). Claim B is a **live, currently-unsettled research question** with real recent work, though this proposal's specific connection of it to a developmental-training framing was not found elsewhere.

## 3. Comparison with Existing Literature

| Prior work | Relationship to this proposal |
|---|---|
| **YODA — Teacher-Student Progressive Learning for Language Models** (arXiv 2401.15670, Jan 2024) | **Closest mechanism-level match.** A teacher agent gives basic examples, generalizes them, poses progressively harder questions, gives feedback; student refines answers. This is an implemented, published, measured version of nearly every "Mentor Society" behavior in the proposal (explanation, correction, adapting difficulty). Measured gains: +17.01% GSM8K, +9.98% MATH over standard SFT on LLaMA2. |
| **"From Model Training to Model Raising"** (arXiv 2511.09287, Nov 2025; also *Communications of the ACM*) | **Closest framing-level match.** Explicitly argues for replacing "train then align" with a developmental process where capability and values grow together from the start, via scaffolded, socially-framed training data. Does not center a live, multi-turn, adaptive mentor-in-the-loop process, and does not address the deployment-artifact question. |
| **Machine Teaching** (Zhu, AAAI 2015 and follow-ups) | Formal academic home for "design an optimal teaching sequence for a target learner." Real theoretical results exist (teaching dimension smaller than sample complexity) but only for simple model classes (ridge regression, SVM, logistic regression) — never validated at open-ended-reasoning, foundation-model scale. |
| **Curriculum Learning at LLM-pretraining scale** (active 2025–2026 research; e.g. arXiv 2506.11300) | Measured, real efficiency gains (18–45% fewer training steps to reach baseline performance across a 200+ model study up to 100B tokens), but the field's consistent finding is that curriculum learning *complements*, not *replaces*, pretraining. |
| **Developmental robotics** (Oudeyer, Cangelosi, and the broader intrinsic-motivation/curriculum-learning-for-robots literature) | Closest field-level parallel to the "Innate Architecture → Progressive Development" pipeline. The field's own accumulated finding: intrinsic-motivation/curriculum mechanisms alone are consistently found *insufficient* without embodiment, task-space structure, and social guidance working together. |
| **RLHF / RLAIF / Constitutional AI** | Already implements "evaluating answers, providing corrections" via a critic/reward model, not raw label-matching — already standard in frontier post-training. The proposal's description of current models ("pretraining then light instruction tuning") is somewhat dated; it understates how developmental modern post-training pipelines already are. |
| **Fast weights / test-time training / weight-space meta-learning** (e.g. arXiv 2310.13807, arXiv 2603.10090) | The active research space for Claim B. Confirms the deployment-artifact question is real and current, but not new, and not previously connected to a developmental-training framing in what was found. |
| **Cognitive architectures** (Soar, ACT-R) | The proposal's core hypothesis — separate the capacity to learn from the knowledge acquired — is the founding premise of this research tradition since the 1980s. Oldest idea on this list, not the newest. |

## 4. Novelty Assessment

| Component | Status |
|---|---|
| Separating learning capacity from acquired knowledge | Not novel — founding premise of cognitive architecture research |
| Progressive difficulty, feedback, fading assistance as a training signal | Not novel, already implemented and measured (YODA, 2024) |
| Reframing the whole training paradigm as developmental/social rather than corpus-scale | Not novel as framing, very recent — "Model Raising" (Nov 2025) makes nearly this exact argument |
| Optimal-teaching theory for a target learner | Not novel (Machine Teaching, 2015–present); never validated at this scale |
| What computational artifact should deploy, if not frozen weights | Genuinely open, actively worked on elsewhere (fast weights, test-time training); not novel as a question, not answered, not previously connected to a developmental framing in what was found |
| **A multi-role "mentor society" (differentiated teacher functions, not one static teacher) as the *primary* route to build foundation-model-scale reasoning, with an explicit, tested graduation/independence criterion** | **The one configuration not found already published.** This is the actual candidate novel contribution, if any exists. |

**Conclusion:** if framed as "developmental AI training" in general, this is not novel — it should engage YODA and Model Raising directly, or risk presenting known work as new. If framed narrowly as "does a *multi-role* mentor society outperform *single-teacher* progressive learning (YODA) with an explicit, rigorously tested independence criterion," that is a legitimate, narrow, currently-untested question.

## 5. Potential Architectural Implications

The strongest internal connection is to **EXP-003** (`docs/06_experiments/Completed.md`): structure/family selection must be driven by a held-out validation-style signal, not training loss, or it reliably collapses toward the wrong answer. A mentor's evaluative feedback is structurally the same kind of signal — external, generalization-oriented judgment rather than raw loss — applied at the level of overall training signal rather than component selection. This is the honest theoretical hook, if this is pursued: not "AI should learn like children," but "EXP-003's already-validated principle generalizes to the training-signal level, and a mentor is one way to manufacture that signal at scale."

The deployment/graduation question connects directly to the still-open `docs/04_architecture/Dynamic_Computation.md` and `Scheduler.md` questions.

## 6. Risks and Weaknesses

1. **Circularity, not addressed in the original proposal:** mentors must already be highly capable to teach well — where does that capability come from, if not large-scale pretraining? As posed, this likely relocates pretraining to the mentor-construction stage rather than eliminating it. The defensible version is narrower: does mentor-guided training on top of a modest pretrained base beat continuing to scale raw pretraining, per unit of compute — not "skip pretraining entirely."
2. **Unmeasured compute cost:** multi-turn, adaptive, evaluative mentoring is plausibly far more expensive per training example than a static batch. The efficiency claim needs direct FLOPs-per-capability-gained measurement against a curriculum-learning baseline, not an assumption.
3. **"Independence" is unfalsifiable without a rigorous graduation test** — without one, this collapses into distillation with extra steps.
4. **The proposal's framing of current training as pretraining-plus-light-instruction-tuning is dated** given how developmental modern RLHF/RLAIF pipelines already are; this needs correcting before any comparison to "current methods" is fair.

## 7. Experimental Roadmap

**EXP-008 (proposed, not yet run): Multi-Role Mentor Society vs. Single-Teacher Progressive Learning.** Reusing the EXP-002/003 rule-family task and infrastructure: train a small model via (a) standard supervised training on the same data, (b) YODA-style single-teacher progressive curriculum, (c) multi-role mentor society (separate explain/question/correct/fade roles). Compare sample efficiency to reach the *same held-out generalization* EXP-002 already validated, and separately measure total compute cost including mentor inference. This targets the proposal's actual candidate-novel claim (multi-role vs. single-teacher) rather than re-proving YODA's already-published result.

## 8. Recommendation

**Requires prerequisite research.** Not Reject (real theoretical grounding exists: Machine Teaching, curriculum learning's measured gains, EXP-003's resonance; a cheap, concrete, falsifiable first experiment is available). Not Integrate (no evidence yet exists for the specific configuration — multi-role, primary-route, explicit graduation test — that would distinguish this from already-published work). Not Archive (a genuinely cheap first experiment exists, unlike the quarantined `council/main` material).

**Prerequisites before this becomes an official ACA research program:**
1. Explicitly cite and distinguish from YODA and Model Raising in any future framing — presenting this as generally novel would be inaccurate.
2. Run EXP-008 to test the actual novel claim (multi-role vs. single-teacher), not re-validate what YODA already showed.
3. Directly confront the mentor-capability circularity question before describing this as an alternative to pretraining rather than a post/mid-training refinement.

---

**Purpose:** Record of a formal CTO scientific evaluation of an external research proposal, for future reference and to prevent re-litigating the same literature search.
**Current Status:** Evaluated; not an accepted ACA direction; EXP-008 not yet run.
**Historical Context:** Proposed during architectural discussion 2026-07-18, evaluated the same day per the DEC-005 build-experiment-validate discipline.
**Known Facts:** See literature comparison table above; all citations verified via web search at evaluation time, not recalled from memory alone.
**Hypotheses:** EXP-008 as specified in section 7, not yet executed.
**Unknowns:** Whether a multi-role mentor society outperforms YODA-style single-teacher progressive learning; actual compute cost of mentor-in-the-loop training; how to construct a rigorous graduation/independence test.
**References:** `docs/06_experiments/Completed.md` (EXP-002, EXP-003), `docs/04_architecture/Dynamic_Computation.md`, `docs/05_research/Literature_Review.md`, `docs/07_future/Roadmap.md`
