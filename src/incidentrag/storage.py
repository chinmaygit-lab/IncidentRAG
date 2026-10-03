from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .chunking import chunk_document
from .models import Chunk, Document

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    source_type TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_source_type ON chunks(source_type);
"""


class SQLiteStore:
    def __init__(self, path: str | Path = "incidentrag.db") -> None:
        self.path = str(path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def reset(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM chunks")
            conn.execute("DELETE FROM documents")

    def upsert_document(self, document: Document, target_chars: int = 900, overlap_chars: int = 140) -> int:
        chunks = chunk_document(document, target_chars=target_chars, overlap_chars=overlap_chars)
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO documents(id,title,text,source_type,metadata_json)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                     title=excluded.title,
                     text=excluded.text,
                     source_type=excluded.source_type,
                     metadata_json=excluded.metadata_json""",
                (
                    document.id,
                    document.title,
                    document.text,
                    document.source_type,
                    json.dumps(document.metadata, sort_keys=True),
                ),
            )
            conn.execute("DELETE FROM chunks WHERE document_id=?", (document.id,))
            conn.executemany(
                """INSERT INTO chunks(id,document_id,title,text,position,source_type,metadata_json)
                   VALUES(?,?,?,?,?,?,?)""",
                [
                    (
                        chunk.id,
                        chunk.document_id,
                        chunk.title,
                        chunk.text,
                        chunk.position,
                        chunk.source_type,
                        json.dumps(chunk.metadata, sort_keys=True),
                    )
                    for chunk in chunks
                ],
            )
        return len(chunks)

    def list_chunks(self) -> list[Chunk]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, document_id, title, text, position, source_type, metadata_json "
                "FROM chunks ORDER BY document_id, position"
            ).fetchall()
        return [self._row_to_chunk(row) for row in rows]

    def list_documents(self) -> list[Document]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id,title,text,source_type,metadata_json FROM documents ORDER BY id"
            ).fetchall()
        return [
            Document(
                id=row["id"],
                title=row["title"],
                text=row["text"],
                source_type=row["source_type"],
                metadata=json.loads(row["metadata_json"]),
            )
            for row in rows
        ]

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id,document_id,title,text,position,source_type,metadata_json FROM chunks WHERE id=?",
                (chunk_id,),
            ).fetchone()
        return self._row_to_chunk(row) if row else None

    @staticmethod
    def _row_to_chunk(row: sqlite3.Row) -> Chunk:
        return Chunk(
            id=row["id"],
            document_id=row["document_id"],
            title=row["title"],
            text=row["text"],
            position=int(row["position"]),
            source_type=row["source_type"],
            metadata=json.loads(row["metadata_json"]),
        )
