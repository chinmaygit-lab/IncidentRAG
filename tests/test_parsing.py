from incidentrag.parsing import parse_incident
from incidentrag.tokenization import tokenize


def test_parse_structured_incident():
    parsed = parse_incident("P1 service=checkout HTTP 503 error_code=UPSTREAM_UNAVAILABLE")
    assert parsed.service == "checkout"
    assert parsed.severity == "P1"
    assert parsed.http_status == 503
    assert parsed.error_code == "UPSTREAM_UNAVAILABLE"


def test_parse_service_colon():
    assert parse_incident("service: payments returned 502").service == "payments"


def test_parse_service_phrase():
    assert parse_incident("inventory service is unhealthy").service == "inventory"


def test_parse_missing_fields_are_none():
    parsed = parse_incident("latency increased")
    assert parsed.service is None
    assert parsed.severity is None
    assert parsed.http_status is None
    assert parsed.error_code is None


def test_parse_uppercase_error_token():
    assert parse_incident("failure DB_POOL_EXHAUSTED observed").error_code == "DB_POOL_EXHAUSTED"


def test_tokenize_preserves_and_splits_compounds():
    tokens = tokenize("DB_POOL-EXHAUSTED auth.service")
    assert "db_pool-exhausted" in tokens
    assert "db" in tokens
    assert "pool-exhausted" in tokens
    assert "auth.service" in tokens
    assert "auth" in tokens
