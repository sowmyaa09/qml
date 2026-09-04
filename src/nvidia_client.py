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

load_dotenv(get_project_root() / ".env")


class NvidiaConfigError(RuntimeError):
    """Missing or invalid NVIDIA settings."""


def nvidia_settings() -> dict[str, str]:
    key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not key:
        raise NvidiaConfigError(
            "NVIDIA_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return {
        "api_key": key,
        "base_url": os.environ.get(
            "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
        ).rstrip("/"),
        "model": os.environ.get("NVIDIA_MODEL", "deepseek-ai/deepseek-v4-pro-0813"),
    }


def complete_json(system_prompt: str, user_prompt: str, *, timeout: float = 60.0) -> dict[str, Any]:
    """Call NIM and parse a JSON object from the assistant message."""
    settings = nvidia_settings()
    from openai import OpenAI

    client = OpenAI(base_url=settings["base_url"], api_key=settings["api_key"])
    response = client.chat.completions.create(
        model=settings["model"],
        temperature=0.0,
        timeout=timeout,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        extra_body={"chat_template_kwargs": {"thinking": False}},
    )
    text = (response.choices[0].message.content or "").strip()
    return parse_json_object(text)


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
