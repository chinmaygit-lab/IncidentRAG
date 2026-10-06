from __future__ import annotations

from dataclasses import dataclass

from .bm25 import BM25Index
from .dense import DenseIndex, HashingEmbedder
from .fusion import reciprocal_rank_fusion
from .models import Chunk, ParsedIncident, SearchHit
from .parsing import parse_incident
from .rerank import rerank_score


def _search_text(chunk: Chunk) -> str:
    metadata = " ".join(f"{key} {value}" for key, value in sorted(chunk.metadata.items()))
    return f"{chunk.title}\n{chunk.text}\n{metadata}"


def _normalize_scores(ranking: list[tuple[str, float]]) -> dict[str, float]:
    if not ranking:
        return {}
    values = [score for _, score in ranking]
    maximum = max(values)
    minimum = min(values)
    if maximum <= 0:
        return {identifier: 0.0 for identifier, _ in ranking}
    if maximum == minimum:
        return {identifier: 1.0 if maximum > 0 else 0.0 for identifier, _ in ranking}
    return {identifier: max(0.0, (score - minimum) / (maximum - minimum)) for identifier, score in ranking}


@dataclass
class HybridRetriever:
    chunks: list[Chunk]
    embedder: HashingEmbedder | None = None

    def __post_init__(self) -> None:
        items = [(chunk.id, _search_text(chunk)) for chunk in self.chunks]
        self._by_id = {chunk.id: chunk for chunk in self.chunks}
        self._lexical = BM25Index.from_texts(items)
        self._dense = DenseIndex(items, self.embedder or HashingEmbedder())

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        parsed: ParsedIncident | None = None,
    ) -> tuple[ParsedIncident, list[SearchHit]]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        parsed = parsed or parse_incident(query)

        lexical = self._lexical.score(query)
        dense = self._dense.score(query)
        rrf = reciprocal_rank_fusion([lexical, dense])

        lexical_norm = _normalize_scores(lexical)
        dense_shifted = [(identifier, max(0.0, score)) for identifier, score in dense]
        dense_norm = _normalize_scores(dense_shifted)
        rrf_norm = _normalize_scores(rrf)

        lexical_raw = dict(lexical)
        dense_raw = dict(dense)
        rrf_raw = dict(rrf)

        hits: list[SearchHit] = []
        for chunk_id, chunk in self._by_id.items():
            final, matched = rerank_score(
                query=query,
                parsed=parsed,
                chunk=chunk,
                lexical_norm=lexical_norm.get(chunk_id, 0.0),
                dense_norm=dense_norm.get(chunk_id, 0.0),
                rrf_norm=rrf_norm.get(chunk_id, 0.0),
            )
            hits.append(
                SearchHit(
                    chunk=chunk,
                    score=final,
                    lexical_score=lexical_raw.get(chunk_id, 0.0),
                    dense_score=dense_raw.get(chunk_id, 0.0),
                    rrf_score=rrf_raw.get(chunk_id, 0.0),
                    rerank_score=final,
                    matched_fields=matched,
                )
            )
        hits.sort(key=lambda hit: (-hit.score, hit.chunk.id))
        return parsed, hits[:top_k]
