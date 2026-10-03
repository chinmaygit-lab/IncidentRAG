# Inventory Internal Error Runbook
service: inventory
http_status: 500
error_code: INVENTORY_DB_ERROR

## Symptoms
Inventory requests return HTTP 500 and logs show INVENTORY_DB_ERROR during database failures.

## Checks
Check database availability, connection pool use, migration status and replica health. Correlate errors with schema changes.

## Recovery
Use the database incident procedure and do not retry write operations blindly when transaction outcome is unknown.
