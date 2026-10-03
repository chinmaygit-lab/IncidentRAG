from __future__ import annotations

import hashlib
import re

from .models import Chunk, Document

PARAGRAPH_RE = re.compile(r"\n\s*\n+")


def _chunk_id(document_id: str, position: int, text: str) -> str:
    digest = hashlib.sha1(f"{document_id}:{position}:{text}".encode()).hexdigest()[:12]
    return f"{document_id}:{position}:{digest}"


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in PARAGRAPH_RE.split(text) if p.strip()]


def chunk_document(document: Document, target_chars: int = 900, overlap_chars: int = 140) -> list[Chunk]:
    if target_chars < 200:
        raise ValueError("target_chars must be >= 200")
    if overlap_chars < 0 or overlap_chars >= target_chars:
        raise ValueError("overlap_chars must be >= 0 and < target_chars")

    paragraphs = _paragraphs(document.text)
    if not paragraphs:
        return []

    raw_chunks: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = para if not current else f"{current}\n\n{para}"
        if len(candidate) <= target_chars or not current:
            current = candidate
            continue
        raw_chunks.append(current.strip())
        carry = current[-overlap_chars:].strip() if overlap_chars else ""
        current = f"{carry}\n\n{para}".strip() if carry else para
    if current.strip():
        raw_chunks.append(current.strip())

    return [
        Chunk(
            id=_chunk_id(document.id, i, text),
            document_id=document.id,
            title=document.title,
            text=text,
            position=i,
            source_type=document.source_type,
            metadata=dict(document.metadata),
        )
        for i, text in enumerate(raw_chunks)
    ]
