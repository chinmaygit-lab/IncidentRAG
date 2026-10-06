# INC-2025-12 Carrier API Outage
service: shipping
severity: P1
http_status: 503
error_code: CARRIER_UNAVAILABLE

## Incident summary
During this historical incident, shipping quote requests return 503 when the primary carrier API is unavailable. Investigation showed carrier outage or exhausted carrier client connections.

## Evidence
The responders correlated deploy and dependency telemetry with the CARRIER_UNAVAILABLE failures. The incident timeline ruled out unrelated services.

## Resolution
Check primary carrier availability and client timeout metrics. Disable the primary carrier route only after fallback validation succeeds. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
