"""
EpisodicMemory (SIP-001 Section 2, row 4/10/13) -- the exact competence-
gated write/evict mechanism validated by EXP-001 (static distribution) and
found NOT to prevent forgetting under staged continual pressure by EXP-018,
with the one tested fix (one-time consolidation replay) also falsified by
EXP-010. Reimplemented faithfully here, not improved upon -- per SIP-001's
Core Principle, this is Class B (real, known-limited), instrumented to
surface its known limitation rather than hide it.

Schemas (fact / unknown / episode) share ONE physical store, namespaced by
key per docs/13_state_model/SOS-001.md Section 3's convention (the same fix
IVS-001's prerequisite audit already required for routing vs. facts) --
this is the mechanism the integration test (Section 12) specifically
exercises for write-starvation risk under three co-resident schemas, not
just the two EXP-019 already tested.
"""

import numpy as np


class EpisodicMemory:
    def __init__(self, capacity):
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
        """EXP-001/018's exact policy: write only if surprising (entropy
        above the running median), evict only the currently-lowest-entropy
        entry, and only if that entry is itself below the median. Known
        limitation (EXP-018): under sequential pressure this evicts
        exactly the content most at risk of being forgotten, right when it
        becomes vulnerable -- not fixed here, faithfully reproduced."""
        key = self.namespace(schema, raw_key)
        self.running_ent.append(float(entropy))
        if key in self.store:
            return "skipped_already_present"
        median = np.median(self.running_ent[-500:]) if len(self.running_ent) >= 10 else entropy
        if entropy <= median:
            return "skipped_not_surprising"
        if len(self.store) >= self.capacity:
            worst_key, worst_ent = None, None
            for k, (_, ent) in self.store.items():
                if worst_ent is None or ent < worst_ent:
                    worst_key, worst_ent = k, ent
            if worst_ent is not None and worst_ent < median:
                del self.store[worst_key]
            else:
                return "skipped_write_starvation"  # SIP-001 Section 2 row 4 / EXP-019's named mechanism
        self.store[key] = (value, float(entropy))
        return "written"

    def unconditional_write(self, schema, raw_key, value, entropy):
        """EXP-019's validated discipline for reserved-partition content
        (working state, and here also used for the episode schema, which
        -- like working state -- tracks 'what just happened', not a
        competing pool of equally-important facts). Never evicted by this
        method; capacity for these schemas must be managed by the caller
        reserving room, exactly as EXP-019's reserved_partition condition did."""
        key = self.namespace(schema, raw_key)
        self.store[key] = (value, float(entropy))
        return "written_unconditional"

    def consolidate_replay(self, schema, model, opt, replay_steps, replay_batch, make_sequence_fn,
                            loss_fn, rng):
        """Knowledge Promotion (SIP-001 Section 2, row 16) -- EXP-010's
        exact one-time replay-burst mechanism, already falsified for
        staged continual pressure (0.160 +/- 0.028 vs. 0.158 +/- 0.027
        baseline -- no measurable improvement). Reproduced exactly, not
        replaced, per the Core Principle: no new consolidation mechanism
        is invented here."""
        keys = [k for k in self.store if k.startswith(f"{schema}:")]
        if not keys:
            return "no_content_to_consolidate"
        raw_keys = [k.split(":", 1)[1] for k in keys]
        for _ in range(replay_steps):
            batch = rng.choice(raw_keys, size=min(replay_batch, len(raw_keys)), replace=True)
            loss_fn(model, opt, batch, make_sequence_fn)
        return f"replayed_{replay_steps}_steps_over_{len(raw_keys)}_entries"
