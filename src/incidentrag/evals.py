from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

from .service import IncidentRAG


@dataclass(slots=True)
class EvalResult:
    queries: int
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    hit_at_1: float


def _dcg(relevances: list[int]) -> float:
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances))


def evaluate(engine: IncidentRAG, fixtures: list[dict], top_k: int = 3) -> EvalResult:
    if not fixtures:
        return EvalResult(queries=0, recall_at_k=0.0, mrr=0.0, ndcg_at_k=0.0, hit_at_1=0.0)

    recall_total = 0.0
    rr_total = 0.0
    ndcg_total = 0.0
    hit1_total = 0.0

    for fixture in fixtures:
        expected = set(fixture["relevant_document_ids"])
        _, hits = engine.search(fixture["query"], top_k=top_k)
        ranked = [hit.chunk.document_id for hit in hits]
        unique_ranked = list(dict.fromkeys(ranked))
        retrieved = set(unique_ranked[:top_k])
        recall_total += len(retrieved & expected) / max(1, len(expected))

        first_rank = next(
            (i + 1 for i, doc_id in enumerate(unique_ranked[:top_k]) if doc_id in expected), None
        )
        rr_total += 1.0 / first_rank if first_rank else 0.0
        hit1_total += 1.0 if unique_ranked and unique_ranked[0] in expected else 0.0

        rels = [1 if doc_id in expected else 0 for doc_id in unique_ranked[:top_k]]
        ideal = [1] * min(len(expected), top_k)
        idcg = _dcg(ideal)
        ndcg_total += (_dcg(rels) / idcg) if idcg else 0.0

    n = len(fixtures)
    return EvalResult(
        queries=n,
        recall_at_k=recall_total / n,
        mrr=rr_total / n,
        ndcg_at_k=ndcg_total / n,
        hit_at_1=hit1_total / n,
    )


def load_fixtures(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate IncidentRAG retrieval")
    parser.add_argument("fixtures", type=Path)
    parser.add_argument("--db", default="incidentrag.db")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    engine = IncidentRAG(args.db)
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
