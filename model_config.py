"""
Resolves the MODEL setting from .env into something an ADK Agent accepts.

- "anthropic/<model>" (e.g. anthropic/claude-sonnet-5-5) -> LiteLlm wrapper that
  calls the Anthropic API directly. Requires ANTHROPIC_API_KEY.
- Anything else (e.g. gemini-2.5-flash) -> passed through as a plain string,
  which ADK resolves to Gemini (Vertex AI or Gemini API key).
"""
import os
from typing import Union

from google.adk.models.lite_llm import LiteLlm

LITELLM_PREFIXES = ("anthropic/",)


def get_model() -> Union[str, LiteLlm]:
    model = os.getenv("MODEL")
    if not model:
        raise RuntimeError("MODEL is not set. Copy .env.example to .env and fill it in.")
    if model.startswith(LITELLM_PREFIXES):
        if model.startswith("anthropic/") and not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError(f"MODEL={model} requires ANTHROPIC_API_KEY in .env.")
        return LiteLlm(model=model)
    return model
