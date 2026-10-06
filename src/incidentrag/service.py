from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .abstention import AbstentionPolicy
from .generation import GroundedGenerator
from .models import Answer, Document, ParsedIncident, SearchHit
from .retrieval import HybridRetriever
from .storage import SQLiteStore
from .telemetry import Telemetry


class IncidentRAG:
    def __init__(
        self,
        db_path: str | Path = "incidentrag.db",
        *,
        abstention_threshold: float = 0.85,
        abstention_min_margin: float = 0.015,
    ):
        self.store = SQLiteStore(db_path)
        self.policy = AbstentionPolicy(abstention_threshold, abstention_min_margin)
        self.generator = GroundedGenerator()
        self.telemetry = Telemetry()

    def ingest(self, document: Document) -> int:
        return len(self.store.upsert_document(document))

    def ingest_many(self, documents: Iterable[Document]) -> int:
        return self.store.upsert_documents(documents)

    def _retriever(self) -> HybridRetriever:
        return HybridRetriever(self.store.all_chunks())

    def search(self, query: str, *, top_k: int = 5) -> tuple[ParsedIncident, list[SearchHit]]:
        with self.telemetry.measure("search"):
            return self._retriever().search(query, top_k=top_k)

    def answer(self, query: str, *, top_k: int = 3) -> Answer:
        with self.telemetry.measure("answer"):
            parsed, hits = self._retriever().search(query, top_k=top_k)
            abstain = self.policy.should_abstain([hit.score for hit in hits])
            if abstain:
                self.telemetry.record_abstention()
            return self.generator.generate(query=query, parsed=parsed, hits=hits, abstain=abstain)

    def health(self) -> dict[str, object]:
        return {
            "status": "ok",
            "documents": self.store.count_documents(),
            "chunks": len(self.store.all_chunks()),
            "telemetry": self.telemetry.snapshot(),
        }


def load_documents_from_directory(root: str | Path) -> list[Document]:
    root = Path(root)
    documents: list[Document] = []
    for source_type in ("runbooks", "incidents"):
        folder = root / source_type
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            metadata: dict[str, object] = {}
            title = path.stem.replace("_", " ").title()
            lines = text.splitlines()
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()
            for line in lines[1:12]:
                if ":" not in line:
                    continue
                key, value = [part.strip() for part in line.split(":", 1)]
                if key.lower() in {"service", "severity", "http_status", "error_code"}:
                    normalized: object = value
                    if key.lower() == "http_status" and value.isdigit():
                        normalized = int(value)
                    metadata[key.lower()] = normalized
            documents.append(
                Document(
                    id=path.stem,
                    title=title,
                    text=text,
                    source_type="runbook" if source_type == "runbooks" else "incident",
                    metadata=metadata,
                )
            )
    return documents


def dump_answer(answer: Answer) -> str:
    payload = {
        "query": answer.query,
        "text": answer.text,
        "abstained": answer.abstained,
        "confidence": round(answer.confidence, 6),
        "citations": [
            {
                "index": citation.index,
                "document_id": citation.document_id,
                "chunk_id": citation.chunk_id,
                "title": citation.title,
                "score": round(citation.score, 6),
                "excerpt": citation.excerpt,
            }
            for citation in answer.citations
        ],
    }
    return json.dumps(payload, indent=2)
