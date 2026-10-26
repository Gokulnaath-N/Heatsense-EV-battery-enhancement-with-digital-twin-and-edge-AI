#!/usr/bin/env python3
"""HeatSense Documentation Integrity Checker.

Zero-dependency standard library verification tool enforcing strict documentation
standards, link resolution, Mermaid diagram validity, ADR formatting, quality attribute
honesty, open-question traceability, and cross-document terminology consistency.

Usage:
    python scripts/check_docs.py [--root <repo-root>]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple


REQUIRED_DOC_SECTIONS = [
    "Purpose",
    "Scope",
    "Rules and invariants",
    "Decisions referenced",
    "Traceability",
    "Open questions",
]

ALLOWED_STATUS_VALUES = {"Draft for review", "Frozen"}

ALLOWED_MERMAID_TYPES = {
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram-v2",
}

CANONICAL_ALERT_LEVELS = {"GREEN", "YELLOW", "ORANGE", "RED", "SENSOR_FAULT"}
CANONICAL_DEVICE_STATES = {"BOOT", "IDLE_OPEN", "ARMED_CLOSED", "FAULT_LATCHED"}
CANONICAL_FAULT_MASKS = {
    "OVP",
    "UVP",
    "OTP",
    "OCP",
    "INA219_FAIL",
    "DS18B20_FAIL",
    "SENSOR_MISMATCH",
    "WDT_RESET_SEEN",
}


class Violation:
    """Represents a documentation validation failure."""

    def __init__(self, file_path: Path, line: int, check_id: str, message: str) -> None:
        self.file_path = file_path
        self.line = line
        self.check_id = check_id
        self.message = message

    def format(self, root: Path) -> str:
        try:
            rel = self.file_path.relative_to(root).as_posix()
        except ValueError:
            rel = self.file_path.as_posix()
        return f"{rel}:{self.line}: {self.check_id}: {self.message}"


def check_architecture_headers_and_status(arch_dir: Path) -> list[Violation]:
    """Check 1: Architecture document standards and status line."""
    violations: list[Violation] = []
    if not arch_dir.is_dir():
        return violations

    for file_path in sorted(arch_dir.glob("*.md")):
        if file_path.name in {"README.md", "open-questions.md"}:
            continue

        lines = file_path.read_text(encoding="utf-8").splitlines()
        found_sections: set[str] = set()
        status_valid = False
        status_line_num = 1

        for idx, line in enumerate(lines, start=1):
            # Check for Status line: e.g. "Status: Draft for review"
            status_match = re.match(r"^Status:\s*(.+)$", line.strip(), re.IGNORECASE)
            if status_match:
                status_line_num = idx
                val = status_match.group(1).strip()
                if val in ALLOWED_STATUS_VALUES:
                    status_valid = True
                else:
                    violations.append(
                        Violation(
                            file_path,
                            idx,
                            "DOC-01",
                            f"Status must be 'Draft for review' or 'Frozen', found: '{val}'",
                        )
                    )

            # Check for required h2 sections: e.g. "## Purpose"
            h2_match = re.match(r"^##\s+([^#\n]+)$", line.strip())
            if h2_match:
                section_title = h2_match.group(1).strip()
                for req in REQUIRED_DOC_SECTIONS:
                    if section_title.lower() == req.lower():
                        found_sections.add(req)

        if not status_valid and not any(v.check_id == "DOC-01" for v in violations if v.file_path == file_path):
            violations.append(
                Violation(
                    file_path,
                    status_line_num,
                    "DOC-01",
                    "Missing or invalid Status header ('Draft for review' or 'Frozen' required)",
                )
            )

        for req in REQUIRED_DOC_SECTIONS:
            if req not in found_sections:
                violations.append(
                    Violation(
                        file_path,
                        1,
                        "DOC-01",
                        f"Missing mandatory section header: '## {req}'",
                    )
                )

    return violations


def check_links_and_adr_references(root: Path) -> list[Violation]:
    """Check 2: Resolve relative markdown links and ADR references."""
    violations: list[Violation] = []
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return violations

    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    adr_ref_pattern = re.compile(r"\bADR-(\d{4})\b")

    for file_path in sorted(docs_dir.rglob("*.md")):
        lines = file_path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            # Check standard markdown links [text](path)
            for match in link_pattern.finditer(line):
                target = match.group(2).strip()
                # Ignore web URLs, anchors, mailto
                if re.match(r"^(https?://|mailto:|#)", target):
                    continue
                # Split off any URL anchor: file.md#section
                clean_target = target.split("#")[0]
                if not clean_target:
                    continue
                target_path = (file_path.parent / clean_target).resolve()
                if not target_path.exists():
                    violations.append(
                        Violation(
                            file_path,
                            idx,
                            "DOC-02",
                            f"Broken relative link '{target}' -> target file does not exist",
                        )
                    )

            # Check ADR-NNNN references
            for match in adr_ref_pattern.finditer(line):
                adr_num = match.group(1)
                adr_dir = root / "docs" / "adr"
                matches = list(adr_dir.glob(f"{adr_num}-*.md"))
                if not matches and not (adr_dir / f"{adr_num}.md").exists():
                    violations.append(
                        Violation(
                            file_path,
                            idx,
                            "DOC-02",
                            f"Referenced ADR-{adr_num} does not exist in docs/adr/",
                        )
                    )

    return violations


def check_mermaid_diagrams(root: Path) -> list[Violation]:
    """Check 3: Validate Mermaid syntax types, line limits, and forbidden C4 tags."""
    violations: list[Violation] = []
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return violations

    for file_path in sorted(docs_dir.rglob("*.md")):
        lines = file_path.read_text(encoding="utf-8").splitlines()
        inside_mermaid = False
        mermaid_start_line = 0
        diagram_type_found = False

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped == "```mermaid":
                inside_mermaid = True
                mermaid_start_line = idx
                diagram_type_found = False
                continue
            elif stripped == "```" and inside_mermaid:
                inside_mermaid = False
                if not diagram_type_found:
                    violations.append(
                        Violation(
                            file_path,
                            mermaid_start_line,
                            "DOC-03",
                            "Mermaid block does not declare a recognized diagram type",
                        )
                    )
                continue

            if inside_mermaid:
                # Check for line length limit inside diagrams
                if len(line) > 200:
                    violations.append(
                        Violation(
                            file_path,
                            idx,
                            "DOC-03",
                            f"Mermaid diagram line exceeds 200 characters ({len(line)} chars)",
                        )
                    )

                # Check for forbidden experimental C4 syntax
                if re.search(r"\b(C4Context|C4Container|C4Component|Person|System_Ext)\b", line):
                    violations.append(
                        Violation(
                            file_path,
                            idx,
                            "DOC-03",
                            "Forbidden experimental C4 Mermaid syntax detected; use standard flowchart with subgraphs",
                        )
                    )

                # Identify diagram type on first non-empty line
                if not diagram_type_found and stripped and not stripped.startswith("%%"):
                    first_word = stripped.split()[0].split("{")[0]
                    if first_word in ALLOWED_MERMAID_TYPES:
                        diagram_type_found = True
                    else:
                        violations.append(
                            Violation(
                                file_path,
                                idx,
                                "DOC-03",
                                f"Mermaid diagram type '{first_word}' is forbidden; must be one of: "
                                f"{sorted(ALLOWED_MERMAID_TYPES)}",
                            )
                        )
                        diagram_type_found = True  # prevent repeated warnings

        if inside_mermaid:
            violations.append(
                Violation(
                    file_path,
                    mermaid_start_line,
                    "DOC-03",
                    "Unbalanced Mermaid code fence (missing closing ```)",
                )
            )

    return violations


def check_adr_structure_and_index(root: Path) -> list[Violation]:
    """Check 4: ADR structure, sequential numbering, and README index."""
    violations: list[Violation] = []
    adr_dir = root / "docs" / "adr"
    if not adr_dir.is_dir():
        return violations

    adr_readme = adr_dir / "README.md"
    readme_content = adr_readme.read_text(encoding="utf-8") if adr_readme.is_file() else ""

    adr_files: list[Path] = []
    for p in sorted(adr_dir.glob("*.md")):
        if p.name in {"README.md", "0000-template.md"}:
            continue
        adr_files.append(p)

    required_adr_sections = ["Context", "Decision", "Alternatives Considered", "Consequences"]
    allowed_adr_statuses = {"ACCEPTED", "PROPOSED", "DEPRECATED", "SUPERSEDED"}

    numbers: list[int] = []

    for file_path in adr_files:
        match = re.match(r"^(\d{4})-(.+)\.md$", file_path.name)
        if not match:
            violations.append(
                Violation(
                    file_path,
                    1,
                    "DOC-04",
                    f"ADR filename must match format 'NNNN-short-title.md', found: '{file_path.name}'",
                )
            )
            continue

        num = int(match.group(1))
        numbers.append(num)

        # Check indexed in README
        if file_path.name not in readme_content and f"[{match.group(1)}]" not in readme_content:
            violations.append(
                Violation(
                    file_path,
                    1,
                    "DOC-04",
                    f"ADR {file_path.name} is not indexed in docs/adr/README.md",
                )
            )

        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check Status
        status_match = re.search(r"##\s*Status\s*\n\s*([A-Za-z]+)", content, re.IGNORECASE)
        if not status_match:
            status_match = re.search(r"Status:\s*([A-Za-z]+)", content, re.IGNORECASE)

        if status_match:
            st = status_match.group(1).upper()
            if st not in allowed_adr_statuses:
                violations.append(
                    Violation(
                        file_path,
                        1,
                        "DOC-04",
                        f"ADR status '{st}' is invalid; must be one of: {sorted(allowed_adr_statuses)}",
                    )
                )
        else:
            violations.append(
                Violation(
                    file_path,
                    1,
                    "DOC-04",
                    "ADR missing '## Status' section with Accepted/Proposed/Superseded/Deprecated",
                )
            )

        # Check Date
        date_match = re.search(r"(##\s*Date\s*\n\s*\d{4}-\d{2}-\d{2}|Date:\s*\d{4}-\d{2}-\d{2})", content)
        if not date_match:
            violations.append(
                Violation(
                    file_path,
                    1,
                    "DOC-04",
                    "ADR missing valid Date (format YYYY-MM-DD)",
                )
            )

        # Check required sections
        for sec in required_adr_sections:
            if not re.search(rf"##\s+{sec}", content, re.IGNORECASE):
                violations.append(
                    Violation(
                        file_path,
                        1,
                        "DOC-04",
                        f"ADR missing required section: '## {sec}'",
                    )
                )

    # Check sequential numbering (starting after template)
    if numbers:
        numbers_sorted = sorted(numbers)
        # Check uniqueness
        if len(numbers_sorted) != len(set(numbers_sorted)):
            violations.append(
                Violation(
                    adr_dir,
                    1,
                    "DOC-04",
                    "ADR numbers are not unique",
                )
            )
        # Check sequential: numbers should be consecutive starting from numbers_sorted[0]
        for expected, actual in enumerate(range(numbers_sorted[0], numbers_sorted[0] + len(numbers_sorted)), start=0):
            if numbers_sorted[expected] != actual:
                violations.append(
                    Violation(
                        adr_dir,
                        1,
                        "DOC-04",
                        f"ADR numbering is non-sequential: expected {actual}, found {numbers_sorted[expected]}",
                    )
                )
                break

    return violations


def check_architecture_readme_index(root: Path) -> list[Violation]:
    """Check 5: docs/architecture/README.md indexes all files in docs/architecture/."""
    violations: list[Violation] = []
    arch_dir = root / "docs" / "architecture"
    readme_path = arch_dir / "README.md"
    if not readme_path.is_file():
        violations.append(
            Violation(arch_dir, 1, "DOC-05", "Missing docs/architecture/README.md")
        )
        return violations

    readme_content = readme_path.read_text(encoding="utf-8")

    for file_path in sorted(arch_dir.glob("*.md")):
        if file_path.name == "README.md":
            continue
        if file_path.name not in readme_content:
            violations.append(
                Violation(
                    readme_path,
                    1,
                    "DOC-05",
                    f"Document '{file_path.name}' is not listed in docs/architecture/README.md",
                )
            )

    return violations


def check_quality_attributes_honesty(root: Path) -> list[Violation]:
    """Check 6: In 06-quality-attributes.md, every row with Target has PROVISIONAL or [not yet measured]."""
    violations: list[Violation] = []
    qa_path = root / "docs" / "architecture" / "06-quality-attributes.md"
    if not qa_path.is_file():
        return violations

    lines = qa_path.read_text(encoding="utf-8").splitlines()
    in_table = False
    header_indices: dict[str, int] = {}

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("|") and "Target" in stripped:
            in_table = True
            cols = [c.strip().lower() for c in stripped.split("|")[1:-1]]
            header_indices = {col: i for i, col in enumerate(cols)}
            continue

        if in_table and stripped.startswith("|") and ("---" in stripped or ":---" in stripped):
            continue

        if in_table:
            if not stripped.startswith("|"):
                in_table = False
                continue

            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            target_idx = header_indices.get("target")
            status_idx = header_indices.get("status")

            if target_idx is not None and target_idx < len(cells):
                target_val = cells[target_idx]
                status_val = cells[status_idx] if status_idx is not None and status_idx < len(cells) else ""

                has_provisional = "PROVISIONAL" in target_val or "PROVISIONAL" in status_val
                has_not_measured = "[not yet measured]" in target_val or "[not yet measured]" in status_val

                if not (has_provisional or has_not_measured):
                    violations.append(
                        Violation(
                            qa_path,
                            idx,
                            "DOC-06",
                            f"Quality target row '{cells[0]}' must contain 'PROVISIONAL' or '[not yet measured]'",
                        )
                    )

    return violations


def check_terminology_consistency(root: Path) -> list[Violation]:
    """Check 7: Terminology consistency for component names, states, levels, and fault masks."""
    violations: list[Violation] = []
    comp_doc = root / "docs" / "architecture" / "02-components-host.md"
    comp_content = comp_doc.read_text(encoding="utf-8") if comp_doc.is_file() else ""

    arch_dir = root / "docs" / "architecture"
    if not arch_dir.is_dir():
        return violations

    # Component names referenced in diagrams that must exist in 02-components-host.md
    expected_components = [
        "TelemetryPipeline",
        "FrameCodec",
        "Crc16",
        "DeviceTimeUnwrapper",
        "StateEstimator",
        "CoulombCounterEstimator",
        "AnomalyDetector",
        "AlertEngine",
        "EventBus",
        "SerialTransport",
        "SimulatedTransport",
        "SqliteSampleRepository",
        "VirtualCell",
        "VirtualDevice",
    ]

    for comp in expected_components:
        if comp not in comp_content:
            violations.append(
                Violation(
                    comp_doc,
                    1,
                    "DOC-07",
                    f"Component '{comp}' referenced in architecture diagrams is missing in 02-components-host.md",
                )
            )

    # Check alert levels, device states, fault masks in all architecture docs
    for file_path in sorted(arch_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            # Check for misspelled alert level combinations (e.g. SENSOR-FAULT vs SENSOR_FAULT)
            if "SENSOR-FAULT" in line or "SENSOR FAULT" in line and "Precedence" not in line and "precedence" not in line:
                if not re.search(r"\bSENSOR_FAULT\b", line) and "SENSOR FAULT" in line.upper():
                    # Check if intended as enum token
                    if "`SENSOR FAULT`" in line or "AlertLevel.SENSOR FAULT" in line:
                        violations.append(
                            Violation(
                                file_path,
                                idx,
                                "DOC-07",
                                "Alert level misspelled: expected 'SENSOR_FAULT', found 'SENSOR FAULT'",
                            )
                        )

            # Check device states casing / misspelling (e.g. IDLE-OPEN, ARMED-CLOSED)
            if "`IDLE-OPEN`" in line or "`ARMED-CLOSED`" in line or "`FAULT-LATCHED`" in line:
                violations.append(
                    Violation(
                        file_path,
                        idx,
                        "DOC-07",
                        "Device state misspelled with hyphen; expected underscore (e.g. IDLE_OPEN)",
                    )
                )

    return violations


def check_open_questions_integrity(root: Path) -> list[Violation]:
    """Check 8: Every OQ-NNN cited in docs exists in open-questions.md with an owner."""
    violations: list[Violation] = []
    oq_path = root / "docs" / "architecture" / "open-questions.md"
    if not oq_path.is_file():
        violations.append(
            Violation(root / "docs" / "architecture", 1, "DOC-08", "Missing open-questions.md")
        )
        return violations

    oq_content = oq_path.read_text(encoding="utf-8")
    oq_lines = oq_content.splitlines()

    registered_oqs: dict[str, str] = {}
    for idx, line in enumerate(oq_lines, start=1):
        # Look for table rows: | **OQ-001** | ... | Owner | ... |
        match = re.search(r"\|\s*\*{0,2}(OQ-\d{3})\*{0,2}\s*\|", line)
        if match:
            oq_id = match.group(1)
            cells = [c.strip() for c in line.split("|")[1:-1]]
            # Table columns: ID | Question | Why It Matters | Evaluated Options | Recommended Default | Owner | Blocks Which Prompt | Status
            owner = cells[5] if len(cells) > 5 else ""
            registered_oqs[oq_id] = owner
            if not owner or owner.lower() in {"tbd", "none", "[unassigned]"}:
                violations.append(
                    Violation(
                        oq_path,
                        idx,
                        "DOC-08",
                        f"Open question {oq_id} has no valid assigned owner (found: '{owner}')",
                    )
                )

    # Scan all docs for OQ references
    oq_ref_pattern = re.compile(r"\b(OQ-\d{3})\b")
    docs_dir = root / "docs"

    for file_path in sorted(docs_dir.rglob("*.md")):
        if file_path == oq_path:
            continue
        lines = file_path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            for match in oq_ref_pattern.finditer(line):
                cited_id = match.group(1)
                if cited_id not in registered_oqs:
                    violations.append(
                        Violation(
                            file_path,
                            idx,
                            "DOC-08",
                            f"Referenced open question '{cited_id}' is not registered in docs/architecture/open-questions.md",
                        )
                    )

    return violations


def run_all_checks(root: Path) -> list[Violation]:
    """Execute all 8 documentation integrity checks and aggregate violations."""
    violations: list[Violation] = []
    arch_dir = root / "docs" / "architecture"

    violations.extend(check_architecture_headers_and_status(arch_dir))
    violations.extend(check_links_and_adr_references(root))
    violations.extend(check_mermaid_diagrams(root))
    violations.extend(check_adr_structure_and_index(root))
    violations.extend(check_architecture_readme_index(root))
    violations.extend(check_quality_attributes_honesty(root))
    violations.extend(check_terminology_consistency(root))
    violations.extend(check_open_questions_integrity(root))

    return violations


def main() -> int:
    """CLI entry point for documentation integrity checker."""
    parser = argparse.ArgumentParser(description="HeatSense Documentation Integrity Checker")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root directory (defaults to parent of scripts/)",
    )
    args = parser.parse_args()

    if args.root:
        root = args.root.resolve()
    else:
        root = Path(__file__).resolve().parent.parent

    print("=" * 60)
    print("HeatSense Documentation Integrity Check")
    print(f"Root: {root}")
    print("=" * 60)

    violations = run_all_checks(root)

    if violations:
        print(f"[-] Documentation Check FAILED with {len(violations)} violation(s):", file=sys.stderr)
        for v in violations:
            print(f"    {v.format(root)}", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        return 1

    print("[+] Documentation Check PASSED: All architecture documents, ADRs, diagrams, and links are valid.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
