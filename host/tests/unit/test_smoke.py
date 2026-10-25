"""HeatSense smoke tests verifying package importability and environment invariants."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest


@pytest.mark.unit
def test_python_version() -> None:
    """Verify runtime environment is strictly Python 3.12."""
    assert sys.version_info[:2] == (3, 12), f"Expected Python 3.12, got {sys.version}"


@pytest.mark.unit
def test_package_importable() -> None:
    """Verify that heatsense and all layer subpackages import without error."""
    packages = [
        "heatsense",
        "heatsense.bootstrap",
        "heatsense.domain",
        "heatsense.domain.entities",
        "heatsense.domain.value_objects",
        "heatsense.domain.ports",
        "heatsense.domain.services",
        "heatsense.domain.errors",
        "heatsense.application",
        "heatsense.application.use_cases",
        "heatsense.application.pipeline",
        "heatsense.application.events",
        "heatsense.application.alerts",
        "heatsense.application.sessions",
        "heatsense.application.commands",
        "heatsense.infrastructure",
        "heatsense.infrastructure.transport",
        "heatsense.infrastructure.storage",
        "heatsense.infrastructure.config",
        "heatsense.infrastructure.logging",
        "heatsense.interfaces",
        "heatsense.interfaces.api",
        "heatsense.interfaces.cli",
        "heatsense.simulation",
        "heatsense.identification",
        "heatsense.evaluation",
    ]

    for pkg_name in packages:
        mod = importlib.import_module(pkg_name)
        assert mod is not None, f"Failed to import package: {pkg_name}"


@pytest.mark.unit
def test_every_package_has_layer_docstring() -> None:
    """Verify that every package under src/heatsense has the required docstring tokens."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    pkg_root = repo_root / "host" / "src" / "heatsense"
    required_tokens = ["Responsibility", "MAY import", "MUST NOT import"]

    for current_dir, _, files in os.walk(pkg_root):
        if "__init__.py" in files:
            init_path = Path(current_dir) / "__init__.py"
            content = init_path.read_text(encoding="utf-8")
            rel_dir = init_path.relative_to(repo_root).as_posix()
            for token in required_tokens:
                assert token in content, f"Missing token '{token}' in {rel_dir}"
