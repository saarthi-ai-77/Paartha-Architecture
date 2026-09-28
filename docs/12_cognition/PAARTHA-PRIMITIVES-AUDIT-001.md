# PAARTHA-PRIMITIVES-AUDIT-001: Adversarial Audit & Redesign of Autonomous Primitive Formation

**Author:** Antigravity AI & Paartha Research Team  
**Date:** September 2026  
**Status:** Adversarial Falsification Audit & Architectural Redesign  
**Target Document:** `docs/12_cognition/PAARTHA-PRIMITIVES-AUDIT-001.md`  
**Target of Audit:** [`docs/12_cognition/PAARTHA-PRIMITIVES-001.md`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-PRIMITIVES-001.md)  
**Historical Context:** [`PAARTHA-RESET-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-RESET-001.md), [`TRANSFER-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-ABSTRACTION-TRANSFER-001.md), [`ABLATION-001`](file:///d:/Paartha/adaptive-computational-architecture/docs/12_cognition/PAARTHA-MECHANISM-ABLATION-001.md)

---

## 1. Executive Summary of the Audit

`PAARTHA-PRIMITIVES-001` proposed that an AI system could start with an irreducible seed substrate and autonomously form reusable, typed 5-tuple primitives ($\pi = \langle \text{Id}, \mathcal{T}, \mathbf{w}_{\text{anchor}}, \mathcal{A}, \Phi \rangle$) via residual buffering, HDBSCAN clustering, symbolic regression, SMT invariant hardening, and MDL filtering.

This document executes an **uncompromising adversarial audit** of that proposal. 

### The Verdict of the Audit:
`PAARTHA-PRIMITIVES-001` in its original form **fails on four fatal theoretical circularities and two empirical design flaws**:
1. **The Point-Anchor Fallacy:** A static vector centroid $\mathbf{w}_{\text{anchor}} \in \mathbb{R}^d$ cannot represent a conditional state transition rule. Residuals form continuous dynamic manifolds, not Euclidean point clusters.
2. **The Cold-Start Routing Paradox:** The system cannot evaluate the predictive MDL gain of a candidate primitive using a learned router before that router has been trained to invoke it, creating an impossible chicken-and-egg optimization deadlock.
3. **The Neuro-Symbolic Handwave:** Invoking unconstrained symbolic regression and Z3 invariant synthesis as an "offline sleep phase" hides an NP-hard combinatorial explosion behind an innocent flowchart box, while remaining hyper-fragile to continuous sensor noise.
4. **The Perceptual Bottleneck & Latent Unobservability:** In the proposed `PhysWorld-Genesis` benchmark, mass is unobservable from instantaneous frames. The proposal conflates *primitive formation* with *partially observable state estimation (POMDP filtering)*.
5. **Brittle Seed Operators:** `OBJECT_PERSISTENCE` as nearest-neighbor tracking collapses during multi-object interactions, crossing trajectories, and fluid domains.

**What survives is the core intuition:** Modular dynamical specialization over structured predictive residuals prevents catastrophic gradient interference across discontinuous regimes and provides verified computational shortcuts.

This document dismantles the flawed components and redesigns **only the surviving core** into a mathematically rigorous, implementable specification: **The Bifurcation-Gated Modular Architecture (BGMA)** and the observable **PhaseWorld-001** benchmark.

---

## 2. Point-by-Point Adversarial Deconstruction

```
                               THE FALSIFICATION MATRIX
┌───────────────────────────────────────┬─────────────────────────────────────────────────────────────────┐
│ Original Component                    │ Fatal Flaw / Circularity Identified                             │
├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ 1. Claimed Novelty vs Prior Art       │ Theoretical Frankenstein: Combines the noise fragility of       │
│                                       │ clustering with the exponential search blowup of DreamCoder.    │
├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ 2. 5-Tuple Primitive Definition       │ The Point-Anchor Fallacy: Conflates trigger conditions (domain) │
│                                       │ with dynamic effects (codomain); point prototype cannot model   │
│                                       │ continuous functional relations.                                │
├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ 3. 5 Seed Meta-Operators              │ • OBJECT_PERSISTENCE assumes nearest-neighbor identity tracking.│
│                                       │ • RELATIONAL_BINDING uses an undefined random MLP ϕ_R.          │
│                                       │ • RESIDUAL_MONITOR drifts as encoder weights update.            │
├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ 4. Residual → HDBSCAN → MDL Pipeline │ • The Cold-Start Routing Paradox: Router cannot route to an     │
│                                       │   unregistered primitive to evaluate ΔL_pred.                   │
│                                       │ • HDBSCAN averages out the dynamic variation in residuals.      │
│                                       │ • Symbolic regression & Z3 invariant synthesis are intractable  │
│                                       │   over noisy continuous clusters.                               │
├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ 5. PhysWorld-Genesis Benchmark        │ Mass is unobservable from a single frame (POMDP). Conflates     │
│                                       │ primitive formation with recurrent latent state estimation.     │
└───────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘
```

---

### Attack 1: Falsification of Claimed Distinctions from Prior Art

`PAARTHA-PRIMITIVES-001` claimed fundamental differentiation from Slot Attention, DreamCoder, and Mixture of Experts:
* **The Claim against DreamCoder:** DreamCoder requires a hand-crafted discrete DSL; Paartha anchors in continuous space.
* **The Reality:** In Section 07, `PAARTHA-PRIMITIVES-001` specifies that affordances $\mathcal{A}$ are discovered via *symbolic regression / neural program synthesis*, and invariants $\Phi$ are extracted via an *SMT solver*. This is literally DreamCoder executed on top of noisy continuous clusters! It inherits the exact same combinatorial AST search blowup while adding the instability of unsupervised clustering.
* **The Claim against Mixture of Experts (MoE) & Recurrent Independent Mechanisms (RIMs):** Paartha claims MoE lacks typed affordances and invariant firewalls.
* **The Reality:** Modern modular architectures (e.g. Goyal et al., *Recurrent Independent Mechanisms*, 2021; Mittal et al., *Modular Continual Learning*, 2022) explicitly specialize neural modules on distinct physical regimes using competitive attention. `PAARTHA-PRIMITIVES-001` merely slapped formal symbols ($\pi, \Phi$) onto what is functionally a dynamic mixture of experts, but without specifying a viable training algorithm for the gating network.

---

### Attack 2: Falsification of the 5-Tuple Primitive Definition

`PAARTHA-PRIMITIVES-001` defined $\pi = \langle \text{Id}, \mathcal{T}_{\text{type}}, \mathbf{w}_{\text{anchor}}, \mathcal{A}_{\text{affordance}}, \Phi_{\text{invariants}} \rangle$.

#### A. The Point-Anchor Fallacy
The specification states that primitive activation is determined by:
$$P(\pi \text{ active} \mid \mathbf{z}) = \sigma\left(\frac{\mathbf{z} \cdot \mathbf{w}_{\text{anchor}}}{\tau}\right)$$
This assumes that the domain of a physical law can be identified by proximity to a single prototype vector $\mathbf{w}_{\text{anchor}} \in \mathbb{R}^d$.
* In physics and computation, a law or mechanism applies over a **region with boundaries**, often defined by relational inequalities (e.g., $x \ge 50 \land v_x > 0$).
* A single prototype vector defines an isotropic or hyper-spherical basin around a point. It cannot represent half-spaces, slabs, directional conditions, or relational conjunctions.
* Conflating the *activation condition* (where does the law hold?) with an *embedding prototype* fails mathematically.

#### B. The Static Invariant Trap
$\Phi_{\text{invariants}}$ is specified as first-order logical constraints verified by an SMT solver (e.g. Z3).
* Continuous sensorimotor systems operate under noise, numerical approximations, and partial observability.
* Exact first-order invariants ($\forall s, \phi(s) = \top$) extracted from empirical data will either be trivially overfit to the exact min/max bounds of the training cluster (e.g., $x \in [49.998, 50.002]$) or will fail on the very first out-of-distribution sample that has $0.1\%$ sensor noise.
* A deterministic SMT invariant firewall will reject valid generalizations due to micro-deviations.

---

### Attack 3: Falsification of the Five Seed Meta-Operators

1. **`OBJECT_PERSISTENCE` ($\text{Track}(z_{t+1}^j \mid z_t^i) = \arg\min_j \|z_{t+1}^j - z_t^i\|_2$):**
   * Nearest-neighbor tracking in Euclidean space is a naive heuristic known since the 1970s to fail catastrophically during:
     1. Trajectory crossing (two particles cross; nearest neighbor swaps identities).
     2. High velocities ($v \Delta t > \text{inter-object distance}$).
     3. Occlusions (object disappears behind an obstacle; nearest neighbor binds to the obstacle or a nearby object).
   * Elevating a broken Euclidean heuristic to an "innate foundational meta-operator" is scientifically untenable. Furthermore, it assumes an object-centric universe, completely failing on fluids, fields, deformations, or continuous state spaces.

2. **`RELATIONAL_BINDING` ($\mathcal{R}(z^i, z^j) = \phi_R([z^i \,\|\, z^j \,\|\, \delta(z^i, z^j)])$):**
   * The specification leaves $\phi_R$ completely undefined. If $\phi_R$ is a neural network, what initializes it? If it is untrained, it produces arbitrary random projections. A random projection is not a "relational binding"; it is random noise. If it is an untrainable fixed mapping, it is merely concatenation.

3. **`RESIDUAL_MONITOR` in a Moving Latent Space:**
   * $\mathbf{r}_t = s_{t+1} - \hat{s}_{t+1}$.
   * If $\mathbf{r}_t$ is computed in the latent space $\mathbf{z}_t$, but the encoder $\Theta_{\text{enc}}$ is simultaneously updated by gradient descent, the coordinate system of the latent space drifts!
   * A residual of magnitude $0.5$ at step 100 has a completely different geometric meaning than a residual of $0.5$ at step 1000. HDBSCAN clustering over a non-stationary drift manifold yields completely spurious clusters.

---

### Attack 4: Falsification of the Residual $\to$ HDBSCAN $\to$ MDL Formation Pipeline

#### A. The Geometry of Residuals: Residuals are Manifolds, Not Clusters
When a physical or operational law is unmodeled (e.g., dynamic friction, barrier rebound, aerodynamic drag), the prediction error is **not** a constant vector that clusters around a single centroid.
$$\mathbf{r}(s, a) = f_{\text{true}}(s, a) - f_{\text{base}}(s, a)$$
* If the true law is an elastic collision ($v' = -e v$), the error vector is $\mathbf{r} = -(1+e)v$. The error depends continuously and linearly on the incoming velocity $v$!
* If velocities vary from $0.1$ to $10.0$, the residuals form a line segment or cone in $\mathbb{R}^d$, **not a dense sphere**.
* HDBSCAN density clustering assumes dense, compact, separated modes. In continuous dynamics, residuals are continuous functions of state. HDBSCAN either merges them into the background or breaks them into arbitrary noise fragments.

#### B. The Cold-Start Routing Paradox
`PAARTHA-PRIMITIVES-001` specifies that candidate primitive $\pi^*$ is evaluated by:
$$\max_{\pi^*} \Delta \mathcal{J}(\pi^*) = \Delta \mathcal{L}_{\text{predictive}}(\mathcal{D}_{\text{eval}}) + \alpha \cdot \Delta \text{Bits} - \beta \cdot \mathcal{K}(\pi^*)$$
* How is $\Delta \mathcal{L}_{\text{predictive}}$ computed? By running the predictive router over $\mathcal{D}_{\text{eval}}$.
* But the router is a learned neural cross-attention network ($\Theta_{\text{trans}}$ in Section 12).
* **The Paradox:** The router has never seen $\pi^*$! Its attention weights have never been trained to route to $\pi^*$.
* Therefore, the router routes to $\pi^*$ with probability zero (or uniform random noise).
* As a result, $\Delta \mathcal{L}_{\text{predictive}} \le 0$.
* The complexity cost $\beta \mathcal{K}(\pi^*)$ is strictly positive ($> 0$).
* Therefore, $\Delta \mathcal{J}(\pi^*) < 0$ **always**.
* Every single autonomously proposed primitive will be rejected by the MDL filter at birth!

---

### Attack 5: Falsification of the PhysWorld-Genesis Benchmark

`PhysWorld-Genesis` introduced a hidden critical barrier at $x = 50$:
* If mass $m < 2.0 \implies$ elastic rebound.
* If mass $m \ge 2.0 \implies$ penetration with drag.

#### The POMDP Confounder:
* Mass $m$ is an **internal, unobservable physical property** from a static visual frame.
* Two particles at $x = 49, v_x = 5$ with identical appearances have identical instantaneous perceptual representations $\mathbf{z}_t$.
* At the barrier, one rebounds and one penetrates.
* To predict this, the system does not need a "primitive"; it needs **temporal history / recurrent state estimation** (e.g. an unscented Kalman filter or an LSTM) to infer $m$ from previous accelerations!
* The benchmark tests *Partially Observable State Estimation*, not *Primitive Formation*.
* An ordinary Recurrent Neural Network (Baseline C: Transformer + Memory) naturally maintains an internal accumulator of historical $F/a$ and solves the task implicitly without any explicit primitive creation.

---

## 3. What Actually Survives the Falsification?

After stripping away the hand-waves, circularities, and broken heuristics, the following **Four Core Principles** survive:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       WHAT ACTUALLY SURVIVES                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Modular Dynamical Separation (Anti-Interference Principle):                                         │
│    A single monolithic neural network trained with gradient descent cannot represent discontinuous,     │
│    mutually conflicting dynamical regimes without suffering catastrophic gradient interference.         │
│    Isolating distinct regimes into modular computational units is mathematically necessary.             │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Predictive Dissonance as the Gating Signal:                                                          │
│    New representation and computation should NOT be synthesized everywhere. Structural expansion        │
│    must be strictly gated by persistent, repeatable prediction failure of the current base model.       │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Explicit Operational Boundaries (Trigger Guards):                                                    │
│    Every specialized module must possess an explicit domain of applicability (a validity guard).        │
│    Without an explicit guard, routing collapses into out-of-distribution hallucination.                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Representation-Computation Coupling:                                                                │
│    A representation is only an architectural primitive if it changes the computational complexity       │
│    of downstream reasoning (e.g. converting multi-step integration into an O(1) jump or discrete test).│
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Architectural Redesign: The Bifurcation-Gated Modular Architecture (BGMA)

We now redesign the surviving core from first principles. No hand-waving. No unconstrained symbolic regression. No Z3 on noisy floats. No chicken-and-egg routing paradox.

```
                  THE BIFURCATION-GATED MODULAR ARCHITECTURE (BGMA)
                  
  Observation s_t ──────────────────────────────────────────┐
         │                                                  │
         ▼                                                  ▼
  [ Base Model M_0 ]                             [ Active Guards { G_k(s) } ]
  (Global Continuous Prior)                                 │
         │                                                  ▼
         │                                      Any G_k(s_t) > 0.5 ?
         │                                      ├─── YES ──► Route to Expert M_k(s_t)
         ▼                                      └─── NO  ──► Use Base Model M_0(s_t)
  Predicted s_{t+1} ◄───────────────────────────────────────┘
         │
         ▼
  Compute Residual: r_t = || s_{t+1}^{actual} - s_{t+1}^{pred} ||^2
         │
         ▼
  Persistent Error Streak? ( r_t > ε for τ consecutive steps in region R )
         │
         ├─── NO  ──► Local gradient update to active model
         └─── YES ──► [ BGMC CONSOLIDATION ENGINE ] (Offline / Sleep Phase)
                             │
                             ▼
              1. Spawn Micro-Expert M_cand (Low-Rank MLP)
                 Train on high-residual buffer via local SGD.
                             │
                             ▼
              2. Train Discriminative Boundary Guard G_cand(s)
                 Binary classifier: 1 if Error(M_cand) < Error(M_0), else 0.
                             │
                             ▼
              3. Evaluate Closed-Form MDL Objective:
                 ΔMDL = ErrorReduction - λ·(Complexity(G_cand) + Complexity(M_cand))
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
         ΔMDL > 0                      ΔMDL ≤ 0
      Register Primitive:           Discard Candidate
      π = < Id, G_cand, M_cand >
```

---

### Redesigned Primitive Definition: The Causal Mechanism Module (CMM)

We abandon the static 5-tuple. A primitive $\pi_k$ is an operational **Causal Mechanism Module (CMM)**:

$$\pi_k = \langle \text{Id}_k, \mathcal{G}_k(s), \mathcal{F}_k(s), \mathcal{C}_k \rangle$$

1. **Identifier ($\text{Id}_k \in \mathbb{N}$):** Discrete index in the module registry.
2. **Discriminative Boundary Guard ($\mathcal{G}_k: \mathcal{S} \to [0, 1]$):**  
   A learned, calibrated binary classifier (e.g. linear support-vector or shallow 2-layer MLP with sigmoid output) that outputs the probability that state $s$ belongs to the operational regime of this module:
   $$\mathcal{G}_k(s) = \sigma\left(\mathbf{w}_g^\top \phi(s) + b_g\right)$$
   *Crucial distinction:* This is **not** an error prototype point anchor! It is a **hyperplane or manifold boundary in state space** that learns *where* the law holds.
3. **Local Dynamical Operator ($\mathcal{F}_k: \mathcal{S} \to \Delta \mathcal{S}$):**  
   A specialized low-rank transformation operator parameterizing the state delta:
   $$\hat{s}_{t+1} = s_t + \mathcal{F}_k(s_t; \theta_k)$$
4. **Computational Cost Profile ($\mathcal{C}_k$):**  
   FLOPs, parameter count, and execution latency.

---

### Redesigned Formation Mechanism: Bifurcation-Gated Modular Consolidation (BGMC)

This completely replaces HDBSCAN, symbolic regression, and SMT solvers with stable, tractable, gradient-based operations:

```
┌─────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Step                            │ Tractable Mathematical Execution                                       │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 1. Anomaly Buffering            │ If prediction error $\|s_{t+1} - \hat{s}_{t+1}\|^2 > \epsilon_{\text{tol}}$ persistently,  │
│                                 │ buffer trajectory segments: $\mathcal{B}_{\text{anom}} = \{(s_i, s_{i+1})\}$.         │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 2. Micro-Expert Fitting         │ Initialize lightweight micro-expert $\mathcal{F}_{\text{cand}}$ (~50K params).       │
│                                 │ Fit $\theta_{\text{cand}}$ on $\mathcal{B}_{\text{anom}}$ using Adam for $N$ steps:    │
│                                 │ $\min_{\theta} \sum_{i} \|\mathcal{F}_{\text{cand}}(s_i) - (s_{i+1} - s_i)\|^2$.     │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 3. Discriminative Guard Fitting │ Form binary dataset over replay memory:                                │
│                                 │ $y_i = 1$ if $\|\mathcal{F}_{\text{cand}}(s_i) - \Delta s_i\| < \|\mathcal{F}_{\text{base}}(s_i) - \Delta s_i\|$,│
│                                 │ else $y_i = 0$. Fit guard $\mathcal{G}_{\text{cand}}(s)$ via binary cross-entropy.      │
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 4. Cold-Start Solution          │ $\mathcal{G}_{\text{cand}}(s)$ **is the router**! No external router retraining.        │
│                                 │ For any state $s$, execution rule is:                                  │
│                                 │ If $\mathcal{G}_{\text{cand}}(s) > 0.5 \implies$ Execute $\mathcal{F}_{\text{cand}}(s)$.│
├─────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 5. Closed-Form MDL Objective    │ Evaluate over validation replay set $\mathcal{D}_{\text{val}}$:        │
│                                 │ $\Delta \text{MDL} = \sum_{s \in \mathcal{D}_{\text{val}}} \left[ \mathcal{L}_{\text{base}}(s) - \mathcal{L}_{\text{active}}(s) \right] - \lambda \cdot (\text{params}(\mathcal{G}) + \text{params}(\mathcal{F}))$. │
│                                 │ If $\Delta \text{MDL} > 0$, commit $\pi_{\text{new}}$ to registry!    │
└─────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

**Why this works where the previous design failed:**
1. It replaces unconstrained symbolic search with **local gradient descent** (fast, continuous, stable).
2. It solves the **Cold-Start Routing Paradox** because the guard $\mathcal{G}(s)$ is explicitly trained on the boundary before registration.
3. It avoids the **Point-Anchor Fallacy** by fitting a separating boundary in state space rather than averaging residual vectors.
4. It avoids the **Static Invariant Trap** because the guard provides a smooth, probabilistic confidence envelope rather than brittle first-order SMT checks.

---

### Redesigned Seed Substrate: 3 Geometric & Temporal Priors

We eliminate the broken nearest-neighbor tracker and undefined relational operators. The innate substrate consists of **Three Non-Parametric Structural Priors**:

1. **Temporal Asymmetry Prior (Causality):**  
   State transitions are strictly directed: $s_t \to s_{t+1}$. Prediction flows forward in time.
2. **Local Smoothness & Metric Continuity:**  
   In the absence of guard activation, states evolve smoothly: $\|s_{t+1} - s_t\| \le v_{\max} \Delta t$. Discontinuous jumps in state derivative signal a regime boundary.
3. **Partitioned State Vector Prior:**  
   State is structured as continuous coordinates (position, velocity) and discrete object IDs.

---

## 5. Redesigned Minimal Falsifiable Experiment: PhaseWorld-001

To eliminate the POMDP mass confounder of `PhysWorld-Genesis`, we design **PhaseWorld-001**: a fully observable environment with sharp, mutually contradictory dynamical regimes.

```
                          PHASEWORLD-001 TESTBED
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   ZONE 1: Inertial Drift Zone (x < 30)                                  │
│   • Dynamics: ds/dt = v (standard Newton / friction)                    │
│                                                                         │
│   ----------------- REGIME BOUNDARY 1 (x = 30) ------------------------ │
│                                                                         │
│   ZONE 2: Non-Linear Vortex Field (30 <= x <= 70)                       │
│   • Dynamics: dx/dt = -ω·(y - 50),  dy/dt = ω·(x - 50)                  │
│     (Rotational non-inertial vector field; contradicts Zone 1)         │
│                                                                         │
│   ----------------- REGIME BOUNDARY 2 (x = 70) ------------------------ │
│                                                                         │
│   ZONE 3: Inelastic Damping Barrier (x > 70)                            │
│   • Dynamics: v' = 0, particle adheres to boundary surface              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why PhaseWorld-001 is a True, Unconfounded Test:
1. **Fully Observable (No POMDP):** Position $x, y$ and velocity $v_x, v_y$ are 100% visible at every frame. No hidden mass or friction variables.
2. **Mutually Contradictory Gradients:** Zone 1 demands linear momentum conservation. Zone 2 forces perpendicular rotational acceleration. Zone 3 forces complete velocity collapse.
3. **The Monolithic Failure Mode:** A single neural network trained across all three zones suffers from severe gradient interference (learning the vortex corrupts linear drift; learning the barrier corrupts momentum).
4. **The BGMA Test:** Can BGMA start with only a Zone 1 base model, encounter persistent residuals in Zone 2, autonomously synthesize `π_vortex = <Id_vortex, G_vortex, F_vortex>`, and achieve 0% catastrophic forgetting on Zone 1?

---

## 6. Controlled Baselines & Pre-Registered Falsification Criteria

```
┌─────┬──────────────────────────┬─────────────────────────────────────────────────────┐
│ ID  │ Baseline Name            │ Controlled Variable                                 │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_1 │ Monolithic MLP           │ Single 2M-param MLP trained end-to-end with Adam.   │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_2 │ Recurrent World Model    │ LSTM / GRU state-space model with memory buffer.    │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_3 │ Static Mixture of Experts│ MoE with 3 fixed experts trained jointly from start.│
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_4 │ Full BGMA Architecture   │ Base model + Autonomous BGMC Module Formation.      │
├─────┼──────────────────────────┼─────────────────────────────────────────────────────┤
│ B_5 │ Random-Guard Ablation    │ Forms modules with random boundaries (no BGMC).     │
└─────┴──────────────────────────┴─────────────────────────────────────────────────────┘
```

### Pre-Registered Falsification Conditions
The redesigned BGMA architecture will be declared **FALSIFIED** if:
1. **The Interference Failure:** Baseline $B_1$ (Monolithic) learns Zone 2 and Zone 3 without degrading Zone 1 performance by more than $5\%$ (proving modular primitives are unnecessary).
2. **The Autonomous Discovery Failure:** BGMA fails to trigger module synthesis in Zone 2 or Zone 3, or the synthesized guard $\mathcal{G}_{\text{cand}}$ achieves $F_1 < 0.80$ on boundary classification.
3. **The Memory Parity Failure:** Baseline $B_2$ (Recurrent Memory) matches BGMA's multi-step trajectory accuracy within $10\%$ with equal or fewer training steps.

---

## 7. Comparative Summary: Original vs. Redesigned

```
┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ Dimension                    │ PAARTHA-PRIMITIVES-001       │ REDESIGNED (BGMA / BGMC)     │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Primitive Structure          │ 5-tuple with point anchor w  │ CMM: <Id, Guard G(s), Op F>  │
│                              │ and brittle SMT invariant Φ  │ with calibrated boundary     │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Operational Trigger          │ Point prototype distance     │ Learned discriminative guard │
│                              │ σ(z · w / τ) [FALLACY]       │ hyperplane G(s) > 0.5        │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Formation Engine             │ HDBSCAN + Symbolic Regr + Z3 │ BGMC: Local micro-expert SGD │
│                              │ [COMBINATORIAL EXPLOSION]    │ + Discriminative boundary fit│
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Routing Evaluation           │ Learned cross-attention      │ Direct evaluation via guard  │
│                              │ [COLD-START PARADOX]         │ [PARADOX RESOLVED]           │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Testbed Environment          │ PhysWorld-Genesis            │ PhaseWorld-001               │
│                              │ [POMDP CONFOUNDER]           │ [FULLY OBSERVABLE REGIMES]   │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

---

## 8. Epistemic Status & Conclusion

**Audit Verdict:**  
`PAARTHA-PRIMITIVES-001` contained fatal theoretical flaws that would have collapsed during empirical execution. Those flaws have been rigorously identified, dissected, and excised.

The surviving core—**Bifurcation-Gated Modular Consolidation (BGMA)** operating over the unconfounded **PhaseWorld-001** benchmark—is mathematically sound, free of circularities, computationally tractable, and ready for empirical falsification.

The research remains classified as **Verdict E — UNDERDETERMINED**, pending the execution of the PhaseWorld-001 trial.
