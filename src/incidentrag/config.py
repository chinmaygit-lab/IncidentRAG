from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    database_path: str = "incidentrag.db"
    abstention_threshold: float = 0.85
    abstention_min_margin: float = 0.015
    api_key: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            database_path=os.getenv("INCIDENTRAG_DB", "incidentrag.db"),
            abstention_threshold=float(os.getenv("INCIDENTRAG_ABSTENTION_THRESHOLD", "0.85")),
            abstention_min_margin=float(os.getenv("INCIDENTRAG_ABSTENTION_MIN_MARGIN", "0.015")),
            api_key=os.getenv("INCIDENTRAG_API_KEY") or None,
        )
