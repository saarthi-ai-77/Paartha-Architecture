**Status: Active — Living Handoff Document, Updated Every Session**

# CTO Context Document — Adaptive Computational Architecture (ACA)

**Read this document first, in full, before touching any other file in this repository.** It is not a summary for casual browsing — it is the operational context a new agent needs to take over active leadership of this research program without re-deriving decisions already made, repeating experiments already run, or violating discipline already established the hard way. If you are an agent being asked to act as CTO / Chief Architect / Chief Experimental Scientist / Chief Systems Engineer (the title has changed as the program matured — see Section 2) for ACA, this document is written for you specifically.

This document is different from every other document in this repository in one respect: **it is meant to be updated at the end of every session**, not written once and left append-only-forever like `docs/06_experiments/Completed.md` or `docs/05_research/Decisions.md`. Section 8 explains exactly how. Do not skip that.

---

## 1. What ACA Is, in One Paragraph

ACA is a long-running research program investigating whether intelligence should be built from one universal computational mechanism (the Transformer, scaled) or from multiple, fundamentally different computational mechanisms, dynamically selected according to the nature of the problem. The real, underlying motivation is engineering efficiency, not philosophy for its own sake — see `docs/02_vision/` and the "Additional CTO Context" material referenced in `docs/05_research/Decisions.md`. The program has moved through several methodologies (council-driven derivation, then build-experiment-validate-iterate, then a formal Evidence-Driven Evolution gate on architectural change) — each shift is a numbered Decision (DEC-NNN) in `docs/05_research/Decisions.md`, preserved permanently, never silently overwritten.

## 2. Your Role, and Why It Keeps Changing

The acting role has changed several times as the program matured, always announced explicitly as a directive, never assumed:

- **Chief Architect** — while research was producing requirements and architecture (ARS-001, ACA v1.0).
- **Chief Experimental Scientist** — once architecture work stopped producing new evidence and the mandate shifted to actual implementation (ACA-MVP-001): "the goal is no longer to extend ACA on paper."
- **Chief Systems Engineer** — once the MVP benchmark sequence completed and the mandate shifted to integration (SIP-001): "the question is no longer 'what should ACA contain' but 'can the validated architecture operate as one coherent system.'"

**As of the most recent directive, the operative constraint is DEC-006 ("Evidence-Driven Evolution")** — regardless of which title you are given, this rule is currently binding: no new computational function, state substrate, or architectural module may be proposed from conceptual reasoning alone. It must first pass, in order: (1) a reproducible runtime observation, (2) isolation of the responsible variable, (3) a dedicated falsification experiment, (4) demonstration that the current validated architecture cannot explain or accommodate the result. Read `docs/05_research/Decisions.md` (DEC-006) and `docs/14_integration/SIP-001.md` Section 18 before proposing anything architectural.

**If you are given a new role/phase directive, update Section 2 of this document accordingly** (append, don't delete the history of prior roles — they explain why later decisions were made).

## 3. Non-Negotiable Discipline (Learned the Hard Way, Do Not Relitigate)

- **Epistemic tagging on every claim, always:** Validated (by ACA's own experiments) / Supported by external literature / Reasoned hypothesis / Speculative. Never state a conclusion without one of these tags. A prior agent violated this once (a council response tagged its own conclusions "Validated Council Decision" when they were not) and it was caught and corrected explicitly — don't repeat it.
- **Never delete history. Archive or supersede, with an explicit pointer note, in place.** `docs/archive/` exists for this. Superseded documents (e.g. `docs/04_architecture/ACA_v0.4_Architecture.md`) remain in the repository, marked superseded, not removed.
- **Append, don't edit in place.** Every major spec document (ARS-001, ACA v1.0, IVS-001, DAS-001, ACA-MVP-001, CTX-001, SOS-001, SIP-001) has a stated revision policy: new findings are appended as new numbered sections or new table rows, never rewritten into prior text. Follow this exactly, including in this document's own Section 8.
- **Negative results are first-class, not failures to hide.** Roughly half of this program's most important findings are falsifications (EXP-002's original hypothesis, EXP-009's unified-EVALUATE hypothesis, EXP-018/010's memory mechanism, EXP-019's proposed new substrate). Report them as prominently as positive results, with the mechanism, not just "it didn't work."
- **Quarantine stays quarantined.** `council/main/` contains a thread with unrecoverable provenance (references artifacts — "RP-003," a "subsumption decision," a "GTC" mechanism — that do not exist anywhere in this repository). Do not treat it as active research, do not integrate it, do not delete it. See `docs/03_foundations/OPEN.md`'s "Quarantined" note.
- **Don't average a negative and a positive result together into a vague verdict.** ACA-MVP-001's own discipline: memory (negative) and compose (positive) are reported as exactly what they are, separately — never smoothed into "ACA is doing okay overall."
- **A fixed hyperparameter is not a validated, general-purpose signal.** This caveat (first stated in `docs/08_requirements/ARS-001.md` for SR-01's confidence threshold) has now been concretely confirmed by SIP-001's integration test — don't assume any threshold/gate tuned for one regime transfers to another without checking.

## 4. How This Repository Is Organized

- `README.md` — the technical/scientific index, with a numbered "Reading Order for New Researchers." Read it second, after this document.
- `docs/01_background/HISTORY.md` — chronological narrative, phase by phase.
- `docs/02_vision/`, `docs/03_foundations/` — mission and categorized findings (`ACCEPTED.md`, `REJECTED.md`, `OPEN.md` — **`OPEN.md` is the single best "what's unresolved right now" file**).
- `docs/04_architecture/ACA_v1.0_Architecture.md` — the current architecture, fully traced (Component → Function → Requirement → Evidence), with appended correction sections (11, 17, 18, 19...) recording every real-scale/integration finding since synthesis.
- `docs/05_research/Decisions.md` — **the methodology decision log. Read every DEC entry.** This is not optional background; DEC-005 and DEC-006 are binding constraints on how you are allowed to work.
- `docs/06_experiments/Completed.md` — **the ground truth experimental record.** Every EXP-NNN, in the format Objective/Hypothesis-stated-in-advance/Methodology/Results/Conclusion/Follow-up. If you are unsure whether something has already been tried, check here before running anything.
- `docs/07_future/Roadmap.md` — current priorities, blast-radius-ranked, updated after every major result.
- `docs/08_requirements/` through `docs/14_integration/` — one new numbered subdirectory per major deliverable type, in the order they were produced (Requirements → Architecture is `04_`, then Validation, Deployment, MVP, Cognition/state-model investigations, State Ownership, System Integration). Each contains one or more `XXX-NNN.md` documents (ARS-001, IVS-001, DAS-001, ACA-MVP-001, CTX-001, SOS-001, SIP-001).
- `experiments/` — one directory per experiment, each self-contained (code + results.json), not importing across directories, by convention.
- `runtime/` — actual executable system code (distinct from `experiments/`), currently `runtime/sip001/`, the first real end-to-end ACA runtime.
- `council/` — the original council-driven methodology, retained only as a secondary diagnostic tool (DEC-005), not the primary discovery method. `council/main/` is quarantined (see Section 3).

## 5. Current State Snapshot (Accurate As Of the Last Session Log Entry Below — Check Section 8 First)

This section gives orientation; **Section 8's most recent entry is the actual source of truth for "what just happened."**

- **Architecture (`docs/04_architecture/ACA_v1.0_Architecture.md`):** three state substrates (S_episodic, S_semantic, S_invariants — not four; a fourth was proposed and falsified, see CTX-001/EXP-019 below), four computational functions (EVALUATE — split into LOCAL/GENERALIZATION/STRUCTURAL — SELECT, UPDATE, COMPOSE).
- **Validated:** competence-gated memory allocation *under a static distribution* (EXP-001); structure-matched COMPOSE, now confirmed at real published-benchmark scale, not just toy scale (EXP-002, EXP-020 — 100.000% vs. a real Transformer's ~0.71%, ~141x); validation-driven family selection (EXP-003); disjoint-parameter composability, toy and real scale (EXP-004, EXP-021); EVALUATE-LOCAL via entropy (EXP-009).
- **Falsified:** competence-gated memory under *staged, non-rehearsed* continual training — provides zero measurable benefit (EXP-018); the obvious fix, one-time consolidation replay (EXP-010); label-free EVALUATE-GENERALIZATION (EXP-009); a proposed fourth state substrate, "S_working," for conversation/reasoning context — a disciplined reserved partition within the existing S_episodic mechanism performs identically (EXP-019).
- **Open, unresolved, actively flagged:** EXP-005 (can a system discover a compositional grammar rather than have it hand-verified? — the central open problem since EXP-002, unchanged by EXP-020's success); whether ME-03 survives staged continual training under a larger fix (interleaved rehearsal, EWC-style weight protection — untested); IVS-001's Stage 3/4 minimal integrated prototype (still not executed in its originally-scoped form); **SIP-001's single-exposure-teaching finding** (a real integration runtime returned "I do not know" for every fact taught exactly once, traced to entropy never dropping below a fixed threshold without repeated exposure — confirmed via a same-code control, not a bug; this is the first case queued under DEC-006's four-step gate, with steps 1-2 done and steps 3-4 explicitly not yet undertaken).
- **Methodology currently in force:** DEC-005 (build-experiment-validate-iterate) + DEC-006 (Evidence-Driven Evolution's four-step gate on any new architecture).

## 6. How to Pick Up Work

1. Read Section 8 (below) for the most recent session's log entry — what was done, what's queued.
2. Cross-check `docs/07_future/Roadmap.md` and `docs/03_foundations/OPEN.md` for the current priority ranking.
3. If picking up a queued item (e.g. SIP-001's single-exposure-teaching finding), follow DEC-006's four-step gate in order — do not skip to "propose a fix."
4. If starting genuinely new investigation, check `docs/06_experiments/Completed.md` first to confirm it hasn't already been tried and found wanting.
5. Follow the existing per-document conventions exactly (epistemic tagging, append-not-edit, footer format: Purpose/Current Status/Historical Context/Known Facts/Hypotheses/Unknowns/References) — consistency across dozens of documents is itself part of this program's credibility.

## 7. Committing and Pushing

This is a real git repository with a real remote (`github.com/saarthi-ai-77/Paartha-Architecture`). Commit real, complete units of work (spec + code + results + write-up together, not code without its results or a claim without its evidence). Push after committing unless told otherwise. Write commit messages that explain *why*, not just *what* — this repo's own commit history is part of its institutional memory.

## 8. Session Log — **Update This Every Session** (Newest Entry First)

**Why newest-first, unlike this repo's other append-only logs (`Completed.md`, `Decisions.md`, which are chronological/oldest-first):** this section exists specifically so a new agent can read the top entry and immediately know "what just happened, what's queued" without scrolling a long history. The other logs are permanent scientific records where chronological order matters for tracing dependency; this one is an operational handoff note where recency matters most. Older entries are preserved below, not deleted — this document follows the same never-delete discipline as everything else, just with the newest-first ordering for usability.

**When you finish a session, add a new entry at the top of this list** (above the most recent one, below this instruction), in this format:

```
### [YYYY-MM-DD] — [your role/title] — [one-line summary]
**Did:** what you actually did this session, concretely.
**Found:** any real result (positive or negative), with the actual numbers/mechanism, not just "it worked" or "it didn't."
**Changed:** which files/docs you created or modified.
**Queued:** what should happen next, and under what discipline (e.g., "next per DEC-006 step 3: ...").
**Committed:** the commit hash(es), if pushed.
```

---

### [2026-07-23] — Chief Systems Engineer — SIP-001 built and run; DEC-006 adopted; this document created
**Did:** Built and ran the first actual executable ACA runtime (`runtime/sip001/`) per SIP-001, combining the recall pathway (ME-03), EVALUATE-LOCAL (SR-01), and the compose pathway (RC-01) behind one traced request pipeline, with every component classified as validated/known-limited/explicit-stub. Ran a real integration scenario (80 episodes). Recorded DEC-006 ("Evidence-Driven Evolution") as a new standing methodology rule. Created this context document per explicit request, to support handoff to future agents/sessions.
**Found:** Compose pathway re-confirmed 100% exact-match (third confirmation, after EXP-020/EXP-021) — no new finding. Recall pathway returned "I do not know" for every single fact query, including facts taught seconds earlier — traced (not assumed) to entropy readings clustered in a narrow 3.7-4.2 nat band, never near the fixed 1.5-nat confidence threshold, because each fact received only one gradient step in this scenario. A same-code control with 30 repeated exposures per fact recovered 100% accuracy entirely through backbone confidence, confirming this is a genuine, previously-untested Architectural Limitation (single-exposure teaching — no prior experiment, including EXP-001/018/010, ever tested this; all used repeated-exposure batch training), not a runtime defect.
**Changed:** Created `docs/14_integration/SIP-001.md`, `runtime/sip001/*.py`, `runtime/sip001/episodes*.jsonl`, `runtime/sip001/integration_test_summary.json`. Appended Section 19 to `docs/04_architecture/ACA_v1.0_Architecture.md` and Section 11 to `docs/09_validation/IVS-001.md`. Recorded DEC-006 in `docs/05_research/Decisions.md`, cross-referenced into `README.md`, `RESEARCH_PHILOSOPHY.md` (Third Philosophical Shift), `docs/01_background/HISTORY.md` (Phase 6), `docs/03_foundations/OPEN.md`. Created this document, `docs/00_orientation/CTO_CONTEXT.md`.
**Queued:** SIP-001's single-exposure-teaching finding sits in DEC-006's pipeline with steps 1-2 (observation, isolation) done. Step 3 (a dedicated falsification experiment testing whether an exposure-count-aware gating rule resolves it) and step 4 (demonstrating the current architecture cannot accommodate the result) are explicitly not yet undertaken — do not invent a fix without them. Also open: EXP-005 (family discovery), ME-03's continual-learning replacement, whether write-starvation (EXP-019) recurs for the routing/self-model schemas or under real capacity pressure on the episode schema (SIP-001's test never filled memory to capacity), IVS-001's Stage 3/4 minimal integrated prototype (still unexecuted in its originally-scoped form, distinct from SIP-001's differently-shaped runtime).
**Committed:** `93ceb03` (SIP-001 + runtime), `f07b159` (DEC-006).

---

**Purpose:** Give any agent — a fresh instance, a different model, a different session — everything needed to act as ACA's CTO/Chief Architect/Chief Experimental Scientist/Chief Systems Engineer (whichever title is current) without re-deriving history or violating established discipline. Updated every session, not written once.
**Current Status:** Active — living document, updated 2026-07-23.
**Historical Context:** Created 2026-07-23 per explicit request to support multi-agent, multi-session continuity on ACA research.
**Known Facts:** Section 5 (snapshot) and Section 8 (log) are the current source of truth; everything else in this document is stable orientation content that changes rarely.
**Hypotheses:** N/A — this document records state and process, not scientific claims.
**Unknowns:** N/A.
**References:** `README.md`, `docs/05_research/Decisions.md`, `docs/03_foundations/OPEN.md`, `docs/07_future/Roadmap.md`, `docs/06_experiments/Completed.md`
