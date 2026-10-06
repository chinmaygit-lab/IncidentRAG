from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from incidentrag.dense import HashingEmbedder
from incidentrag.evals import evaluate, load_fixtures
from incidentrag.postgres import FTS_SCHEMA_SQL, PGVECTOR_SCHEMA_SQL
from incidentrag.service import IncidentRAG, load_documents_from_directory

PROJECT = Path(__file__).resolve().parents[1]


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed: {detail}")
    print(f"PASS {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    check("python", sys.version_info >= (3, 11), sys.version.split()[0])

    documents = load_documents_from_directory(PROJECT / "data" / "sample")
    check("sample documents", len(documents) == 20, f"{len(documents)} documents")
    check(
        "sample split",
        sum(doc.source_type == "runbook" for doc in documents) == 10
        and sum(doc.source_type == "incident" for doc in documents) == 10,
        "10 runbooks + 10 incidents",
    )

    fixtures = load_fixtures(PROJECT / "benchmark" / "fixtures.json")
    check("benchmark size", len(fixtures) == 60, "60 queries")
    check(
        "benchmark labels",
        sum(bool(item["expected_document_ids"]) for item in fixtures) == 40,
        "40 answerable + 20 no-answer",
    )

    with tempfile.TemporaryDirectory(prefix="incidentrag-validate-") as temp:
        engine = IncidentRAG(Path(temp) / "validation.db", abstention_threshold=0.85)
        check("ingestion", engine.ingest_many(documents) == 20)
        check("chunk persistence", len(engine.store.all_chunks()) >= 20)

        metrics = evaluate(engine, fixtures, top_k=3)
        check("recall@3", metrics.recall_at_k >= 0.95, f"{metrics.recall_at_k:.4f}")
        check("MRR", metrics.mrr >= 0.95, f"{metrics.mrr:.4f}")
        check("nDCG@3", metrics.ndcg_at_k >= 0.95, f"{metrics.ndcg_at_k:.4f}")
        check("Hit@1", metrics.hit_at_1 >= 0.90, f"{metrics.hit_at_1:.4f}")
        check(
            "balanced abstention",
            metrics.balanced_abstention_accuracy >= 0.80,
            f"{metrics.balanced_abstention_accuracy:.4f} @ {metrics.calibrated_threshold:.4f}",
        )

        answer = engine.answer("P1 service=checkout HTTP 503 error_code=UPSTREAM_UNAVAILABLE")
        check("grounded answer", not answer.abstained and bool(answer.citations))
        valid_chunk_ids = {chunk.id for chunk in engine.store.all_chunks()}
        check(
            "citation markers",
            "[1]" in answer.text and answer.citations[0].chunk_id in valid_chunk_ids,
        )

        unknown = engine.answer("P1 service=video HTTP 507 disk quota exceeded after transcoder change")
        check("no-answer abstention", unknown.abstained and not unknown.citations)

    embedder = HashingEmbedder()
    check("deterministic embedding", embedder.embed("checkout 503") == embedder.embed("checkout 503"))
    check("PostgreSQL FTS SQL", "USING GIN" in FTS_SCHEMA_SQL and "tsvector" in FTS_SCHEMA_SQL)
    check("pgvector SQL", "vector(256)" in PGVECTOR_SCHEMA_SQL and "hnsw" in PGVECTOR_SCHEMA_SQL)

    compile_result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "src", "tests", "scripts"],
        cwd=PROJECT,
        check=False,
    )
    check("compileall", compile_result.returncode == 0)

    suspicious = []
    secret_re = re.compile(r"(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})")
    for path in PROJECT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        text_suffixes = {
            ".py", ".md", ".toml", ".yml", ".yaml", ".json",
            ".sql", ".ps1", ".sh", ".example", ".txt",
        }
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if secret_re.search(text):
            suspicious.append(str(path.relative_to(PROJECT)))
    check("secret pattern scan", not suspicious, json.dumps(suspicious))

    print("\nINCIDENTRAG VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
