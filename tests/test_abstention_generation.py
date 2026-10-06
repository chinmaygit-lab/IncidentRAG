import pytest

from incidentrag.abstention import AbstentionPolicy, calibrate_threshold
from incidentrag.generation import CallableGroundedGenerator, GroundedGenerator
from incidentrag.models import Chunk, ParsedIncident, SearchHit


def _hit(score=0.8):
    chunk = Chunk(
        id="c1",
        document_id="d1",
        title="Checkout Runbook",
        text="Check readiness failures. Rollback the deployment when confirmed.",
        position=0,
        source_type="runbook",
        metadata={"service": "checkout"},
    )
    return SearchHit(chunk=chunk, score=score)


def test_policy_abstains_without_scores():
    assert AbstentionPolicy().should_abstain([])


def test_policy_accepts_strong_score():
    assert not AbstentionPolicy(threshold=0.4, min_margin=0.01).should_abstain([0.8, 0.4])


def test_policy_abstains_low_score():
    assert AbstentionPolicy(threshold=0.4).should_abstain([0.2])


def test_calibration_separates_simple_scores():
    threshold, balanced = calibrate_threshold([(0.9, True), (0.8, True), (0.2, False), (0.1, False)])
    assert 0.2 < threshold <= 0.8
    assert balanced == 1.0


def test_calibration_rejects_empty():
    with pytest.raises(ValueError):
        calibrate_threshold([])


def test_grounded_generator_abstains():
    answer = GroundedGenerator().generate(
        query="unknown", parsed=ParsedIncident(raw="unknown"), hits=[], abstain=True
    )
    assert answer.abstained
    assert not answer.citations


def test_grounded_generator_cites_actions():
    answer = GroundedGenerator().generate(
        query="checkout",
        parsed=ParsedIncident(raw="checkout", service="checkout"),
        hits=[_hit()],
        abstain=False,
    )
    assert not answer.abstained
    assert "[1]" in answer.text
    assert answer.citations[0].document_id == "d1"


def test_callable_generator_validates_citations():
    generator = CallableGroundedGenerator(lambda prompt: "Use the runbook [1].")
    assert generator.generate_text("q", [_hit()]) == "Use the runbook [1]."


def test_callable_generator_rejects_uncited_output():
    generator = CallableGroundedGenerator(lambda prompt: "Do a thing.")
    with pytest.raises(ValueError):
        generator.generate_text("q", [_hit()])


def test_callable_generator_rejects_invalid_citation():
    generator = CallableGroundedGenerator(lambda prompt: "Use evidence [2].")
    with pytest.raises(ValueError):
        generator.generate_text("q", [_hit()])
