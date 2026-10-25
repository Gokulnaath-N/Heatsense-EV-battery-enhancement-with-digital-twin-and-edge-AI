#!/usr/bin/env python3
"""HeatSense Test Coverage Threshold Enforcer.

Enforces per-package and overall coverage thresholds from host/coverage.json.

Thresholds:
    - Overall repository: 80%
    - heatsense/domain: 90% (enforced when domain contains measurable executable code)

Usage:
    python scripts/check_coverage.py [--file host/coverage.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Coverage thresholds in percent
THRESHOLDS: dict[str, float] = {
    "overall": 80.0,
    "domain": 90.0,
}


def load_coverage_data(json_path: Path) -> dict:
    """Load coverage metrics from coverage.json."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_file_metrics(files_dict: dict) -> Tuple[int, int, int, int]:
    """Calculate (num_statements, covered_statements, missing_statements, branch_coverage) for domain files."""
    domain_statements = 0
    domain_covered = 0

    for file_path, data in files_dict.items():
        norm_path = file_path.replace("\\", "/")
        if "/domain/" in norm_path or norm_path.endswith("/domain"):
            summary = data.get("summary", {})
            num_stmts = summary.get("num_statements", 0)
            cov_stmts = summary.get("covered_lines", 0)
            domain_statements += num_stmts
            domain_covered += cov_stmts

    return domain_statements, domain_covered, 0, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check HeatSense coverage thresholds")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path("host/coverage.json"),
        help="Path to coverage.json (default: host/coverage.json)",
    )
    args = parser.parse_args()

    coverage_path = args.file.resolve()
    if not coverage_path.exists():
        print(f"[-] Coverage file not found at {coverage_path}. Run coverage first.", file=sys.stderr)
        return 1

    try:
        data = load_coverage_data(coverage_path)
    except Exception as e:
        print(f"[-] Failed to read {coverage_path}: {e}", file=sys.stderr)
        return 1

    totals = data.get("totals", {})
    overall_percent = totals.get("percent_covered", 0.0)
    total_statements = totals.get("num_statements", 0)

    files_dict = data.get("files", {})
    domain_statements, domain_covered, _, _ = calculate_file_metrics(files_dict)

    print("=" * 65)
    print("HeatSense Test Coverage Report")
    print("=" * 65)
    print(f"{'Target':<20} | {'Statements':<10} | {'Actual (%)':<12} | {'Required (%)':<12} | {'Status'}")
    print("-" * 65)

    failures: list[str] = []

    # Check Overall
    overall_req = THRESHOLDS["overall"]
    if total_statements == 0:
        overall_status = "PASS (no code yet)"
    elif overall_percent >= overall_req:
        overall_status = "PASS"
    else:
        overall_status = "FAIL"
        failures.append(f"Overall coverage ({overall_percent:.1f}%) is below required {overall_req:.1f}%")

    print(f"{'Overall Host':<20} | {total_statements:<10} | {overall_percent:<12.1f} | {overall_req:<12.1f} | {overall_status}")

    # Check Domain
    domain_req = THRESHOLDS["domain"]
    if domain_statements == 0:
        domain_status = "PASS (no measurable code yet)"
        domain_percent_str = "N/A"
    else:
        domain_percent = (domain_covered / domain_statements) * 100.0 if domain_statements > 0 else 0.0
        domain_percent_str = f"{domain_percent:.1f}"
        if domain_percent >= domain_req:
            domain_status = "PASS"
        else:
            domain_status = "FAIL"
            failures.append(f"Domain coverage ({domain_percent:.1f}%) is below required {domain_req:.1f}%")

    print(f"{'heatsense.domain':<20} | {domain_statements:<10} | {domain_percent_str:<12} | {domain_req:<12.1f} | {domain_status}")
    print("=" * 65)

    if failures:
        print(f"[-] Coverage check FAILED with {len(failures)} issue(s):", file=sys.stderr)
        for f in failures:
            print(f"    - {f}", file=sys.stderr)
        return 1

    print("[+] Coverage check PASSED: All coverage thresholds satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
