from __future__ import annotations

import json
from pathlib import Path

from incidentrag.service import IncidentRAG

DB_PATH = Path("incidentrag.db")
ANSWERABLE_PATH = Path("benchmark/fixtures_v2.json")
NO_ANSWER_PATH = Path("benchmark/no_answer_queries.json")


def top_score(engine: IncidentRAG, query: str) -> float:
    _, hits = engine.search(query, top_k=3)
    return hits[0].score if hits else 0.0


def main() -> None:
    engine = IncidentRAG(DB_PATH)

    answerable = json.loads(ANSWERABLE_PATH.read_text(encoding="utf-8"))

    no_answer = json.loads(NO_ANSWER_PATH.read_text(encoding="utf-8"))

    positives = [top_score(engine, item["query"]) for item in answerable]

    negatives = [top_score(engine, query) for query in no_answer]

    print("ANSWERABLE TOP-1 SCORES")
    for score in sorted(positives):
        print(f"{score:.4f}")

    print()
    print("NO-ANSWER TOP-1 SCORES")
    for score in sorted(negatives):
        print(f"{score:.4f}")

    candidates = sorted(set([0.0, *positives, *negatives]))

    best = None

    for threshold in candidates:
        true_positive = sum(score >= threshold for score in positives)

        true_negative = sum(score < threshold for score in negatives)

        recall = true_positive / len(positives) if positives else 0.0

        specificity = true_negative / len(negatives) if negatives else 0.0

        balanced_accuracy = (recall + specificity) / 2.0

        result = (
            balanced_accuracy,
            threshold,
            recall,
            specificity,
        )

        if best is None or result > best:
            best = result

    if best is None:
        raise SystemExit("No calibration data.")

    balanced_accuracy, threshold, recall, specificity = best

    print()
    print("CALIBRATION RESULT")
    print(f"threshold={threshold:.4f}")
    print(f"answerable_recall={recall:.4f}")
    print(f"no_answer_specificity={specificity:.4f}")
    print(f"balanced_accuracy={balanced_accuracy:.4f}")


if __name__ == "__main__":
    main()
