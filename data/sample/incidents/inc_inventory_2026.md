# INC-2026-06 Inventory Migration Failure
service: inventory
severity: P1
http_status: 500
error_code: INVENTORY_DB_ERROR

## Incident summary
During this historical incident, inventory writes return 500 after a schema migration. Investigation showed an incompatible migration or missing column.

## Evidence
The responders correlated deploy and dependency telemetry with the INVENTORY_DB_ERROR failures. The incident timeline ruled out unrelated services.

## Resolution
Check migration history and database errors for the inventory schema. Rollback the incompatible migration using the approved database procedure. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
