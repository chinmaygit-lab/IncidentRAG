from incidentrag.models import Document
from incidentrag.storage import SQLiteStore


def test_store_upsert_replaces_document(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    store.upsert_document(Document(id="a", title="A", text="first", metadata={"service": "x"}))
    store.upsert_document(Document(id="a", title="A2", text="second", metadata={"service": "y"}))
    docs = store.list_documents()
    assert len(docs) == 1
    assert docs[0].title == "A2"
    assert docs[0].metadata["service"] == "y"


def test_store_reset_clears_rows(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    store.upsert_document(Document(id="a", title="A", text="hello world"))
    assert store.list_chunks()
    store.reset()
    assert store.list_chunks() == []
    assert store.list_documents() == []
