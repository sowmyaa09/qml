"""Probe NVIDIA NIM chat until one model returns a short reply. Does not print the key."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PREFERRED = (
    "ibm/granite-3.0-8b-instruct",
    "ibm/granite-3.0-3b-a800m-instruct",
    "ibm/granite-8b-code-instruct",
    "mistralai/mistral-nemotron",
    "mistralai/mistral-7b-instruct-v0.3",
    "microsoft/phi-3.5-moe-instruct",
    "google/gemma-3-4b-it",
    "google/gemma-3-12b-it",
    "google/gemma-4-31b-it",
    "meta/llama-3.2-11b-vision-instruct",
    "meta/muse-glimmer-30b",
    "nvidia/mistral-nemotron",
    "moonshotai/kimi-k2.6",
    "deepseek-ai/deepseek-v4-pro-0813",
    "deepseek-ai/deepseek-v4-flash-0731",
)


def _redact(text: str) -> str:
    text = re.sub(r"nvapi-[A-Za-z0-9_-]+", "nvapi-REDACTED", text)
    return re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", text)


def main() -> int:
    key = os.environ.get("NVIDIA_API_KEY", "").strip().strip('"').strip("'")
    base = os.environ.get(
        "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
    ).rstrip("/")
    if not key:
        print("NVIDIA_API_KEY empty")
        return 2

    from openai import OpenAI

    client = OpenAI(base_url=base, api_key=key)
    listed = []
    try:
        listed = [m.id for m in client.models.list().data]
        print("listed", len(listed))
    except Exception as exc:
        print("list_failed", _redact(str(exc))[:200])

    ordered = list(PREFERRED)
    for mid in listed:
        if mid not in ordered:
            ordered.append(mid)

    max_try = int(os.environ.get("NVIDIA_PROBE_LIMIT", "25"))
    tried = 0
    for model in ordered:
        if tried >= max_try:
            break
        tried += 1
        try:
            extra = {}
            if "deepseek" in model.lower() or "kimi" in model.lower():
                extra["extra_body"] = {"chat_template_kwargs": {"thinking": False}}
            response = client.chat.completions.create(
                model=model,
                temperature=0,
                timeout=40,
                max_tokens=24,
                messages=[{"role": "user", "content": "Reply with only the word pong."}],
                **extra,
            )
            text = (response.choices[0].message.content or "").strip()[:120]
            print("WORKING", model)
            print("reply", text)
            return 0
        except Exception as exc:
            msg = _redact(str(exc))
            code = "?"
            if "410" in msg:
                code = "410"
            elif "403" in msg:
                code = "403"
            elif "404" in msg:
                code = "404"
            print("fail", code, model)
    print("NO_WORKING_MODEL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
