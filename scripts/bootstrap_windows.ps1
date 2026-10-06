$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

function Assert-NativeSuccess {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE"
    }
}

$Python = $null
foreach ($Candidate in @("python", "python3", "py")) {
    $Command = Get-Command $Candidate -ErrorAction SilentlyContinue
    if (-not $Command) { continue }
    try {
        if ($Candidate -eq "py") {
            $Probe = & py -3 -c "import sys; print(int(sys.version_info >= (3,11)))"
            if ($Probe -eq "1") { $Python = @("py", "-3"); break }
        }
        else {
            $Probe = & $Candidate -c "import sys; print(int(sys.version_info >= (3,11)))"
            if ($Probe -eq "1") { $Python = @($Candidate); break }
        }
    }
    catch { }
}

if (-not $Python) { throw "Python 3.11+ was not found." }

Write-Host "=== CREATE VENV ==="
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    if ($Python.Count -eq 2) { & $Python[0] $Python[1] -m venv .venv }
    else { & $Python[0] -m venv .venv }
    Assert-NativeSuccess "virtual environment creation"
}

$Py = ".\.venv\Scripts\python.exe"

Write-Host "=== INSTALL ==="
& $Py -m pip install --upgrade pip
Assert-NativeSuccess "pip upgrade"
& $Py -m pip install -e ".[api,dev]"
Assert-NativeSuccess "project installation"

Write-Host "=== RUFF ==="
& $Py -m ruff check src tests scripts
Assert-NativeSuccess "Ruff"

Write-Host "=== COMPILE ==="
& $Py -m compileall -q src tests scripts
Assert-NativeSuccess "compileall"

Write-Host "=== TEST + COVERAGE ==="
& $Py -m coverage run -m pytest -q
Assert-NativeSuccess "pytest"
& $Py -m coverage report --fail-under=90
Assert-NativeSuccess "coverage"

Write-Host "=== INTERNAL VALIDATION ==="
& $Py scripts\validate.py
Assert-NativeSuccess "internal validation"

Write-Host "=== SAMPLE DATABASE ==="
if (Test-Path "incidentrag.db") { Remove-Item "incidentrag.db" -Force }
& $Py -m incidentrag --db incidentrag.db seed-sample --root data\sample
Assert-NativeSuccess "sample seed"
& $Py -m incidentrag --db incidentrag.db benchmark benchmark\fixtures.json --top-k 3
Assert-NativeSuccess "benchmark"
& $Py -m incidentrag --db incidentrag.db answer "P1 service=checkout HTTP 503 error_code=UPSTREAM_UNAVAILABLE"
Assert-NativeSuccess "demo answer"

Write-Host "INCIDENTRAG READY"
