from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


@dataclass(slots=True)
class ParsedIncident:
    raw: str
    severity: str | None = None
    service: str | None = None
    http_status: int | None = None
    error_codes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Document:
    id: str
    title: str
    text: str
    source_type: str = "runbook"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Chunk:
    id: str
    document_id: str
    title: str
    text: str
    position: int
    source_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SearchHit:
    chunk: Chunk
    score: float
    lexical_score: float
    metadata_boost: float
    matched_fields: list[str] = field(default_factory=list)


class IngestRequest(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)
    source_type: str = "runbook"
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class CitationModel(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    source_type: str
    excerpt: str
    score: float


class SearchResponse(BaseModel):
    query: str
    parsed: dict[str, Any]
    citations: list[CitationModel]


class AnswerResponse(SearchResponse):
    answer: str
