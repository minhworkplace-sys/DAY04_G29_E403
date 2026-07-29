from __future__ import annotations

from providers.gemini_provider import GeminiProvider


class OpenAIProvider(GeminiProvider):
    """Compatibility alias that now routes through the Gemini SDK."""

    def __init__(
        self,
        *,
        api_key_env: str = "GEMINI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gemini-3.6-flash",
    ) -> None:
        # `base_url` is retained for backward compatibility with older callers.
        super().__init__(api_key_env=api_key_env, default_model=default_model)
        self.base_url = base_url
