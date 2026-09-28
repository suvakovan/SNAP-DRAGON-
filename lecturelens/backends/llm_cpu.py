"""
CPU LLM Backend — connects to a real local inference engine.

Supported engines (in priority order):
  1. Ollama HTTP API (http://localhost:11434)
  2. llama.cpp server (OpenAI-compatible, http://localhost:8080/v1)

If neither is reachable, raises BackendUnavailable with install instructions.
This backend must NEVER return canned/template text.
"""

import time
import json
from typing import Optional

import requests

from lecturelens.backends.base import LLMBackend, BackendInfo, LLMResult, BackendUnavailable
from lecturelens.config import config
from lecturelens.logging_setup import logger

_OLLAMA_BASE = "http://localhost:11434"
_LLAMA_CPP_BASE = "http://localhost:8080/v1"

# Plausibility guard: flag if CPU TPS is outside this range
_CPU_TPS_MIN = 0.5
_CPU_TPS_MAX = 150.0


class CPULLMBackend(LLMBackend):
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.llm_model_name
        self._engine = None   # "ollama" | "llama_cpp"
        self._base_url = None

        self.info = BackendInfo(
            name=self.model_name,
            runtime="cpu-local-llm",
            device="CPU",
            verified_npu=False,
            is_real=False,
            is_simulated=True,
            details={}
        )

    def load(self) -> None:
        """Probe available local LLM engines in priority order."""
        # 1. Try Ollama
        try:
            r = requests.get(f"{_OLLAMA_BASE}/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                self._engine = "ollama"
                self._base_url = _OLLAMA_BASE
                self.info.details["engine"] = "ollama"
                self.info.details["ollama_models"] = models
                self.info.details["base_url"] = _OLLAMA_BASE
                self.info.is_real = True
                self.info.is_simulated = False
                # Pick first available model if configured one not listed
                if self.model_name not in models and models:
                    self.model_name = models[0]
                    self.info.name = self.model_name
                    logger.info(f"Model override: using available Ollama model '{self.model_name}'")
                logger.info(f"CPU LLM Backend: Ollama connected. Model: {self.model_name}")
                return
        except Exception as e:
            logger.debug(f"Ollama not reachable: {e}")

        # 2. Try llama.cpp OpenAI-compatible server
        try:
            r = requests.get(f"{_LLAMA_CPP_BASE}/models", timeout=3)
            if r.status_code == 200:
                self._engine = "llama_cpp"
                self._base_url = _LLAMA_CPP_BASE
                self.info.details["engine"] = "llama_cpp"
                self.info.details["base_url"] = _LLAMA_CPP_BASE
                self.info.is_real = True
                self.info.is_simulated = False
                logger.info(f"CPU LLM Backend: llama.cpp server connected at {_LLAMA_CPP_BASE}")
                return
        except Exception as e:
            logger.debug(f"llama.cpp server not reachable: {e}")

        # No engine found
        raise BackendUnavailable(
            "No real local LLM found. Please start one of:\n"
            "  Ollama:      ollama serve   (then: ollama pull phi3)\n"
            "  llama.cpp:   llama-server -m model.gguf --port 8080\n"
            "See docs/DECISIONS.md for more details."
        )

    def generate(
        self,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> LLMResult:
        if self.info.is_simulated:
            raise BackendUnavailable(
                "CPULLMBackend is not loaded with a real engine. Call load() first."
            )

        start_t = time.time()
        first_token_time: Optional[float] = None
        full_text = ""

        if self._engine == "ollama":
            full_text, first_token_time, prompt_tokens, completion_tokens = \
                self._generate_ollama(system, user, max_tokens, temperature)
        else:
            full_text, first_token_time, prompt_tokens, completion_tokens = \
                self._generate_llama_cpp(system, user, max_tokens, temperature)

        total_seconds = time.time() - start_t

        # Token-per-second calculation with plausibility guard
        tps_estimated = False
        if completion_tokens and completion_tokens > 0:
            tps = completion_tokens / max(total_seconds, 0.001)
        else:
            tps = len(full_text.split()) / max(total_seconds, 0.001)
            tps_estimated = True

        if not (_CPU_TPS_MIN <= tps <= _CPU_TPS_MAX):
            logger.warning(
                f"PLAUSIBILITY GUARD: CPU TPS={tps:.1f} is outside expected range "
                f"({_CPU_TPS_MIN}–{_CPU_TPS_MAX}). Flagging row as suspicious."
            )
            self.info.details["tps_suspicious"] = True

        self.info.details["tps_estimated"] = tps_estimated

        return LLMResult(
            text=full_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            time_to_first_token=first_token_time,
            total_seconds=total_seconds,
            tokens_per_second=tps
        )

    def _generate_ollama(
        self, system: str, user: str, max_tokens: int, temperature: float
    ):
        """Stream from Ollama API and return (text, ttft, prompt_tokens, completion_tokens)."""
        prompt_tokens = None
        completion_tokens = None
        first_token_time = None
        chunks = []

        payload = {
            "model": self.model_name,
            "prompt": f"{system}\n\n{user}",
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        start = time.time()
        with requests.post(
            f"{_OLLAMA_BASE}/api/generate", json=payload, stream=True, timeout=120
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                try:
                    data = json.loads(raw_line)
                except Exception:
                    continue
                token = data.get("response", "")
                if token and first_token_time is None:
                    first_token_time = time.time() - start
                chunks.append(token)
                if data.get("done"):
                    prompt_tokens = data.get("prompt_eval_count")
                    completion_tokens = data.get("eval_count")
                    break

        return "".join(chunks), first_token_time, prompt_tokens, completion_tokens

    def _generate_llama_cpp(
        self, system: str, user: str, max_tokens: int, temperature: float
    ):
        """Stream from llama.cpp OpenAI-compatible API."""
        first_token_time = None
        chunks = []
        completion_tokens = None
        prompt_tokens = None

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }

        start = time.time()
        with requests.post(
            f"{self._base_url}/chat/completions", json=payload, stream=True, timeout=120
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if line.startswith("data: "):
                    line = line[6:]
                if line == "[DONE]":
                    break
                try:
                    data = json.loads(line)
                except Exception:
                    continue
                delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta and first_token_time is None:
                    first_token_time = time.time() - start
                chunks.append(delta)
                usage = data.get("usage")
                if usage:
                    prompt_tokens = usage.get("prompt_tokens")
                    completion_tokens = usage.get("completion_tokens")

        return "".join(chunks), first_token_time, prompt_tokens, completion_tokens
