import json
from pathlib import Path

from incidentrag.evals import evaluate, load_fixtures


def test_evaluate_returns_bounded_metrics(engine):
    fixtures = [
        {"query": "service=checkout HTTP 503", "relevant_document_ids": ["checkout_503"]},
        {"query": "service=auth HTTP 401", "relevant_document_ids": ["auth_401"]},
    ]
    result = evaluate(engine, fixtures, top_k=3)
    assert result.queries == 2
    for value in [result.recall_at_k, result.mrr, result.ndcg_at_k, result.hit_at_1]:
        assert 0.0 <= value <= 1.0


def test_empty_fixture_metrics_are_zero(engine):
    result = evaluate(engine, [], top_k=3)
    assert result.queries == 0
    assert result.mrr == 0.0


def test_load_fixtures(tmp_path: Path):
    p = tmp_path / "fixtures.json"
    p.write_text(json.dumps([{"query": "x", "relevant_document_ids": ["d"]}]), encoding="utf-8")
    assert load_fixtures(p)[0]["query"] == "x"
