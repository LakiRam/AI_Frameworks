"""LLM factory.

Single chokepoint used by every supervisor/specialist node. Swap the backend
via the `LLM_PROVIDER` env var (`ollama` or `gemini`).
"""
from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from .config import (
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
)


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Return a cached chat model bound to the configured provider."""
    provider = (LLM_PROVIDER or "ollama").lower()

    if provider == "gemini":
        if not GOOGLE_API_KEY:
            raise RuntimeError(
                "LLM_PROVIDER=gemini but GOOGLE_API_KEY is empty. "
                "Set it in .env (get a key at https://aistudio.google.com/app/apikey)."
            )
        # Imported lazily so Ollama-only installs don't need google deps.
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=LLM_TEMPERATURE,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=LLM_TEMPERATURE,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER={provider!r}. Expected 'ollama' or 'gemini'."
    )
