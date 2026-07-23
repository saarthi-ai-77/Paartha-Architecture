"""
ACARuntime -- the orchestrator implementing SIP-001 Section 6 (Execution
Lifecycle) and Section 7 (Learning Lifecycle). Wires together every
component in Section 2's table behind ONE `handle_request` entry point,
logging every stage into an Episode (Section 8-10) and routing every
detected anomaly through the four-category failure taxonomy (Section 9).

Fixed, non-learned routing throughout (EXP-004/EXP-021's validated design)
-- request `kind` determines the pathway directly; no learned dispatch
(RC-02, stubbed in stubs.py) is used.
"""

import torch
import torch.nn.functional as F
import numpy as np

from context_state import WorkingStateStore
from memory import EpisodicMemory
from evaluate import evaluate_local, knowledge_boundary, evaluate_generalization
from compose import StructureMatchedCompose
from recall_model import CausalTransformerLM
from episode import EpisodeLog
import stubs

WAS, BORN, IN, DOT = 0, 1, 2, 3
N_SPECIAL = 4
MAX_NAMES, MAX_CITIES = 50, 20
NAME_BASE, CITY_BASE = N_SPECIAL, N_SPECIAL + MAX_NAMES
VOCAB_SIZE = CITY_BASE + MAX_CITIES
SEQ_LEN = 6
CITY_POS = 4
CONFIDENCE_THRESHOLD_NATS = 1.5  # a fixed hyperparameter, not a general calibrated signal (evaluate.py's own caveat)


class ACARuntime:
    def __init__(self, episode_log_path, device=None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.working_state = WorkingStateStore(slot_names=["topic", "last_speaker_intent"])
        self.memory = EpisodicMemory(capacity=30)  # deliberately small: forces real capacity pressure, per EXP-018/019
        self.recall_model = CausalTransformerLM(VOCAB_SIZE, SEQ_LEN).to(self.device)
        self.opt = torch.optim.Adam(self.recall_model.parameters(), lr=3e-4)
        self.compose = StructureMatchedCompose(self.device)
        self.compose_opt = torch.optim.Adam(self.compose.model.parameters(), lr=1e-2)
        self.episode_log = EpisodeLog(episode_log_path)
        self.name_ids, self.city_ids = {}, {}
        self.rng = np.random.RandomState(0)

    # -- vocabulary --------------------------------------------------
    def _name_id(self, name):
        if name not in self.name_ids:
            assert len(self.name_ids) < MAX_NAMES, "MAX_NAMES exceeded -- fixed vocab, by design (Core Principle: no new dynamic-vocab mechanism introduced)"
            self.name_ids[name] = NAME_BASE + len(self.name_ids)
        return self.name_ids[name]

    def _city_id(self, city):
        if city not in self.city_ids:
            assert len(self.city_ids) < MAX_CITIES
            self.city_ids[city] = CITY_BASE + len(self.city_ids)
        return self.city_ids[city]

    def _fact_sequence(self, name_tok, city_tok):
        return [name_tok, WAS, BORN, IN, city_tok, DOT]

    # -- pipeline ------------------------------------------------------
    def handle_request(self, request):
        ep = self.episode_log.new_episode(request)
        ep.log("user_request", "ingress", "none", request)

        kind = request.get("kind")
        if kind == "context_update":
            self.working_state.update(request["slot"], request["value"])
            ep.log("context_resolution", "WorkingStateStore", "unconditional_overwrite",
                   {"slot": request["slot"], "value": request["value"]})
            ep.response = "context updated"

        elif kind == "context_query":
            val = self.working_state.resolve(request["slot"])
            ep.log("context_resolution", "WorkingStateStore", "read", {"slot": request["slot"], "value": val})
            ep.response = val

        elif kind == "teach_fact":
            self._handle_teach_fact(request, ep)

        elif kind == "query_fact":
            self._handle_query_fact(request, ep)

        elif kind == "scan_command":
            self._handle_scan_command(request, ep)

        else:
            ep.flag("routing", f"unrecognized request kind: {kind!r}", "implementation_bug",
                    detail={"request": request})
            ep.response = None

        self._store_experience(ep)
        self.episode_log.write(ep)
        return ep

    def _store_experience(self, ep):
        """Experience Storage (SIP-001 Section 2, row 10) -- writes the
        episode into the SAME shared EpisodicMemory used by the fact
        schema, under an 'episode' schema, via the ordinary gated_write
        path (not unconditional) -- this is what actually exercises
        Section 14's open question: does a THIRD schema sharing capacity
        with facts reproduce EXP-019's write-starvation mechanism, which
        no prior experiment (EXP-018/019 tested at most two schemas)
        actually tested."""
        entropy_proxy = getattr(ep, "_entropy_for_storage", None)
        if entropy_proxy is None:
            entropy_proxy = 3.0  # a fixed, moderate default for context-only requests with no evaluation score
        outcome = self.memory.gated_write("episode", ep.episode_id, ep.response, entropy_proxy)
        ep.log("experience_storage", "EpisodicMemory", "gated_write(episode schema)", outcome)
        if outcome == "skipped_write_starvation":
            ep.flag("experience_storage", "episode write starved by fact-schema capacity contention",
                    "architectural_limitation",
                    detail={"episode_id": ep.episode_id,
                            "mechanism": "third-schema instance of EXP-019's write-starvation pattern"})

    def _handle_teach_fact(self, request, ep):
        name, city = request["name"], request["city"]
        name_tok, city_tok = self._name_id(name), self._city_id(city)
        seq = torch.tensor([self._fact_sequence(name_tok, city_tok)], dtype=torch.long, device=self.device)
        logits = self.recall_model(seq)
        loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seq[:, 1:].reshape(-1))
        self.opt.zero_grad(); loss.backward(); self.opt.step()
        ep.log("routing", "fixed_router", "dispatch", "recall_pathway")

        with torch.no_grad():
            ent = evaluate_local(logits, CITY_POS - 1)[0].item()
        ep.log("evaluation", "evaluate_local", "score", {"entropy": ent})
        ep._entropy_for_storage = ent

        outcome = self.memory.gated_write("fact", name, city, ent)
        ep.log("memory_access", "EpisodicMemory", "gated_write", outcome)
        if outcome == "skipped_write_starvation":
            ep.flag("memory_access", "fact write starved by capacity contention", "algorithmic_limitation",
                    detail={"name": name, "mechanism": "EXP-019's named write-starvation pattern"})

        ep.response = f"learned: {name} -> {city}"

    def _handle_query_fact(self, request, ep):
        name = request["name"]
        if name not in self.name_ids:
            ep.log("memory_access", "EpisodicMemory", "read_miss", {"name": name})
            ep.response = "I do not know."
            self._create_learning_opportunity(name, ep)
            return

        name_tok = self._name_id(name)
        # Position CITY_POS (4) is a placeholder, never read: CITY_POS-1's logits (position 3, "IN")
        # are computed under the causal mask, which cannot see position 4 regardless of its value.
        # Using DOT here (rather than name_tok, an earlier harmless-but-misleading placeholder)
        # keeps the sequence shape self-documenting -- classified as an Implementation Bug (SIP-001
        # Section 9), fixed directly; it was behaviorally inert, not the cause of Section 19's finding.
        seq = torch.tensor([[name_tok, WAS, BORN, IN, DOT, DOT]], dtype=torch.long, device=self.device)
        with torch.no_grad():
            logits = self.recall_model(seq)
            pred_city_tok = logits[:, CITY_POS - 1, :].argmax(dim=-1).item()
            ent = evaluate_local(logits, CITY_POS - 1)[0].item()
        ep.log("routing", "fixed_router", "dispatch", "recall_pathway")
        ep.log("evaluation", "evaluate_local", "score", {"entropy": ent})
        ep._entropy_for_storage = ent

        stored = self.memory.get("fact", name)
        used_memory = stored is not None
        pred_city_tok = self._city_id(stored) if used_memory else pred_city_tok
        ep.log("memory_access", "EpisodicMemory", "read", {"coverage": used_memory})

        confident = knowledge_boundary(ent, CONFIDENCE_THRESHOLD_NATS) or used_memory
        city_by_tok = {v: k for k, v in self.city_ids.items()}
        if confident and pred_city_tok in city_by_tok:
            ep.response = city_by_tok[pred_city_tok]
        else:
            ep.response = "I do not know."
            self._create_learning_opportunity(name, ep)

    def _handle_scan_command(self, request, ep):
        ep.log("routing", "fixed_router", "dispatch", "compose_pathway")
        tokens = request["tokens"]
        try:
            actions, logits_seq = self.compose.run(tokens)
            ep.log("composition_decision", "StructureMatchedCompose", "parse_and_compose",
                   {"tokens": tokens, "actions": actions})
            ep.response = " ".join(actions)
        except Exception as e:
            ep.flag("composition_decision", f"compose pathway raised: {e}", "implementation_bug",
                    detail={"tokens": tokens})
            ep.response = None

    def train_compose_on(self, train_pairs, steps=200, batch_size=32):
        """Not part of the per-request pipeline -- offline training of the
        compose pathway's tiny learned lookup, exactly as EXP-020 did."""
        import compose as compose_mod
        compiled = []
        for toks, out in train_pairs:
            slots = compose_mod.compile_slots(toks)
            true_idx = torch.tensor([compose_mod.ACTION_STOI[t] for t in out], dtype=torch.long)
            compiled.append((slots, true_idx))
        for _ in range(steps):
            idx = self.rng.randint(0, len(compiled), size=min(batch_size, len(compiled)))
            table = self.compose.model()
            loss = 0.0
            for i in idx:
                slots, true_idx = compiled[i]
                logits_seq = compose_mod.build_logit_sequence(slots, table, self.device)
                loss = loss + F.cross_entropy(logits_seq, true_idx.to(self.device))
            loss = loss / len(idx)
            self.compose_opt.zero_grad(); loss.backward(); self.compose_opt.step()

    def _create_learning_opportunity(self, name, ep):
        """Learning Opportunity Creation (SIP-001 Section 2, row 13) --
        CTX-001 Section 3's reduction: a schema-tagged episodic entry, not
        new machinery."""
        outcome = self.memory.unconditional_write("unknown", name, True, entropy=999.0)
        ep.log("memory_access", "EpisodicMemory", "unconditional_write(unknown schema)", outcome)

        curriculum = stubs.generate_curriculum([name])
        ep.log("learning_lifecycle", "stubs.generate_curriculum", "no_op", curriculum)

        val_result, val_status = evaluate_generalization(None, held_out_labels=None)
        ep.log("learning_lifecycle", "evaluate_generalization", val_status, val_result)

    def run_knowledge_promotion(self):
        """Knowledge Promotion (SIP-001 Section 2, row 16) -- EXP-010's
        exact, already-falsified one-time replay burst. Invoked
        explicitly (not per-request), matching Benchmark A's stage-
        boundary consolidation timing."""
        def loss_fn(model, opt, batch_names, _make_seq):
            seqs = []
            for name in batch_names:
                if name not in self.name_ids:
                    continue
                stored_city = self.memory.get("fact", name)
                if stored_city is None:
                    continue
                seqs.append(self._fact_sequence(self._name_id(name), self._city_id(stored_city)))
            if not seqs:
                return
            seqs_t = torch.tensor(seqs, dtype=torch.long, device=self.device)
            logits = model(seqs_t)
            loss = F.cross_entropy(logits[:, :-1, :].reshape(-1, VOCAB_SIZE), seqs_t[:, 1:].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()

        return self.memory.consolidate_replay("fact", self.recall_model, self.opt,
                                               replay_steps=20, replay_batch=32,
                                               make_sequence_fn=self._fact_sequence,
                                               loss_fn=loss_fn, rng=self.rng)
