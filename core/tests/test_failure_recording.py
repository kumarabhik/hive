# core/tests/test_failure_recording.py

from pathlib import Path

from framework.testing.runner import run_and_record
from framework.testing.test_storage import TestStorage


def test_failure_recording_creates_latest_json(tmp_path: Path):
    # Create a fake agent export folder with tests/
    agent_path = tmp_path / "exports" / "my_agent"
    tests_dir = agent_path / "tests"
    tests_dir.mkdir(parents=True)

    # Create a failing pytest test
    (tests_dir / "test_constraints.py").write_text(
        """
def test_constraint_always_fails():
    assert 1 == 2
"""
    )

    storage_base = agent_path / ".hive" / "testing"

    # In the real repo, pythonpath_root should point to project root.
    # In unit tests inside this repo, we can use the repo root by walking up.
    # This file lives under core/tests, so root is two levels up from core/.
    pythonpath_root = Path(__file__).resolve().parents[2]

    exit_code, suite = run_and_record(
        agent_path=agent_path,
        goal_id="goal_123",
        test_paths=[tests_dir],
        fail_fast=False,
        storage_base=storage_base,
        pythonpath_root=pythonpath_root,
    )

    assert exit_code != 0
    assert suite.failed == 1

    # Validate a result exists on disk
    storage = TestStorage(storage_base)

    # Find the test_id from suite results
    test_id = suite.results[0].test_id
    latest = storage.get_latest_result(test_id)

    assert latest is not None
    assert latest.passed is False
    assert latest.stack_trace is not None
    assert len(latest.stack_trace) > 0
