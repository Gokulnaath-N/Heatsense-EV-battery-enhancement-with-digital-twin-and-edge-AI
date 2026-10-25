#!/usr/bin/env python3
"""HeatSense Dependency Documentation Synchronisation Checker.

Verifies that docs/DEPENDENCIES.md stays strictly synchronised with host/pyproject.toml
and host/uv.lock.

Checks:
    1. Every direct runtime and dev dependency in pyproject.toml is documented in DEPENDENCIES.md.
    2. The resolved version documented in DEPENDENCIES.md matches host/uv.lock exactly.

Usage:
    python scripts/check_dependencies_doc.py
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from typing import Dict, List, Set, Tuple


def parse_package_name(spec: str) -> str:
    """Extract canonical package name from a PEP 508 dependency specification."""
    # Split by version specifiers, extras, or semicolons
    cleaned = spec.split(";")[0].strip()
    match = re.match(r"^([A-Za-z0-9_\-\.]+)", cleaned)
    if not match:
        return cleaned.lower()
    return match.group(1).lower().replace("_", "-")


def load_pyproject_deps(pyproject_path: Path) -> Tuple[set[str], set[str], set[str]]:
    """Load runtime, dev, and build dependency names from pyproject.toml."""
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    runtime_specs = data.get("project", {}).get("dependencies", [])
    runtime_deps = {parse_package_name(s) for s in runtime_specs}

    dev_specs = data.get("dependency-groups", {}).get("dev", [])
    dev_deps = {parse_package_name(s) for s in dev_specs}

    build_specs = data.get("build-system", {}).get("requires", [])
    build_deps = {parse_package_name(s) for s in build_specs}

    return runtime_deps, dev_deps, build_deps


def load_lockfile_versions(lock_path: Path) -> dict[str, str]:
    """Load package resolved versions from uv.lock."""
    with open(lock_path, "rb") as f:
        data = tomllib.load(f)

    packages = data.get("package", [])
    versions: dict[str, str] = {}
    for p in packages:
        name = p["name"].lower().replace("_", "-")
        versions[name] = p["version"]
    return versions


def parse_markdown_table_rows(content: str, section_header: str) -> dict[str, str]:
    """Parse a markdown table under a section header into {package_name: documented_version}."""
    lines = content.splitlines()
    in_section = False
    pkg_versions: dict[str, str] = {}

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("# "):
            if section_header.lower() in stripped.lower():
                in_section = True
            else:
                in_section = False
            continue

        if in_section and stripped.startswith("|") and not stripped.startswith("| :---"):
            columns = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(columns) >= 2:
                raw_name = columns[0]
                raw_ver = columns[1]
                # Filter out table header row
                if raw_name.lower() in {"package", "tool", "component"} or not raw_name:
                    continue
                norm_name = raw_name.lower().replace("_", "-").replace("`", "").strip()
                norm_ver = raw_ver.replace("`", "").strip()
                pkg_versions[norm_name] = norm_ver

    return pkg_versions


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    pyproject_path = root / "host" / "pyproject.toml"
    lock_path = root / "host" / "uv.lock"
    doc_path = root / "docs" / "DEPENDENCIES.md"

    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} missing", file=sys.stderr)
        return 1
    if not lock_path.exists():
        print(f"Error: {lock_path} missing. Run 'uv lock' first.", file=sys.stderr)
        return 1
    if not doc_path.exists():
        print(f"Error: {doc_path} missing", file=sys.stderr)
        return 1

    runtime_deps, dev_deps, build_deps = load_pyproject_deps(pyproject_path)
    locked_versions = load_lockfile_versions(lock_path)
    doc_content = doc_path.read_text(encoding="utf-8")

    runtime_doc = parse_markdown_table_rows(doc_content, "Python runtime dependencies")
    dev_doc = parse_markdown_table_rows(doc_content, "Python dev dependencies")
    build_doc = parse_markdown_table_rows(doc_content, "Build requirements")

    all_doc = {**runtime_doc, **dev_doc, **build_doc}
    errors: list[str] = []

    # Check 1: All runtime dependencies documented
    for dep in sorted(runtime_deps):
        if dep not in all_doc:
            errors.append(f"Runtime dependency '{dep}' from pyproject.toml is missing in docs/DEPENDENCIES.md")

    # Check 2: All dev dependencies documented
    for dep in sorted(dev_deps):
        if dep not in all_doc:
            errors.append(f"Dev dependency '{dep}' from pyproject.toml is missing in docs/DEPENDENCIES.md")

    # Check 3: All build dependencies documented
    for dep in sorted(build_deps):
        if dep not in all_doc:
            errors.append(f"Build dependency '{dep}' from pyproject.toml is missing in docs/DEPENDENCIES.md")

    # Check 4: Documented versions match uv.lock
    for pkg_name, doc_ver in sorted(all_doc.items()):
        if pkg_name in locked_versions:
            lock_ver = locked_versions[pkg_name]
            if doc_ver != lock_ver:
                errors.append(
                    f"Version mismatch for '{pkg_name}': docs/DEPENDENCIES.md states '{doc_ver}' "
                    f"but host/uv.lock has '{lock_ver}'"
                )

    if errors:
        print(f"[-] Dependency doc check FAILED with {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"    - {err}", file=sys.stderr)
        return 1

    print("[+] Dependency doc check PASSED: docs/DEPENDENCIES.md matches pyproject.toml and uv.lock.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
