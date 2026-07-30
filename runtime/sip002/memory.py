"""
EpisodicMemory (SIP-002 / SOS-001 / EXP-022 / EXP-023) -- Shared memory store
with SOS-001 unconditional write discipline for primary entries and FIFO/LRU eviction.
"""

import numpy as np

class EpisodicMemory:
    def __init__(self, capacity=30):
        self.capacity = capacity
        self.store = {}  # namespaced_key -> (value, entropy)
        self.running_ent = []

    @staticmethod
    def namespace(schema, raw_key):
        return f"{schema}:{raw_key}"

    def get(self, schema, raw_key):
        v = self.store.get(self.namespace(schema, raw_key))
        return v[0] if v else None

    def coverage(self, schema, raw_keys):
        keys = [self.namespace(schema, k) for k in raw_keys]
        covered = sum(1 for k in keys if k in self.store)
        return covered / len(keys) if keys else 0.0

    def gated_write(self, schema, raw_key, value, entropy):
        """EXP-001/018 surprise gating policy"""
        key = self.namespace(schema, raw_key)
        self.running_ent.append(float(entropy))
        if key in self.store:
            return "skipped_already_present"
        median = np.median(self.running_ent[-500:]) if len(self.running_ent) >= 10 else entropy
        if entropy <= median:
            return "skipped_not_surprising"
        if len(self.store) >= self.capacity:
            worst_k = min(self.store.keys(), key=lambda k: self.store[k][1])
            if self.store[worst_k][1] < median:
                del self.store[worst_k]
            else:
                return "skipped_write_starvation"
        self.store[key] = (value, float(entropy))
        return "written_gated"

    def unconditional_write(self, schema, raw_key, value, entropy, policy_controller=None):
        """SOS-001 Section 4 discipline: unconditional write for primary entries
        (facts, unknown, episode, working state). FIFO eviction when full."""
        key = self.namespace(schema, raw_key)
        if len(self.store) >= self.capacity and key not in self.store:
            first_k = next(iter(self.store))
            if policy_controller is not None:
                parts = first_k.split(":", 1)
                ev_schema = parts[0]
                ev_raw_key = parts[1] if len(parts) > 1 else first_k
                ev_val, ev_ent = self.store[first_k]
                policy_controller.on_before_evict(ev_schema, ev_raw_key, ev_val, ev_ent)
            del self.store[first_k]
        self.store[key] = (value, float(entropy))
        return "written_unconditional"
