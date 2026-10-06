from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
class ParsedIncident:
    raw: str
    service: str | None = None
    severity: str | None = None
    http_status: int | None = None
    error_code: str | None = None
    tokens: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SearchHit:
    chunk: Chunk
    score: float
    lexical_score: float = 0.0
    dense_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0
    matched_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Citation:
    index: int
    document_id: str
    chunk_id: str
    title: str
    source_type: str
    score: float
    excerpt: str


@dataclass(slots=True)
class Answer:
    query: str
    text: str
    abstained: bool
    confidence: float
    citations: list[Citation] = field(default_factory=list)
    parsed: ParsedIncident | None = None
