"""Local research-mapper API. Not a medical device.

    uvicorn src.api_server:app --reload --port 8000

Requires NVIDIA_API_KEY in .env for /v1/research-map.
"""

from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.research_map import map_and_score, map_notes_with_llm, score_catalog
from src.utils import LONG_DISCLAIMER, RESEARCH_DISCLAIMER, get_project_root

load_dotenv(get_project_root() / ".env")

app = FastAPI(
    title="Q-Care research mapper",
    description=LONG_DISCLAIMER + " " + RESEARCH_DISCLAIMER,
    version="0.1.0",
)


class MapRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Notes or extracted PDF text.")


class ScoreRequest(BaseModel):
    catalog_key: str
    features: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "disclaimer": RESEARCH_DISCLAIMER}


@app.post("/v1/research-map")
def research_map(body: MapRequest) -> dict[str, Any]:
    try:
        mapped = map_notes_with_llm(body.text)
        return map_and_score(body.text, mapped=mapped)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/research-score")
def research_score(body: ScoreRequest) -> dict[str, Any]:
    try:
        result = score_catalog(body.catalog_key, body.features)
        return {"disclaimer": RESEARCH_DISCLAIMER, "result": result}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
