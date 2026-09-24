**Status: Active**

# Research Log

## Chronological Timeline

### Phase 1: The Design Model Initiative
* **Event:** Project inception.
* **Focus:** Attempting to invent a fundamentally new foundation model for design generation (specifically web design).
* **Outcome:** Encountered structural limitations in representation. Led to the development of the Council methodology for rigorous review.

### Phase 2: The CCA v0.1 Pipeline
* **Event:** Formulation of the Cognitive Computational Architecture (CCA v0.1).
* **Focus:** Establishing a rigid pipeline of cognitive functions (Observation -> Difference -> Pattern -> Concept -> etc.).
* **Outcome:** Realization that a static pipeline, while conceptually sound, fails to adapt to diverse problem structures.

### Phase 3: The Adaptive Pivot
* **Event:** Council decision to broaden the research objective beyond design and beyond static pipelines.
* **Focus:** Investigating whether intelligence requires fundamentally different computational mechanisms dynamically selected according to the nature of the problem.
* **Outcome:** Current research state. Web design relegated to an evaluation domain.

### Phase 4: Domain-Oriented Council Hierarchy
* **Event:** Refactoring of the research repository into specialized domain councils.
* **Focus:** Allowing independent research domains to evolve autonomously. Initial sprint focused on the Knowledge Foundation Council to discover the computational nature of knowledge before resuming architecture work.
* **Outcome:** The Main Council assumes oversight of mature theories, while specialized councils take over localized domains. Ran Knowledge Foundation Council Sprints 1 through 3A; produced a refined validation methodology but no validated primitive and no empirical contact with data (see DEC-005).

### Phase 5: Build-Experiment-Validate-Iterate (Current)
* **Event:** DEC-005 — pivot from council-driven first-principles derivation to empirical, code-based experimentation.
* **Focus:** Propose a small, concrete, trainable architectural mechanism; implement and test it against an honest baseline with multiple seeds; report the result — including outright falsification — before generalizing anything. Council system retained only as a diagnostic tool for root-causing experiment failures.
* **Outcome so far:** EXP-001 (surprise-gated episodic memory allocation) confirmed. EXP-002 (compositional rule module) falsified in its original form across three attempts, then confirmed in a much narrower, mechanistically-understood form (constrain the operator to the true symmetry family), with a clearly identified open problem (automatic family discovery). EXP-003 (automatic family selection) confirmed that selection must be driven by held-out generalization, not training loss, falsifying two naive alternatives in the process. Next: EXP-004, an integration test combining the validated memory and rule-module mechanisms. See `docs/06_experiments/Completed.md`.
* **2026-09-22 (GDR Cognitive Sprint):** Formulated Goal-Directed Reasoning (GDR-001). Adversarially audited and dismantled premature 7-faculty taxonomy and static PCE (GDR-002). Formulated and empirically evaluated Closed-Loop Discrepancy Reduction vs. Search in EXP-CCS-0 (GDR-003): falsified pure myopic discrepancy reduction due to deceptive local minima and epistemic blindness; confirmed heuristic tree search over isolated primitives with state rollback (SET-CR) achieves 100% composition success and runtime fault recovery.
* **2026-09-24 (Substrate Archaeology & Capability Ladder — CTX-002):** Conducted rigorous archaeological recovery of Paartha's research on state, context, memory, weights, and inference (`docs/12_cognition/CTX-002.md`). Established the Option B 7-stage progressive capability ladder ($\text{Speak} \to \text{Understand} \to \text{Brainstorm} \to \text{Plan} \to \text{Code} \to \text{Act} \to \text{General}$). Re-grounded architecture on verified three-tier state ($S_{semantic}, S_{episodic}, S_{invariants}$) and the reserved working-state partition (`WorkingStateStore`), formalizing Paartha's functional equivalents of weights, context window, KV cache, and inference. Identified the critical unsolved gap for Stage 1: lightweight natural-language ingress grounding and proof-trace surface realization.
* **2026-09-24 (JEv Study & Calibrated Decision Substrate — JEV-001):** Investigated TypeSafe AI's Jev model (System 1 non-autoregressive decision model trained via RLCD). Recovered earlier Paartha formulations of amortized risk prediction ($g_\phi(e, c) \to (\mu_c, \sigma_c)$) and routing regret, connecting them to EXP-003 and EXP-009. Determined that a calibrated decision substrate serves as Paartha's System 1 engine (Option E: front-door speech act routing, SET-CR search branch heuristics, and semantic verification) cleanly separated from System 2 deliberative search and surface realization. Formulated the minimal validating experiment (EXP-JEV-0) for Stage 1. See `docs/12_cognition/JEV-001.md`.
* **2026-09-24 (Paartha Computational Architecture Specification — PAARTHA-ARCH-001):** Derived the formal computational architecture for Stage 1 (Speak) capable of scaling across the entire 7-stage capability ladder. Formalized the 6-step universal computational primitive ($\text{Perceive} \to \text{Resolve} \to \text{Decide} \to \text{Transform} \to \text{Verify} \to \text{Update}$). Defined state formally as $\mathcal{S} = \langle \Theta, \mathcal{L}, \mathcal{K}, S_{episodic}, S_{working}, s^{hist}, S_{decision} \rangle$, inference as discrete state transitions with sandboxed rollback, and three-tier parameter allocation ($\le 1.2\text{B}$ shared weights + modular $\mathcal{L}$ + zero-parameter invariants). Designed the falsification trial EXP-SPEAK-0. See `docs/12_cognition/PAARTHA-ARCH-001.md`.
* **2026-09-24 (Competence Acquisition & Non-End-to-End Learning Trial — EXP-032):** Empirically investigated whether a system of learned/frozen representations, explicit executable capabilities, proposal-guided search, and independent verification can acquire reusable competence without end-to-end gradient updates across its neural substrate. Built minimal executable trial (`experiments/exp032_competence_accumulation/run.py`). Results: (1) Proposal-guided search reduced node exploration by 5.57x and execution count by 19.46x over uninformed BFS ($b^*$ dropped from 4.27 to 2.14); (2) Verified macro abstraction passed all 4 levels of generalization (exact, parameter, structural, compositional); (3) Longitudinal accumulation accelerated deep task search by 5.37x via subroutine reuse; (4) Counterfactual ablation achieved 100% root-cause failure attribution across 6 independent error types without backpropagation; (5) Library bloat collapsed Recall@3 to 0.000, which deduplication compression restored to 0.667; (6) Teacher distillation under an independent verification firewall successfully accepted sound procedures while rejecting hallucinated tools and semantic bugs. Proved that intelligence changes via topological growth of the verified capability library $\mathcal{L}$, while the neural substrate remains fixed ($\Delta \Theta = 0$). See `docs/12_cognition/PAARTHA-COMPETENCE-001.md`.


---

**Purpose:** Provide a high-level chronological timeline of major research phases.
**Current Status:** Active
**Historical Context:** Covers project inception to present day.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `docs/01_background/HISTORY.md`

