"""
Episode and EpisodeLog (SIP-002) -- Full request instrumentation and anomaly logging.
"""

import time
import json
import os

class Episode:
    def __init__(self, episode_id, request):
        self.episode_id = episode_id
        self.timestamp = time.time()
        self.request = request
        self.trace = []
        self.anomalies = []
        self.response = None
        self._entropy_for_storage = None

    def log(self, stage, owner, mutation, result):
        self.trace.append({
            "stage": stage,
            "owner": owner,
            "mutation": mutation,
            "result": str(result)
        })

    def flag(self, stage, anomaly, classification, detail=None):
        self.anomalies.append({
            "stage": stage,
            "anomaly": anomaly,
            "classification": classification,
            "detail": detail or {}
        })

    def to_dict(self):
        return {
            "episode_id": self.episode_id,
            "timestamp": self.timestamp,
            "request": self.request,
            "response": self.response,
            "trace": self.trace,
            "anomalies": self.anomalies
        }

class EpisodeLog:
    def __init__(self, log_path):
        self.path = log_path
        self.counter = 0
        os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)

    def new_episode(self, request):
        self.counter += 1
        return Episode(f"ep_{self.counter:05d}", request)

    def write(self, episode):
        with open(self.path, "a") as f:
            f.write(json.dumps(episode.to_dict()) + "\n")

    def read_all(self):
        if not os.path.exists(self.path):
            return []
        episodes = []
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    episodes.append(json.loads(line))
        return episodes
