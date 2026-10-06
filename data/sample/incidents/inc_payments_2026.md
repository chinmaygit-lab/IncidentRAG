# INC-2026-08 Payments Provider Degradation
service: payments
severity: P1
http_status: 502
error_code: PAYMENT_GATEWAY_TIMEOUT

## Incident summary
During this historical incident, payment authorization returns 502 while the external gateway latency spikes. Investigation showed provider latency or an exhausted outbound connection pool.

## Evidence
The responders correlated deploy and dependency telemetry with the PAYMENT_GATEWAY_TIMEOUT failures. The incident timeline ruled out unrelated services.

## Resolution
Check provider latency and timeout metrics for the payment gateway. Disable the degraded provider route only when the approved failover path is healthy. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
