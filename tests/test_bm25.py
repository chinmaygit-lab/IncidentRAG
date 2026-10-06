from incidentrag.bm25 import BM25Index


def test_bm25_ranks_matching_document_first():
    index = BM25Index.from_texts([("a", "checkout 503 readiness"), ("b", "payments 502 timeout")])
    assert index.score("checkout 503")[0][0] == "a"


def test_bm25_unseen_query_scores_zero():
    index = BM25Index.from_texts([("a", "checkout")])
    assert index.score("kafka")[0] == ("a", 0.0)


def test_bm25_empty_corpus():
    assert BM25Index.from_texts([]).score("x") == []


def test_bm25_tie_breaks_by_identifier():
    index = BM25Index.from_texts([("b", "same"), ("a", "same")])
    assert [item[0] for item in index.score("missing")] == ["a", "b"]


def test_bm25_repeated_query_term_increases_score():
    index = BM25Index.from_texts([("a", "checkout checkout")])
    assert index.score("checkout checkout")[0][1] > index.score("checkout")[0][1]
