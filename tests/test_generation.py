def test_answer_contains_cited_title(engine):
    _, hits, answer = engine.answer("service=payments HTTP 504 timeout", top_k=3)
    assert hits
    assert hits[0].chunk.title in answer
    assert "[1]" in answer


def test_no_evidence_abstains(engine):
    _, hits, answer = engine.answer("quantum banana telescope", top_k=3)
    assert hits == []
    assert "No supporting" in answer
