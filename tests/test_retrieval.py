def test_checkout_query_retrieves_checkout_evidence(engine):
    _, hits = engine.search("P1 service=checkout HTTP 503 after deployment", top_k=4)
    ids = [h.chunk.document_id for h in hits]
    assert "checkout_503" in ids[:3]
    assert "inc_checkout_2026_09" in ids[:3]


def test_metadata_boost_is_exposed(engine):
    _, hits = engine.search("service=auth HTTP 401", top_k=3)
    assert hits[0].metadata_boost > 0
    assert "service" in hits[0].matched_fields


def test_unrelated_query_returns_no_or_low_evidence(engine):
    _, hits = engine.search("quantum banana telescope", top_k=5)
    assert hits == []


def test_retrieval_is_deterministic(engine):
    q = "inventory HTTP 500 migration"
    _, a = engine.search(q, top_k=5)
    _, b = engine.search(q, top_k=5)
    assert [(h.chunk.id, h.score) for h in a] == [(h.chunk.id, h.score) for h in b]
