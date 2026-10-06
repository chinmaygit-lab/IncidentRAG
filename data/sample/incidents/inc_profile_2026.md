# INC-2025-11 Profile Schema Regression
service: profile
severity: P1
http_status: 500
error_code: SCHEMA_MISMATCH

## Incident summary
During this historical incident, profile reads return 500 after a deployment changes a response field. Investigation showed application schema mismatch between deployed versions.

## Evidence
The responders correlated deploy and dependency telemetry with the SCHEMA_MISMATCH failures. The incident timeline ruled out unrelated services.

## Resolution
Check profile serialization errors and deployment version skew. Rollback the incompatible profile deployment when mixed-version traffic is unsafe. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
