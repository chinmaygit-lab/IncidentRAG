from __future__ import annotations

from pathlib import Path

import pytest

from incidentrag.cli import _load_directory
from incidentrag.service import IncidentRAG


@pytest.fixture()
def engine(tmp_path: Path) -> IncidentRAG:
    app = IncidentRAG(tmp_path / "test.db")
    root = Path(__file__).parents[1] / "data" / "sample"
    _load_directory(app, root / "runbooks", "runbook")
    _load_directory(app, root / "incidents", "incident")
    return app
