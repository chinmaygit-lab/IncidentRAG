from __future__ import annotations

from pathlib import Path

from .generation import GroundedTemplateGenerator
from .models import Document, SearchHit
from .retrieval import IncidentRetriever
from .storage import SQLiteStore


class IncidentRAG:
    def __init__(self, db_path: str | Path = "incidentrag.db") -> None:
        self.store = SQLiteStore(db_path)
        self.retriever = IncidentRetriever(self.store)
        self.generator = GroundedTemplateGenerator()

    def ingest(self, document: Document) -> int:
        return self.store.upsert_document(document)

    def search(self, query: str, top_k: int = 5):
        return self.retriever.search(query, top_k=top_k)

    def answer(self, query: str, top_k: int = 5) -> tuple[object, list[SearchHit], str]:
        parsed, hits = self.search(query, top_k=top_k)
        answer = self.generator.generate(parsed, hits)
        return parsed, hits, answer
