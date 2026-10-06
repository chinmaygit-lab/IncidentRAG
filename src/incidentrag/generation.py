from __future__ import annotations

import json
import re
import urllib.request
from collections.abc import Callable

from .models import Answer, Citation, ParsedIncident, SearchHit

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_ACTION_WORDS = (
    "check",
    "verify",
    "rollback",
    "restart",
    "drain",
    "disable",
    "restore",
    "compare",
    "inspect",
)
_CITATION_RE = re.compile(r"\[(\d+)\]")


def _excerpt(text: str, limit: int = 320) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def _extract_action_sentences(text: str, limit: int = 3) -> list[str]:
    sentences = [segment.strip() for segment in _SENTENCE_RE.split(" ".join(text.split())) if segment.strip()]
    actions = [sentence for sentence in sentences if any(word in sentence.lower() for word in _ACTION_WORDS)]
    return actions[:limit]


class GroundedGenerator:
    """Extractive generator: every recommendation is copied from retrieved evidence."""

    def generate(
        self,
        *,
        query: str,
        parsed: ParsedIncident,
        hits: list[SearchHit],
        abstain: bool,
    ) -> Answer:
        if abstain or not hits:
            return Answer(
                query=query,
                text=(
                    "No sufficiently strong supporting runbook or historical incident was retrieved. "
                    "Escalate for manual investigation rather than inventing remediation."
                ),
                abstained=True,
                confidence=hits[0].score if hits else 0.0,
                citations=[],
                parsed=parsed,
            )

        citations = [
            Citation(
                index=index,
                document_id=hit.chunk.document_id,
                chunk_id=hit.chunk.id,
                title=hit.chunk.title,
                source_type=hit.chunk.source_type,
                score=hit.score,
                excerpt=_excerpt(hit.chunk.text),
            )
            for index, hit in enumerate(hits, start=1)
        ]

        descriptor = []
        if parsed.service:
            descriptor.append(f"service={parsed.service}")
        if parsed.http_status:
            descriptor.append(f"HTTP {parsed.http_status}")
        if parsed.severity:
            descriptor.append(parsed.severity)
        incident_desc = ", ".join(descriptor) or "this incident"

        action_lines: list[str] = []
        seen: set[str] = set()
        for index, hit in enumerate(hits, start=1):
            for sentence in _extract_action_sentences(hit.chunk.text):
                key = sentence.lower()
                if key not in seen:
                    seen.add(key)
                    action_lines.append(f"- {sentence} [{index}]")
                if len(action_lines) >= 4:
                    break
            if len(action_lines) >= 4:
                break

        if not action_lines:
            action_lines = ["- Review the strongest evidence excerpt before acting. [1]"]

        text = (
            f"For {incident_desc}, the strongest evidence is '{hits[0].chunk.title}' [1].\n\n"
            "Evidence-backed investigation steps:\n"
            + "\n".join(action_lines)
            + "\n\nOnly cited evidence is used; uncited remediation is intentionally omitted."
        )
        return Answer(
            query=query,
            text=text,
            abstained=False,
            confidence=hits[0].score,
            citations=citations,
            parsed=parsed,
        )


class CallableGroundedGenerator:
    """Optional model-backed generator with strict citation validation."""

    def __init__(self, call_model: Callable[[str], str]):
        self.call_model = call_model

    @staticmethod
    def build_prompt(query: str, hits: list[SearchHit]) -> str:
        evidence = "\n\n".join(
            f"[{index}] {hit.chunk.title}\n{hit.chunk.text}"
            for index, hit in enumerate(hits, start=1)
        )
        return (
            "Answer the incident using ONLY the evidence below. Cite every factual recommendation "
            "with [n]. If evidence is insufficient, say so.\n\n"
            f"INCIDENT:\n{query}\n\nEVIDENCE:\n{evidence}"
        )

    def generate_text(self, query: str, hits: list[SearchHit]) -> str:
        if not hits:
            return "Insufficient evidence."
        text = self.call_model(self.build_prompt(query, hits)).strip()
        citations = {int(value) for value in _CITATION_RE.findall(text)}
        if not citations or any(value < 1 or value > len(hits) for value in citations):
            raise ValueError("model response failed citation validation")
        return text


class OpenAICompatibleHTTPGenerator(CallableGroundedGenerator):
    """Tiny optional adapter for an OpenAI-compatible chat endpoint; stdlib only."""

    def __init__(self, *, endpoint: str, api_key: str, model: str, timeout: float = 30.0):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        super().__init__(self._call)

    def _call(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            }
        ).encode()
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode())
        return str(body["choices"][0]["message"]["content"])
