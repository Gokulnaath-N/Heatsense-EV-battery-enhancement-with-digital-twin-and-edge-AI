"""Tests verifying that the Architecture Guard correctly protects layer boundaries."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.unit
def test_real_tree_is_clean() -> None:
    """Verify that the actual HeatSense codebase passes the architecture guard."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    guard_script = repo_root / "scripts" / "arch_guard.py"
    target_root = repo_root / "host" / "src" / "heatsense"

    result = subprocess.run(  # noqa: S603 -- test runner invokes internal python script
        [sys.executable, str(guard_script), "--root", str(target_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Architecture guard failed on real tree:\n{result.stderr}\n{result.stdout}"
    )
    assert "Architecture Guard PASSED" in result.stdout


@pytest.mark.unit
@pytest.mark.parametrize(
    ("rule_id", "bad_file_rel", "bad_code"),
    [
        ("R1", "domain/bad.py", "import fastapi\n"),
        ("R2", "application/bad.py", "import fastapi\n"),
        ("R3", "infrastructure/bad.py", "from heatsense.interfaces import api\n"),
        ("R4", "interfaces/bad.py", "from heatsense.infrastructure import storage\n"),
        ("R5", "simulation/bad.py", "from heatsense.application import use_cases\n"),
        ("R6", "identification/bad.py", "from heatsense.interfaces import api\n"),
        ("R7", "domain/bad.py", "import firmware.core\n"),
        ("R9", "domain/bad.py", "UNPROTECTED_CACHE = {}\n"),
    ],
)
def test_detects_each_rule(tmp_path: Path, rule_id: str, bad_file_rel: str, bad_code: str) -> None:
    """Verify that architecture guard fails and outputs the specific rule ID when violated."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    guard_script = repo_root / "scripts" / "arch_guard.py"

    # Create root mock structure
    mock_root = tmp_path / "heatsense"
    bad_file = mock_root / bad_file_rel
    bad_file.parent.mkdir(parents=True, exist_ok=True)
    bad_file.write_text(bad_code, encoding="utf-8")

    result = subprocess.run(  # noqa: S603 -- test runner invokes internal python script
        [sys.executable, str(guard_script), "--root", str(mock_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, (
        f"Expected guard to fail on {rule_id}, but passed.\nStdout: {result.stdout}"
    )
    assert rule_id in result.stderr, f"Expected {rule_id} in stderr:\n{result.stderr}"


@pytest.mark.unit
def test_good_tree_passes(tmp_path: Path) -> None:
    """Verify that a synthetic tree complying with all rules passes cleanly."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    guard_script = repo_root / "scripts" / "arch_guard.py"

    mock_root = tmp_path / "heatsense"
    # Domain with numpy and stdlib
    domain_file = mock_root / "domain" / "services.py"
    domain_file.parent.mkdir(parents=True, exist_ok=True)
    domain_file.write_text("import numpy as np\nfrom math import sqrt\n", encoding="utf-8")

    # Application importing domain
    app_file = mock_root / "application" / "pipeline.py"
    app_file.parent.mkdir(parents=True, exist_ok=True)
    app_file.write_text("from heatsense.domain import services\n", encoding="utf-8")

    result = subprocess.run(  # noqa: S603 -- test runner invokes internal python script
        [sys.executable, str(guard_script), "--root", str(mock_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Expected clean tree to pass, but failed:\n{result.stderr}"
