from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .abstention import calibrate_threshold


@dataclass(slots=True)
class RetrievalMetrics:
    queries: int
    answerable_queries: int
    no_answer_queries: int
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    hit_at_1: float
    no_answer_accuracy: float
    answerable_acceptance: float
    balanced_abstention_accuracy: float
    calibrated_threshold: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dcg(relevances: list[int]) -> float:
    return sum(rel / math.log2(index + 2) for index, rel in enumerate(relevances))


def evaluate(engine: Any, fixtures: list[dict[str, Any]], *, top_k: int = 3) -> RetrievalMetrics:
    answerable = [fixture for fixture in fixtures if fixture.get("expected_document_ids")]
    no_answer = [fixture for fixture in fixtures if not fixture.get("expected_document_ids")]

    recall_total = 0.0
    reciprocal_total = 0.0
    ndcg_total = 0.0
    hit1_total = 0.0
    labeled_scores: list[tuple[float, bool]] = []
    cached: list[tuple[dict[str, Any], list[Any]]] = []

    for fixture in fixtures:
        _parsed, hits = engine.search(fixture["query"], top_k=top_k)
        cached.append((fixture, hits))
        labeled_scores.append((hits[0].score if hits else 0.0, bool(fixture.get("expected_document_ids"))))

        expected = set(fixture.get("expected_document_ids", []))
        if not expected:
            continue
        unique_ranked: list[str] = []
        for hit in hits:
            if hit.chunk.document_id not in unique_ranked:
                unique_ranked.append(hit.chunk.document_id)
        retrieved = set(unique_ranked[:top_k])
        recall_total += len(retrieved & expected) / len(expected)
        first_rank = next(
            (index + 1 for index, doc_id in enumerate(unique_ranked[:top_k]) if doc_id in expected),
            None,
        )
        reciprocal_total += 1.0 / first_rank if first_rank else 0.0
        hit1_total += 1.0 if unique_ranked and unique_ranked[0] in expected else 0.0
        relevances = [1 if doc_id in expected else 0 for doc_id in unique_ranked[:top_k]]
        ideal = [1] * min(len(expected), top_k)
        denominator = _dcg(ideal)
        ndcg_total += _dcg(relevances) / denominator if denominator else 0.0

    threshold, balanced = calibrate_threshold(labeled_scores)
    no_answer_correct = 0
    answerable_accepted = 0
    for fixture, hits in cached:
        score = hits[0].score if hits else 0.0
        if fixture.get("expected_document_ids"):
            answerable_accepted += int(score >= threshold)
        else:
            no_answer_correct += int(score < threshold)

    n_answerable = max(1, len(answerable))
    n_no_answer = max(1, len(no_answer))
    return RetrievalMetrics(
        queries=len(fixtures),
        answerable_queries=len(answerable),
        no_answer_queries=len(no_answer),
        recall_at_k=recall_total / n_answerable,
        mrr=reciprocal_total / n_answerable,
        ndcg_at_k=ndcg_total / n_answerable,
        hit_at_1=hit1_total / n_answerable,
        no_answer_accuracy=no_answer_correct / n_no_answer,
        answerable_acceptance=answerable_accepted / n_answerable,
        balanced_abstention_accuracy=balanced,
        calibrated_threshold=threshold,
    )


def load_fixtures(path: str | Path) -> list[dict[str, Any]]:
    return list(json.loads(Path(path).read_text(encoding="utf-8")))
