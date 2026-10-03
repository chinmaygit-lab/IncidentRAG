from __future__ import annotations

from .models import ParsedIncident, SearchHit


class GroundedTemplateGenerator:
    """Deterministic evidence-only generator used before adding an external LLM."""

    def generate(self, parsed: ParsedIncident, hits: list[SearchHit]) -> str:
        if not hits:
            return (
                "No supporting runbook or incident evidence was retrieved. Escalate for manual investigation."
            )

        lead = hits[0]
        incident_bits: list[str] = []
        if parsed.service:
            incident_bits.append(f"service={parsed.service}")
        if parsed.http_status:
            incident_bits.append(f"HTTP {parsed.http_status}")
        if parsed.severity:
            incident_bits.append(parsed.severity)
        incident_desc = ", ".join(incident_bits) or "the reported incident"

        excerpts = []
        for i, hit in enumerate(hits[:3], start=1):
            compact = " ".join(hit.chunk.text.split())
            excerpt = compact[:220] + ("…" if len(compact) > 220 else "")
            excerpts.append(f"[{i}] {hit.chunk.title}: {excerpt}")

        return (
            f"For {incident_desc}, the strongest retrieved evidence is '{lead.chunk.title}'. "
            "Use the cited material as the investigation starting point; "
            "this foundation build does not invent remediation steps that are "
            "absent from the evidence.\n\n" + "\n".join(excerpts)
        )
