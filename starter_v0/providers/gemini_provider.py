from __future__ import annotations

import json
import os
import time
from typing import Any

from providers.base import ModelResponse, ToolCall


def _to_gemini_declarations(tools: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    declarations: list[dict[str, Any]] = []
    for item in tools or []:
        function = item.get("function", item)
        declarations.append({
            "name": function["name"],
            "description": function.get("description", ""),
            "parameters": function.get("parameters", {"type": "object", "properties": {}}),
        })
    return declarations


def _make_gemini_object(types: Any, class_name: str, **kwargs: Any) -> Any:
    factory = getattr(types, class_name, None)
    if factory is None:
        return kwargs
    return factory(**kwargs)


def _to_gemini_contents(messages: list[dict[str, str]], types: Any) -> tuple[str | None, list[Any]]:
    system_parts: list[str] = []
    contents: list[Any] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            system_parts.append(content)
        elif role == "assistant":
            contents.append(_make_gemini_object(
                types,
                "Content",
                role="model",
                parts=[_make_gemini_object(types, "Part", text=content)],
            ))
        elif role == "user":
            contents.append(_make_gemini_object(
                types,
                "Content",
                role="user",
                parts=[_make_gemini_object(types, "Part", text=content)],
            ))
    return ("\n\n".join(system_parts) if system_parts else None), contents


def _part_text(part: Any) -> str | None:
    if hasattr(part, "text"):
        return getattr(part, "text")
    if isinstance(part, dict):
        return part.get("text")
    return None


def _part_function_call(part: Any) -> Any | None:
    if hasattr(part, "function_call"):
        return getattr(part, "function_call")
    if isinstance(part, dict):
        return part.get("function_call")
    return None


def _function_call_name(call: Any) -> str | None:
    if hasattr(call, "name"):
        return getattr(call, "name")
    if isinstance(call, dict):
        return call.get("name")
    return None


def _function_call_args(call: Any) -> dict[str, Any]:
    if hasattr(call, "args"):
        return dict(getattr(call, "args") or {})
    if isinstance(call, dict):
        return dict(call.get("args") or {})
    return {}


def _build_tool_config(types: Any, declarations: list[dict[str, Any]], tool_choice: Any | None) -> Any | None:
    if not declarations or tool_choice is None:
        return None

    function_calling_config = _make_gemini_object(
        types,
        "FunctionCallingConfig",
        mode="ANY",
        allowed_function_names=[item["name"] for item in declarations],
    )
    return _make_gemini_object(
        types,
        "ToolConfig",
        function_calling_config=function_calling_config,
    )


class GeminiProvider:
    """Google Gemini API provider with normalized tool_calls output."""

    # Valid Gemini models (as of 2025-2026):
    # gemini-2.0-flash, gemini-2.0-flash-lite
    # gemini-1.5-flash, gemini-1.5-flash-8b, gemini-1.5-pro
    # gemini-2.5-flash, gemini-2.5-pro

    def __init__(
        self,
        *,
        api_key_env: str = "GEMINI_API_KEY",
        default_model: str = "gemini-3.5-flash-lite",
        max_retries: int = 5,
        retry_base_delay: float = 20.0,
    ) -> None:
        self.api_key_env = api_key_env
        self.default_model = default_model
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError("Install live provider dependency first: pip install google-genai") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        system_instruction, contents = _to_gemini_contents(messages, types)
        declarations = _to_gemini_declarations(tools)
        config_kwargs: dict[str, Any] = {"temperature": temperature}
        if temperature in (0, 0.0):
            config_kwargs.pop("temperature", None)
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if declarations:
            function_declarations = [
                _make_gemini_object(
                    types,
                    "FunctionDeclaration",
                    name=item["name"],
                    description=item.get("description", ""),
                    parameters=item.get("parameters", {"type": "object", "properties": {}}),
                )
                for item in declarations
            ]
            config_kwargs["tools"] = [
                _make_gemini_object(types, "Tool", function_declarations=function_declarations),
            ]
        tool_config = _build_tool_config(types, declarations, tool_choice)
        if tool_config is not None:
            config_kwargs["tool_config"] = tool_config

        client = genai.Client(api_key=api_key)
        _model = model or self.default_model
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                resp = client.models.generate_content(
                    model=_model,
                    contents=contents,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
                break
            except Exception as exc:
                err_str = str(exc)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = self.retry_base_delay * (attempt + 1)
                    print(f"  [gemini] Rate limited (429), waiting {wait:.0f}s (attempt {attempt + 1}/{self.max_retries})...")
                    time.sleep(wait)
                    last_exc = exc
                else:
                    raise
        else:
            raise RuntimeError(f"Gemini rate limit: exceeded {self.max_retries} retries") from last_exc

        text_parts: list[str] = []
        calls: list[ToolCall] = []

        def append_call(function_call: Any) -> None:
            name = _function_call_name(function_call)
            if name:
                calls.append(ToolCall(name=name, args=_function_call_args(function_call)))

        for candidate in getattr(resp, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                text = _part_text(part)
                if text:
                    text_parts.append(text)
                function_call = _part_function_call(part)
                if function_call:
                    append_call(function_call)

        # Some SDK versions expose function calls directly on the response.
        for function_call in getattr(resp, "function_calls", []) or []:
            append_call(function_call)

        if not text_parts:
            response_text = getattr(resp, "text", None)
            if response_text:
                text_parts.append(response_text)

        deduped_calls: list[ToolCall] = []
        seen: set[tuple[str, str]] = set()
        for call in calls:
            key = (call.name, json.dumps(call.args, ensure_ascii=False, sort_keys=True))
            if key not in seen:
                seen.add(key)
                deduped_calls.append(call)

        return ModelResponse(text="\n".join(part for part in text_parts if part) or None, tool_calls=deduped_calls, raw=resp)
