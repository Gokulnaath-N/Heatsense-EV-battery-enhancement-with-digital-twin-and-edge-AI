#!/usr/bin/env python3
"""HeatSense Repository Structure Verification Guard.

Zero-dependency standard library verification tool enforcing repository layout,
directory markers, docstring requirements, safety boundaries, and claims policy.

Usage:
    python scripts/verify_structure.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Set

# Expected directories relative to repository root
EXPECTED_DIRECTORIES: list[str] = [
    "contracts",
    "contracts/golden",
    "contracts/schemas",
    "dashboard",
    "data",
    "data/external",
    "data/processed",
    "data/raw",
    "data/sessions",
    "docs",
    "docs/adr",
    "docs/architecture",
    "docs/figures",
    "docs/hardware",
    "docs/protocol",
    "docs/test-plans",
    "firmware",
    "firmware/include",
    "firmware/lib",
    "firmware/lib/core",
    "firmware/lib/drivers",
    "firmware/lib/hal",
    "firmware/src",
    "firmware/test",
    "host",
    "host/configs",
    "host/migrations",
    "host/parameters",
    "host/scenarios",
    "host/src",
    "host/src/heatsense",
    "host/src/heatsense/application",
    "host/src/heatsense/application/alerts",
    "host/src/heatsense/application/commands",
    "host/src/heatsense/application/events",
    "host/src/heatsense/application/pipeline",
    "host/src/heatsense/application/sessions",
    "host/src/heatsense/application/use_cases",
    "host/src/heatsense/domain",
    "host/src/heatsense/domain/entities",
    "host/src/heatsense/domain/errors",
    "host/src/heatsense/domain/ports",
    "host/src/heatsense/domain/services",
    "host/src/heatsense/domain/value_objects",
    "host/src/heatsense/evaluation",
    "host/src/heatsense/identification",
    "host/src/heatsense/infrastructure",
    "host/src/heatsense/infrastructure/config",
    "host/src/heatsense/infrastructure/logging",
    "host/src/heatsense/infrastructure/storage",
    "host/src/heatsense/infrastructure/transport",
    "host/src/heatsense/interfaces",
    "host/src/heatsense/interfaces/api",
    "host/src/heatsense/interfaces/cli",
    "host/src/heatsense/simulation",
    "host/tests",
    "host/tests/contract",
    "host/tests/e2e",
    "host/tests/integration",
    "host/tests/property",
    "host/tests/unit",
    "host/tests/unit/application",
    "host/tests/unit/domain",
    "host/tests/unit/infrastructure",
    "host/tests/unit/interfaces",
    "host/tests/unit/simulation",
    "notebooks",
    "runs",
    "scripts",
]

ALLOWED_TOP_LEVEL_DIRS: set[str] = {
    ".git",
    "contracts",
    "dashboard",
    "data",
    "docs",
    "firmware",
    "host",
    "notebooks",
    "runs",
    "scripts",
    "Knowlegde_reference",  # Pre-existing project reference asset
}

REQUIRED_MARKER_NAMES: set[str] = {"README.md", "__init__.py", ".gitkeep"}

DOCSTRING_REQUIRED_TOKENS: list[str] = [
    "Responsibility",
    "MAY import",
    "MUST NOT import",
]

FORBIDDEN_PHRASES: list[str] = [
    "thermal runaway prediction",
    "preventing thermal runaway",
    "measured SoH",
    "measured core temperature",
    "AI protects the battery",
]

EXEMPT_FORBIDDEN_SCAN_FILES: set[str] = {
    "docs/claims-policy.md",
    "AGENTS.md",
    "agents.md",
    "scripts/verify_structure.py",
}


def find_repo_root() -> Path:
    """Resolve repository root directory from this script's location."""
    return Path(__file__).resolve().parent.parent


def check_expected_directories(root: Path) -> list[str]:
    """Check (a): every expected directory exists."""
    errors: list[str] = []
    for rel_dir in EXPECTED_DIRECTORIES:
        path = root / rel_dir
        if not path.is_dir():
            errors.append(f"Missing expected directory: {rel_dir}")
    return errors


def check_directory_markers(root: Path) -> list[str]:
    """Check (b): every expected directory has README.md, __init__.py or .gitkeep."""
    errors: list[str] = []
    for rel_dir in EXPECTED_DIRECTORIES:
        dir_path = root / rel_dir
        if not dir_path.is_dir():
            continue  # Already flagged in check (a)
        
        has_marker = any((dir_path / marker).exists() for marker in REQUIRED_MARKER_NAMES)
        if not has_marker:
            errors.append(f"Directory missing required marker (README.md, __init__.py, or .gitkeep): {rel_dir}")
    return errors


def check_package_docstrings(root: Path) -> list[str]:
    """Check (c): every Python package under host/src/heatsense has __init__.py with required tokens."""
    errors: list[str] = []
    pkg_root = root / "host" / "src" / "heatsense"
    if not pkg_root.is_dir():
        return [f"Package root directory does not exist: {pkg_root}"]

    for current_dir, dirs, files in os.walk(pkg_root):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        if os.path.basename(current_dir) == "__pycache__":
            continue
        rel_dir = Path(current_dir).relative_to(root).as_posix()
        if "__init__.py" not in files:
            errors.append(f"Python package directory missing __init__.py: {rel_dir}")
            continue

        init_file = Path(current_dir) / "__init__.py"
        try:
            content = init_file.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"Could not read {init_file}: {e}")
            continue

        for token in DOCSTRING_REQUIRED_TOKENS:
            if token not in content:
                errors.append(
                    f"__init__.py in {rel_dir} is missing required docstring token: '{token}'"
                )
    return errors


def check_top_level_directories(root: Path) -> list[str]:
    """Check (d): no unexpected top-level folders."""
    errors: list[str] = []
    for entry in root.iterdir():
        if entry.is_dir() and entry.name not in ALLOWED_TOP_LEVEL_DIRS:
            errors.append(f"Unexpected top-level directory found: {entry.name}")
    return errors


def check_tracked_data_runs_files(root: Path) -> list[str]:
    """Check (e): data/ and runs/ contain no tracked files other than README.md and .gitkeep."""
    errors: list[str] = []
    git_dir = root / ".git"
    if not git_dir.exists():
        return errors

    try:
        result = subprocess.run(
            ["git", "ls-files", "data", "runs"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception as e:
        errors.append(f"Failed to execute git ls-files: {e}")
        return errors

    tracked = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    for filepath in tracked:
        basename = os.path.basename(filepath)
        if basename not in {"README.md", ".gitkeep"}:
            errors.append(
                f"Forbidden tracked file found in data/ or runs/: {filepath} (only README.md and .gitkeep may be tracked)"
            )
    return errors


def check_host_no_firmware_imports(root: Path) -> list[str]:
    """Check (f): no file under host/ contains firmware import statements."""
    errors: list[str] = []
    host_dir = root / "host"
    if not host_dir.is_dir():
        return errors

    import_pattern = re.compile(r"^\s*(import\s+.*firmware|from\s+firmware)", re.IGNORECASE)

    for current_dir, _, files in os.walk(host_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = Path(current_dir) / file
            rel_file = file_path.relative_to(root).as_posix()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, start=1):
                        if import_pattern.search(line):
                            errors.append(
                                f"Forbidden firmware import statement in {rel_file}:{line_num}: {line.strip()}"
                            )
            except Exception as e:
                errors.append(f"Could not read {rel_file}: {e}")
    return errors


def check_forbidden_wording_scan(root: Path) -> list[str]:
    """Check (g): forbidden wording scan outside docs/claims-policy.md and AGENTS.md."""
    errors: list[str] = []
    # Scanned extensions
    text_extensions = {".md", ".py", ".cpp", ".hpp", ".h", ".c", ".yaml", ".yml", ".json", ".txt"}

    for current_dir, _, files in os.walk(root):
        rel_dir = Path(current_dir).relative_to(root).as_posix()
        # Skip git directory
        if rel_dir == ".git" or rel_dir.startswith(".git/"):
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in text_extensions:
                continue

            file_path = Path(current_dir) / file
            rel_path = file_path.relative_to(root).as_posix()

            if rel_path in EXEMPT_FORBIDDEN_SCAN_FILES:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                # Binary or unreadable file
                continue

            for phrase in FORBIDDEN_PHRASES:
                # Case-insensitive search
                if re.search(re.escape(phrase), content, re.IGNORECASE):
                    errors.append(
                        f"Forbidden phrase '{phrase}' detected in {rel_path} (violates docs/claims-policy.md)"
                    )
    return errors


def main() -> int:
    """Run all checks and report PASS/FAIL status."""
    root = find_repo_root()
    print("=" * 60)
    print(f"HeatSense Repository Structure Verification")
    print(f"Root: {root}")
    print("=" * 60)

    checks = [
        ("Check (a): Expected directories exist", check_expected_directories),
        ("Check (b): Directory markers present", check_directory_markers),
        ("Check (c): Python package docstrings valid", check_package_docstrings),
        ("Check (d): No unexpected top-level folders", check_top_level_directories),
        ("Check (e): data/ and runs/ tracked file hygiene", check_tracked_data_runs_files),
        ("Check (f): Host isolation from firmware imports", check_host_no_firmware_imports),
        ("Check (g): Forbidden claims wording scan", check_forbidden_wording_scan),
    ]

    all_errors: list[str] = []

    for name, check_fn in checks:
        errors = check_fn(root)
        if errors:
            print(f"[-] FAIL: {name} ({len(errors)} error(s))")
            for err in errors:
                print(f"    - {err}")
            all_errors.extend(errors)
        else:
            print(f"[+] PASS: {name}")

    print("=" * 60)
    if all_errors:
        print(f"OVERALL RESULT: FAILED with {len(all_errors)} error(s).")
        print("=" * 60)
        return 1
    else:
        print("OVERALL RESULT: PASSED (All repository structure checks green).")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
