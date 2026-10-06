from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[._:-][A-Za-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    """Tokenize operational text while preserving useful error/status compounds."""
    tokens: list[str] = []
    for raw in _TOKEN_RE.findall(text.lower()):
        tokens.append(raw)
        for separator in ("_", "-", ".", ":"):
            if separator in raw:
                tokens.extend(part for part in raw.split(separator) if part)
    return tokens


def unique_tokens(text: str) -> set[str]:
    return set(tokenize(text))
