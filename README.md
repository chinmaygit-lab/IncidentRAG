# IncidentRAG v1.0.2

IncidentRAG is a portfolio-grade incident-response retrieval system that finds operational evidence from runbooks and historical incidents, combines lexical and dense retrieval, reranks evidence, abstains when support is weak, and produces citation-grounded investigation guidance.

The core path is deliberately **offline-runnable**. You can validate the complete retrieval and grounding pipeline without an API key, Docker, PostgreSQL, or a hosted embedding model. PostgreSQL FTS, pgvector, and an OpenAI-compatible LLM adapter are included as optional production-style extensions.

## What is implemented

- Incident parsing for service, severity, HTTP status, and error codes.
- Deterministic paragraph-aware chunking with stable SHA-256 chunk IDs.
- BM25 implemented in the repository.
- Deterministic 256-dimensional signed feature-hashing embeddings for an offline dense baseline.
- Hybrid retrieval with reciprocal-rank fusion (RRF).
- Metadata-aware lightweight reranking.
- Calibrated confidence/abstention policy.
- Evidence-only extractive answer generation with exact chunk citations.
- Optional callable/model-backed generator with citation validation.
- SQLite persistence for a zero-setup local experience.
- PostgreSQL full-text-search schema using generated `tsvector`, GIN, `websearch_to_tsquery`, and `ts_rank_cd`.
- Optional pgvector schema using 256-dimensional vectors and HNSW cosine search.
- FastAPI endpoints, optional API-key guard, CLI, health/readiness, and in-process telemetry.
- Synthetic sample corpus: 10 runbooks + 10 historical incidents.
- 60-query benchmark: 40 answerable + 20 adversarial/no-answer queries.
- CI, Dockerfile, Compose/Postgres profile, Windows/Unix bootstrap, validation scripts, tests, and release docs.

## Architecture

```text
incident text
    |
    v
signal parser -------- service / severity / HTTP / error code
    |
    v
query representation
    |                         |
    |                         +--> deterministic dense embedding
    +--> BM25 lexical search       (offline baseline)
              |                    |
              +---------+----------+
                        v
                   RRF fusion
                        |
                        v
              metadata-aware reranker
                        |
                        v
               confidence / abstention
                 |               |
           weak evidence     strong evidence
                 |               |
              abstain       grounded generator
                                 |
                                 v
                         answer + citations
```

Optional production adapters replace or augment local retrieval with PostgreSQL FTS and pgvector; the grounding contract remains the same.

## Fast start

### Windows PowerShell

```powershell
Set-Location IncidentRAG
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\bootstrap_windows.ps1
```

### macOS / Linux

```bash
cd IncidentRAG
bash scripts/bootstrap_unix.sh
```

### Manual setup

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Unix: source .venv/bin/activate
python -m pip install -e ".[api,dev]"
incidentrag --db incidentrag.db seed-sample --root data/sample
incidentrag --db incidentrag.db benchmark benchmark/fixtures.json --top-k 3
incidentrag --db incidentrag.db answer "P1 service=checkout HTTP 503 error_code=UPSTREAM_UNAVAILABLE"
```

## API

```bash
incidentrag --db incidentrag.db seed-sample --root data/sample
INCIDENTRAG_DB=incidentrag.db incidentrag serve --host 127.0.0.1 --port 8000
```

Endpoints:

- `GET /healthz`
- `GET /readyz`
- `POST /v1/search`
- `POST /v1/answer`
- `GET /v1/metrics`

Set `INCIDENTRAG_API_KEY` to require an `X-API-Key` header on `/v1/*` routes.

## PostgreSQL FTS and pgvector

The local core does not require PostgreSQL. For a production-style database backend, see `docs/POSTGRES.md` and `migrations/`.

```bash
pip install -e ".[postgres]"
incidentrag postgres-schema
```

`migrations/001_postgres_fts.sql` creates a generated weighted `tsvector` and a GIN index. `migrations/002_pgvector.sql` enables `vector`, adds `vector(256)`, and creates an HNSW cosine index.

## Model-backed grounded generation

The default generator is extractive and has no network dependency. `CallableGroundedGenerator` and `OpenAICompatibleHTTPGenerator` allow a model to be inserted behind the same evidence-only contract. Model output must contain valid `[n]` citations or it is rejected. See `docs/LLM_GROUNDING.md`.

## Evaluation

Run:

```bash
incidentrag --db incidentrag.db benchmark benchmark/fixtures.json --top-k 3
```

The included benchmark is deliberately synthetic and small enough to run instantly. Perfect or near-perfect scores on this corpus are **not production claims**. The purpose is regression testing of retrieval, hybrid fusion, and no-answer behavior. See `docs/EVALUATION.md` for the interpretation rules.

## Verification

```bash
python -m compileall -q src tests scripts
coverage run -m pytest -q
coverage report
python scripts/validate.py
```

`VALIDATION.md` records the checks executed for the packaged release.

## Repository layout

```text
src/incidentrag/        application code
 tests/                 unit/integration/API tests
 data/sample/           synthetic runbooks and incidents
 benchmark/             60-query evaluation fixture
 migrations/            PostgreSQL FTS + pgvector SQL
 scripts/               bootstrap and validation utilities
 docs/                  architecture/operations/evaluation notes
 .github/workflows/     CI
```

## Safety boundary

IncidentRAG is decision support, not an autonomous remediation agent. It intentionally abstains when evidence is weak and preserves citations so operators can inspect sources before acting. Do not use sample thresholds or synthetic benchmark scores as a substitute for evaluation on your own incident corpus.

## License

MIT.
