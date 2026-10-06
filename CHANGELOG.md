# Changelog

## 1.0.2 — 2026-10-06

- Fixed the final four Ruff E402 findings in `scripts/validate.py` by restoring canonical import ordering.
- Kept strict Windows native-exit checking so bootstrap stops on any failed validation gate.
- No retrieval, benchmark, API, PostgreSQL/pgvector, or generation behavior changed.

## 1.0.1 — 2026-10-06

- Fixed Ruff/static-analysis violations discovered on Windows validation.
- Explicitly close SQLite connections so temporary validation databases are removable on Windows.
- Preserved the v1.0 retrieval, abstention, API, PostgreSQL/pgvector, benchmark, and test behavior.

## 1.0.0 - 2026-10-06

- Completed offline hybrid retrieval with BM25, deterministic dense embeddings, RRF, and reranking.
- Added calibrated abstention and grounded citation generation.
- Added PostgreSQL FTS and pgvector adapters/migrations.
- Added FastAPI, CLI, optional API-key guard, telemetry, Docker/Compose, CI, and bootstrap scripts.
- Expanded synthetic corpus to 20 documents and benchmark to 60 queries.
- Added comprehensive unit, integration, API, CLI, grounding, and SQL contract tests.
