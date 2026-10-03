# IncidentRAG

IncidentRAG is a **foundational incident-response retrieval system** built to learn the core engineering behind NLP + RAG before adding agent/workflow complexity.

It accepts an operational alert such as:

```text
P1 service=checkout HTTP 503 after deployment
```

and performs:

```text
incident text
   ↓
structured NLP extraction
(service / severity / HTTP status / error codes)
   ↓
runbook + postmortem chunking
   ↓
from-scratch BM25 retrieval
   ↓
metadata-aware ranking boosts
   ↓
ranked evidence + citations
   ↓
Recall@K / MRR / nDCG / Hit@1 evaluation
   ↓
FastAPI + CLI
```

## Why this repository exists

This is deliberately **not** a generic “chat with documents” project. The learning goal is to make retrieval behavior inspectable and measurable before embeddings, rerankers, LLM orchestration, or durable agents are introduced.

The first release therefore emphasizes:

- deterministic incident parsing;
- explainable lexical retrieval;
- provenance and citations;
- retrieval benchmarks;
- persistent SQLite ingestion;
- a clean service/API boundary;
- testable failure behavior.

The response generator is intentionally evidence-only and deterministic. It does not invent remediation steps that are absent from retrieved material. A later phase can add a real LLM behind the same retrieval/evidence interface.

## Features

- Python 3.11+
- FastAPI API
- SQLite persistence
- Markdown document ingestion
- deterministic paragraph-aware chunking with overlap
- incident NLP extraction for service, severity, HTTP status, error codes and keywords
- BM25 implemented from scratch (no search library)
- service/status/error metadata boosts
- evidence-only response generation
- citations with document/chunk provenance
- offline benchmark runner
- Recall@K, MRR, nDCG@K and Hit@1
- sample runbooks/postmortems
- pytest tests
- Docker + Docker Compose
- GitHub Actions CI

## Quick start (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

incidentrag --db incidentrag.db seed-sample
incidentrag --db incidentrag.db search "P1 service=checkout HTTP 503 after deployment"
incidentrag --db incidentrag.db answer "P1 service=checkout HTTP 503 after deployment"
incidentrag --db incidentrag.db benchmark benchmark\fixtures.json --top-k 3

python -m pytest -q
python -m ruff check src tests
python -m uvicorn incidentrag.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API explorer.

## API

### `GET /health`
Health check.

### `POST /documents`
Ingest or replace a document.

### `GET /documents`
List document metadata.

### `POST /search`
Retrieve ranked evidence with structured incident parsing.

### `POST /answer`
Return an evidence-grounded deterministic answer plus citations.

## Benchmark philosophy

The bundled benchmark is synthetic and intentionally small. Its purpose is to verify that the evaluation pipeline is real and repeatable; **high scores on the sample fixtures are not a production-quality claim**.

For a serious next phase, expand the dataset with:

1. larger incident/runbook corpora;
2. paraphrased and noisy alerts;
3. distractor documents;
4. negative/no-answer queries;
5. service aliases and renamed components;
6. temporal versions of runbooks;
7. retrieval regression tests.

## Planned progression

### Phase 1 — implemented here
- parsing
- chunking
- BM25
- metadata ranking
- SQLite
- citations
- evaluation
- FastAPI/CLI

### Phase 2
- PostgreSQL full-text search
- embeddings + pgvector
- hybrid fusion (RRF)
- reranker
- retrieval tracing
- larger benchmark suite

### Phase 3
- pluggable LLM generation with strict citation grounding
- faithfulness / answer-relevance evaluation
- abstention when evidence is weak
- prompt/version tracking

### Phase 4
- connect this retrieval core into the later ProcedureOps flagship for durable workflow and workforce automation.

## Repository layout

```text
src/incidentrag/
  api.py          FastAPI endpoints
  bm25.py         from-scratch BM25
  chunking.py     deterministic chunker
  cli.py          command-line interface
  evals.py        retrieval metrics
  generation.py   evidence-only generator
  models.py       domain + API models
  nlp.py          incident parsing/tokenization
  retrieval.py    BM25 + metadata ranking
  service.py      application service
  storage.py      SQLite persistence
benchmark/
  fixtures.json
data/sample/
  runbooks/
  incidents/
tests/
```

## Design constraints

- Retrieval must be measurable independently from generation.
- Every response must expose provenance.
- No silent external API calls.
- No agent framework in the foundation release.
- Fail closed when no evidence is retrieved.
- Keep ranking deterministic for reproducible tests.

## License
MIT.
