"""Tests verifying that the Documentation Integrity Checker detects defects."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.mark.unit
def test_real_docs_tree_passes() -> None:
    """Verify that the actual HeatSense documentation passes check_docs.py."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    check_script = repo_root / "scripts" / "check_docs.py"

    result = subprocess.run(  # noqa: S603
        [sys.executable, str(check_script), "--root", str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Documentation checker failed on real docs tree:\n{result.stderr}\n{result.stdout}"
    )
    assert "Documentation Check PASSED" in result.stdout


def _setup_minimal_valid_docs(tmp_path: Path) -> Path:
    """Helper to create a fully valid minimal docs tree."""
    mock_root = tmp_path / "repo"
    arch_dir = mock_root / "docs" / "architecture"
    adr_dir = mock_root / "docs" / "adr"
    arch_dir.mkdir(parents=True, exist_ok=True)
    adr_dir.mkdir(parents=True, exist_ok=True)

    # 1. Open questions
    (arch_dir / "open-questions.md").write_text(
        "# Open Questions\n\n| ID | Question | Why | Options | Rec | Owner | Blocks | Status |\n"
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        "| **OQ-001** | Q1 | Why | Opt | Rec | Hardware Teammate | Prompt 11 | Open |\n",
        encoding="utf-8",
    )

    # 2. Arch README
    (arch_dir / "README.md").write_text(
        "# Architecture Index\n\n- [00-context.md](00-context.md)\n- [02-components-host.md](02-components-host.md)\n"
        "- [06-quality-attributes.md](06-quality-attributes.md)\n- [open-questions.md](open-questions.md)\n",
        encoding="utf-8",
    )

    # 3. Valid arch doc 00-context.md
    (arch_dir / "00-context.md").write_text(
        "# Context\n\nStatus: Draft for review\n\n"
        "## Purpose\nContext purpose.\n\n## Scope\nContext scope.\n\n"
        "## Main Content\nSee OQ-001.\n\n"
        "## Rules and invariants\nRule 1.\n\n## Decisions referenced\nNone.\n\n"
        "## Traceability\nTrace.\n\n## Open questions\nOQ-001.\n",
        encoding="utf-8",
    )

    # 4. Valid arch doc 02-components-host.md
    (arch_dir / "02-components-host.md").write_text(
        "# Components\n\nStatus: Draft for review\n\n"
        "## Purpose\nHost components.\n\n## Scope\nHost scope.\n\n"
        "## Main Content\n"
        "TelemetryPipeline FrameCodec Crc16 DeviceTimeUnwrapper StateEstimator "
        "CoulombCounterEstimator AnomalyDetector AlertEngine EventBus SerialTransport "
        "SimulatedTransport SqliteSampleRepository VirtualCell VirtualDevice.\n\n"
        "## Rules and invariants\nRule 1.\n\n## Decisions referenced\nNone.\n\n"
        "## Traceability\nTrace.\n\n## Open questions\nNone.\n",
        encoding="utf-8",
    )

    # 5. Valid 06-quality-attributes.md
    (arch_dir / "06-quality-attributes.md").write_text(
        "# Quality Attributes\n\nStatus: Draft for review\n\n"
        "## Purpose\nQA purpose.\n\n## Scope\nQA scope.\n\n"
        "## Quality Register\n\n"
        "| ID | Quality Attribute | Requirement Description | Target | Status |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| QA-01 | Safety | Relay open | <= 100 ms (PROVISIONAL) | PROVISIONAL |\n"
        "| QA-02 | Performance | Latency | <= 150 ms | [not yet measured] |\n\n"
        "## Rules and invariants\nRule 1.\n\n## Decisions referenced\nNone.\n\n"
        "## Traceability\nTrace.\n\n## Open questions\nNone.\n",
        encoding="utf-8",
    )

    # 6. ADR README
    (adr_dir / "README.md").write_text(
        "# ADR Index\n\n| Number | Title |\n| :--- | :--- |\n| [0001](0001-layout.md) | Layout |\n",
        encoding="utf-8",
    )

    # 7. Valid ADR 0001-layout.md
    (adr_dir / "0001-layout.md").write_text(
        "# ADR 0001: Layout\n\n## Status\nACCEPTED\n\n## Date\n2026-10-26\n\n"
        "## Context\nContext.\n\n## Decision\nDecision.\n\n"
        "## Alternatives Considered\nAlt.\n\n## Consequences\nConsequences.\n",
        encoding="utf-8",
    )

    return mock_root


@pytest.mark.unit
def test_synthetic_valid_tree_passes(tmp_path: Path) -> None:
    """Verify that a minimal valid documentation tree passes check_docs.py."""
    mock_root = _setup_minimal_valid_docs(tmp_path)
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    check_script = repo_root / "scripts" / "check_docs.py"

    result = subprocess.run(  # noqa: S603
        [sys.executable, str(check_script), "--root", str(mock_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Expected clean mock docs to pass:\n{result.stderr}\n{result.stdout}"
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("check_id", "modifier_fn"),
    [
        (
            "DOC-01",
            lambda root: (root / "docs" / "architecture" / "00-context.md").write_text(
                "# Context\n\nStatus: InvalidStatus\n\n## Purpose\nOnly Purpose.\n",
                encoding="utf-8",
            ),
        ),
        (
            "DOC-02",
            lambda root: (root / "docs" / "architecture" / "00-context.md").write_text(
                "# Context\n\nStatus: Draft for review\n\n"
                "## Purpose\n[Broken Link](non_existent_file.md)\n\n## Scope\nScope.\n\n"
                "## Rules and invariants\nR.\n\n## Decisions referenced\nNone.\n\n"
                "## Traceability\nT.\n\n## Open questions\nNone.\n",
                encoding="utf-8",
            ),
        ),
        (
            "DOC-03",
            lambda root: (root / "docs" / "architecture" / "00-context.md").write_text(
                "# Context\n\nStatus: Draft for review\n\n"
                "## Purpose\nPurpose.\n\n## Scope\nScope.\n\n"
                "## Diagram\n```mermaid\nC4Context\nPerson(x, y)\n```\n\n"
                "## Rules and invariants\nR.\n\n## Decisions referenced\nNone.\n\n"
                "## Traceability\nT.\n\n## Open questions\nNone.\n",
                encoding="utf-8",
            ),
        ),
        (
            "DOC-04",
            lambda root: (root / "docs" / "adr" / "0002-broken.md").write_text(
                "# ADR 0002\n\nMissing status and date.\n",
                encoding="utf-8",
            ),
        ),
        (
            "DOC-05",
            lambda root: (root / "docs" / "architecture" / "99-unindexed.md").write_text(
                "# Unindexed\n\nStatus: Draft for review\n\n## Purpose\nP.\n\n## Scope\nS.\n\n"
                "## Rules and invariants\nR.\n\n## Decisions referenced\nNone.\n\n"
                "## Traceability\nT.\n\n## Open questions\nNone.\n",
                encoding="utf-8",
            ),
        ),
        (
            "DOC-06",
            lambda root: (root / "docs" / "architecture" / "06-quality-attributes.md").write_text(
                "# Quality Attributes\n\nStatus: Draft for review\n\n"
                "## Purpose\nQA purpose.\n\n## Scope\nQA scope.\n\n"
                "| ID | Quality Attribute | Requirement Description | Target | Status |\n"
                "| :--- | :--- | :--- | :--- | :--- |\n"
                "| QA-01 | Safety | Trip | <= 100 ms | CONFIRMED |\n\n"
                "## Rules and invariants\nR.\n\n## Decisions referenced\nNone.\n\n"
                "## Traceability\nT.\n\n## Open questions\nNone.\n",
                encoding="utf-8",
            ),
        ),
        (
            "DOC-07",
            lambda root: (root / "docs" / "architecture" / "02-components-host.md").write_text(
                "# Components\n\nStatus: Draft for review\n\n"
                "## Purpose\nP.\n\n## Scope\nS.\n\n"
                "Missing component names here.\n\n"
                "## Rules and invariants\nR.\n\n## Decisions referenced\nNone.\n\n"
                "## Traceability\nT.\n\n## Open questions\nNone.\n",
                encoding="utf-8",
            ),
        ),
        (
            "DOC-08",
            lambda root: (root / "docs" / "architecture" / "00-context.md").write_text(
                "# Context\n\nStatus: Draft for review\n\n"
                "## Purpose\nReferences OQ-999.\n\n## Scope\nS.\n\n"
                "## Rules and invariants\nR.\n\n## Decisions referenced\nNone.\n\n"
                "## Traceability\nT.\n\n## Open questions\nOQ-999.\n",
                encoding="utf-8",
            ),
        ),
    ],
)
def test_detects_each_check_violation(
    tmp_path: Path, check_id: str, modifier_fn: Callable[[Path], None]
) -> None:
    """Verify that check_docs.py fails and reports the expected check ID for each failure mode."""
    mock_root = _setup_minimal_valid_docs(tmp_path)
    modifier_fn(mock_root)

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    check_script = repo_root / "scripts" / "check_docs.py"

    result = subprocess.run(  # noqa: S603
        [sys.executable, str(check_script), "--root", str(mock_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, (
        f"Expected check_docs.py to fail with {check_id}, but passed.\nStdout: {result.stdout}"
    )
    assert check_id in result.stderr, f"Expected {check_id} in stderr:\n{result.stderr}"
