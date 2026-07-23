"""
Episode/trace instrumentation for SIP-001 (docs/14_integration/SIP-001.md
Sections 8-10). Every stage of the runtime pipeline appends one TraceEntry
to the current Episode; this is the literal implementation of the
directive's "State Traceability" requirement (Input, State Owner, State
Mutation, Evaluation Result, Memory Access, Routing Decision, Composition
Decision, Output) and of the Failure Taxonomy (every anomaly is logged with
exactly one of four classifications before any code change is made).
"""

import json
import time
import dataclasses
from dataclasses import dataclass, field
from typing import Any, Optional

FAILURE_CATEGORIES = ("implementation_bug", "algorithmic_limitation",
                      "architectural_limitation", "theoretical_contradiction")


@dataclass
class TraceEntry:
    stage: str
    state_owner: str
    mutation: str
    result: Any
    timestamp: float = field(default_factory=time.time)


@dataclass
class Anomaly:
    stage: str
    description: str
    classification: str  # one of FAILURE_CATEGORIES
    detail: Any = None

    def __post_init__(self):
        assert self.classification in FAILURE_CATEGORIES, \
            f"classification must be one of {FAILURE_CATEGORIES}, got {self.classification!r}"


@dataclass
class Episode:
    episode_id: int
    request: dict
    trace: list = field(default_factory=list)
    anomalies: list = field(default_factory=list)
    response: Optional[str] = None

    def log(self, stage, state_owner, mutation, result):
        self.trace.append(TraceEntry(stage, state_owner, mutation, result))

    def flag(self, stage, description, classification, detail=None):
        self.anomalies.append(Anomaly(stage, description, classification, detail))

    def to_dict(self):
        return {
            "episode_id": self.episode_id,
            "request": self.request,
            "trace": [dataclasses.asdict(t) for t in self.trace],
            "anomalies": [dataclasses.asdict(a) for a in self.anomalies],
            "response": self.response,
        }


class EpisodeLog:
    """Append-only JSONL episode log -- Section 10's logging architecture."""
    def __init__(self, path):
        self.path = path
        self._next_id = 0

    def new_episode(self, request):
        ep = Episode(episode_id=self._next_id, request=request)
        self._next_id += 1
        return ep

    def write(self, episode):
        with open(self.path, "a") as f:
            f.write(json.dumps(episode.to_dict()) + "\n")

    def read_all(self):
        episodes = []
        try:
            with open(self.path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        episodes.append(json.loads(line))
        except FileNotFoundError:
            pass
        return episodes
