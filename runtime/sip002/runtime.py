"""
ACASustainedRuntime (SIP-002 / Phase IV Orchestrator) -- Sustained autonomous runtime
combining interaction, recall, composition, working context, memory micro-replay,
and offline mentor curriculum generation + knowledge promotion.
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
from mentor import MentorModule

WAS, BORN, IN, DOT = 0, 1, 2, 3
N_SPECIAL = 4
MAX_NAMES, MAX_CITIES = 200, 50
NAME_BASE, CITY_BASE = N_SPECIAL, N_SPECIAL + MAX_NAMES
VOCAB_SIZE = CITY_BASE + MAX_CITIES
SEQ_LEN = 6
CITY_POS = 4
CONFIDENCE_THRESHOLD_NATS = 1.5

class ACASustainedRuntime:
    def __init__(self, episode_log_path, capacity=30, micro_replay_steps=5, device=None, policy_controller=None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.working_state = WorkingStateStore(slot_names=["topic", "user_intent"])
        self.memory = EpisodicMemory(capacity=capacity)
        self.recall_model = CausalTransformerLM(VOCAB_SIZE, SEQ_LEN).to(self.device)
        self.opt = torch.optim.Adam(self.recall_model.parameters(), lr=3e-4)
        self.compose = StructureMatchedCompose(self.device)
        self.compose_opt = torch.optim.Adam(self.compose.model.parameters(), lr=1e-2)
        self.episode_log = EpisodeLog(episode_log_path)
        self.mentor = MentorModule(self.device)
        self.micro_replay_steps = micro_replay_steps
        self.policy_controller = policy_controller
        self.name_ids, self.city_ids = {}, {}
        self.rng = np.random.RandomState(0)

    def _name_id(self, name):
        if name not in self.name_ids:
            assert len(self.name_ids) < MAX_NAMES, "MAX_NAMES exceeded"
            self.name_ids[name] = NAME_BASE + len(self.name_ids)
        return self.name_ids[name]

    def _city_id(self, city):
        if city not in self.city_ids:
            assert len(self.city_ids) < MAX_CITIES, "MAX_CITIES exceeded"
            self.city_ids[city] = CITY_BASE + len(self.city_ids)
        return self.city_ids[city]

    def _fact_sequence(self, name_tok, city_tok):
        return [name_tok, WAS, BORN, IN, city_tok, DOT]

    def handle_request(self, request):
        ep = self.episode_log.new_episode(request)
        ep.log("user_request", "ingress", "none", request)

        kind = request.get("kind")
        if kind == "context_update":
            self.working_state.update(request["slot"], request["value"])
            ep.log("context_resolution", "WorkingStateStore", "unconditional_overwrite",
                   {"slot": request["slot"], "value": request["value"]})
            ep.response = "context_updated"

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
            ep.flag("routing", f"unrecognized request kind: {kind!r}", "implementation_bug", detail={"request": request})
            ep.response = None

        self._store_experience(ep)
        self.episode_log.write(ep)
        return ep

    def _store_experience(self, ep):
        entropy_proxy = getattr(ep, "_entropy_for_storage", None)
        if entropy_proxy is None:
            entropy_proxy = 3.0
        outcome = self.memory.unconditional_write("episode", ep.episode_id, ep.response, entropy_proxy)
        ep.log("experience_storage", "EpisodicMemory", "unconditional_write(episode schema)", outcome)

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

        # SOS-001 Section 4 discipline: unconditional write to S_episodic
        outcome = self.memory.unconditional_write("fact", name, city, ent, policy_controller=self.policy_controller)
        ep.log("memory_access", "EpisodicMemory", "unconditional_write", outcome)

        # EXP-022 / EXP-023 validated accommodation: 5-step local micro-replay
        if self.micro_replay_steps > 0:
            stored = [k.split(":", 1)[1] for k in self.memory.store if k.startswith("fact:")]
            if stored:
                for _ in range(self.micro_replay_steps):
                    sub = self.rng.choice(stored, size=min(8, len(stored)), replace=True)
                    seqs = [self._fact_sequence(self._name_id(fn), self._city_id(self.memory.get("fact", fn))) for fn in sub]
                    seqs_t = torch.tensor(seqs, dtype=torch.long, device=self.device)
                    l_rep = F.cross_entropy(self.recall_model(seqs_t)[:, :-1, :].reshape(-1, VOCAB_SIZE), seqs_t[:, 1:].reshape(-1))
                    self.opt.zero_grad(); l_rep.backward(); self.opt.step()
                ep.log("memory_access", "MicroReplay", f"{self.micro_replay_steps}_step_replay", {"replayed_count": len(stored)})

        ep.response = f"learned: {name} -> {city}"

    def _handle_query_fact(self, request, ep):
        name = request["name"]
        if name not in self.name_ids:
            ep.log("memory_access", "EpisodicMemory", "read_miss", {"name": name})
            ep.response = "I do not know."
            self._create_learning_opportunity(name, ep)
            return

        name_tok = self._name_id(name)
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
            actions, _ = self.compose.run(tokens)
            ep.log("composition_decision", "StructureMatchedCompose", "parse_and_compose",
                   {"tokens": tokens, "actions": actions})
            ep.response = " ".join(actions)
        except Exception as e:
            ep.flag("composition_decision", f"compose pathway raised: {e}", "implementation_bug", detail={"tokens": tokens})
            ep.response = None

    def train_compose_on(self, train_pairs, steps=200, batch_size=32):
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
        outcome = self.memory.unconditional_write("unknown", name, True, entropy=999.0)
        ep.log("memory_access", "EpisodicMemory", "unconditional_write(unknown schema)", outcome)

    def run_offline_mentor_cycle(self):
        curr_names, curr_status = self.mentor.generate_mentor_curriculum(self.memory)
        staging_q = getattr(self.policy_controller, "staging_queue", None) if self.policy_controller else None
        promo_res = self.mentor.execute_knowledge_promotion(
            self.memory, self.recall_model, self.opt,
            self.name_ids, self.city_ids, self._fact_sequence,
            VOCAB_SIZE, steps=30, batch_size=32, rng=self.rng,
            staging_queue=staging_q
        )
        return {
            "curriculum_status": curr_status,
            "curriculum_names": curr_names,
            "promotion_results": promo_res
        }
