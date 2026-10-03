import importlib

from fastapi.testclient import TestClient


def _client(tmp_path, monkeypatch):
    monkeypatch.setenv("INCIDENTRAG_DB", str(tmp_path / "api.db"))
    import incidentrag.api as api

    importlib.reload(api)
    return TestClient(api.app)


def test_health(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_search_and_answer(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    payload = {
        "id": "runbook-x",
        "title": "Checkout 503",
        "text": (
            "service checkout returns HTTP 503 after deployment. Check readiness and rollback if approved."
        ),
        "source_type": "runbook",
        "metadata": {"service": "checkout", "http_status": 503},
    }
    assert client.post("/documents", json=payload).status_code == 200
    search = client.post("/search", json={"query": "service=checkout HTTP 503", "top_k": 3})
    assert search.status_code == 200
    assert search.json()["citations"][0]["document_id"] == "runbook-x"
    answer = client.post("/answer", json={"query": "service=checkout HTTP 503", "top_k": 3})
    assert answer.status_code == 200
    assert "Checkout 503" in answer.json()["answer"]


def test_answer_404_when_no_evidence(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    response = client.post("/answer", json={"query": "nothing here", "top_k": 3})
    assert response.status_code == 404
