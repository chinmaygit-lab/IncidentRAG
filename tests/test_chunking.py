import pytest

from incidentrag.chunking import chunk_document
from incidentrag.models import Document


def test_chunking_preserves_document_metadata():
    doc = Document(
        id="d1", title="Doc", text="First paragraph.\n\nSecond paragraph.", metadata={"service": "x"}
    )
    chunks = chunk_document(doc, target_chars=200, overlap_chars=20)
    assert chunks
    assert all(c.metadata["service"] == "x" for c in chunks)


def test_chunk_ids_are_deterministic():
    doc = Document(id="d1", title="Doc", text="Alpha.\n\nBeta.")
    a = [c.id for c in chunk_document(doc)]
    b = [c.id for c in chunk_document(doc)]
    assert a == b


def test_empty_document_yields_no_chunks():
    doc = Document(id="empty", title="Empty", text="   \n\n  ")
    assert chunk_document(doc) == []


def test_invalid_overlap_rejected():
    doc = Document(id="d", title="D", text="hello")
    with pytest.raises(ValueError):
        chunk_document(doc, target_chars=200, overlap_chars=200)
