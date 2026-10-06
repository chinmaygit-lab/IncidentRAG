from __future__ import annotations

import re

from .models import ParsedIncident
from .tokenization import tokenize

_SERVICE_PATTERNS = (
    re.compile(r"\bservice\s*[=:]\s*([a-z0-9_-]+)", re.I),
    re.compile(r"\b([a-z0-9_-]+)\s+service\b", re.I),
)
_SEVERITY_RE = re.compile(r"\bP([0-4])\b", re.I)
_HTTP_RE = re.compile(r"\b(?:HTTP\s*)?([1-5][0-9]{2})\b", re.I)
_ERROR_KV_RE = re.compile(r"\b(?:error(?:_code)?|code)\s*[=:]\s*([A-Z][A-Z0-9_-]{2,})\b")
_ERROR_TOKEN_RE = re.compile(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+){1,})\b")


def parse_incident(text: str) -> ParsedIncident:
    service = None
    for pattern in _SERVICE_PATTERNS:
        match = pattern.search(text)
        if match:
            service = match.group(1).lower()
            break

    severity_match = _SEVERITY_RE.search(text)
    severity = f"P{severity_match.group(1)}" if severity_match else None

    http_match = _HTTP_RE.search(text)
    http_status = int(http_match.group(1)) if http_match else None

    error_match = _ERROR_KV_RE.search(text) or _ERROR_TOKEN_RE.search(text)
    error_code = error_match.group(1).upper() if error_match else None

    return ParsedIncident(
        raw=text,
        service=service,
        severity=severity,
        http_status=http_status,
        error_code=error_code,
        tokens=tokenize(text),
    )
