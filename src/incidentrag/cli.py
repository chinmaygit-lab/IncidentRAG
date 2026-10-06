from __future__ import annotations

import argparse
import json
import os
import sys

from .evals import evaluate, load_fixtures
from .postgres import FTS_QUERY_SQL, FTS_SCHEMA_SQL, PGVECTOR_SCHEMA_SQL, VECTOR_QUERY_SQL
from .service import IncidentRAG, dump_answer, load_documents_from_directory


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="incidentrag", description="Grounded incident-response RAG")
    parser.add_argument("--db", default=os.getenv("INCIDENTRAG_DB", "incidentrag.db"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed = subparsers.add_parser("seed-sample", help="load markdown runbooks/incidents")
    seed.add_argument("--root", default="data/sample")

    search = subparsers.add_parser("search", help="hybrid retrieval")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=5)

    answer = subparsers.add_parser("answer", help="grounded answer with citations")
    answer.add_argument("query")
    answer.add_argument("--top-k", type=int, default=3)

    benchmark = subparsers.add_parser("benchmark", help="evaluate retrieval")
    benchmark.add_argument("fixtures")
    benchmark.add_argument("--top-k", type=int, default=3)

    subparsers.add_parser("health", help="print health information")
    subparsers.add_parser("postgres-schema", help="print PostgreSQL FTS + pgvector SQL")

    serve = subparsers.add_parser("serve", help="run FastAPI via uvicorn")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "postgres-schema":
        print("-- PostgreSQL FTS schema\n" + FTS_SCHEMA_SQL)
        print("\n-- pgvector extension\n" + PGVECTOR_SCHEMA_SQL)
        print("\n-- FTS query\n" + FTS_QUERY_SQL)
        print("\n-- vector query\n" + VECTOR_QUERY_SQL)
        return 0

    if args.command == "serve":
        try:
            import uvicorn
        except ImportError:
            print("serve requires: pip install .[api]", file=sys.stderr)
            return 2
        uvicorn.run("incidentrag.api:app", host=args.host, port=args.port, reload=False)
        return 0

    engine = IncidentRAG(args.db)

    if args.command == "seed-sample":
        documents = load_documents_from_directory(args.root)
        count = engine.ingest_many(documents)
        print(json.dumps({"documents": count, "chunks": len(engine.store.all_chunks())}, indent=2))
        return 0

    if args.command == "search":
        parsed, hits = engine.search(args.query, top_k=args.top_k)
        print(
            json.dumps(
                {
                    "parsed": {
                        "service": parsed.service,
                        "severity": parsed.severity,
                        "http_status": parsed.http_status,
                        "error_code": parsed.error_code,
                    },
                    "hits": [
                        {
                            "document_id": hit.chunk.document_id,
                            "title": hit.chunk.title,
                            "score": round(hit.score, 6),
                            "matched_fields": hit.matched_fields,
                        }
                        for hit in hits
                    ],
                },
                indent=2,
            )
        )
        return 0

    if args.command == "answer":
        print(dump_answer(engine.answer(args.query, top_k=args.top_k)))
        return 0

    if args.command == "benchmark":
        metrics = evaluate(engine, load_fixtures(args.fixtures), top_k=args.top_k)
        print(json.dumps(metrics.to_dict(), indent=2))
        return 0

    if args.command == "health":
        print(json.dumps(engine.health(), indent=2))
        return 0

    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
