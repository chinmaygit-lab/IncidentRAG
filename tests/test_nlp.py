from incidentrag.nlp import parse_incident, tokenize


def test_parse_structured_alert():
    parsed = parse_incident("P1 service=checkout HTTP 503 error=UPSTREAM_UNAVAILABLE after deployment")
    assert parsed.severity == "P1"
    assert parsed.service == "checkout"
    assert parsed.http_status == 503
    assert "UPSTREAM_UNAVAILABLE" in parsed.error_codes


def test_parse_sev_alias():
    assert parse_incident("SEV2 service=auth 401").severity == "P2"


def test_http_200_not_used_as_incident_error_status():
    assert parse_incident("service=search HTTP 200 but very slow").http_status is None


def test_tokenize_removes_common_stopwords():
    tokens = tokenize("The checkout service is failing after deployment")
    assert "the" not in tokens
    assert "checkout" in tokens
    assert "deployment" in tokens


def test_keywords_are_bounded():
    parsed = parse_incident("alpha beta beta gamma delta epsilon zeta eta theta iota kappa", keyword_limit=4)
    assert len(parsed.keywords) <= 4
