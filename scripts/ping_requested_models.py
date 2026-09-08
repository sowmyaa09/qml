"""One-shot ping of NVIDIA_MODEL plus a short candidate list. Never prints the key."""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=True)


def _redact(text: object) -> str:
    return re.sub(r"nvapi-[A-Za-z0-9_-]+", "nvapi-REDACTED", str(text))[:500]


def main() -> int:
    key = os.environ.get("NVIDIA_API_KEY", "").strip().strip('"').strip("'")
    base = os.environ.get(
        "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
    ).rstrip("/")
    primary = os.environ.get("NVIDIA_MODEL", "").strip()
    print("key_set", bool(key), flush=True)
    print("key_len", len(key), flush=True)
    print("key_prefix", (key[:6] + "...") if key else "(empty)", flush=True)
    print("primary", primary, flush=True)
    if not key:
        print("NVIDIA_API_KEY empty")
        return 2

    import httpx

    ordered: list[str] = []
    for item in (
        primary,
        "nvidia/nemotron-3-ultra-550b-a55b",
        "google/gemma-4-31b-it",
        "deepseek-ai/deepseek-v4-pro-0813",
        "deepseek-ai/deepseek-r1",
        "meta/muse-glimmer-30b",
    ):
        if item and item not in ordered:
            ordered.append(item)

    url = f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    for model in ordered:
        extras: list = [{"chat_template_kwargs": {"thinking": False}}, None]
        for extra in extras:
            label = "thinking_off" if extra else "plain"
            print("try", model, label, flush=True)
            body = {
                "model": model,
                "temperature": 0,
                "max_tokens": 32,
                "messages": [{"role": "user", "content": "Reply with only the word pong."}],
            }
            if extra:
                body["chat_template_kwargs"] = extra["chat_template_kwargs"]
            try:
                response = httpx.post(url, headers=headers, json=body, timeout=20.0)
            except Exception as exc:
                print("fail", type(exc).__name__, model, label, flush=True)
                print("detail", _redact(exc), flush=True)
                continue
            print("http", response.status_code, model, label, flush=True)
            if response.status_code < 400:
                try:
                    payload = response.json()
                    text = (
                        payload.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content")
                        or ""
                    )
                except Exception:
                    text = response.text[:160]
                print("WORKING", model, label, flush=True)
                print("reply", str(text).strip()[:160], flush=True)
                return 0
            print("fail", response.status_code, model, label, flush=True)
            print("detail", _redact(response.text)[:240], flush=True)
    print("NO_WORKING_MODEL", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
