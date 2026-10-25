"""Tests verifying dependency specifications adhere to repository bounds and pinning policies."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest


@pytest.mark.unit
def test_dependency_specifications_have_bounds() -> None:
    """Verify that all runtime and dev dependencies have explicit lower and upper bounds."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    pyproject_path = repo_root / "host" / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    runtime_deps = data.get("project", {}).get("dependencies", [])
    dev_deps = data.get("dependency-groups", {}).get("dev", [])

    all_specs = runtime_deps + dev_deps

    # Exempt type stubs from strict upper-bound requirements
    exempt_prefixes = ("types-",)

    for spec in all_specs:
        cleaned = spec.split(";")[0].strip()
        pkg_name = cleaned.split("<")[0].split(">")[0].split("=")[0].strip()

        if any(pkg_name.startswith(pfx) for pfx in exempt_prefixes):
            continue

        # Must have lower bound >= and upper bound < or ~=
        assert ">=" in cleaned or "~=" in cleaned, (
            f"Dependency '{spec}' lacks an explicit lower bound (>= or ~=)."
        )
        if "~=" not in cleaned:
            assert "<" in cleaned, f"Dependency '{spec}' lacks an explicit upper bound (<)."

        # No pre-release specifiers allowed in version bounds
        version_portion = cleaned[len(pkg_name) :]
        prerelease_match = re.search(r"(?:[0-9]+)(?:a|b|rc|dev)\d*", version_portion, re.IGNORECASE)
        assert not prerelease_match, (
            f"Dependency '{spec}' contains a forbidden pre-release specifier."
        )
