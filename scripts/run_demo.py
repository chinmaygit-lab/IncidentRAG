from __future__ import annotations

import json
import tempfile
from pathlib import Path

from incidentrag.evals import evaluate, load_fixtures
from incidentrag.service import IncidentRAG, dump_answer, load_documents_from_directory

PROJECT = Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory(prefix="incidentrag-demo-") as temp:
    engine = IncidentRAG(Path(temp) / "demo.db", abstention_threshold=0.85)
    engine.ingest_many(load_documents_from_directory(PROJECT / "data" / "sample"))
    print("=== GROUNDED ANSWER ===")
    print(dump_answer(engine.answer("P1 service=checkout HTTP 503 error_code=UPSTREAM_UNAVAILABLE")))
    print("\n=== NO-ANSWER CASE ===")
    print(dump_answer(engine.answer("service=video HTTP 507 disk quota exceeded")))
    print("\n=== BENCHMARK ===")
    metrics = evaluate(engine, load_fixtures(PROJECT / "benchmark" / "fixtures.json"), top_k=3)
    print(json.dumps(metrics.to_dict(), indent=2))
