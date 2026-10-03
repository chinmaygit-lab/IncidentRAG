from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .nlp import tokenize


@dataclass(slots=True)
class BM25Document:
    identifier: str
    tokens: list[str]


class BM25Index:
    """Small dependency-free BM25 implementation suitable for learning and tests."""

    def __init__(self, documents: list[BM25Document], k1: float = 1.5, b: float = 0.75) -> None:
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.doc_lengths = [len(doc.tokens) for doc in documents]
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        self.term_freqs = [Counter(doc.tokens) for doc in documents]
        self.doc_freqs: Counter[str] = Counter()
        for tf in self.term_freqs:
            self.doc_freqs.update(tf.keys())

    @classmethod
    def from_texts(cls, items: list[tuple[str, str]]) -> BM25Index:
        return cls([BM25Document(identifier=identifier, tokens=tokenize(text)) for identifier, text in items])

    def idf(self, term: str) -> float:
        n = len(self.documents)
        df = self.doc_freqs.get(term, 0)
        if n == 0:
            return 0.0
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def score_tokens(self, query_tokens: list[str]) -> list[tuple[str, float]]:
        if not self.documents:
            return []
        scores: list[tuple[str, float]] = []
        for i, doc in enumerate(self.documents):
            score = 0.0
            dl = self.doc_lengths[i]
            tf = self.term_freqs[i]
            for term in query_tokens:
                freq = tf.get(term, 0)
                if freq == 0:
                    continue
                denom = freq + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1.0))
                score += self.idf(term) * ((freq * (self.k1 + 1)) / denom)
            scores.append((doc.identifier, score))
        return sorted(scores, key=lambda pair: (-pair[1], pair[0]))

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        return self.score_tokens(tokenize(query))[:top_k]
