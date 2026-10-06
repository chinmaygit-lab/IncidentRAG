# INC-2026-05 Auth Clock Skew
service: auth
severity: P1
http_status: 401
error_code: TOKEN_EXPIRED

## Incident summary
During this historical incident, valid users receive 401 because token validation rejects recently issued tokens. Investigation showed clock skew, stale signing keys, or token expiry configuration.

## Evidence
The responders correlated deploy and dependency telemetry with the TOKEN_EXPIRED failures. The incident timeline ruled out unrelated services.

## Resolution
Check clock skew across auth nodes and identity provider hosts. Restore time synchronization before rotating keys. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
