from __future__ import annotations

import json
import os
from typing import Any

import requests

from providers.base import ModelResponse, ToolCall


class OpenRouterProvider:
    """OpenRouter chat-completions provider without the OpenAI SDK dependency."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENROUTER_API_KEY",
        base_url: str | None = None,
        default_model: str = "google/gemini-2.0-flash-001",
    ) -> None:
        self.api_key_env = api_key_env
        self.base_url = (base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/")
        self.default_model = default_model

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        text = message.get("content")

        calls: list[ToolCall] = []
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            arguments = function.get("arguments") or "{}"
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError:
                args = {}
            calls.append(ToolCall(name=function.get("name", ""), args=args))

        return ModelResponse(text=text, tool_calls=calls, raw=data)
