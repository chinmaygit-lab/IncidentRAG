#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("IncidentRAG requires Python 3.11+")
print("Python", sys.version.split()[0])
PY

"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[api,dev]"
python -m ruff check src tests scripts
python -m compileall -q src tests scripts
coverage run -m pytest -q
coverage report --fail-under=85
python scripts/validate.py
rm -f incidentrag.db
incidentrag --db incidentrag.db seed-sample --root data/sample
incidentrag --db incidentrag.db benchmark benchmark/fixtures.json --top-k 3
incidentrag --db incidentrag.db answer "P1 service=checkout HTTP 503 error_code=UPSTREAM_UNAVAILABLE"
echo "INCIDENTRAG READY"
