# INC-2026-04 Search Traffic Surge
service: search
severity: P1
http_status: 429
error_code: RATE_LIMITED

## Incident summary
During this historical incident, search traffic receives 429 during a demand spike. Investigation showed rate limiter saturation or insufficient query capacity.

## Evidence
The responders correlated deploy and dependency telemetry with the RATE_LIMITED failures. The incident timeline ruled out unrelated services.

## Resolution
Check rate-limit counters and search worker saturation. Drain overloaded search workers only after replacement capacity is ready. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
