**Status: Active** (revised 2026-07-18 per DEC-005; prior "Draft" pipeline preserved in `docs/archive/Deprecated.md`)

# Research Milestones

Milestones for the build-experiment-validate track (DEC-005). Each milestone is a concrete, testable result, not a research phase to be argued through.

1. **Individual component validation** ✅ — EXP-001 (episodic memory allocation), EXP-002 (constrained rule module), EXP-003 (validation-driven family selection). Complete; see `docs/06_experiments/Completed.md`.
2. **Component composability** ✅ — EXP-004: confirmed the validated memory and rule-module components work together in one model, one optimizer, without interfering — under a disjoint-parameter design. See `docs/06_experiments/Completed.md`.
3. **Family/structure discovery** — extend EXP-003's family-*selection* result (choosing among a known library) to family-*discovery* (constructing or identifying a suitable constrained family for a domain with no pre-known correct answer). Not started; this is the central open problem flagged by EXP-002/003.
3b. **Shared-substrate integration** — EXP-004 deliberately kept the two components' parameters disjoint (sharing a learned embedding would have broken the rule module's validated constraint). Whether they can share a real substrate (e.g. one token embedding space, as a real architecture would need) is untested and flagged as the more pressing near-term gap.
4. **Dynamic scheduling** — a mechanism that routes between validated components (and any future ones) at runtime, built on the validation-driven-selection constraint established by EXP-003. Not started; depends on milestones 2–3b.
5. **Real-backbone, real-data integration** — move from synthetic toy tasks to an actual small transformer/language-model backbone and a real (or semi-real) dataset. Not started; depends on milestones 2–4 producing something worth integrating.
6. **Small-scale trainable proof of concept (SLM)** — a trained small language model using the validated architecture, initially benchmarked on basic English fluency (not code/math/reasoning — those are explicitly deferred, per the architecture's own extensibility requirement that nothing in the design assumes natural-language-only).
7. **Compute-grant readiness** — a working POC and honest results sufficient to support an India AI compute grant application for further training and experimentation.

---

**Purpose:** Track concrete, testable milestones for the current research methodology.
**Current Status:** Active
**Historical Context:** Revised 2026-07-18 per DEC-005; the prior taxonomy-first pipeline (Knowledge Foundation → Taxonomy → Representation Theory → Learning Theory → Inference Theory → Architecture → Experimental Validation) is preserved in `docs/archive/Deprecated.md`.
**Known Facts:** Milestone 1 is complete.
**Hypotheses:** N/A
**Unknowns:** Timelines for milestones 2–7 depend on experimental results, not a fixed schedule.
**References:** `docs/06_experiments/Completed.md`, `docs/07_future/Roadmap.md`, `docs/05_research/Decisions.md` (DEC-005)
