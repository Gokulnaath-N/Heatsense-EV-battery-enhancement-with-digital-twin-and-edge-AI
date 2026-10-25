#!/usr/bin/env bash
# HeatSense Automated Quality Gate (POSIX Bash)
# Enforces strict repository invariants, linting, typing, testing, and coverage.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_DIR="$REPO_ROOT/host"

echo "============================================================"
echo "HeatSense Quality Gate"
echo "Repository: $REPO_ROOT"
echo "============================================================"

run_step() {
    local step_num="$1"
    local name="$2"
    shift 2
    echo "[Step $step_num/9] $name..."
    if "$@"; then
        echo "  -> PASS"
    else
        echo "  -> FAIL"
        echo "GATE: FAIL (step $step_num: $name)"
        exit 1
    fi
}

# Step 1: verify_structure.py
run_step 1 "Verify Repository Structure" python3 "$REPO_ROOT/scripts/verify_structure.py"

# Step 2: arch_guard.py
run_step 2 "Architecture Guard" python3 "$REPO_ROOT/scripts/arch_guard.py" --root "$REPO_ROOT/host/src/heatsense"

# Step 3: uv lock --check
(cd "$HOST_DIR" && run_step 3 "Verify Lockfile Consistency" uv lock --check)

# Step 4: check_dependencies_doc.py
run_step 4 "Check Dependency Documentation" python3 "$REPO_ROOT/scripts/check_dependencies_doc.py"

# Step 5: ruff check
(cd "$HOST_DIR" && run_step 5 "Ruff Lint" uv run ruff check)

# Step 6: ruff format --check
(cd "$HOST_DIR" && run_step 6 "Ruff Format Check" uv run ruff format --check)

# Step 7: mypy
(cd "$HOST_DIR" && run_step 7 "Mypy Strict Type Check" uv run mypy)

# Step 8: pytest with coverage
(cd "$HOST_DIR" && HYPOTHESIS_PROFILE=ci run_step 8 "Pytest with Coverage" uv run coverage run -m pytest)

# Step 9: coverage report & thresholds
(cd "$HOST_DIR" && uv run coverage json -o coverage.json)
run_step 9 "Check Coverage Thresholds" python3 "$REPO_ROOT/scripts/check_coverage.py" --file "$HOST_DIR/coverage.json"

echo "============================================================"
echo "GATE: PASS"
echo "============================================================"
exit 0
