from __future__ import annotations

from pathlib import Path

import pytest

from incidentrag.service import IncidentRAG, load_documents_from_directory

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def sample_root() -> Path:
    return PROJECT_ROOT / "data" / "sample"


@pytest.fixture()
def seeded_engine(tmp_path: Path, sample_root: Path) -> IncidentRAG:
    engine = IncidentRAG(tmp_path / "test.db", abstention_threshold=0.85)
    engine.ingest_many(load_documents_from_directory(sample_root))
    return engine
