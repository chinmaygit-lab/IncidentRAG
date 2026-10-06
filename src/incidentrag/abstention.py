from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AbstentionPolicy:
    threshold: float = 0.42
    min_margin: float = 0.015

    def should_abstain(self, scores: list[float]) -> bool:
        if not scores:
            return True
        if scores[0] < self.threshold:
            return True
        return (
            len(scores) > 1
            and scores[0] - scores[1] < self.min_margin
            and scores[0] < self.threshold + 0.08
        )


def calibrate_threshold(labeled_scores: list[tuple[float, bool]]) -> tuple[float, float]:
    """Return threshold maximizing balanced accuracy for (top_score, answerable)."""
    if not labeled_scores:
        raise ValueError("labeled_scores cannot be empty")
    candidates = sorted({0.0, 1.0, *(score for score, _ in labeled_scores)})
    candidates.extend((a + b) / 2 for a, b in zip(candidates, candidates[1:], strict=False))

    best_threshold = 0.0
    best_balanced = -1.0
    for threshold in sorted(set(candidates)):
        positives = [score >= threshold for score, answerable in labeled_scores if answerable]
        negatives = [score < threshold for score, answerable in labeled_scores if not answerable]
        tpr = sum(positives) / len(positives) if positives else 1.0
        tnr = sum(negatives) / len(negatives) if negatives else 1.0
        balanced = (tpr + tnr) / 2
        if balanced > best_balanced or (balanced == best_balanced and threshold > best_threshold):
            best_balanced = balanced
            best_threshold = threshold
    return best_threshold, best_balanced
