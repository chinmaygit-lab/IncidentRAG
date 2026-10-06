from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from incidentrag import api
from incidentrag.service import IncidentRAG, load_documents_from_directory


@pytest.fixture()
def client(tmp_path: Path, sample_root: Path):
    engine = IncidentRAG(tmp_path / "api.db", abstention_threshold=0.85)
    engine.ingest_many(load_documents_from_directory(sample_root))
    api.get_engine.cache_clear()
    app = api.create_app()
    app.dependency_overrides[api.get_engine] = lambda: engine
    return TestClient(app)


def test_health(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["documents"] == 20


def test_search(client):
    response = client.post("/v1/search", json={"query": "service=checkout HTTP 503", "top_k": 3})
    assert response.status_code == 200
    assert response.json()["hits"][0]["document_id"] in {"checkout_503", "inc_checkout_2026"}


def test_answer(client):
    response = client.post("/v1/answer", json={"query": "service=auth HTTP 401 TOKEN_EXPIRED"})
    assert response.status_code == 200
    assert response.json()["citations"]


def test_validation_rejects_empty_query(client):
    response = client.post("/v1/search", json={"query": ""})
    assert response.status_code == 422


def test_api_key_guard(tmp_path, sample_root, monkeypatch):
    engine = IncidentRAG(tmp_path / "api-key.db")
    engine.ingest_many(load_documents_from_directory(sample_root))
    monkeypatch.setenv("INCIDENTRAG_API_KEY", "secret-key")
    app = api.create_app()
    app.dependency_overrides[api.get_engine] = lambda: engine
    client = TestClient(app)
    assert client.post("/v1/search", json={"query": "checkout"}).status_code == 401
    assert client.post(
        "/v1/search", json={"query": "checkout"}, headers={"x-api-key": "secret-key"}
    ).status_code == 200
