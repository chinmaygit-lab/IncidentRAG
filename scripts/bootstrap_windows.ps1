$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "=== INCIDENTRAG FOUNDATION SETUP ==="

$PythonExe = $null

foreach ($candidate in @("python", "python3")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue

    if ($cmd) {
        try {
            $versionOutput = & $candidate --version 2>&1

            if ($LASTEXITCODE -eq 0 -and $versionOutput -match "Python\s+(\d+)\.(\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]

                if (($major -gt 3) -or ($major -eq 3 -and $minor -ge 11)) {
                    $PythonExe = $candidate
                    Write-Host "Using $candidate : $versionOutput"
                    break
                }
            }
        }
        catch {
        }
    }
}

if (-not $PythonExe) {
    throw "Python 3.11 or newer was not found."
}

Write-Host ""
Write-Host "=== CREATE VIRTUAL ENVIRONMENT ==="

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $PythonExe -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "=== PYTHON ==="
python --version
python -c "import sys; print(sys.executable)"

Write-Host ""
Write-Host "=== INSTALL ==="
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

Write-Host ""
Write-Host "=== TEST ==="
python -m pytest -q

Write-Host ""
Write-Host "=== RUFF ==="
python -m ruff check src tests

Write-Host ""
Write-Host "=== COMPILE ==="
python -m compileall -q src tests

Write-Host ""
Write-Host "=== SEED SAMPLE CORPUS ==="

if (Test-Path "incidentrag.db") {
    Remove-Item "incidentrag.db" -Force
}

incidentrag --db incidentrag.db seed-sample

Write-Host ""
Write-Host "=== BENCHMARK ==="
incidentrag `
    --db incidentrag.db `
    benchmark benchmark\fixtures.json `
    --top-k 3

Write-Host ""
Write-Host "=== DEMO QUERY ==="
incidentrag `
    --db incidentrag.db `
    answer "P1 service=checkout HTTP 503 after deployment" `
    --top-k 3

Write-Host ""
Write-Host "=== GIT ==="

if (-not (Test-Path ".git")) {
    git init
}

$ExistingBranches = @(git for-each-ref --format="%(refname:short)" refs/heads)

if ($ExistingBranches.Count -eq 0) {
    # Fresh repository with no commits yet.
    git symbolic-ref HEAD refs/heads/main
}
else {
    git branch -M main
}

Write-Host ""
Write-Host "=== STATUS BEFORE STAGING ==="
git -c core.pager=cat status --short

Write-Host ""
Write-Host "=== DIFF CHECK ==="
git diff --check

Write-Host ""
Write-Host "=== STAGE ==="
git add .

git diff --cached --check

Write-Host ""
Write-Host "=== STAGED SUMMARY ==="
git -c core.pager=cat diff --cached --stat

Write-Host ""
Write-Host "=== COMMIT ==="

$staged = git diff --cached --name-only

if ($staged) {
    git commit -m "feat: build IncidentRAG retrieval foundation"
}
else {
    Write-Host "Nothing new to commit."
}

Write-Host ""
Write-Host "=== FINAL VERIFY ==="
git -c core.pager=cat log -3 --oneline --decorate
git status -sb

Write-Host ""
Write-Host "=== FINAL TEST ==="
python -m pytest -q

Write-Host ""
Write-Host "=== FINAL RUFF ==="
python -m ruff check src tests

Write-Host ""
Write-Host "INCIDENTRAG FOUNDATION READY."