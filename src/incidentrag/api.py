from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .models import AnswerResponse, CitationModel, Document, IngestRequest, QueryRequest, SearchResponse
from .service import IncidentRAG

DB_PATH = Path(os.getenv("INCIDENTRAG_DB", "incidentrag.db"))
engine = IncidentRAG(DB_PATH)
app = FastAPI(title="IncidentRAG", version="0.1.0")


def _citation(hit) -> CitationModel:
    compact = " ".join(hit.chunk.text.split())
    excerpt = compact[:500] + ("…" if len(compact) > 500 else "")
    return CitationModel(
        document_id=hit.chunk.document_id,
        chunk_id=hit.chunk.id,
        title=hit.chunk.title,
        source_type=hit.chunk.source_type,
        excerpt=excerpt,
        score=round(hit.score, 6),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents")
def ingest_document(request: IngestRequest) -> dict[str, int | str]:
    document = Document(
        id=request.id,
        title=request.title,
        text=request.text,
        source_type=request.source_type,
        metadata=request.metadata,
    )
    chunk_count = engine.ingest(document)
    return {"document_id": document.id, "chunks": chunk_count}


@app.get("/documents")
def list_documents() -> list[dict]:
    return [
        {"id": d.id, "title": d.title, "source_type": d.source_type, "metadata": d.metadata}
        for d in engine.store.list_documents()
    ]


@app.post("/search", response_model=SearchResponse)
def search(request: QueryRequest) -> SearchResponse:
    parsed, hits = engine.search(request.query, top_k=request.top_k)
    return SearchResponse(
        query=request.query,
        parsed={
            "severity": parsed.severity,
            "service": parsed.service,
            "http_status": parsed.http_status,
            "error_codes": parsed.error_codes,
            "keywords": parsed.keywords,
        },
        citations=[_citation(hit) for hit in hits],
    )


@app.post("/answer", response_model=AnswerResponse)
def answer(request: QueryRequest) -> AnswerResponse:
    parsed, hits, generated = engine.answer(request.query, top_k=request.top_k)
    if not hits:
        raise HTTPException(status_code=404, detail="No relevant evidence found")
    return AnswerResponse(
        query=request.query,
        parsed={
            "severity": parsed.severity,
            "service": parsed.service,
            "http_status": parsed.http_status,
            "error_codes": parsed.error_codes,
            "keywords": parsed.keywords,
        },
        citations=[_citation(hit) for hit in hits],
        answer=generated,
    )
