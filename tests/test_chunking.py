import pytest

from incidentrag.chunking import chunk_document
from incidentrag.models import Document


def test_chunking_preserves_metadata():
    doc = Document(
        id="d1",
        title="Doc",
        text="First paragraph.\n\nSecond paragraph.",
        metadata={"service": "x"},
    )
    chunks = chunk_document(doc, target_chars=200, overlap_chars=20)
    assert chunks
    assert chunks[0].metadata == {"service": "x"}


def test_chunking_is_deterministic():
    doc = Document(id="d1", title="Doc", text="A paragraph.\n\nB paragraph.")
    first = chunk_document(doc)
    second = chunk_document(doc)
    assert [c.id for c in first] == [c.id for c in second]


def test_chunking_positions_are_sequential():
    text = "\n\n".join(["x" * 90, "y" * 90, "z" * 90])
    chunks = chunk_document(Document(id="d", title="D", text=text), target_chars=120, overlap_chars=10)
    assert [c.position for c in chunks] == list(range(len(chunks)))


def test_chunking_empty_document():
    assert chunk_document(Document(id="d", title="D", text="   ")) == []


@pytest.mark.parametrize("target,overlap", [(99, 0), (100, -1), (100, 100)])
def test_chunking_rejects_invalid_parameters(target, overlap):
    with pytest.raises(ValueError):
        chunk_document(Document(id="d", title="D", text="text"), target_chars=target, overlap_chars=overlap)
