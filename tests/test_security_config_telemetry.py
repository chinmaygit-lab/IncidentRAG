import pytest

from incidentrag.config import Settings
from incidentrag.security import redact_secrets
from incidentrag.telemetry import Telemetry


def test_redacts_api_key_password_and_bearer():
    text = "api_key=abc password=secret Authorization: Bearer token123"
    redacted = redact_secrets(text)
    assert "abc" not in redacted
    assert "secret" not in redacted
    assert "token123" not in redacted
    assert redacted.count("[REDACTED]") == 3


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("INCIDENTRAG_DB", "x.db")
    monkeypatch.setenv("INCIDENTRAG_ABSTENTION_THRESHOLD", "0.5")
    monkeypatch.setenv("INCIDENTRAG_API_KEY", "k")
    settings = Settings.from_env()
    assert settings.database_path == "x.db"
    assert settings.abstention_threshold == 0.5
    assert settings.api_key == "k"


def test_telemetry_records_operations_and_latency():
    telemetry = Telemetry()
    with telemetry.measure("search"):
        pass
    snapshot = telemetry.snapshot()
    assert snapshot["requests"] == 1
    assert snapshot["searches"] == 1
    assert snapshot["avg_latency_ms"] >= 0


def test_telemetry_records_failure():
    telemetry = Telemetry()
    with pytest.raises(RuntimeError), telemetry.measure("answer"):
        raise RuntimeError("boom")
    assert telemetry.snapshot()["failures"] == 1
