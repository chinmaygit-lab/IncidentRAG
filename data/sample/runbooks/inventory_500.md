# Inventory 500 Migration Runbook
service: inventory
severity: P1
http_status: 500
error_code: INVENTORY_DB_ERROR

## Symptoms
Inventory writes return 500 after a schema migration. The canonical error code is INVENTORY_DB_ERROR.

## Likely causes
The leading hypothesis is an incompatible migration or missing column. Confirm evidence before remediation.

## Investigation and remediation
- Check migration history and database errors for the inventory schema.
- Verify application and database schema versions match.
- Rollback the incompatible migration using the approved database procedure.
- Compare write success and replica health after rollback.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
