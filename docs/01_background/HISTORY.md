**Status: Active**

# History of the Research Program

## Origins
The research originally began with a highly specific objective: *Invent a fundamentally new foundation model for design generation.* 

The initial focus was driven by the limitations of existing models in handling structural, spatial, and aesthetic relationships required for tasks like web design. This period, known as the representation research phase, was dedicated to figuring out how an AI could native-ly represent and manipulate design concepts without treating them merely as text tokens.

## Council Methodology
To ensure rigorous scientific discipline, the project originally adopted a singular "Council methodology." This structure separated roles into:
* **The Architect:** Responsible for proposing architectural changes, computational primitives, and implementation ideas.
* **The Reviewer(s):** Responsible for aggressive critique, highlighting logical flaws, identifying assumptions, and enforcing first principles.

This dialectic process ensured that no hypothesis was accepted as fact without intense scrutiny. As the research expanded, this methodology evolved into a **modular Council System**, dividing the research into specialized domain councils (such as the Knowledge Foundation Council) with tailored roles, overseen by a Main Council.

## The Evolution of the Research Question
During extensive literature reviews, architectural discussions, and multiple rounds of Council critiques, a pivotal discovery occurred. The team realized that the struggles encountered in design generation were not isolated domain issues. They were symptoms of a much larger flaw in current AI paradigms: the assumption that a single, uniform computational process (like predicting the next token in a Transformer) should be applied to all forms of cognition.

The objective fundamentally shifted. The research question evolved from "How do we build a design model?" to:

> **"Whether intelligence should be implemented through one universal computational framework, or through multiple fundamentally different computational mechanisms dynamically selected according to the nature of the problem."**

Following this discovery, web design was downgraded from the ultimate goal to merely one evaluation domain among many. The project transitioned its focus to discovering the computational foundations of true adaptive intelligence.

## Phase 5: The Pivot from Council-Driven Derivation to Build-Experiment-Validate

Following the design-to-foundations pivot, the project pursued a council-driven, first-principles methodology: a Knowledge Foundation Council of specialized roles (Research Theorist, Scientific Reviewer, Reductionist) progressively investigated "What is knowledge?" (Sprint 1), "What is a computational primitive?" (Sprint 2), "How should primitive claims be validated?" (Sprint 3), and finally attempted to freeze a complete scientific research standard (Sprint 3A). A parallel, less formally tracked thread (`council/main`) explored a knowledge taxonomy directly; it was later quarantined pending provenance recovery after review found it referenced prior artifacts (an "RP-003," a "subsumption decision," a "GTC" mechanism) that do not exist anywhere in the repository.

After four sprints, the program had produced a progressively more sophisticated *methodology for evaluating claims*, but no validated primitive, no architecture, no code, and no contact with real data or experiments — each sprint's conclusion was structurally the same as the last ("the previous validation approach wasn't rigorous enough"), with nothing external to the process forcing it to converge. This was identified as a serious risk: the same kind of system was both generating and critiquing every claim, and the closest historical analogue (cybernetics-era first-principles programs) has a poor track record of producing systems that actually got built.

DEC-005 records the resulting decision: ACA's primary methodology shifted to building small, real, trainable models that test specific architectural mechanisms against honest baselines, reporting negative results as prominently as positive ones, and using the council system only afterward, as a diagnostic tool for root-causing experiment failures — not as the primary discovery method. Three experiments (EXP-001, EXP-002, EXP-003; see `docs/06_experiments/Completed.md`) were run within the same session this decision was made, producing more validated, falsifiable, and reproducible findings than the entire prior council-driven phase. The Knowledge Foundation Council's work and the quarantined `council/main` material remain in the repository as permanent historical record — this pivot changed the primary method going forward, it did not retroactively invalidate work already completed.

---

**Purpose:** Provide a chronological narrative of the project's inception and evolution.
**Current Status:** Historical Record
**Historical Context:** Covers the period from the project's start to the pivot toward adaptive computation.
**Known Facts:** The project shifted focus due to limitations discovered during representation research.
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `RESEARCH_PHILOSOPHY.md`, `docs/02_vision/VISION.md`

