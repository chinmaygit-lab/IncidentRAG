import pytest

from incidentrag.retrieval import HybridRetriever


def test_checkout_retrieval_hits_expected_document(seeded_engine):
    parsed, hits = seeded_engine.search("P1 service=checkout HTTP 503 UPSTREAM_UNAVAILABLE", top_k=3)
    assert parsed.service == "checkout"
    assert hits[0].chunk.document_id in {"checkout_503", "inc_checkout_2026"}
    assert "service" in hits[0].matched_fields
    assert "http_status" in hits[0].matched_fields


def test_each_service_structured_query_ranks_correct_family(seeded_engine):
    cases = [
        ("payments", 502, "PAYMENT_GATEWAY_TIMEOUT"),
        ("inventory", 500, "INVENTORY_DB_ERROR"),
        ("auth", 401, "TOKEN_EXPIRED"),
        ("search", 429, "RATE_LIMITED"),
        ("orders", 504, "DB_POOL_EXHAUSTED"),
        ("notifications", 500, "SMTP_PROVIDER_ERROR"),
        ("catalog", 404, "STALE_CACHE"),
        ("shipping", 503, "CARRIER_UNAVAILABLE"),
        ("profile", 500, "SCHEMA_MISMATCH"),
    ]
    for service, status, code in cases:
        _, hits = seeded_engine.search(f"P1 service={service} HTTP {status} {code}", top_k=2)
        assert hits[0].chunk.metadata["service"] == service


def test_scores_are_sorted_and_bounded(seeded_engine):
    _, hits = seeded_engine.search("checkout 503 readiness", top_k=8)
    scores = [hit.score for hit in hits]
    assert scores == sorted(scores, reverse=True)
    assert all(0.0 <= score <= 1.0 for score in scores)


def test_search_top_k_validation(tmp_path):
    retriever = HybridRetriever([])
    with pytest.raises(ValueError):
        retriever.search("x", top_k=0)


def test_search_empty_corpus_returns_no_hits(tmp_path):
    parsed, hits = HybridRetriever([]).search("checkout", top_k=3)
    assert parsed.raw == "checkout"
    assert hits == []
