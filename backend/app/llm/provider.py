"""LLM provider dispatch.

Set LLM_PROVIDER=openai and OPENAI_API_KEY to enable narrative polishing of
the deterministic reasoning output. With no key configured (the default),
`generate_text` returns None and callers fall back to template-based text,
so the project is fully reviewable without any paid API key.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import get_settings


class LLMProvider:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return self.settings.llm_provider == "openai" and bool(self.settings.openai_api_key)

    def generate_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 400) -> str | None:
        if not self.enabled:
            return None
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            content = response.choices[0].message.content
            return content.strip() if content else None
        except Exception:
            return None


@lru_cache
def get_llm_provider() -> LLMProvider:
    return LLMProvider()
