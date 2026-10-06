import pytest

from incidentrag.postgres import (
    FTS_QUERY_SQL,
    FTS_SCHEMA_SQL,
    PGVECTOR_SCHEMA_SQL,
    VECTOR_QUERY_SQL,
    PostgresStore,
    vector_literal,
)


def test_fts_schema_has_generated_tsvector_and_gin():
    assert "tsvector GENERATED ALWAYS" in FTS_SCHEMA_SQL
    assert "USING GIN" in FTS_SCHEMA_SQL


def test_pgvector_schema_has_vector_and_hnsw():
    assert "CREATE EXTENSION IF NOT EXISTS vector" in PGVECTOR_SCHEMA_SQL
    assert "vector(256)" in PGVECTOR_SCHEMA_SQL
    assert "USING hnsw" in PGVECTOR_SCHEMA_SQL


def test_fts_query_uses_websearch_and_rank():
    assert "websearch_to_tsquery" in FTS_QUERY_SQL
    assert "ts_rank_cd" in FTS_QUERY_SQL


def test_vector_query_uses_cosine_distance():
    assert "<=>" in VECTOR_QUERY_SQL


def test_vector_literal_is_postgres_compatible():
    assert vector_literal([0.1, -0.2]) == "[0.10000000,-0.20000000]"


def test_postgres_without_optional_dependency_fails_cleanly():
    store = PostgresStore("postgresql://invalid")
    try:
        import psycopg  # noqa: F401
    except ImportError:
        with pytest.raises(RuntimeError, match="optional 'postgres' extra"):
            store.initialize()
