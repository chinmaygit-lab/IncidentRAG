from incidentrag.bm25 import BM25Index


def test_bm25_ranks_matching_document_first():
    index = BM25Index.from_texts([("a", "checkout 503 deployment"), ("b", "payment timeout 504")])
    assert index.search("checkout 503", top_k=2)[0][0] == "a"


def test_bm25_empty_index():
    assert BM25Index.from_texts([]).search("anything") == []


def test_bm25_idf_is_positive_for_seen_term():
    index = BM25Index.from_texts([("a", "alpha beta"), ("b", "beta gamma")])
    assert index.idf("alpha") > 0
