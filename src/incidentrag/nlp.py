from __future__ import annotations

import re
from collections import Counter

from .models import ParsedIncident

TOKEN_RE = re.compile(r"[a-zA-Z0-9_.:/-]+")
SEVERITY_RE = re.compile(r"\b(P[0-4]|SEV[0-4])\b", re.IGNORECASE)
SERVICE_RE = re.compile(r"\bservice\s*[=:]\s*([a-zA-Z0-9_.-]+)", re.IGNORECASE)
HTTP_RE = re.compile(r"\b(?:HTTP\s*)?([1-5][0-9]{2})\b", re.IGNORECASE)
ERROR_RE = re.compile(r"\b(?:error|err|code)\s*[=:]?\s*([A-Z][A-Z0-9_-]{2,}|[0-9]{3,6})\b")

STOPWORDS = {
    "a",
    "an",
    "and",
    "after",
    "are",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "was",
    "were",
    "with",
    "service",
    "http",
    "error",
}


def normalize_token(token: str) -> str:
    return token.strip("._:/-").lower()


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        token = normalize_token(raw)
        if token and token not in STOPWORDS:
            tokens.append(token)
    return tokens


def parse_incident(text: str, keyword_limit: int = 8) -> ParsedIncident:
    sev_match = SEVERITY_RE.search(text)
    severity = sev_match.group(1).upper().replace("SEV", "P") if sev_match else None

    svc_match = SERVICE_RE.search(text)
    service = svc_match.group(1).lower() if svc_match else None

    http_status: int | None = None
    for match in HTTP_RE.finditer(text):
        value = int(match.group(1))
        if 400 <= value <= 599:
            http_status = value
            break

    error_codes: list[str] = []
    for match in ERROR_RE.finditer(text):
        code = match.group(1).upper()
        if code not in error_codes:
            error_codes.append(code)

    counts = Counter(tokenize(text))
    keywords = [tok for tok, _ in counts.most_common(keyword_limit)]
    for structured in [service, str(http_status) if http_status else None, *(c.lower() for c in error_codes)]:
        if structured and structured not in keywords:
            keywords.insert(0, structured)
    keywords = keywords[:keyword_limit]

    return ParsedIncident(
        raw=text,
        severity=severity,
        service=service,
        http_status=http_status,
        error_codes=error_codes,
        keywords=keywords,
    )
