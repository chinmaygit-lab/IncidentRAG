from __future__ import annotations

import json
from pathlib import Path

from incidentrag.service import (
    DEFAULT_MIN_SCORE,
    IncidentRAG,
)


def test_default_threshold_matches_calibrated_baseline():
    assert DEFAULT_MIN_SCORE == 2.7510


def test_strong_incident_query_is_retained(engine):
    _, hits = engine.search(
        "P1 service=checkout HTTP 503 after deployment",
        top_k=3,
    )

    assert hits
    assert hits[0].score >= DEFAULT_MIN_SCORE


def test_raw_search_is_available_for_calibration(engine):
    _, raw_hits = engine.raw_search(
        "service=checkout confirmation email template typo",
        top_k=3,
    )

    _, filtered_hits = engine.search(
        "service=checkout confirmation email template typo",
        top_k=3,
    )

    assert len(filtered_hits) <= len(raw_hits)


def test_threshold_can_be_disabled(tmp_path: Path):
    engine = IncidentRAG(
        tmp_path / "threshold-disabled.db",
        min_score=None,
    )

    assert engine.min_score is None


def test_calibration_dataset_contains_low_scoring_no_answer_case(engine):
    root = Path(__file__).parents[1]

    queries = json.loads((root / "benchmark" / "no_answer_queries.json").read_text(encoding="utf-8"))

    found_low_positive = False

    for query in queries:
        _, raw_hits = engine.raw_search(
            query,
            top_k=3,
        )

        if raw_hits and 0.0 < raw_hits[0].score < DEFAULT_MIN_SCORE:
            _, filtered_hits = engine.search(
                query,
                top_k=3,
            )

            assert filtered_hits == []
            found_low_positive = True
            break

    assert found_low_positive
