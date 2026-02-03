# core/framework/testing/runner.py

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

from framework.testing.test_result import TestResult, TestSuiteResult
from framework.testing.test_storage import TestStorage


def _stable_test_id(nodeid: str) -> str:

    safe = (
        nodeid.replace(os.sep, "_")
        .replace("::", "__")
        .replace(":", "_")
        .replace("[", "_")
        .replace("]", "_")
        .replace(" ", "_")
    )
    digest = hashlib.sha1(nodeid.encode("utf-8")).hexdigest()[:10]
    return f"{safe}__{digest}"


@dataclass
class _Captured:
    nodeid: str
    outcome: str
    duration_s: float
    longreprtext: Optional[str]


class _PytestCapturePlugin:
    def __init__(self) -> None:
        self.captured: list[_Captured] = []

    def pytest_runtest_logreport(self, report):  # noqa: N802
        # Only record "call" phase (the actual test body)
        if report.when != "call":
            return

        longreprtext = None
        if report.failed:
            # longreprtext is the readable traceback string pytest provides
            longreprtext = getattr(report, "longreprtext", None)

        self.captured.append(
            _Captured(
                nodeid=report.nodeid,
                outcome=report.outcome,  # "passed", "failed", "skipped"
                duration_s=getattr(report, "duration", 0.0) or 0.0,
                longreprtext=longreprtext,
            )
        )


def run_and_record(
    *,
    agent_path: Path,
    goal_id: str,
    test_paths: list[Path],
    fail_fast: bool,
    storage_base: Path,
    pythonpath_root: Path,
) -> tuple[int, TestSuiteResult]:

    storage = TestStorage(storage_base)
    plugin = _PytestCapturePlugin()

    # Build pytest args
    args: list[str] = []
    args.extend([str(p) for p in test_paths])
    args.append("-v")
    args.append("--tb=short")
    if fail_fast:
        args.append("-x")

    # Ensure imports work for agent tests that use framework code
    old_pythonpath = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = f"{pythonpath_root}:{old_pythonpath}".strip(":")

    started = time.time()
    exit_code = pytest.main(args, plugins=[plugin])
    total_ms = int((time.time() - started) * 1000)

    # Convert to TestResult + persist
    passed = failed = errors = skipped = 0
    results: list[TestResult] = []

    for item in plugin.captured:
        duration_ms = int(item.duration_s * 1000)

        is_passed = item.outcome == "passed"
        is_skipped = item.outcome == "skipped"
        is_failed = item.outcome == "failed"

        if is_passed:
            passed += 1
        elif is_skipped:
            skipped += 1
        elif is_failed:
            failed += 1
        else:
            # unexpected outcome; treat as error
            errors += 1

        test_id = _stable_test_id(item.nodeid)

        result = TestResult(
            test_id=test_id,
            passed=is_passed,
            duration_ms=max(duration_ms, 0),
            error_message=None if is_passed or is_skipped else "Test failed",
            stack_trace=None if is_passed or is_skipped else (item.longreprtext or ""),
        )
        storage.save_result(test_id, result)
        results.append(result)

    suite = TestSuiteResult(
        goal_id=goal_id,
        total=len(results),
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
        results=results,
        duration_ms=total_ms,
    )

    return exit_code, suite
