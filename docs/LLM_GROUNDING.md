# LLM grounding adapter

The default IncidentRAG answer path does not call a model. It extracts investigation/remediation sentences directly from evidence.

For a hosted or local model, use `CallableGroundedGenerator` or `OpenAICompatibleHTTPGenerator`. The prompt contains only the incident and numbered retrieved evidence. The response is rejected if it has no citations or references a citation number that does not exist.

This is a guardrail, not a proof of factual correctness. A stronger production implementation should also validate that cited claims are entailed by the cited evidence and should log model/prompt versions for evaluation.
