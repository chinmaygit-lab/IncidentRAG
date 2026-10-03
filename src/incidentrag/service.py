from __future__ import annotations

from pathlib import Path

from .generation import GroundedTemplateGenerator
from .models import Document, SearchHit
from .retrieval import IncidentRetriever
from .storage import SQLiteStore

# Baseline calibrated against:
# benchmark/fixtures_v2.json
# benchmark/no_answer_queries.json
#
# Recalibrate whenever the corpus or retrieval algorithm changes.
DEFAULT_MIN_SCORE = 2.7510


class IncidentRAG:
    def __init__(
        self,
        db_path: str | Path = "incidentrag.db",
        min_score: float | None = DEFAULT_MIN_SCORE,
    ) -> None:
        self.store = SQLiteStore(db_path)
        self.retriever = IncidentRetriever(self.store)
        self.generator = GroundedTemplateGenerator()
        self.min_score = min_score

    def ingest(self, document: Document) -> int:
        return self.store.upsert_document(document)

    def raw_search(
        self,
        query: str,
        top_k: int = 5,
    ):
        """Return retrieval results before confidence filtering."""
        return self.retriever.search(
            query,
            top_k=top_k,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):
        """Return only evidence meeting the calibrated score threshold."""
        parsed, hits = self.raw_search(
            query,
            top_k=top_k,
        )

        if self.min_score is None:
            return parsed, hits

        accepted = [hit for hit in hits if hit.score >= self.min_score]

        return parsed, accepted

    def answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> tuple[object, list[SearchHit], str]:
        parsed, hits = self.search(
            query,
            top_k=top_k,
        )

        answer = self.generator.generate(
            parsed,
            hits,
        )

        return parsed, hits, answer
