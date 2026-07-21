**Status: Active** (populated 2026-07-18 per DEC-005; prior placeholder superseded)

# Cognitive Primitives → Rule/Family-Selection Module

*Terminology note: this file predates DEC-005 and was named for the council-driven search for a single "computational primitive" (Distinction, Constraint, etc. — see `council/knowledge-foundation/`, never validated). No such primitive has been validated. What has been validated under the current methodology is a much narrower, concrete component described below; the file is kept at this path for continuity but its content reflects the build-experiment-validate track, not the primitive-search track.*

## Validated: Constrained, Validation-Selected Rule Modules (EXP-002, EXP-003)

**EXP-002 finding:** a "rule module" — a component meant to apply an operator to an operand compositionally — does not generalize to unseen (operator, operand) combinations if its operator representation is a generic, high-parameter factorization (a learned or fixed operand encoding combined with an unconstrained linear per-operator layer, ~30 parameters). This failed identically across a learned embedding, a fixed sin/cos encoding, and a full weight-decay sweep (0 to 1.0) — always exactly 0% held-out accuracy. It succeeds — exactly, recovering the true parameters — when the operator is instead constrained to a 2-parameter family matching the true structure of the domain (in the tested case, rotation/reflection of a cyclic group).

**EXP-003 finding:** given a small library of candidate constrained families, a model can automatically select the correct one per operator — but only if selection is driven by measured performance on a held-out split, not by training loss or a fixed complexity penalty (both of those were tested and reliably failed, always drifting toward the more expressive, non-generalizing option).

Full methodology, code, and honest limitations, including a caveat on interpretability: `docs/06_experiments/Completed.md` (EXP-002, EXP-003); code at `experiments/exp002_factorized_rule_module/`, `experiments/exp003_family_selection/`.

**This component is now formally incorporated into ACA v0.4** (`docs/04_architecture/ACA_v0.4_Architecture.md`, Section 2.1) as the COMPOSE function's typed module library, and its validated selection logic (Section 2.3) as SELECT's held-out-driven family choice. See that document for how this fits alongside the memory substrate and the still-open routing/scheduling questions below.

## The Open Problem This Surfaces (not yet solved)

Both experiments required a human to already know the correct constrained family existed and belonged in the candidate library. **The unresolved question is how a rule module discovers or expands its family library for an unfamiliar domain, rather than a human hand-designing the correct family per task** — this is now considered the central open problem for this component, more important than "can a constrained family generalize" (already answered: yes).

## Relationship to Prior (Council-Era) Primitive Concepts

The Knowledge Foundation Council's multi-sprint search for a single computational primitive (Distinction, Constraint, Difference, Relation — `council/knowledge-foundation/DECISIONS.md`) is a different, superseded research line (DEC-005). Nothing in that search was validated, and nothing here should be read as vindicating or refuting it — the current validated finding is about *how to build a generalizing rule/operator component*, not about identifying a single universal primitive concept.

---

**Purpose:** Document the architecture's rule/operator component, distinguishing validated mechanism from the open family-discovery problem.
**Current Status:** Active — narrow mechanism validated, central problem (family discovery) open
**Historical Context:** Populated 2026-07-18 per DEC-005; previously a placeholder stating "architecture research has not yet begun," and before that implicitly tied to the now-superseded council-driven primitive search.
**Known Facts:** Constrained families generalize exactly when matched to true structure; validation-driven selection correctly picks among a given library (EXP-002, EXP-003, 5 seeds each, reproducible).
**Hypotheses:** A larger family library plus a family-discovery (not just family-selection) mechanism could handle domains without a pre-known correct family.
**Unknowns:** How to discover/construct new families automatically; behavior with more than 2 candidate families; behavior beyond cyclic-group arithmetic.
**References:** `docs/06_experiments/Completed.md`, `docs/03_foundations/ACCEPTED.md` (FP-2, FP-3), `docs/03_foundations/OPEN.md`
