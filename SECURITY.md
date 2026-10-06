# Security

IncidentRAG is a decision-support project, not an autonomous remediation agent. Treat retrieved material as evidence, preserve normal production approvals, and never place secrets in incident text or sample data.

Report suspected vulnerabilities privately to the repository owner. Do not include credentials, production incident data, or customer information in reports.

The API can require `INCIDENTRAG_API_KEY`. The included secret redactor is defensive logging hygiene, not a DLP system.
