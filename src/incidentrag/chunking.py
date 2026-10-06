from __future__ import annotations

import hashlib
import re

from .models import Chunk, Document

_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n+")


def _chunk_id(document_id: str, position: int, text: str) -> str:
    digest = hashlib.sha256(f"{document_id}:{position}:{text}".encode()).hexdigest()[:16]
    return f"{document_id}:{position}:{digest}"


def chunk_document(
    document: Document,
    *,
    target_chars: int = 900,
    overlap_chars: int = 120,
) -> list[Chunk]:
    """Create deterministic paragraph-aware chunks with bounded text overlap."""
    if target_chars < 100:
        raise ValueError("target_chars must be >= 100")
    if overlap_chars < 0 or overlap_chars >= target_chars:
        raise ValueError("overlap_chars must be >= 0 and < target_chars")

    paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT.split(document.text) if p.strip()]
    if not paragraphs and document.text.strip():
        paragraphs = [document.text.strip()]

    bodies: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if current and len(candidate) > target_chars:
            bodies.append(current)
            overlap = current[-overlap_chars:].lstrip() if overlap_chars else ""
            current = f"{overlap}\n\n{paragraph}".strip() if overlap else paragraph
        else:
            current = candidate
    if current:
        bodies.append(current)

    return [
        Chunk(
            id=_chunk_id(document.id, position, body),
            document_id=document.id,
            title=document.title,
            text=body,
            position=position,
            source_type=document.source_type,
            metadata=dict(document.metadata),
        )
        for position, body in enumerate(bodies)
    ]
