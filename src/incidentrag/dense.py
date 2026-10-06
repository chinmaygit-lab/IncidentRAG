from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from .tokenization import tokenize


def _stable_bucket(feature: str, dimensions: int) -> tuple[int, float]:
    digest = hashlib.blake2b(feature.encode(), digest_size=8).digest()
    value = int.from_bytes(digest, "big")
    bucket = value % dimensions
    sign = -1.0 if value & 1 else 1.0
    return bucket, sign


@dataclass(slots=True)
class HashingEmbedder:
    """Dependency-free deterministic embedding baseline using signed feature hashing."""

    dimensions: int = 256

    def embed(self, text: str) -> list[float]:
        if self.dimensions < 16:
            raise ValueError("dimensions must be >= 16")
        tokens = tokenize(text)
        vector = [0.0] * self.dimensions
        features = tokens + [f"{a}::{b}" for a, b in zip(tokens, tokens[1:], strict=False)]
        for feature in features:
            bucket, sign = _stable_bucket(feature, self.dimensions)
            vector[bucket] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return vector


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vectors must have equal dimensions")
    return sum(x * y for x, y in zip(a, b, strict=True))


class DenseIndex:
    def __init__(self, items: list[tuple[str, str]], embedder: HashingEmbedder | None = None):
        self.embedder = embedder or HashingEmbedder()
        self._vectors = [(identifier, self.embedder.embed(text)) for identifier, text in items]

    def score(self, query: str) -> list[tuple[str, float]]:
        q = self.embedder.embed(query)
        values = [(identifier, cosine_similarity(q, vector)) for identifier, vector in self._vectors]
        return sorted(values, key=lambda item: (-item[1], item[0]))
