from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

from .chunking import chunk_document
from .models import Chunk, Document

_SCHEMA = """
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
    document_id TEXT NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id, position);
CREATE INDEX IF NOT EXISTS idx_chunks_source_type ON chunks(source_type);
"""


class SQLiteStore:
    def __init__(self, path: str | Path = "incidentrag.db"):
        self.path = str(path)
        self.initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    def upsert_document(self, document: Document) -> list[Chunk]:
        chunks = chunk_document(document)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents(id,title,text,source_type,metadata_json)
                VALUES(?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    text=excluded.text,
                    source_type=excluded.source_type,
                    metadata_json=excluded.metadata_json
                """,
                (
                    document.id,
                    document.title,
                    document.text,
                    document.source_type,
                    json.dumps(document.metadata, sort_keys=True),
                ),
            )
            connection.execute("DELETE FROM chunks WHERE document_id=?", (document.id,))
            connection.executemany(
                """
                INSERT INTO chunks(id,document_id,title,text,position,source_type,metadata_json)
                VALUES(?,?,?,?,?,?,?)
                """,
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
        return chunks

    def upsert_documents(self, documents: Iterable[Document]) -> int:
        count = 0
        for document in documents:
            self.upsert_document(document)
            count += 1
        return count

    def all_documents(self) -> list[Document]:
        with self._connect() as connection:
            rows = connection.execute(
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

    def all_chunks(self) -> list[Chunk]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id,document_id,title,text,position,source_type,metadata_json
                FROM chunks ORDER BY document_id, position
                """
            ).fetchall()
        return [self._row_to_chunk(row) for row in rows]

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id,document_id,title,text,position,source_type,metadata_json
                FROM chunks WHERE id=?
                """,
                (chunk_id,),
            ).fetchone()
        return self._row_to_chunk(row) if row else None

    def count_documents(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0])

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
