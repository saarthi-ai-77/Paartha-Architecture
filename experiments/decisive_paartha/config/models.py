"""
Model Provider Configuration for Paartha Decisive Experiment.
Configurable via environment variables (e.g. SARVAM_API_KEY, SARVAM_MODEL),
or automatically read from local .env / .env.example files.
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelConfig:
    provider: str
    api_key: Optional[str]
    model_name: str
    api_base_url: str
    temperature: float
    max_tokens: int
    timeout_seconds: int

def load_key_from_env_files() -> Optional[str]:
    # Check parent and current directories for .env or .env.example
    search_dirs = [
        os.getcwd(),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ]
    for d in search_dirs:
        for fname in [".env", ".env.example"]:
            p = os.path.join(d, fname)
            if os.path.isfile(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                k, v = line.split("=", 1)
                                k_clean = k.strip().lower()
                                v_clean = v.strip().strip("'").strip('"')
                                if k_clean in ["sarvam_api", "sarvam_api_key"]:
                                    return v_clean
                except Exception:
                    pass
    return None

def get_model_config() -> ModelConfig:
    sarvam_key = os.environ.get("SARVAM_API_KEY", "").strip() or os.environ.get("sarvam_api", "").strip()
    if not sarvam_key:
        loaded = load_key_from_env_files()
        if loaded:
            sarvam_key = loaded

    sarvam_model = os.environ.get("SARVAM_MODEL", "sarvam-105b-conversations").strip()
    api_base = os.environ.get("SARVAM_BASE_URL", "https://api.sarvam.ai/v1/chat/completions").strip()
    
    provider = "sarvam" if sarvam_key else "simulated_frontier"
    
    return ModelConfig(
        provider=provider,
        api_key=sarvam_key if sarvam_key else None,
        model_name=sarvam_model,
        api_base_url=api_base,
        temperature=float(os.environ.get("MODEL_TEMPERATURE", "0.2")),
        max_tokens=int(os.environ.get("MODEL_MAX_TOKENS", "2048")),
        timeout_seconds=int(os.environ.get("MODEL_TIMEOUT", "45"))
    )
