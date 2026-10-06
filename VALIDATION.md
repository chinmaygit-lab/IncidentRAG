# IncidentRAG v1.0.2 validation report

Validated in the packaging environment on **2026-10-06** with Python **3.13.5**.

## Release gates executed

| Gate | Result |
|---|---|
| Python byte compilation (`compileall`) | PASS |
| Pytest | **70 passed** |
| Coverage | **94% total** |
| Coverage release gate (`>=90%`) | PASS |
| Internal end-to-end validator | PASS |
| Sample corpus load | **20 docs: 10 runbooks + 10 incidents** |
| Benchmark fixture integrity | **60 queries: 40 answerable + 20 no-answer** |
| Recall@3 on included synthetic benchmark | **1.0000** |
| MRR on included synthetic benchmark | **1.0000** |
| nDCG@3 on included synthetic benchmark | **1.0000** |
| Hit@1 on included synthetic benchmark | **1.0000** |
| Calibrated balanced abstention accuracy | **1.0000** |
| Calibrated threshold on included benchmark | **0.8588** |
| Grounded answer + citation contract | PASS |
| No-answer abstention regression | PASS |
| Deterministic embedding regression | PASS |
| PostgreSQL FTS SQL contract | PASS |
| pgvector SQL contract | PASS |
| Secret-pattern scan | PASS |
| Python lines > 110 characters | **0** |
| Python trailing whitespace | **0** |
| Python tab characters | **0** |
| Editable package build/install | PASS |
| Wheel build | PASS |
| Wheel install in fresh venv | PASS |
| Installed CLI seed/search/answer/benchmark smoke | PASS |
| FastAPI health/search/answer smoke | PASS |
| Fresh-wheel `pip check` | PASS |

Repository snapshot at validation time: **82 files**, **37 Python files**, **2,202 Python lines** before generated packaging artifacts.

## Benchmark interpretation

The included benchmark is deliberately synthetic and compact. Perfect scores here are useful as regression evidence, **not** as a production-quality claim. Real deployment should evaluate on a held-out corpus containing real vocabulary, ambiguous incidents, stale runbooks, near-duplicate incidents, incomplete alerts, and realistic no-answer cases.

## Environment limitations / checks not claimed

- Ruff is configured in `pyproject.toml` and enforced by GitHub Actions. The Windows v1.0.0 run exposed 30 Ruff findings and v1.0.1 revealed four remaining E402 import-order findings; v1.0.2 fixes all reported findings. This packaging sandbox still could not install Ruff because external package resolution was unavailable, so the final Ruff pass is intentionally rechecked by `bootstrap_windows.ps1` on Windows before release publication. Local substitutes executed here included compile checks, the 70-test suite, 94% coverage, line-length validation, trailing-whitespace/tab validation, and import/package smoke tests.
- PostgreSQL/pgvector SQL and adapter contracts are included and statically tested. The sandbox did not have `psycopg` or a PostgreSQL service, so this report **does not claim a live database integration test**.
- The OpenAI-compatible grounded generator is an optional adapter. No external model was called in this sandbox, so this report **does not claim model-provider quality or latency results**.
- Docker/Compose files are included but Docker was not available in the packaging sandbox; no container runtime result is claimed.

## Reproduce locally

```bash
python -m pip install -e ".[api,dev]"
python -m ruff check src tests scripts
python -m compileall -q src tests scripts
coverage run -m pytest -q
coverage report --fail-under=90
python scripts/validate.py
```

For Windows, `scripts/bootstrap_windows.ps1` performs the same setup plus sample seeding, benchmark execution, and a demo grounded answer.

## Live PostgreSQL 18.6 validation

Live integration validation was completed on Windows with PostgreSQL
18.6 on 2026-10-07.

Verified:

- PostgreSQL administrator authentication
- dedicated `incidentrag_app` application role
- dedicated `incidentrag` database
- PostgreSQL FTS migration
- `incidentrag_chunks` table
- PostgreSQL full-text-search indexes
- 20 sample chunks ingested
- live FTS query: `checkout HTTP 503 deployment`
- `checkout_503` ranked first
- live PostgreSQL row count: 20

Observed live FTS ranking:

1. `checkout_503` — Checkout 503 Deployment Runbook
2. `inc_checkout_2026` — INC-2026-09 Checkout Readiness Regression

The local PostgreSQL installation did not provide the `vector`
extension. The pgvector adapter, SQL, and migration are included and
statically validated, but this release does not claim a live pgvector
integration test.

Final release validation:

- Ruff: PASS
- pytest: 70 passed
- coverage: 94%
- internal validation: PASS
- benchmark queries: 60
- answerable queries: 40
- no-answer queries: 20
- Recall@3: 1.0000
- MRR: 1.0000
- nDCG@3: 1.0000
- Hit@1: 1.0000
- balanced abstention accuracy: 1.0000
- calibrated threshold: 0.8588

The included benchmark uses a synthetic regression corpus. These
metrics are regression-test results and are not production-quality
performance claims.