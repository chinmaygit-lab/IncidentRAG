from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated, Any

from .config import Settings
from .service import IncidentRAG, load_documents_from_directory

try:
    from fastapi import Depends, FastAPI, Header, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - optional dependency guard
    raise RuntimeError("API support requires: pip install .[api]") from exc


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)


class AnswerRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=3, ge=1, le=10)


@lru_cache(maxsize=1)
def get_engine() -> IncidentRAG:
    settings = Settings.from_env()
    engine = IncidentRAG(
        settings.database_path,
        abstention_threshold=settings.abstention_threshold,
        abstention_min_margin=settings.abstention_min_margin,
    )
    sample_root = os.getenv("INCIDENTRAG_SAMPLE_ROOT")
    if sample_root and engine.store.count_documents() == 0:
        engine.ingest_many(load_documents_from_directory(sample_root))
    return engine


def _authorize(x_api_key: Annotated[str | None, Header()] = None) -> None:
    expected = Settings.from_env().api_key
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid API key")


EngineDep = Annotated[IncidentRAG, Depends(get_engine)]


def create_app() -> FastAPI:
    app = FastAPI(title="IncidentRAG", version="1.0.2")

    @app.get("/healthz")
    def health(engine: EngineDep) -> dict[str, Any]:
        return engine.health()

    @app.get("/readyz")
    def ready(engine: EngineDep) -> dict[str, Any]:
        return {"ready": True, "documents": engine.store.count_documents()}

    @app.post("/v1/search", dependencies=[Depends(_authorize)])
    def search(request: SearchRequest, engine: EngineDep) -> dict[str, Any]:
        parsed, hits = engine.search(request.query, top_k=request.top_k)
        return {
            "parsed": {
                "service": parsed.service,
                "severity": parsed.severity,
                "http_status": parsed.http_status,
                "error_code": parsed.error_code,
            },
            "hits": [
                {
                    "document_id": hit.chunk.document_id,
                    "chunk_id": hit.chunk.id,
                    "title": hit.chunk.title,
                    "score": round(hit.score, 6),
                    "lexical_score": round(hit.lexical_score, 6),
                    "dense_score": round(hit.dense_score, 6),
                    "rrf_score": round(hit.rrf_score, 6),
                    "matched_fields": hit.matched_fields,
                }
                for hit in hits
            ],
        }

    @app.post("/v1/answer", dependencies=[Depends(_authorize)])
    def answer(request: AnswerRequest, engine: EngineDep) -> dict[str, Any]:
        result = engine.answer(request.query, top_k=request.top_k)
        return {
            "query": result.query,
            "text": result.text,
            "abstained": result.abstained,
            "confidence": round(result.confidence, 6),
            "citations": [
                {
                    "index": citation.index,
                    "document_id": citation.document_id,
                    "chunk_id": citation.chunk_id,
                    "title": citation.title,
                    "score": round(citation.score, 6),
                    "excerpt": citation.excerpt,
                }
                for citation in result.citations
            ],
        }

    @app.get("/v1/metrics", dependencies=[Depends(_authorize)])
    def metrics(engine: EngineDep) -> dict[str, Any]:
        return engine.telemetry.snapshot()

    return app


app = create_app()
