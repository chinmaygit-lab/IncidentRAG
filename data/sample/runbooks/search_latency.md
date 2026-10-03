# Search Latency Runbook
service: search
http_status: 200
error_code: SEARCH_SLOW

## Symptoms
Search succeeds but latency increases sharply. Logs may contain SEARCH_SLOW while HTTP responses remain successful.

## Checks
Inspect query latency percentiles, cache hit rate, index refresh activity and CPU saturation.

## Recovery
Throttle expensive maintenance jobs and follow the approved capacity procedure if saturation persists.
