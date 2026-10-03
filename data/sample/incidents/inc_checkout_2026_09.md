# INC-2026-09 Checkout Deployment Regression
service: checkout
severity: P1
http_status: 503
error_code: UPSTREAM_UNAVAILABLE

A checkout rollout introduced a readiness regression. HTTP 503 errors rose immediately after deployment. Rolling back the affected revision restored normal traffic. The postmortem action was to add a staging readiness regression check.
