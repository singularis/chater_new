from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

logger = logging.getLogger("models_processor.ollama")


class ModelNotRunningError(RuntimeError):
    """Raised when the Ollama model is not currently running."""


def _normalize_model_name(model_name: Optional[str]) -> Optional[str]:
    if model_name is None:
        return None
    return model_name.split(":", maxsplit=1)[0]


@dataclass(frozen=True)
class _EndpointConfig:
    host: str

    def url_for(self, path: str) -> str:
        return urljoin(f"{self.host.rstrip('/')}/", path.lstrip("/"))


class OllamaClient:
    def __init__(
        self,
        host: str,
        model: str,
        request_timeout: int = 60,
        health_timeout: int = 5,
    ) -> None:
        self._config = _EndpointConfig(host=host or "")
        self.model = model
        self.request_timeout = request_timeout
        self.health_timeout = health_timeout

    def _get_running_models(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                self._config.url_for("api/ps"),
                timeout=self.health_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to contact Ollama host: %s", exc)
            raise ModelNotRunningError("Unable to reach Ollama host") from exc

        try:
            data = response.json()
        except ValueError as exc:
            logger.error("Unexpected response when checking Ollama models: %s", exc)
            raise ModelNotRunningError("Invalid response from Ollama host") from exc

        models: List[Dict[str, Any]] = (
            data.get("models", []) if isinstance(data, dict) else []
        )
        return models

    def assert_model_running(self) -> None:
        if not self.model:
            raise ModelNotRunningError("OLLAMA_MODEL environment variable is not set")

        configured = _normalize_model_name(self.model)
        for model in self._get_running_models():
            candidate = model.get("model")
            if (
                candidate == self.model
                or _normalize_model_name(candidate) == configured
            ):
                return

        raise ModelNotRunningError(
            f"Configured model '{self.model}' is not currently running on Ollama host"
        )

    def analyze_photo_with_ollama(
        self, prompt: str, photo_base64: str
    ) -> Optional[str]:
        if not prompt or not photo_base64:
            logger.warning("Prompt or photo missing; skipping Ollama analysis")
            return None

        self.assert_model_running()

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [photo_base64],
                }
            ],
            "stream": False,
        }

        try:
            response = requests.post(
                self._config.url_for("api/chat"),
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to analyze photo with Ollama: %s", exc)
            return None

        try:
            response_json = response.json()
        except ValueError as exc:
            logger.error("Invalid JSON response from Ollama: %s", exc)
            return None

        message = response_json.get("message") or {}
        analysis = message.get("content") or response_json.get("response")

        if not analysis:
            logger.warning(
                "Ollama response did not include analysis content: %s", response_json
            )

        return analysis

    def analyze_text_with_ollama(self, message: Dict[str, Any]) -> Optional[str]:
        if not isinstance(message, dict):
            logger.warning(
                "Unexpected message type for text analysis; expected dict but got %s",
                type(message),
            )
            return None

        prompt_candidates = [
            message.get("prompt"),
            message.get("question"),
            message.get("text"),
            message.get("content"),
        ]

        prompt: Optional[str] = None
        for candidate in prompt_candidates:
            if isinstance(candidate, str) and candidate.strip():
                prompt = candidate.strip()
                break

        if prompt is None:
            logger.warning(
                "Message payload did not contain a usable text prompt: %s", message
            )
            return None

        self.assert_model_running()

        respond_in_language = message.get("respond_in_language")
        system_prompt = message.get("system_prompt") or message.get("system")

        messages: List[Dict[str, str]] = []

        if isinstance(system_prompt, str) and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})

        if isinstance(respond_in_language, str) and respond_in_language.strip():
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Respond entirely in language code "
                        f"'{respond_in_language.strip()}'."
                    ),
                }
            )

        messages.append({"role": "user", "content": prompt})

        history = message.get("history")
        if isinstance(history, list):
            for entry in history:
                if (
                    isinstance(entry, dict)
                    and isinstance(entry.get("role"), str)
                    and isinstance(entry.get("content"), str)
                ):
                    messages.append(
                        {
                            "role": entry["role"],
                            "content": entry["content"],
                        }
                    )

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        try:
            response = requests.post(
                self._config.url_for("api/chat"),
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to analyze text with Ollama: %s", exc)
            return None

        try:
            response_json = response.json()
        except ValueError as exc:
            logger.error("Invalid JSON response from Ollama: %s", exc)
            return None

        message_block = response_json.get("message") or {}
        analysis = message_block.get("content") or response_json.get("response")

        if not analysis:
            logger.warning(
                "Ollama response did not include text analysis content: %s",
                response_json,
            )

        return analysis
