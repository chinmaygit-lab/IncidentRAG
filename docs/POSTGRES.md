# PostgreSQL FTS and pgvector

Install the optional driver:

```bash
pip install -e ".[postgres]"
```

Create a database and apply:

```text
migrations/001_postgres_fts.sql
migrations/002_pgvector.sql   # optional; requires pgvector extension
```

The FTS design uses:

- generated weighted `tsvector`
- GIN index
- `websearch_to_tsquery('english', ...)`
- `ts_rank_cd`

The vector design uses:

- `vector(256)` to match the offline hashing embedder dimensions
- HNSW index
- cosine distance (`<=>`)

`incidentrag.postgres.PostgresStore` intentionally imports `psycopg` only when used, so the default project remains dependency-free.

For local Docker testing, `docker-compose.yml` starts a pgvector-enabled PostgreSQL service. Change the development password before any non-local use.
