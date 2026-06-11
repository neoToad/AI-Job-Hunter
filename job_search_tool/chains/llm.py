"""LLM factory — returns a configured ChatOllama instance.

All other chain modules import `get_llm` from here so that switching the
model or base URL only requires editing one place (the .env file / config).
"""

from __future__ import annotations

from langchain_ollama import ChatOllama

import config


def get_llm(temperature: float = 0.3) -> ChatOllama:
    """Return a ChatOllama instance configured from `config.py`.

    Args:
        temperature: Sampling temperature passed to the model. Lower values
            (e.g. 0.1) give more deterministic output, useful for structured
            extraction. Higher values (e.g. 0.5) give more natural prose.
            Defaults to 0.3 — a reasonable middle ground.

    Returns:
        A `ChatOllama` instance bound to the configured `OLLAMA_BASE_URL` and
        `OLLAMA_MODEL`. If `OLLAMA_API_KEY` is set (e.g. for Ollama Cloud Pro),
        it is forwarded to the client.
    """
    return ChatOllama(
        base_url=config.OLLAMA_BASE_URL,
        model=config.OLLAMA_MODEL,
        temperature=temperature,
        **( {"headers": {"Authorization": f"Bearer {config.OLLAMA_API_KEY}"}}
           if config.OLLAMA_API_KEY else {} ),
    )
