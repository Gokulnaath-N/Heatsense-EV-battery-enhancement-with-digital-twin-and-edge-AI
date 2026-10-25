#!/usr/bin/env python3
"""HeatSense Architecture Guard.

Enforces Hexagonal Architecture layer rules and dependency invariants using Python's AST.

Rules Enforced:
    R1: domain may import only: stdlib, numpy, typing_extensions, and other domain modules.
    R2: application may import only: stdlib, numpy, typing_extensions, domain, application.
    R3: infrastructure must not import interfaces.
    R4: interfaces must not import infrastructure directly (bootstrap.py wires instances).
    R5: simulation may import only: stdlib, numpy, scipy, domain, simulation.
    R6: identification and evaluation must not import interfaces.
    R7: No host module may import firmware code.
    R8: Only bootstrap.py may import from every layer.
    R9: No module-level mutable globals (list/dict/set literals or comprehensions) in
        domain and application, unless name ends with _TABLE, _MAP, or _CONSTANTS and is
        annotated as Final.

Usage:
    python scripts/arch_guard.py [--root host/src/heatsense]
    python scripts/arch_guard.py --list-rules
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Tuple

RULES: dict[str, str] = {
    "R1": "domain may import only: stdlib, numpy, and other domain modules.",
    "R2": "application may import only: stdlib, numpy, domain, application. (No pydantic, no fastapi).",
    "R3": "infrastructure must not import interfaces.",
    "R4": "interfaces must not import infrastructure directly (bootstrap.py wires instances).",
    "R5": "simulation may import only: stdlib, numpy, scipy, domain, simulation.",
    "R6": "identification and evaluation must not import interfaces.",
    "R7": "ANY module importing a path that contains the word 'firmware'.",
    "R8": "Only bootstrap.py may import from every layer.",
    "R9": "No module-level mutable globals in domain and application.",
}

# Standard library modules supported in Python 3.12
STDLIB_MODULES: set[str] = set(sys.stdlib_module_names) | {"typing_extensions", "_typeshed"}

LAYERS: set[str] = {
    "domain",
    "application",
    "infrastructure",
    "interfaces",
    "simulation",
    "identification",
    "evaluation",
    "bootstrap",
}


@dataclass
class ImportRecord:
    """Record of an import detected in source code."""

    source_file: Path
    line: int
    raw_module: str
    resolved_layer: str
    is_firmware: bool


@dataclass
class Violation:
    """An architectural invariant violation."""

    file_path: Path
    line: int
    rule_id: str
    message: str

    def __str__(self) -> str:
        rel_path = self.file_path.as_posix()
        return f"{rel_path}:{self.line}: {self.rule_id}: {self.message}"


def get_source_layer(file_path: Path, root_dir: Path) -> str:
    """Determine which architectural layer a source file belongs to."""
    try:
        rel_path = file_path.relative_to(root_dir)
    except ValueError:
        return "unknown"

    parts = rel_path.parts
    if not parts:
        return "unknown"

    # If file is bootstrap.py at root of heatsense
    if parts[0] == "bootstrap.py":
        return "bootstrap"

    if parts[0] in LAYERS:
        return parts[0]

    return "root"


def resolve_import_layer(
    import_module: str,
    level: int,
    file_path: Path,
    root_dir: Path,
) -> Tuple[str, bool]:
    """Resolve an import target to an architectural layer or external category.

    Returns:
        (resolved_layer, is_firmware)
    """
    is_firmware = "firmware" in import_module.split(".")

    # Handle relative imports: from . import x, from ..domain import y
    if level > 0:
        try:
            rel_parts = list(file_path.relative_to(root_dir).parent.parts)
            # level 1 is current directory, level 2 is parent directory, etc.
            steps_up = level - 1
            if steps_up < len(rel_parts):
                target_base = rel_parts[: len(rel_parts) - steps_up]
                if import_module:
                    full_target = target_base + import_module.split(".")
                else:
                    full_target = target_base

                if full_target and full_target[0] in LAYERS:
                    return full_target[0], is_firmware
                if full_target and full_target[0] == "bootstrap.py":
                    return "bootstrap", is_firmware
        except Exception:
            pass

    parts = import_module.split(".")
    first = parts[0]

    # Explicit heatsense module import: from heatsense.domain.value_objects import ...
    if first == "heatsense":
        if len(parts) > 1:
            second = parts[1]
            if second in LAYERS:
                return second, is_firmware
            if second.startswith("bootstrap"):
                return "bootstrap", is_firmware
        return "heatsense_root", is_firmware

    if first in LAYERS:
        return first, is_firmware

    if first in STDLIB_MODULES:
        return "stdlib", is_firmware

    if first == "numpy":
        return "numpy", is_firmware

    if first == "scipy":
        return "scipy", is_firmware

    return first, is_firmware


def check_mutable_globals(tree: ast.Module, file_path: Path, layer: str) -> list[Violation]:
    """Check R9: No module-level mutable globals in domain and application."""
    violations: list[Violation] = []
    if layer not in {"domain", "application"}:
        return violations

    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            # Check target names and values
            is_mutable = isinstance(stmt.value, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp))
            if is_mutable:
                for target in stmt.targets:
                    name = getattr(target, "id", None)
                    if name:
                        violations.append(
                            Violation(
                                file_path=file_path,
                                line=stmt.lineno,
                                rule_id="R9",
                                message=(
                                    f"Module-level mutable global assignment to '{name}' is forbidden in {layer} "
                                    f"(detects list/dict/set literal or comprehension without Final typing)."
                                ),
                            )
                        )
        elif isinstance(stmt, ast.AnnAssign):
            is_mutable = isinstance(stmt.value, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp))
            name = getattr(stmt.target, "id", None)
            if is_mutable and name:
                # Check exception: ends in _TABLE, _MAP, _CONSTANTS and annotated as Final
                is_named_constant = any(name.endswith(sfx) for sfx in ("_TABLE", "_MAP", "_CONSTANTS"))
                is_final = False
                annotation_str = ast.unparse(stmt.annotation) if hasattr(ast, "unparse") else ""
                if "Final" in annotation_str:
                    is_final = True

                if not (is_named_constant and is_final):
                    violations.append(
                        Violation(
                            file_path=file_path,
                            line=stmt.lineno,
                            rule_id="R9",
                            message=(
                                f"Module-level mutable assignment to '{name}' is forbidden in {layer} "
                                f"unless name ends in _TABLE/_MAP/_CONSTANTS and is annotated with Final."
                            ),
                        )
                    )

    return violations


def extract_imports(tree: ast.Module, file_path: Path, root_dir: Path) -> list[ImportRecord]:
    """Extract all import records from an AST module."""
    records: list[ImportRecord] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                layer, is_fw = resolve_import_layer(alias.name, 0, file_path, root_dir)
                records.append(
                    ImportRecord(
                        source_file=file_path,
                        line=node.lineno,
                        raw_module=alias.name,
                        resolved_layer=layer,
                        is_firmware=is_fw,
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            mod_name = node.module or ""
            layer, is_fw = resolve_import_layer(mod_name, node.level, file_path, root_dir)
            records.append(
                ImportRecord(
                    source_file=file_path,
                    line=node.lineno,
                    raw_module=f"{'.' * node.level}{mod_name}",
                    resolved_layer=layer,
                    is_firmware=is_fw,
                )
            )
    return records


def verify_file(file_path: Path, root_dir: Path) -> list[Violation]:
    """Verify architectural rules on a single Python source file."""
    violations: list[Violation] = []
    source_layer = get_source_layer(file_path, root_dir)

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except Exception as e:
        violations.append(
            Violation(
                file_path=file_path,
                line=1,
                rule_id="SYNTAX",
                message=f"Failed to parse AST: {e}",
            )
        )
        return violations

    # Check R9 for mutable globals
    violations.extend(check_mutable_globals(tree, file_path, source_layer))

    # Check import rules
    imports = extract_imports(tree, file_path, root_dir)
    for imp in imports:
        # R7: No host module may ever import firmware code
        if imp.is_firmware:
            violations.append(
                Violation(
                    file_path=file_path,
                    line=imp.line,
                    rule_id="R7",
                    message=f"Forbidden firmware import '{imp.raw_module}': host must never import firmware code.",
                )
            )

        target_layer = imp.resolved_layer

        # R1: domain rules
        if source_layer == "domain":
            allowed_domain_targets = {"domain", "stdlib", "numpy"}
            if target_layer not in allowed_domain_targets:
                violations.append(
                    Violation(
                        file_path=file_path,
                        line=imp.line,
                        rule_id="R1",
                        message=(
                            f"Domain layer may import only stdlib, numpy, and domain modules. "
                            f"Forbidden target: '{imp.raw_module}' (resolved as '{target_layer}')."
                        ),
                    )
                )

        # R2: application rules
        elif source_layer == "application":
            allowed_app_targets = {"domain", "application", "stdlib", "numpy"}
            if target_layer not in allowed_app_targets:
                violations.append(
                    Violation(
                        file_path=file_path,
                        line=imp.line,
                        rule_id="R2",
                        message=(
                            f"Application layer may import only stdlib, numpy, domain, and application. "
                            f"Forbidden target: '{imp.raw_module}' (resolved as '{target_layer}')."
                        ),
                    )
                )

        # R3: infrastructure must not import interfaces
        elif source_layer == "infrastructure":
            if target_layer == "interfaces":
                violations.append(
                    Violation(
                        file_path=file_path,
                        line=imp.line,
                        rule_id="R3",
                        message=(
                            f"Infrastructure must not import interfaces. "
                            f"Forbidden target: '{imp.raw_module}'."
                        ),
                    )
                )

        # R4: interfaces must not import infrastructure directly
        elif source_layer == "interfaces":
            if target_layer == "infrastructure":
                violations.append(
                    Violation(
                        file_path=file_path,
                        line=imp.line,
                        rule_id="R4",
                        message=(
                            f"Interfaces must not import infrastructure directly (instances must be injected via bootstrap.py). "
                            f"Forbidden target: '{imp.raw_module}'."
                        ),
                    )
                )

        # R5: simulation may import only: stdlib, numpy, scipy, domain, simulation
        elif source_layer == "simulation":
            allowed_sim_targets = {"domain", "simulation", "stdlib", "numpy", "scipy"}
            if target_layer not in allowed_sim_targets:
                violations.append(
                    Violation(
                        file_path=file_path,
                        line=imp.line,
                        rule_id="R5",
                        message=(
                            f"Simulation layer may import only stdlib, numpy, scipy, domain, and simulation. "
                            f"Forbidden target: '{imp.raw_module}' (resolved as '{target_layer}')."
                        ),
                    )
                )

        # R6: identification and evaluation must not import interfaces
        elif source_layer in {"identification", "evaluation"}:
            if target_layer == "interfaces":
                violations.append(
                    Violation(
                        file_path=file_path,
                        line=imp.line,
                        rule_id="R6",
                        message=(
                            f"{source_layer.capitalize()} must not import interfaces. "
                            f"Forbidden target: '{imp.raw_module}'."
                        ),
                    )
                )

    return violations


def run_guard(root_dir: Path) -> list[Violation]:
    """Scan all Python files under root_dir and collect rule violations."""
    violations: list[Violation] = []
    for current_dir, _, files in os.walk(root_dir):
        for file in sorted(files):
            if file.endswith(".py"):
                file_path = Path(current_dir) / file
                violations.extend(verify_file(file_path, root_dir))
    return violations


def main() -> int:
    """CLI entry point for architecture guard."""
    parser = argparse.ArgumentParser(description="HeatSense Hexagonal Architecture Guard")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("host/src/heatsense"),
        help="Root directory of the heatsense package (default: host/src/heatsense)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="Print the architectural rule catalogue and exit",
    )
    args = parser.parse_args()

    if args.list_rules:
        print("HeatSense Architecture Guard Rules:")
        for rule_id, desc in RULES.items():
            print(f"  {rule_id}: {desc}")
        return 0

    root = args.root.resolve()
    if not root.exists():
        print(f"Error: Target directory does not exist: {root}", file=sys.stderr)
        return 1

    violations = run_guard(root)

    if violations:
        print(f"[-] Architecture Guard FAILED with {len(violations)} violation(s):", file=sys.stderr)
        for v in violations:
            print(f"    {v}", file=sys.stderr)
        return 1

    print("[+] Architecture Guard PASSED: All layer dependency rules respected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
