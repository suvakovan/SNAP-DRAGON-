"""
LLM Backend interface for Microsoft Foundry Local endpoints.
"""

import time
import requests
from typing import Optional
from lecturelens.backends.base import LLMBackend, BackendInfo, LLMResult
from lecturelens.config import config
from lecturelens.logging_setup import logger


class FoundryLLMBackend(LLMBackend):
    def __init__(self, endpoint: Optional[str] = None, model_name: Optional[str] = None):
        self.endpoint = endpoint or config.foundry_endpoint
        self.model_name = model_name or config.llm_model_name
        self.info = BackendInfo(
            name=self.model_name,
            runtime="foundry-local",
            device="CPU",  # default, will be updated if NPU variant verified
            verified_npu=False,
            details={"endpoint": self.endpoint}
        )

    def load(self) -> None:
        """Verify Foundry Local service availability."""
        try:
            resp = requests.get(f"{self.endpoint}/models", timeout=3)
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                self.info.details["available_models"] = models
                # Check if model name indicates NPU
                if any("npu" in str(m).lower() or "qnn" in str(m).lower() for m in models):
                    self.info.device = "NPU"
                    self.info.verified_npu = True
                logger.info(f"Foundry Local connected at {self.endpoint}")
            else:
                raise ConnectionError(f"Foundry local returned status code {resp.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to Foundry Local endpoint ({e}).")
            raise e

    def generate(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> LLMResult:
        """Generate LLM response via Foundry OpenAI-compatible API."""
        start_t = time.time()
        # Mock/HTTP call skeleton
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            resp = requests.post(f"{self.endpoint}/chat/completions", json=payload, timeout=30)
            total_seconds = time.time() - start_t
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                prompt_tokens = data.get("usage", {}).get("prompt_tokens")
                completion_tokens = data.get("usage", {}).get("completion_tokens")
                tps = (completion_tokens / total_seconds) if completion_tokens and total_seconds > 0 else None
                return LLMResult(
                    text=text,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    time_to_first_token=None,
                    total_seconds=total_seconds,
                    tokens_per_second=tps
                )
            else:
                raise RuntimeError(f"Foundry error: {resp.text}")
        except Exception as e:
            logger.error(f"Foundry LLM generation error: {e}")
            raise e
