from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .models import Chunk

FTS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS incidentrag_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(text, '')), 'B') ||
        setweight(to_tsvector('simple', coalesce(metadata::text, '')), 'C')
    ) STORED
);
CREATE INDEX IF NOT EXISTS idx_incidentrag_chunks_fts
    ON incidentrag_chunks USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_incidentrag_chunks_document
    ON incidentrag_chunks(document_id, position);
""".strip()

PGVECTOR_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE incidentrag_chunks
    ADD COLUMN IF NOT EXISTS embedding vector(256);
CREATE INDEX IF NOT EXISTS idx_incidentrag_chunks_embedding
    ON incidentrag_chunks USING hnsw (embedding vector_cosine_ops);
""".strip()

FTS_QUERY_SQL = """
WITH q AS (
    SELECT websearch_to_tsquery('english', %(query)s) AS tsq
)
SELECT
    c.id,
    c.document_id,
    c.title,
    c.text,
    c.position,
    c.source_type,
    c.metadata,
    ts_rank_cd(c.search_vector, q.tsq, 32) AS score
FROM incidentrag_chunks AS c, q
WHERE c.search_vector @@ q.tsq
ORDER BY score DESC, c.id ASC
LIMIT %(limit)s;
""".strip()

VECTOR_QUERY_SQL = """
SELECT
    id,
    document_id,
    title,
    text,
    position,
    source_type,
    metadata,
    1 - (embedding <=> %(embedding)s::vector) AS score
FROM incidentrag_chunks
WHERE embedding IS NOT NULL
ORDER BY embedding <=> %(embedding)s::vector, id ASC
LIMIT %(limit)s;
""".strip()


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def _require_psycopg() -> Any:
    try:
        import psycopg  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "PostgreSQL support requires the optional 'postgres' extra: pip install .[postgres]"
        ) from exc
    return psycopg


@dataclass(slots=True)
class PostgresStore:
    dsn: str

    def initialize(self, *, enable_pgvector: bool = False) -> None:
        psycopg = _require_psycopg()
        with psycopg.connect(self.dsn) as connection, connection.cursor() as cursor:
            cursor.execute(FTS_SCHEMA_SQL)
            if enable_pgvector:
                cursor.execute(PGVECTOR_SCHEMA_SQL)

    def upsert_chunks(self, chunks: Iterable[Chunk]) -> int:
        psycopg = _require_psycopg()
        count = 0
        sql = """
            INSERT INTO incidentrag_chunks(
                id, document_id, title, text, position, source_type, metadata
            ) VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
            ON CONFLICT(id) DO UPDATE SET
                document_id=excluded.document_id,
                title=excluded.title,
                text=excluded.text,
                position=excluded.position,
                source_type=excluded.source_type,
                metadata=excluded.metadata
        """
        with psycopg.connect(self.dsn) as connection, connection.cursor() as cursor:
            for chunk in chunks:
                cursor.execute(
                    sql,
                    (
                        chunk.id,
                        chunk.document_id,
                        chunk.title,
                        chunk.text,
                        chunk.position,
                        chunk.source_type,
                        json.dumps(chunk.metadata, sort_keys=True),
                    ),
                )
                count += 1
        return count

    def search_fts(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        psycopg = _require_psycopg()
        with psycopg.connect(self.dsn) as connection, connection.cursor() as cursor:
            cursor.execute(FTS_QUERY_SQL, {"query": query, "limit": limit})
            columns = [desc.name for desc in cursor.description]
            return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

    def search_vector(self, embedding: list[float], *, limit: int = 5) -> list[dict[str, Any]]:
        psycopg = _require_psycopg()
        with psycopg.connect(self.dsn) as connection, connection.cursor() as cursor:
            cursor.execute(
                VECTOR_QUERY_SQL,
                {"embedding": vector_literal(embedding), "limit": limit},
            )
            columns = [desc.name for desc in cursor.description]
            return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
