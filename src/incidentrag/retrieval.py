from __future__ import annotations

from .bm25 import BM25Index
from .models import ParsedIncident, SearchHit
from .nlp import parse_incident, tokenize
from .storage import SQLiteStore


class IncidentRetriever:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    @staticmethod
    def _query_tokens(parsed: ParsedIncident) -> list[str]:
        tokens = tokenize(parsed.raw)
        structured = [
            parsed.service,
            str(parsed.http_status) if parsed.http_status else None,
            parsed.severity.lower() if parsed.severity else None,
            *(code.lower() for code in parsed.error_codes),
        ]
        for token in structured:
            if token and token not in tokens:
                tokens.append(token)
        return tokens

    @staticmethod
    def _metadata_boost(parsed: ParsedIncident, metadata: dict, text: str) -> tuple[float, list[str]]:
        boost = 0.0
        matched: list[str] = []
        lowered = text.lower()
        service = str(metadata.get("service", "")).lower()
        if parsed.service and (parsed.service == service or parsed.service in lowered):
            boost += 2.5
            matched.append("service")
        if parsed.http_status and (
            str(parsed.http_status) == str(metadata.get("http_status", "")) or str(parsed.http_status) in text
        ):
            boost += 1.5
            matched.append("http_status")
        if parsed.severity and parsed.severity == str(metadata.get("severity", "")).upper():
            boost += 0.35
            matched.append("severity")
        for code in parsed.error_codes:
            if code.lower() in lowered or code.lower() == str(metadata.get("error_code", "")).lower():
                boost += 1.0
                matched.append(f"error:{code}")
        return boost, matched

    def search(self, query: str, top_k: int = 5) -> tuple[ParsedIncident, list[SearchHit]]:
        parsed = parse_incident(query)
        chunks = self.store.list_chunks()
        if not chunks:
            return parsed, []

        index = BM25Index.from_texts([(chunk.id, f"{chunk.title}\n{chunk.text}") for chunk in chunks])
        score_map = dict(index.score_tokens(self._query_tokens(parsed)))
        hits: list[SearchHit] = []
        for chunk in chunks:
            lexical = score_map.get(chunk.id, 0.0)
            boost, matched = self._metadata_boost(parsed, chunk.metadata, chunk.text)
            score = lexical + boost
            if score <= 0:
                continue
            hits.append(
                SearchHit(
                    chunk=chunk,
                    score=score,
                    lexical_score=lexical,
                    metadata_boost=boost,
                    matched_fields=matched,
                )
            )
        hits.sort(key=lambda hit: (-hit.score, -hit.lexical_score, hit.chunk.id))
        return parsed, hits[:top_k]
