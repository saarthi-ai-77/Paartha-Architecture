"""
WorkingStateStore (SIP-002 Section 2, row 2-3) -- EXP-019's validated discipline:
reserved S_episodic partition, written via unconditional overwrite.
"""

class WorkingStateStore:
    def __init__(self, slot_names):
        self.slot_names = slot_names
        self.state = {slot: None for slot in slot_names}

    def update(self, slot, value):
        assert slot in self.state, f"Slot {slot!r} not in working state schema"
        self.state[slot] = value
        return "working_state_updated"

    def resolve(self, slot):
        return self.state.get(slot, None)
