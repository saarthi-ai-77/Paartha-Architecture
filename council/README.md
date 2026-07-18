# Council System

**Status as of DEC-005 (2026-07-18): secondary, diagnostic tool — not the primary research method.**

This directory houses the hierarchical council system that guided ACA's research through Sprints 1–3A. As recorded in `docs/05_research/Decisions.md` (DEC-005), the council-driven methodology — propose a theory, critique it, reduce it, repeat — produced an increasingly refined *methodology for evaluating claims* across four sprints, but no validated primitive, no architecture, and no contact with real data or experiments. ACA's primary methodology has since shifted to build-experiment-validate-iterate (see `docs/06_experiments/Completed.md`).

**The council system's role going forward:** root-cause analysis when a real experiment fails. If a build-experiment-validate cycle produces a confusing or unexplained result, a council session (Research Theorist proposes a diagnosis, Scientific Reviewer challenges it, Reductionist simplifies it) can be used to work through *why* — the same role structure, redirected at a concrete, already-observed failure instead of an abstract first-principles question. It is not used to originate new architectural claims without an experiment behind them.

**Everything below this line describes the prior, now-secondary methodology and its historical output, preserved in place — not deleted, not moved, and not treated as invalidated by the pivot.** The Knowledge Foundation Council's Sprint 1–3A work remains a real (if inconclusive) piece of research history; the `main/` directory's RP-001 content remains quarantined pending provenance recovery (see `docs/03_foundations/OPEN.md`), a separate and older issue than the methodology pivot.

---

The project transitioned from a single research council into a hierarchy of specialized domain councils, allowing independent research domains to evolve while maintaining complete historical traceability. Councils are domain-oriented rather than project-oriented.

## Current Council Hierarchy

**1. Main Council** (`/main/`)
The Main Council acts as the primary governing body. It is responsible for reviewing mature research, validating major architectural decisions, and reviewing derived theories across all domains.

↓

**2. Knowledge Foundation Council** (`/knowledge-foundation/`)
This council is responsible only for discovering the computational nature of knowledge. Its purpose is to answer one question: *What is knowledge from a computational perspective?* It derives answers from first principles without inheriting assumptions from existing AI architectures. It progressively discovers the computational definition, intrinsic properties, and minimal fundamental properties of knowledge, producing foundations that later research can inherit. **Architecture is explicitly outside the scope of this council.**

## Future Councils
As the research progresses, the modular structure will be expanded to include dedicated councils for:
* Representation Theory
* Learning Theory
* Inference Theory
* Architecture
* Evaluation
