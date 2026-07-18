**Status: Active** (revised 2026-07-18 per DEC-005; prior "Frozen" version preserved in `docs/archive/Deprecated.md`)

# Success Criteria

*   **Empirical Validation:** Each proposed architectural mechanism must be demonstrated in a real, small, trainable model against an honest baseline, across multiple seeds, before being treated as a validated design principle. See `docs/06_experiments/Completed.md`.
*   **Efficiency Demonstrated, Not Assumed:** The proposed architecture must show measured evidence (accuracy, sample efficiency, or compute cost) of an advantage over a parameter-matched uniform baseline on a benchmark specifically designed to expose the mechanism under test — not merely a plausible efficiency story.
*   **Composability:** Independently-validated mechanisms (e.g. the memory allocator from EXP-001, the rule module from EXP-002/003) must be shown to compose in one model without interfering with each other (EXP-004 and onward), before any claim is made about a complete architecture.
*   **Scale-Up Path:** A working small-scale proof of concept (an SLM trained on the validated architecture, initially benchmarked on basic English fluency) that can justify further investment (e.g. the India AI compute grant) — with code, feasibility, and a limitations trail preserved and honest.
*   **Reproducibility:** A clear, traceable, and historically preserved path from hypothesis to validated (or falsified) result, with code and results retained alongside the write-up — not argument alone. The council methodology remains available as a secondary, diagnostic tool for root-causing experiment failures (see `council/README.md`), not as the primary path to a decision.
