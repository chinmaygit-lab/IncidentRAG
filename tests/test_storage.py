from incidentrag.models import Document
from incidentrag.storage import SQLiteStore


def test_store_round_trip(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    doc = Document(id="d", title="Title", text="hello world", metadata={"service": "x"})
    store.upsert_document(doc)
    loaded = store.all_documents()[0]
    assert loaded == doc


def test_store_upsert_replaces_chunks(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    store.upsert_document(Document(id="d", title="Title", text="old text"))
    old_ids = [c.id for c in store.all_chunks()]
    store.upsert_document(Document(id="d", title="Title", text="new text"))
    new_ids = [c.id for c in store.all_chunks()]
    assert old_ids != new_ids
    assert len(new_ids) == 1


def test_store_count_documents(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    assert store.count_documents() == 0
    store.upsert_documents([Document(id="a", title="A", text="a"), Document(id="b", title="B", text="b")])
    assert store.count_documents() == 2


def test_store_get_chunk(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    chunk = store.upsert_document(Document(id="a", title="A", text="alpha"))[0]
    assert store.get_chunk(chunk.id) == chunk
    assert store.get_chunk("missing") is None

def test_store_releases_database_file_handle(tmp_path):
    db_path = tmp_path / "releasable.db"
    store = SQLiteStore(db_path)
    store.upsert_document(Document(id="a", title="A", text="alpha"))
    assert store.count_documents() == 1
    db_path.unlink()
    assert not db_path.exists()
