# INC-2026-06 Inventory Migration Failure
service: inventory
severity: P1
http_status: 500
error_code: INVENTORY_DB_ERROR

An incompatible database migration caused inventory HTTP 500 errors. The team halted the rollout, restored schema compatibility and added a migration validation gate.
