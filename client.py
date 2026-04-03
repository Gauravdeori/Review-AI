"""OpenEnv client for the CodeReview RL environment."""

import requests
from typing import Tuple, Dict, Any
from models import Action, Observation, ResetResponse, StepRequest, StepResponse


class EnvClient:
    """HTTP client that communicates with the CodeReview environment server."""

    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        """Check if the server is alive."""
        resp = requests.get(f"{self.base_url}/health", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def reset(self, options: dict = None) -> Tuple[Observation, Dict[str, Any]]:
        """Reset the environment and return initial observation + info."""
        payload = options or {}
        resp = requests.post(
            f"{self.base_url}/reset",
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = ResetResponse(**resp.json())
        return data.observation, data.info

    def step(self, action: int) -> Tuple[Observation, float, bool, bool, Dict[str, Any]]:
        """Take a step in the environment."""
        payload = StepRequest(action=action)
        resp = requests.post(
            f"{self.base_url}/step",
            json=payload.model_dump(),
            timeout=30,
        )
        resp.raise_for_status()
        data = StepResponse(**resp.json())
        return data.observation, data.reward, data.terminated, data.truncated, data.info


if __name__ == "__main__":
    client = EnvClient()
    print("Health:", client.health())
    obs, info = client.reset()
    print("Reset obs:", obs.features)
    obs, reward, done, trunc, info = client.step(1)
    print(f"Step: reward={reward}, done={done}, score={info.get('score')}")
