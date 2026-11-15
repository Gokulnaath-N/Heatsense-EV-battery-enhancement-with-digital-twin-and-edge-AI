"""Lightweight, zero-dependency unit test runner for HeatSense host test suite.

Discovers and executes all test functions across host/tests/unit/.
"""

import sys
import time
import inspect
import types
from pathlib import Path
import importlib.util

# 1. Provide a standard library pytest shim if pytest is not installed
if "pytest" not in sys.modules:
    class RaisesContext:
        def __init__(self, exc_type, match=None):
            self.exc_type = exc_type
            self.match = match
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                raise AssertionError(f"Expected {self.exc_type}, but no exception was raised")
            return issubclass(exc_type, self.exc_type)

    mock_pytest = types.ModuleType("pytest")
    mock_pytest.raises = RaisesContext
    class Mark:
        @staticmethod
        def unit(func): return func
        @staticmethod
        def parametrize(*args, **kwargs):
            def decorator(func): return func
            return decorator
    mock_pytest.mark = Mark()
    sys.modules["pytest"] = mock_pytest

# 2. Add host/src and repo_root to sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "host" / "src"))
sys.path.insert(0, str(repo_root))

test_files = [
    repo_root / "host" / "tests" / "unit" / "domain" / "test_ekf.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_thermal.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_cusum.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_voltage_residual_issue01.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_thermal_initialization_issue02.py",
    repo_root / "host" / "tests" / "unit" / "application" / "test_digital_twin_pipeline.py",
    repo_root / "host" / "tests" / "unit" / "interfaces" / "test_api_endpoints_issue03.py",
    repo_root / "host" / "tests" / "unit" / "infrastructure" / "test_hybrid_ml.py",
    repo_root / "host" / "tests" / "unit" / "research" / "test_mit_ingestion.py",
    repo_root / "host" / "tests" / "unit" / "research" / "test_lfp_calibration.py",
    repo_root / "host" / "tests" / "unit" / "research" / "test_mit_physics_features.py",
    repo_root / "host" / "tests" / "unit" / "research" / "test_ml_benchmarking.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_crc16.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_frames_vo.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_result.py",
    repo_root / "host" / "tests" / "unit" / "domain" / "test_sequence.py",
]

passed = 0
failed = 0
total_start = time.perf_counter()

print("=" * 70)
print("HEATSENSE HOST UNIT TEST SUITE (ZERO-DEPENDENCY RUNNER)")
print("=" * 70)

for test_path in test_files:
    if not test_path.is_file():
        print(f"[-] Warning: Test file not found: {test_path.name}")
        continue

    module_name = f"tests.{test_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, str(test_path))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"[FAIL] Error loading module {test_path.name}: {e}")
        failed += 1
        continue

    # Find test functions
    test_funcs = [
        (name, func) for name, func in inspect.getmembers(mod, inspect.isfunction)
        if name.startswith("test_")
    ]

    for name, func in test_funcs:
        t0 = time.perf_counter()
        try:
            func()
            elapsed_ms = (time.perf_counter() - t0) * 1000
            print(f"  [PASS] {test_path.stem}::{name} ({elapsed_ms:.1f} ms)")
            passed += 1
        except Exception as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            print(f"  [FAIL] {test_path.stem}::{name} ({elapsed_ms:.1f} ms): {e}")
            failed += 1

total_elapsed = time.perf_counter() - total_start
print("=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed in {total_elapsed:.2f}s")
print("=" * 70)

if failed > 0:
    sys.exit(1)
sys.exit(0)
