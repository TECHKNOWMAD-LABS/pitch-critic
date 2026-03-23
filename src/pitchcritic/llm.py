"""LLM interface wrapping the Anthropic client."""

import hashlib
import os
from functools import lru_cache
from typing import Callable

import anthropic

LLMCaller = Callable[[str, str], str]

_default_caller: LLMCaller | None = None

# In-memory cache for LLM responses keyed by content hash
_response_cache: dict[str, str] = {}
MAX_CACHE_SIZE = 128


def _cache_key(system: str, user: str) -> str:
    """Create a stable hash key for caching LLM responses."""
    combined = f"{system}||{user}"
    return hashlib.sha256(combined.encode()).hexdigest()


def make_llm_caller(
    api_key: str | None = None,
    *,
    enable_cache: bool = True,
    timeout: float = 120.0,
) -> LLMCaller:
    """Create an LLM caller backed by Claude Opus 4.6."""
    client = anthropic.Anthropic(
        api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
        timeout=timeout,
    )

    def call(system: str, user: str) -> str:
        if enable_cache:
            key = _cache_key(system, user)
            if key in _response_cache:
                return _response_cache[key]

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        result = response.content[0].text  # type: ignore[union-attr]

        if enable_cache:
            if len(_response_cache) >= MAX_CACHE_SIZE:
                oldest = next(iter(_response_cache))
                del _response_cache[oldest]
            _response_cache[key] = result

        return result

    return call


def get_default_caller() -> LLMCaller:
    """Return the module-level default caller (lazy-initialised)."""
    global _default_caller
    if _default_caller is None:
        _default_caller = make_llm_caller()
    return _default_caller
