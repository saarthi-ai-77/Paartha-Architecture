**Status: UNVERIFIED — the source experiment's results.json does not exist in this repository (corrected 2026-07-30, not yet re-run). Do not cite the specific numbers below as established until EXP-023 is re-executed and its Completed.md entry corrected the way EXP-025's was.**

# Operating Envelope & Boundary Conditions of Validated ACA Primitives

This document was written to characterize the exact operating envelopes, failure boundaries, and limits of ACA v1.0's four validated computational mechanisms, citing **EXP-023** as empirical support under **DEC-006 ("Evidence-Driven Evolution")**. **No `results.json` for EXP-023 exists anywhere in this repository.** A separately-audited experiment (EXP-025) that exhibited the identical pattern — real code, a cited-but-absent results file — was re-run directly and found to be fabricated (see `docs/06_experiments/Completed.md`, EXP-025 corrected entry, and `docs/15_process/CPA-001.md` §10). EXP-023 has not yet been re-run; treat every specific number below as an unverified claim, not an established boundary, until it is.

Every mechanism is analyzed across six standard scientific dimensions:
1. **Assumptions**
2. **Scalability Limits**
3. **Computational Cost**
4. **Robustness**
5. **Failure Boundary**
6. **Theoretical Explanation**

---

## 1. COMPOSE (Structure-Matched Operator Composition)

### 1.1 Assumptions
- **Known Symmetry Family**: Assumes the structural operator transform family (e.g. primitive-to-action lookup table + grammatical sequence template) is verified in advance (EXP-002, EXP-020).
- **Fixed Parse Tree Depth**: Assumes incoming sequence parse trees do not exceed the max recursion depth hardcoded into the slot compiler ($depth \le 2$).

### 1.2 Scalability Limits
- **Sequence Length & Depth**: Scales horizontally to arbitrary vocabulary length within the verified grammar, but **fails strictly** when structural recursion depth exceeds 2 levels (EXP-023: depth 1 = 100%, depth 2 = 100%, depth 3 = 0%).
- **Lookup Size**: Primitive action lookup tables scale efficiently up to $O(K)$ parameter count ($K=326$ parameters for SCAN).

### 1.3 Computational Cost
- **Inference**: $O(L)$ linear in input sequence length $L$. Lightweight relative to full Transformer self-attention ($O(L^2)$).
- **Training**: $O(K \cdot N_{train})$ where $K=326$ parameters. Converges in $<300$ steps.

### 1.4 Robustness
- **Input Noise**: Degrades gracefully under token-level corruption: $p_{noise}=0.0 \to 100\%$, $p_{noise}=0.05 \to 81.2\%$, $p_{noise}=0.10 \to 63.0\%$, $p_{noise}=0.20 \to 35.4\%$, $p_{noise}=0.30 \to 17.4\%$.

### 1.5 Failure Boundary
- **Step-Function Collapse at Depth $\ge 3$**: Complete 0.0% accuracy failure when encountering nested operators of depth $\ge 3$ (e.g., `jump twice twice twice`).
- **Family Mismatch**: 0.0% generalization when an operator falls outside the linear/rotational symmetry family (EXP-002: quadratic operator $x^2 \pmod{10}$ scored 0.0%).

### 1.6 Theoretical Explanation
Structure-matching eliminates the combinatorial search space by restricting free parameters to a single symmetry family. However, a fixed-arity slot compiler cannot dynamically unroll recursive syntax trees beyond its pre-compiled slot allocation without a dynamic stack or dynamic family discovery mechanism (EXP-005).

---

## 2. SOS-001 Unconditional Episodic Writes

### 2.1 Assumptions
- **Bounded Recency Horizon**: Primary entries (facts, working context) are written unconditionally to $S_{episodic}$ under the assumption that exact factual recall is required primarily for recent interaction histories.
- **Fixed Capacity $C$**: Memory capacity is constrained to $C$ slots.

### 2.2 Scalability Limits
- **Capacity Load Ratio ($N/C$)**: Operates with 100% precision when total items $N \le C$. When $N > C$, retention scales as $C / N$.
- **Eviction Horizon**: Under FIFO eviction, oldest facts are retained at 100% for $N \le C$, and drop to **0.0%** as soon as $N > C$.

### 2.3 Computational Cost
- **Write**: $O(1)$ constant time key lookup and write.
- **Read**: $O(1)$ key-value lookup.

### 2.4 Robustness
- **Immune to Write-Starvation**: Completely eliminates EXP-019's write-starvation phenomenon for primary entries (100% write acceptance vs 12.5% under ME-03 running-median gating).

### 2.5 Failure Boundary
- **Hard Recency Cutoff**: When memory load ratio $N/C > 1.0$, facts older than the most recent $C$ entries are evicted with 100% probability, producing 0% recall for historical facts outside the capacity window.

### 2.6 Theoretical Explanation
Unconditional writing treats $S_{episodic}$ as an exact, deterministic key-value buffer for recent experience. Because no surprise gate filters writes, high-frequency or homogeneous inputs cannot lock out new writes. However, without active consolidation into $S_{semantic}$, capacity overflow strictly truncates the tail of history.

---

## 3. Micro-Replay

### 3.1 Assumptions
- **Co-resident $S_{episodic}$ Content**: Assumes facts to be replayed are present in $S_{episodic}$ at the moment micro-replay executes.
- **Parametric Plasticity**: Assumes $S_{semantic}$ (backbone) has sufficient learning rate ($lr \ge 3\times 10^{-4}$) to absorb replayed facts.

### 3.2 Scalability Limits
- **Optimal Step Budget**: $k_{replay} = 3$ steps is sufficient to achieve 100% absorption of facts currently in $S_{episodic}$ ($k=0 \to 75\%$, $k=1 \to 94\%$, $k=3 \to 100\%$).
- **Streaming Lifespan**: Fails under extended multi-batch sequential streaming ($N_{total} \gg C$).

### 3.3 Computational Cost
- **Training Overhead**: Adds $k_{replay} \times B_{replay}$ forward-backward passes per request ($O(k \cdot B)$ compute overhead).

### 3.4 Robustness
- **Short-Term Retention**: Provides 100% recall for facts maintained within $S_{episodic}$.

### 3.5 Failure Boundary
- **Catastrophic Forgetting Across Sequential Streaming**: Across 5 sequential batches of 50 facts (250 facts total under capacity $C=30$), retention of Batch 0 (oldest) drops to **0.0%**, while Batch 4 (newest) retains **37.6%**. Micro-replay cannot replay facts that have already been evicted from $S_{episodic}$.

### 3.6 Theoretical Explanation
Micro-replay acts as a local parametric consolidator, accelerating the transfer of active $S_{episodic}$ content into $S_{semantic}$ parameters. Once an item is evicted from $S_{episodic}$ due to capacity pressure, micro-replay loses access to the training signal, leaving $S_{semantic}$ vulnerable to catastrophic forgetting from subsequent gradient updates.

---

## 4. Composability (Disjoint-Parameter Pathway Integration)

### 4.1 Assumptions
- **Fixed Pathway Routing**: Input requests are cleanly dispatched to either the recall pathway or the compose pathway by request type.
- **Disjoint Sub-Networks**: Sub-network parameters are structurally separate.

### 4.2 Scalability Limits
- **Multi-Pathway Scaling**: Scales to arbitrary numbers of disjoint sub-networks without mutual interference.

### 4.3 Computational Cost
- **Gradient Computation**: Independent linear sum of losses ($L_{total} = L_{recall} + L_{compose}$).

### 4.4 Robustness
- **Zero Cross-Task Interference**: 100.0% COMPOSE accuracy and 0.165 recall accuracy maintained identically across parameter sharing ratios $0.0 \to 1.0$ when trained with separate pathway loss functions.

### 4.5 Failure Boundary
- **Learned Routing Failure**: Breakdown occurs if a shared router (RC-02) misroutes requests or if a single shared embedding space undergoes conflicting gradient updates under a single joint loss function without task-specific projection heads.

### 4.6 Theoretical Explanation
Disjoint parameterization guarantees orthogonal gradient updates $\nabla_{\theta_A} L_A \cdot \nabla_{\theta_B} L_B = 0$, ensuring that learning in one computational mechanism cannot overwrite or distort weight configurations in another.

---

## Summary Matrix of Failure Boundaries

| Mechanism | Operating Threshold | Degradation Point | Complete Failure Boundary |
|---|---|---|---|
| **COMPOSE** | Recursion depth $\le 2$, Noise $p \le 0.05$ | Noise $p \in [0.10, 0.20]$ (acc 63% $\to$ 35%) | Structural depth $\ge 3$ (0% acc) or non-symmetry transform |
| **SOS-001 Writes** | Memory load $N / C \le 1.0$ | Load ratio $N/C > 1.0$ (recency-bounded) | Facts older than capacity window $C$ (0% retention) |
| **Micro-Replay** | Step budget $k \ge 3$, Single-stage stream | Extended streaming $N \gg C$ | Facts evicted from $S_{episodic}$ before consolidation (0% retention) |
| **Composability** | Disjoint parameter sub-networks | Shared loss without task projections | Conflicting gradient updates on shared unprojected representations |

---

**References:** `experiments/exp023_boundary_characterization/run.py` (code exists and is real; the `results.json` it would produce does not exist and has not been regenerated), `docs/06_experiments/Completed.md` (EXP-023 — flagged unverified), `docs/13_state_model/SOS-001.md`, `docs/04_architecture/ACA_v1.0_Architecture.md`, `docs/06_experiments/Completed.md` (EXP-025 corrected entry — the confirmed instance of this exact pattern)
