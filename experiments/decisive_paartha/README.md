# Paartha Decisive Experiment

## Controlled Benchmark for Testing Competence Acquisition Beyond a Frontier LLM + Tools

This experimental suite evaluates whether the Paartha computational architecture allows a system to acquire and reuse generalizable competence through experience and abstraction discovery, beyond what the same frontier LLM can achieve alone or with the same tools/contracts.

### Quick Start & Execution

```bash
# Optional: Set Sarvam API key or custom endpoint
export SARVAM_API_KEY="your-api-key"
export SARVAM_MODEL="sarvam-2b"

# Run the complete experiment
python experiments/decisive_paartha/run_experiment.py
```

### The 5 Evaluated Systems

1. **System A (Frontier LLM Alone)**: Zero-shot in-context reasoning with zero external tools or contracts.
2. **System B1 (Frontier LLM + Primitive Tools)**: Standard ReAct agent with 12 typed primitive tools and contracts.
3. **System B2 (Frontier LLM + Tools + Discovered Abstractions)**: Critical control equipping the ReAct agent with newly discovered abstractions.
4. **System C (Paartha Runtime without Abstractions)**: Paartha architecture (contract reflection, capability selection, RESOLVE parameter binding, verification) with only primitive capabilities.
5. **System D (Paartha + Experience + Abstraction Discovery)**: Solves experience tasks, extracts motifs, runs Plotkin anti-unification and MDL selection, verifies synthesized contracts, freezes learning, and evaluates on held-out and cross-domain transfer tasks.

### Architecture

```
experiments/
  decisive_paartha/
    config/          # Configurable model providers
    tools/           # 12 typed primitive tools
    systems/         # System implementations (A, B1, B2, C, D)
    benchmark/       # Tasks across 3 levels and automated leakage audit
    evaluation/      # Blinded scoring, failure taxonomy, metrics
    run_experiment.py# Master runner for Phases 0 through 6
    results/         # Serialized empirical results
```
