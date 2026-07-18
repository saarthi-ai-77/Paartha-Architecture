# Build Prompt: Architecture Test Harness ("Arch-Ops")

## What this system is for

We are designing a novel neural architecture (not a standard Transformer/MoE/Mamba variant — it decomposes computation into typed subsystems, e.g. episodic memory / semantic weights / procedural skill modules / rule-execution modules / manifold-similarity modules, connected by a lightweight router). The architecture will go through many iterations. Each iteration needs to be trained, tested, and compared against a baseline quickly, without a human re-building the training/eval pipeline from scratch every time.

Build a system — call it **Arch-Ops** — that plays the role of a dev/ops engineer for this research process: given a candidate architecture and a description of how to train it, Arch-Ops sets up the run, trains it, evaluates it, compares it to a baseline, and produces a structured report a human can act on. It does **not** design architectures, does **not** decide research direction, and does **not** curate the underlying datasets from scratch — it executes and reports on what it's given.

---

## Input Contract: the Architecture Manifest

Arch-Ops must accept a **self-contained submission package** per experiment, consisting of:

1. **Model code** — a Python module exposing the architecture as a standard trainable model (e.g. a PyTorch `nn.Module` or equivalent), with a clear entry point (`build_model(config) -> model`).
2. **A manifest file** (YAML or JSON) describing:
   - **Modules**: a list of named submodules with a declared *type* (e.g. `semantic`, `episodic`, `procedural`, `rule`, `manifold`, `router`) — this typing is metadata for reporting, not something Arch-Ops needs to interpret semantically.
   - **Per-module training requirements**: which loss function(s) apply to which module, whether a module is trained by gradient descent at all (episodic modules may be write-only, no backprop), and any auxiliary objectives beyond the main task loss.
   - **Data requirements per module**: what shape/format of data each module consumes (e.g. semantic module wants raw token sequences; procedural module wants action-sequence traces; episodic module wants key-value fact pairs). Arch-Ops does not generate this data — it expects a path or loader function per requirement, supplied by the submitter.
   - **Declared hyperparameters** and their valid ranges (for reproducibility and for any sweep Arch-Ops is asked to run).
   - **Resource budget**: max GPU-hours, max wall-clock time, target model size (param count), so Arch-Ops can size the run appropriately and abort runaway experiments.
3. **A baseline reference**: either "use the standard parameter-matched Transformer baseline already registered in Arch-Ops" (default) or a submitted alternative baseline model, so every result is reported *relative to* something, never in isolation.
4. **The benchmark suite to run**: a named set of eval tasks (Arch-Ops maintains a registry; the submission just references which ones apply, e.g. "english-fluency-v1", "long-tail-recall-v1", "compositional-generalization-v1"). New benchmarks can be registered independently of any specific architecture submission.

If any required field is missing or a data loader is unavailable, Arch-Ops must fail fast at submission time with a specific error, not partway through a training run.

---

## Pipeline Arch-Ops Must Run, In Order

1. **Static validation** — manifest schema check, model instantiates without error, forward pass runs on a single dummy batch of the declared shape, parameter count matches the declared budget within tolerance.
2. **Smoke test** — a short training run (a few hundred steps, small data slice) checking for: NaN/Inf losses, gradient explosion, any module receiving zero gradient when it shouldn't, memory usage within budget. Abort with a diagnostic report if this fails — do not proceed to a full run.
3. **Full training run** — executes to the declared budget or a convergence criterion (specified per-submission or defaulted), with checkpointing at regular intervals so a crashed run can resume rather than restart.
4. **Per-module diagnostics captured throughout training**, not just final metrics:
   - Per-module loss curves (if the module has its own objective).
   - Router decision distribution over time (what fraction of inputs/tokens get sent to each module type, and whether that distribution is stable or degenerate — e.g. router collapsing to always pick one module is a reportable failure mode, not just a number).
   - Gradient norms per module.
   - For episodic/memory modules specifically: write/read counts, memory occupancy over time, retrieval hit-rate if applicable.
5. **Baseline run** — the same benchmark suite executed against the registered baseline, using the same data and compute budget, so comparisons are apples-to-apples. Reuse a cached baseline result if one already exists for this exact benchmark+budget combination rather than re-running it every time.
6. **Benchmark evaluation** — run the declared benchmark suite against both the candidate and the baseline, producing task-level scores plus whatever the benchmark defines as a "qualitative" comparison (e.g. learning-curve shape, not just final accuracy — some of our hypotheses are specifically about *how* performance improves with data/scale, not just the endpoint).
7. **Report generation** (see Output Contract below).

Arch-Ops must be able to run this pipeline **unattended** end-to-end once a submission is accepted — the human (CTO/architecture designer) hands off a submission and comes back to a report, not to a series of manual steps.

---

## Output Contract: the Experiment Report

Every run produces a single structured report (JSON + a human-readable summary) containing:

- **Pass/fail on each pipeline stage** (static validation, smoke test, full run, evaluation) with the specific failure reason if any stage failed.
- **Candidate vs. baseline metrics**, side by side, for every benchmark task run.
- **Per-module diagnostics** as captured above — this is the most important part for failure analysis. When something goes wrong, the report should contain enough detail (which module's loss stalled, whether the router degenerated, whether a specific module never received gradient) that a subsequent root-cause discussion doesn't need to re-run the experiment just to find out what happened.
- **Resource actuals** — GPU-hours, wall-clock time, peak memory — versus the declared budget, so we can track whether the efficiency claims we're testing actually hold up in practice, not just in theory.
- **A verdict summary**: one of `PASSED`, `FAILED (stage X)`, or `INCONCLUSIVE (needs more data/budget)` — Arch-Ops should not average failures into an ambiguous partial-success signal; if a run failed, say so plainly and say at which stage.

Reports must be versioned and retained (never overwritten) — each submission gets a permanent experiment ID, and its full report history stays queryable, so architecture iterations can be compared against each other over time, not just against the baseline.

---

## Operational Requirements

- **Resource guardrails**: hard timeouts and hard GPU-hour caps per run, with automatic termination (not just a warning) if exceeded — this will run on subsidized/limited compute and must not silently overrun budget.
- **Reproducibility**: every run records the exact code version (git commit hash of the submitted model code), manifest, random seeds, and library versions, so a reported result can be reproduced or disputed later.
- **Idempotent resubmission**: resubmitting the same manifest + code + data should either reuse a cached result or clearly re-run and version the new result — never silently overwrite a prior report.
- **Extensibility without rebuilding**: adding a new module *type* label, a new benchmark, or a new baseline must not require changing Arch-Ops' core pipeline code — these should be registries/config, not hardcoded branches.

---

## Explicit Non-Goals

- Arch-Ops does not design or modify the architecture. It runs what it's given.
- Arch-Ops does not curate or generate training data. It consumes data loaders/paths supplied in the manifest.
- Arch-Ops does not make research-direction decisions (e.g. "this architecture is a dead end, try X instead"). It reports facts; a human (or a separate council-style review process) makes that call.
- Arch-Ops is not a hyperparameter-search product in the general sense — a basic sweep capability over declared ranges is useful, but exhaustive NAS/HPO is out of scope for v1.

---

## Suggested v1 Scope (don't over-build)

For the first working version: support one model submission format (PyTorch), one baseline (a standard decoder-only Transformer at matched parameter count), 2–3 registered benchmarks (to be supplied separately, e.g. an English-fluency perplexity/generation benchmark and a long-tail factual recall benchmark), local or single-node GPU execution (no need for distributed training orchestration yet), and the static-validation + smoke-test + full-run + report pipeline described above. Multi-node scaling, exhaustive hyperparameter search, and a web UI can come later — the priority is a correct, unattended, trustworthy report loop.
