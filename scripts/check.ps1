# HeatSense Automated Quality Gate (PowerShell)
# Enforces strict repository invariants, linting, typing, testing, and coverage.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$HostDir = Join-Path $RepoRoot "host"

function Run-Step {
    param (
        [int]$StepNum,
        [string]$Name,
        [scriptblock]$Action
    )
    Write-Host "[Step $StepNum/9] $Name..." -ForegroundColor Cyan
    try {
        & $Action
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            throw "Step failed with exit code $LASTEXITCODE"
        }
        Write-Host "  -> PASS" -ForegroundColor Green
    }
    catch {
        Write-Host "  -> FAIL" -ForegroundColor Red
        Write-Host "GATE: FAIL (step $StepNum`: $Name)" -ForegroundColor Red
        exit 1
    }
}

Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "HeatSense Quality Gate" -ForegroundColor Yellow
Write-Host "Repository: $RepoRoot" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

# Step 1: verify_structure.py
Run-Step 1 "Verify Repository Structure" {
    python "$RepoRoot\scripts\verify_structure.py"
}

# Step 2: arch_guard.py
Run-Step 2 "Architecture Guard" {
    python "$RepoRoot\scripts\arch_guard.py" --root "$RepoRoot\host\src\heatsense"
}

# Step 3: uv lock --check
Run-Step 3 "Verify Lockfile Consistency" {
    Push-Location $HostDir
    try {
        uv lock --check
    }
    finally {
        Pop-Location
    }
}

# Step 4: check_dependencies_doc.py
Run-Step 4 "Check Dependency Documentation" {
    python "$RepoRoot\scripts\check_dependencies_doc.py"
}

# Step 5: ruff check
Run-Step 5 "Ruff Lint" {
    Push-Location $HostDir
    try {
        uv run ruff check
    }
    finally {
        Pop-Location
    }
}

# Step 6: ruff format --check
Run-Step 6 "Ruff Format Check" {
    Push-Location $HostDir
    try {
        uv run ruff format --check
    }
    finally {
        Pop-Location
    }
}

# Step 7: mypy
Run-Step 7 "Mypy Strict Type Check" {
    Push-Location $HostDir
    try {
        uv run mypy
    }
    finally {
        Pop-Location
    }
}

# Step 8: pytest with coverage
Run-Step 8 "Pytest with Coverage" {
    Push-Location $HostDir
    try {
        $env:HYPOTHESIS_PROFILE = "ci"
        uv run coverage run -m pytest
    }
    finally {
        Remove-Item env:HYPOTHESIS_PROFILE -ErrorAction SilentlyContinue
        Pop-Location
    }
}

# Step 9: coverage report & thresholds
Run-Step 9 "Check Coverage Thresholds" {
    Push-Location $HostDir
    try {
        uv run coverage json -o coverage.json
    }
    finally {
        Pop-Location
    }
    python "$RepoRoot\scripts\check_coverage.py" --file "$HostDir\coverage.json"
}

Write-Host "============================================================" -ForegroundColor Green
Write-Host "GATE: PASS" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
exit 0
