"""
MentorModule (SIP-002 / CTX-001 / DEC-006) -- Active Offline Mentor Module:
scans logged "unknown"-schema entries, synthesizes gap-fill mentor curriculum,
and executes offline knowledge promotion into S_semantic (backbone).
"""

import torch
import torch.nn.functional as F

class MentorModule:
    def __init__(self, device):
        self.device = device

    def generate_mentor_curriculum(self, memory):
        """Scans 'unknown'-schema entries in EpisodicMemory and returns target names."""
        unknown_keys = [k for k in memory.store if k.startswith("unknown:")]
        if not unknown_keys:
            return [], "no_unknowns_logged"
        raw_names = [k.split(":", 1)[1] for k in unknown_keys]
        return raw_names, f"curriculum_generated_for_{len(raw_names)}_unknowns"

    def execute_knowledge_promotion(self, memory, model, opt, name_ids, city_ids, fact_seq_fn, vocab_size, steps=20, batch_size=32, rng=None, staging_queue=None):
        """Executes offline batch promotion over facts stored in memory and staging queue."""
        keys = [k for k in memory.store if k.startswith("fact:")]
        fact_dict = {k.split(":", 1)[1]: memory.store[k][0] for k in keys}
        if staging_queue:
            for k, (v, _) in staging_queue.items():
                fact_dict[k] = v

        if not fact_dict:
            return "no_facts_in_memory"

        raw_names = list(fact_dict.keys())
        if rng is None:
            import numpy as np
            rng = np.random.RandomState(0)

        step_losses = []
        for _ in range(steps):
            batch = rng.choice(raw_names, size=min(batch_size, len(raw_names)), replace=True)
            seqs = []
            for name in batch:
                city = fact_dict.get(name)
                if city is not None and name in name_ids and city in city_ids:
                    seqs.append(fact_seq_fn(name_ids[name], city_ids[city]))

            if not seqs:
                continue

            seqs_t = torch.tensor(seqs, dtype=torch.long, device=self.device)
            logits = model(seqs_t)
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, vocab_size), seqs_t[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()
            step_losses.append(loss.item())

        mean_loss = sum(step_losses) / len(step_losses) if step_losses else 0.0
        return {
            "status": "promotion_complete",
            "steps": len(step_losses),
            "mean_loss": mean_loss,
            "facts_promoted_count": len(raw_names)
        }
