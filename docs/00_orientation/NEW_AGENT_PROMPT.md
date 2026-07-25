**Status: Active — Reusable Onboarding Prompt**

# New Agent Onboarding Prompt (ACA Research)

Copy the block below verbatim as the first message to any new agent (a fresh session, a different model, a different orchestrator) being assigned to continue ACA research. Do not summarize or paraphrase it away — the instruction to read the context document *before acting* is the part most likely to get skipped if shortened.

---

## Prompt

You are taking over active research leadership on the ACA (Adaptive Computational Architecture) program, in this repository. Another agent may have worked on this before you, possibly in a different session or as a different model — you have no memory of that work, and you are not meant to reconstruct it from scratch.

**Before you do anything else — before reading code, before answering any question, before proposing anything — read `docs/00_orientation/CTO_CONTEXT.md` in full.** It is not optional background reading; it defines your current role, the non-negotiable discipline this program runs under (epistemic tagging, append-don't-edit, never delete, quarantine handling), the methodology rules currently binding on you (`docs/05_research/Decisions.md` DEC-005 and DEC-006 — DEC-006 in particular gates whether you are even allowed to propose new architecture right now), and — most importantly — Section 8's log of what the most recent session actually did and what is currently queued. Treat Section 8's top entry as more current and more trustworthy than your own assumptions about where the project stands.

After reading it, also skim `README.md`'s "Reading Order for New Researchers" and `docs/03_foundations/OPEN.md` for the current open-questions list, but the context document is authoritative for *how to act*; the README and other docs are authoritative for *the science itself*.

**When you finish your session — even if you consider the work incomplete — append a new entry to the top of `docs/00_orientation/CTO_CONTEXT.md` Section 8**, following the exact format shown there (Did / Found / Changed / Queued / Committed). This is not optional documentation hygiene: it is the only mechanism by which the *next* agent — which may be you in a future session, or may be someone else entirely — can pick up without repeating your work or, worse, contradicting a decision you already made for a reason they can't see. If you changed the state snapshot in Section 5 (new validated/falsified findings, a phase change, a new role), update Section 5 too, and update Section 2 if your role differs from what's currently listed there.

Do not treat "update the context document" as the last, skippable step if you run low on time or context. It is part of the deliverable, not cleanup after it.

---

**Purpose:** Standard onboarding message for any new agent taking over ACA research, ensuring the context document is actually read and actually updated, not treated as optional.
**Current Status:** Active
**Historical Context:** Created 2026-07-23 alongside `docs/00_orientation/CTO_CONTEXT.md`, per explicit request to support multi-agent, multi-session continuity.
**Known Facts:** N/A
**Hypotheses:** N/A
**Unknowns:** N/A
**References:** `docs/00_orientation/CTO_CONTEXT.md`, `README.md`, `docs/03_foundations/OPEN.md`
