import math

import pytest

from incidentrag.dense import DenseIndex, HashingEmbedder, cosine_similarity
from incidentrag.fusion import reciprocal_rank_fusion


def test_embedding_is_deterministic_and_normalized():
    embedder = HashingEmbedder(64)
    a = embedder.embed("checkout readiness 503")
    b = embedder.embed("checkout readiness 503")
    assert a == b
    assert math.isclose(sum(x * x for x in a), 1.0, rel_tol=1e-9)


def test_embedding_empty_text_is_zero_vector():
    assert sum(HashingEmbedder(32).embed("")) == 0


def test_embedding_rejects_tiny_dimensions():
    with pytest.raises(ValueError):
        HashingEmbedder(8).embed("x")


def test_cosine_identical_is_one():
    vector = HashingEmbedder(64).embed("auth token")
    assert math.isclose(cosine_similarity(vector, vector), 1.0, rel_tol=1e-9)


def test_cosine_rejects_dimension_mismatch():
    with pytest.raises(ValueError):
        cosine_similarity([1.0], [1.0, 2.0])


def test_dense_ranks_similar_first():
    index = DenseIndex(
        [("a", "payments provider timeout"), ("b", "catalog stale cache")],
        HashingEmbedder(64),
    )
    assert index.score("payments timeout")[0][0] == "a"


def test_rrf_combines_rankings():
    result = reciprocal_rank_fusion([[('a', 10), ('b', 5)], [('b', 10), ('a', 1)]], k=60)
    assert {identifier for identifier, _ in result} == {"a", "b"}


def test_rrf_rejects_nonpositive_k():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([], k=0)
