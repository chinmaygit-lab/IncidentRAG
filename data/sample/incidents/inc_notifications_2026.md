# INC-2026-02 Notification Provider Outage
service: notifications
severity: P1
http_status: 500
error_code: SMTP_PROVIDER_ERROR

## Incident summary
During this historical incident, email notification jobs fail with 500 while provider delivery errors rise. Investigation showed provider outage, rejected credentials, or API quota failure.

## Evidence
The responders correlated deploy and dependency telemetry with the SMTP_PROVIDER_ERROR failures. The incident timeline ruled out unrelated services.

## Resolution
Check provider status and notification delivery error codes. Switch to the approved backup provider when the primary provider is unavailable. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
