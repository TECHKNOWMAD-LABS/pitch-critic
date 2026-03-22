"""LLM interface wrapping the Anthropic client."""

import os
from typing import Callable

import anthropic

LLMCaller = Callable[[str, str], str]

_default_caller: LLMCaller | None = None


def make_llm_caller(api_key: str | None = None) -> LLMCaller:
    """Create an LLM caller backed by Claude Opus 4.6."""
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def call(system: str, user: str) -> str:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text  # type: ignore[union-attr]

    return call


def get_default_caller() -> LLMCaller:
    """Return the module-level default caller (lazy-initialised)."""
    global _default_caller
    if _default_caller is None:
        _default_caller = make_llm_caller()
    return _default_caller
