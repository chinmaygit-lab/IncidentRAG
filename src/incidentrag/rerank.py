from __future__ import annotations

from .models import Chunk, ParsedIncident
from .tokenization import unique_tokens


def metadata_matches(parsed: ParsedIncident, chunk: Chunk) -> tuple[float, list[str]]:
    score = 0.0
    matched: list[str] = []
    metadata = chunk.metadata

    if parsed.service and str(metadata.get("service", "")).lower() == parsed.service:
        score += 0.10
        matched.append("service")
    if parsed.http_status and metadata.get("http_status") == parsed.http_status:
        score += 0.07
        matched.append("http_status")
    if parsed.error_code and str(metadata.get("error_code", "")).upper() == parsed.error_code:
        score += 0.10
        matched.append("error_code")
    if parsed.severity and str(metadata.get("severity", "")).upper() == parsed.severity:
        score += 0.03
        matched.append("severity")
    return score, matched


def title_overlap(query: str, chunk: Chunk) -> float:
    query_tokens = unique_tokens(query)
    title_tokens = unique_tokens(chunk.title)
    if not query_tokens or not title_tokens:
        return 0.0
    return len(query_tokens & title_tokens) / len(query_tokens)


def rerank_score(
    *,
    query: str,
    parsed: ParsedIncident,
    chunk: Chunk,
    lexical_norm: float,
    dense_norm: float,
    rrf_norm: float,
) -> tuple[float, list[str]]:
    boost, matched = metadata_matches(parsed, chunk)
    overlap = title_overlap(query, chunk)
    score = 0.38 * lexical_norm + 0.30 * dense_norm + 0.17 * rrf_norm + 0.05 * overlap + boost
    return min(max(score, 0.0), 1.0), matched
