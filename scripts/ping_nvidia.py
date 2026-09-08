"""One-shot NVIDIA NIM ping. Does not print the API key."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=True)


def _redact(text: str) -> str:
    text = re.sub(r"nvapi-[A-Za-z0-9_-]+", "nvapi-REDACTED", text)
    return re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", text)


def main() -> int:
    key = os.environ.get("NVIDIA_API_KEY", "").strip().strip('"').strip("'")
    base = os.environ.get(
        "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
    ).rstrip("/")
    model = os.environ.get("NVIDIA_MODEL", "meta/muse-glimmer-30b")
    print("key_set", bool(key))
    print("key_len", len(key))
    print("key_prefix", (key[:6] + "...") if key else "(empty)")
    print("base_url", base)
    print("model", model)
    if not key:
        print("NVIDIA_API_KEY is empty in .env")
        return 2

    from openai import OpenAI

    client = OpenAI(base_url=base, api_key=key)
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "list":
            models = client.models.list()
            names = [m.id for m in models.data][:40]
            print("http_ok", True)
            print("model_count_preview", len(models.data))
            print("sample_ids", ", ".join(names))
            return 0
        kwargs = {}
        if "deepseek" in model.lower() or "muse" in model.lower():
            kwargs["extra_body"] = {"chat_template_kwargs": {"thinking": False}}
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            timeout=60,
            max_tokens=256,
            messages=[{"role": "user", "content": "Reply with only the word pong."}],
            **kwargs,
        )
        msg = response.choices[0].message
        text = (msg.content or getattr(msg, "reasoning_content", None) or "").strip()
        print("http_ok", True)
        print("reply", text[:200])
        return 0
    except Exception as exc:
        print("http_ok", False)
        print("error_type", type(exc).__name__)
        print("error", _redact(str(exc))[:800])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
