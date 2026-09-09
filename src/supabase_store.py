"""Optional Supabase insert for generated PDF unlock keys. Server-side only."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

from dotenv import load_dotenv

from src.utils import RESEARCH_DISCLAIMER, get_project_root

load_dotenv(get_project_root() / ".env")

TABLE = "report_unlock_keys"


def supabase_configured() -> bool:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return bool(url and key)


def store_unlock_key(
    *,
    catalog_key: str,
    subject_name: str,
    date_of_birth: str | date,
    unlock_key: str,
    key_fingerprint: str,
    research_score: float | None,
) -> bool:
    """Insert one row. Returns False if not configured or the insert fails."""
    if not supabase_configured():
        return False
    try:
        from supabase import create_client
    except ImportError:
        return False

    url = os.environ["SUPABASE_URL"].strip()
    service = os.environ["SUPABASE_SERVICE_ROLE_KEY"].strip()
    dob = (
        date_of_birth.isoformat()
        if isinstance(date_of_birth, date)
        else str(date_of_birth)
    )
    row: dict[str, Any] = {
        "catalog_key": catalog_key,
        "subject_name": subject_name.strip(),
        "date_of_birth": dob,
        "key_fingerprint": key_fingerprint,
        "unlock_key": unlock_key,
        "research_score": research_score,
        "disclaimer": RESEARCH_DISCLAIMER,
    }
    try:
        client = create_client(url, service)
        client.table(TABLE).insert(row).execute()
    except Exception:
        return False
    return True
