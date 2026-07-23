"""
Working conversation state (SIP-001 Section 2, rows 2-3) -- the resolved
form of CTX-001's "S_working" question. EXP-019 falsified a genuinely
separate substrate: a reserved capacity partition inside the same
S_episodic mechanism, written unconditionally rather than surprise-gated,
performed identically (1.000 +/- 0.000 recall) to full structural
separation. This class implements exactly that validated discipline --
not a new substrate, a disciplined policy on the existing one.

Class A (validated, real) per SIP-001's three-way classification.
"""


class WorkingStateStore:
    """A small, fixed set of slots, each unconditionally overwritten on
    every update -- never subject to competence-gated eviction, because
    there is nothing to evict: exactly one entry per slot, always."""

    def __init__(self, slot_names):
        self.slots = {name: None for name in slot_names}

    def resolve(self, slot_name):
        """Context Resolution (SIP-001 Section 2, row 2)."""
        if slot_name not in self.slots:
            raise KeyError(f"unknown context slot: {slot_name}")
        return self.slots[slot_name]

    def update(self, slot_name, value):
        """Unconditional overwrite -- EXP-019's validated write discipline.
        No entropy gate, no eviction check: this is precisely what
        distinguishes working state from the ordinary fact schema."""
        if slot_name not in self.slots:
            raise KeyError(f"unknown context slot: {slot_name}")
        self.slots[slot_name] = value

    def snapshot(self):
        return dict(self.slots)
