import json
from pathlib import Path

from incidentrag.evals import evaluate, load_fixtures
from incidentrag.service import dump_answer


def test_service_health_counts_seeded_documents(seeded_engine):
    health = seeded_engine.health()
    assert health["status"] == "ok"
    assert health["documents"] == 20
    assert health["chunks"] >= 20


def test_answer_checkout_has_citations(seeded_engine):
    answer = seeded_engine.answer("P1 service=checkout HTTP 503 UPSTREAM_UNAVAILABLE")
    assert not answer.abstained
    assert answer.citations


def test_dump_answer_is_json(seeded_engine):
    payload = json.loads(dump_answer(seeded_engine.answer("service=auth HTTP 401 TOKEN_EXPIRED")))
    assert payload["query"].startswith("service=auth")
    assert isinstance(payload["citations"], list)


def test_evaluate_full_benchmark(seeded_engine, sample_root):
    project = Path(sample_root).parents[1]
    fixtures = load_fixtures(project / "benchmark" / "fixtures.json")
    metrics = evaluate(seeded_engine, fixtures, top_k=3)
    assert metrics.queries == 60
    assert metrics.answerable_queries == 40
    assert metrics.no_answer_queries == 20
    assert metrics.recall_at_k >= 0.95
    assert metrics.hit_at_1 >= 0.90
    assert metrics.balanced_abstention_accuracy >= 0.75


def test_load_fixtures_returns_list(sample_root):
    project = Path(sample_root).parents[1]
    fixtures = load_fixtures(project / "benchmark" / "fixtures.json")
    assert isinstance(fixtures, list)
    assert fixtures[0]["expected_document_ids"]


def test_unknown_incident_abstains(seeded_engine):
    answer = seeded_engine.answer("service=video HTTP 507 disk quota exceeded")
    assert answer.abstained
    assert not answer.citations
