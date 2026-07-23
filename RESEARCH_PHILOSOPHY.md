# Research Philosophy

## Evolution of Philosophy

### Original Objective
The research originally began with a focused objective: *Invent a fundamentally new foundation model for design generation.* The intent was to create an AI architecture specifically optimized for understanding and generating design representations, with web design acting as the primary target domain.

### How and Why the Objective Changed
During extensive research, literature review, architectural discussions, and multiple rounds of AI council critiques, the objective evolved. Observations indicated that the limitations faced in design generation were indicative of broader, fundamental limitations in how artificial intelligence handles different structural problems. The real research question was larger than design generation. It became clear that applying a single computational paradigm to all cognitive tasks was fundamentally flawed. Consequently, web design is now considered only one evaluation domain among many.

## Current Worldview

We view current frontier models as reliant on a uniform computational process (such as autoregressive token prediction over attention layers) applied indiscriminately to all problems. Our worldview is that intelligence in a complex environment cannot be optimally achieved through a single mechanism. Instead, true cognition requires structurally distinct mechanisms that are dynamically invoked.

## Current Research Philosophy

Our core philosophical tenets are:
* Intelligence should not be assumed to emerge from one universal computation.
* Different classes of cognition may require different computational primitives.
* Computation itself may need to adapt according to problem structure.
* Language is treated as an interface rather than intelligence itself.
* Architecture must emerge from first principles and evidence rather than copying existing models.

## Current Understanding of Intelligence

Intelligence is not merely the ability to predict the next token in a linguistic sequence. It is the capacity to dynamically allocate the correct cognitive primitive—whether that be observation, pattern recognition, memory retrieval, composition, or planning—to the specific structural constraints of a given problem. 

## Difference Between This Research and Conventional LLM Research

Conventional LLM research asks: *"How can we scale or route within a Transformer to improve performance?"*
This research asks: *"Should every form of cognition use the same computational process at all?"*

While conventional research assumes language is the substrate of intelligence, we treat language merely as an interface. We are searching for the underlying computational foundations of adaptive intelligence that operate below the linguistic level.

## Recent Conceptual Shift: The Nature of Knowledge

The project has recently moved beyond asking: *"What computational primitive should exist?"*
The current question is now: *"What is the intrinsic nature of different kinds of knowledge, and what computational processes naturally emerge from those structures?"*

Before searching for computational primitives, we must first understand the nature of knowledge itself. The architecture should not determine how different knowledge is processed. Instead, the intrinsic structure of each knowledge class should determine how it is represented, how it should be learned, and how it should be reasoned about. This represents the current philosophical direction and the new starting point of our research.

## Second Philosophical Shift: From Council-Derived First Principles to Build-Experiment-Validate

The "understand knowledge before proposing primitives" direction above was pursued through a council-driven methodology: propose a theory, subject it to critique, reduce it, repeat. After four sprints (Knowledge Foundation Council Sprints 1 through 3A), this had produced an increasingly refined *methodology for evaluating claims*, but no validated primitive, no architecture, and no contact with real data. Every sprint's conclusion had the same shape — "the previous validation approach wasn't rigorous enough" — with nothing external to the process forcing convergence, since the same kind of system was both proposing and critiquing every claim.

**We no longer believe philosophical derivation, on its own, is a reliable way to find a computationally efficient architecture.** As of DEC-005, the research methodology is build-experiment-validate-iterate: propose a small, concrete, trainable mechanism; implement it; test it against an honest baseline across multiple seeds; report the result — including outright falsification — before generalizing anything. The council system is retained, but demoted to a diagnostic tool used to root-cause an experiment's failure, not the primary way a claim gets established.

This does not mean the underlying research question changed. It means we no longer believe we can answer "what computational structure does this kind of knowledge need?" by argument alone — the answer has to be discovered by building the candidate structure and observing whether it actually works, the same way the field's own scaling and architecture progress has actually happened. First-principles reasoning still has a role: it's how a candidate mechanism gets proposed and how a failure gets diagnosed. It is no longer treated as sufficient, by itself, to validate a claim.

## Third Philosophical Shift: From Proposing-Then-Testing to Evidence-Driven Evolution

The Second Shift still left room for a proposal to originate from reasoning — the mechanism was invented first, then tested. `docs/14_integration/SIP-001.md` (2026-07-23), the first document in this program to generate a finding through actual system integration rather than a hypothesis-first experiment, showed something further was possible: its integration runtime *produced* a research question (why does every fact query return "I do not know"?) that no one had reasoned their way to in advance, and the same runtime's own control condition isolated the cause without a separately-designed experiment.

**As of DEC-006, this is now the required order, not an incidental discovery:** a new computational function, substrate, or module may not be proposed from conceptual reasoning alone. It must first pass a four-step gate — a reproducible runtime observation, isolation of the responsible variable, a dedicated falsification experiment, and demonstration that the current architecture cannot accommodate the result — before a new mechanism becomes proposable at all. Runtime observation, not conceptual proposal, is now the primary generator of research questions. A proposed fix that fails, or an observation that turns out explainable by existing architecture, is a first-class scientific outcome under this rule, not a failed attempt to be quietly dropped.

This does not reverse the Second Shift's empiricism — it sharpens where in the process empiricism is required to start. Reasoning can still explain a mechanism once evidence has forced its necessity; it can no longer be the thing that first proposes it.

---

**Purpose:** Document the philosophical evolution and current worldview of the research.
**Current Status:** Active
**Historical Context:** Reflects the transition from the CCA v0.1 era to the current adaptive computation focus, the DEC-005 pivot from council-derived first principles to build-experiment-validate-iterate, and the DEC-006 sharpening into Evidence-Driven Evolution.
**Known Facts:** Philosophy dictates a multi-mechanism approach to cognition. Two specific mechanisms (a competence-aware memory allocator, a validation-driven rule/family-selection module) have been empirically validated at small scale — see `docs/06_experiments/Completed.md`.
**Hypotheses:** Intelligence emerges from dynamic selection of different mechanisms; this is now being tested by building and combining validated components rather than derived by argument alone.
**Unknowns:** The complete taxonomy of necessary cognitive classes; how a dynamic scheduler would route between validated mechanisms at scale. Whether SIP-001's single-exposure-teaching finding, the first case queued under DEC-006's gate, ultimately requires an architectural change or resolves within the current design.
**References:** `RESEARCH_MANIFESTO.md`, `docs/02_vision/VISION.md`, `archive/CCA_v0.1.md`, `docs/05_research/Decisions.md` (DEC-005, DEC-006), `docs/06_experiments/Completed.md`, `docs/14_integration/SIP-001.md`
