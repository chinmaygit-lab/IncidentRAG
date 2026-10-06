from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .tokenization import tokenize


@dataclass(slots=True)
class BM25Document:
    identifier: str
    tokens: list[str]


class BM25Index:
    def __init__(self, documents: list[BM25Document], *, k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self._term_frequencies = [Counter(doc.tokens) for doc in documents]
        self._lengths = [len(doc.tokens) for doc in documents]
        self._avgdl = sum(self._lengths) / len(self._lengths) if self._lengths else 0.0
        self._document_frequency: Counter[str] = Counter()
        for doc in documents:
            self._document_frequency.update(set(doc.tokens))

    @classmethod
    def from_texts(cls, items: list[tuple[str, str]]) -> BM25Index:
        return cls([BM25Document(identifier=i, tokens=tokenize(text)) for i, text in items])

    def _idf(self, term: str) -> float:
        n = len(self.documents)
        df = self._document_frequency.get(term, 0)
        if n == 0:
            return 0.0
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def score(self, query: str) -> list[tuple[str, float]]:
        query_terms = tokenize(query)
        results: list[tuple[str, float]] = []
        for doc, frequencies, length in zip(
            self.documents, self._term_frequencies, self._lengths, strict=True
        ):
            score = 0.0
            for term in query_terms:
                tf = frequencies.get(term, 0)
                if tf == 0:
                    continue
                norm = 1.0 - self.b
                if self._avgdl:
                    norm += self.b * length / self._avgdl
                denominator = tf + self.k1 * norm
                score += self._idf(term) * tf * (self.k1 + 1.0) / denominator
            results.append((doc.identifier, score))
        return sorted(results, key=lambda item: (-item[1], item[0]))
