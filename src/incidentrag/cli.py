from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evals import evaluate, load_fixtures
from .models import Document
from .service import IncidentRAG


def _load_directory(engine: IncidentRAG, directory: Path, source_type: str) -> int:
    count = 0
    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        metadata: dict[str, str | int] = {}
        first_lines = [line.strip() for line in text.splitlines()[:12]]
        for line in first_lines:
            if line.lower().startswith("service:"):
                metadata["service"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("severity:"):
                metadata["severity"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("http_status:"):
                value = line.split(":", 1)[1].strip()
                if value.isdigit():
                    metadata["http_status"] = int(value)
            elif line.lower().startswith("error_code:"):
                metadata["error_code"] = line.split(":", 1)[1].strip()
        engine.ingest(
            Document(
                id=path.stem,
                title=path.stem.replace("_", " ").title(),
                text=text,
                source_type=source_type,
                metadata=metadata,
            )
        )
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(prog="incidentrag")
    parser.add_argument("--db", default="incidentrag.db")
    sub = parser.add_subparsers(dest="command", required=True)

    seed = sub.add_parser("seed-sample", help="Load bundled sample runbooks/incidents")
    seed.add_argument("--root", type=Path, default=Path("data/sample"))

    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=5)

    answer = sub.add_parser("answer")
    answer.add_argument("query")
    answer.add_argument("--top-k", type=int, default=5)

    bench = sub.add_parser("benchmark")
    bench.add_argument("fixtures", type=Path)
    bench.add_argument("--top-k", type=int, default=3)

    args = parser.parse_args()
    engine = IncidentRAG(args.db)

    if args.command == "seed-sample":
        engine.store.reset()
        runbooks = _load_directory(engine, args.root / "runbooks", "runbook")
        incidents = _load_directory(engine, args.root / "incidents", "incident")
        print(
            json.dumps(
                {"runbooks": runbooks, "incidents": incidents, "total": runbooks + incidents}, indent=2
            )
        )
    elif args.command == "search":
        parsed, hits = engine.search(args.query, top_k=args.top_k)
        print(
            json.dumps(
                {
                    "parsed": parsed.__dict__
                    if hasattr(parsed, "__dict__")
                    else {
                        "severity": parsed.severity,
                        "service": parsed.service,
                        "http_status": parsed.http_status,
                        "error_codes": parsed.error_codes,
                        "keywords": parsed.keywords,
                    },
                    "hits": [
                        {
                            "document_id": h.chunk.document_id,
                            "title": h.chunk.title,
                            "score": round(h.score, 4),
                            "matched": h.matched_fields,
                        }
                        for h in hits
                    ],
                },
                indent=2,
            )
        )
    elif args.command == "answer":
        _, hits, generated = engine.answer(args.query, top_k=args.top_k)
        print(generated)
        print("\nCITATIONS")
        for i, hit in enumerate(hits, start=1):
            print(f"[{i}] {hit.chunk.document_id} score={hit.score:.3f} chunk={hit.chunk.id}")
    elif args.command == "benchmark":
        result = evaluate(engine, load_fixtures(args.fixtures), top_k=args.top_k)
        print(
            json.dumps(
                {
                    "queries": result.queries,
                    f"recall@{args.top_k}": round(result.recall_at_k, 4),
                    "mrr": round(result.mrr, 4),
                    f"ndcg@{args.top_k}": round(result.ndcg_at_k, 4),
                    "hit@1": round(result.hit_at_1, 4),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
