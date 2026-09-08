"""NVIDIA NIM chat client (OpenAI-compatible). API key from the environment.

Never log the key. Research mapper only — not a medical device.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv

from src.utils import get_project_root

load_dotenv(get_project_root() / ".env", override=True)

# Live chat on the current key (2026-09-06): meta/muse-glimmer-30b HTTP 200.
# DeepSeek V4 / Nemotron Ultra / Gemma 4 often hang past 20s instead of 403.
DEFAULT_MODEL_CANDIDATES = ("meta/muse-glimmer-30b",)


class NvidiaConfigError(RuntimeError):
    """Missing or invalid NVIDIA settings."""


class NvidiaChatError(RuntimeError):
    """All candidate models failed chat completions."""


def nvidia_settings() -> dict[str, str]:
    key = os.environ.get("NVIDIA_API_KEY", "").strip().strip('"').strip("'")
    if not key:
        raise NvidiaConfigError(
            "NVIDIA_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return {
        "api_key": key,
        "base_url": os.environ.get(
            "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
        ).rstrip("/"),
        "model": os.environ.get("NVIDIA_MODEL", DEFAULT_MODEL_CANDIDATES[0]).strip(),
    }


def model_candidates() -> list[str]:
    """Primary NVIDIA_MODEL plus optional comma-separated fallbacks."""
    settings = nvidia_settings()
    ordered: list[str] = []
    extra = os.environ.get("NVIDIA_FALLBACK_MODELS", "")
    for item in [settings["model"], *extra.split(","), *DEFAULT_MODEL_CANDIDATES]:
        name = item.strip()
        if name and name not in ordered:
            ordered.append(name)
    return ordered


def _needs_thinking_off(model: str) -> bool:
    lower = model.lower()
    return any(token in lower for token in ("deepseek", "kimi", "muse", "nemotron", "gemma-4"))


def assistant_text(message: Any) -> str:
    """NIM sometimes fills reasoning_content and leaves content empty."""
    content = getattr(message, "content", None)
    if isinstance(message, dict):
        content = message.get("content")
        reasoning = message.get("reasoning_content")
    else:
        reasoning = getattr(message, "reasoning_content", None)
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()
    return ""


def complete_json(system_prompt: str, user_prompt: str, *, timeout: float = 60.0) -> dict[str, Any]:
    """Call NIM and parse a JSON object from the assistant message.

    Tries NVIDIA_MODEL first, then NVIDIA_FALLBACK_MODELS / built-in candidates.
    """
    settings = nvidia_settings()
    from openai import OpenAI

    client = OpenAI(base_url=settings["base_url"], api_key=settings["api_key"])
    errors: list[str] = []
    for model in model_candidates():
        try:
            kwargs: dict[str, Any] = {}
            if _needs_thinking_off(model):
                kwargs["extra_body"] = {"chat_template_kwargs": {"thinking": False}}
            response = client.chat.completions.create(
                model=model,
                temperature=0.0,
                timeout=timeout,
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": f"{system_prompt}\n\n{user_prompt}",
                    }
                ],
                **kwargs,
            )
            text = assistant_text(response.choices[0].message)
            payload = parse_json_object(text)
            payload["_nvidia_model_used"] = model
            return payload
        except NvidiaConfigError:
            raise
        except Exception as exc:
            errors.append(f"{model}: {type(exc).__name__}")
            continue
    raise NvidiaChatError(
        "NVIDIA chat failed for every candidate model ("
        + "; ".join(errors[:6])
        + "). Use the local regex mapper or pick a live id on build.nvidia.com."
    )


def parse_json_object(text: str) -> dict[str, Any]:
    """Extract a JSON object from model text (fences allowed)."""
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            cleaned = cleaned[start : end + 1]
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"NIM did not return JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("NIM JSON root must be an object.")
    return payload
