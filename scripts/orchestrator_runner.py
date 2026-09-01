#!/usr/bin/env python3
"""Run CI/CD readiness checks for the AI Expense Advisor project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_DOCUMENTS = (
    "requirements.md",
    "architecture.md",
    "design-review.md",
    "impl-plan.md",
    "pr.md",
    "executive-summary.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check deliverables, run tests, and log agentic workflow state."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root directory (defaults to the repository root).",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path(".agentic-workflow-state.json"),
        help="JSON file receiving the execution state.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest and mark the test check as skipped.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_path(path: Path, project_root: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def check_deliverables(project_root: Path) -> dict[str, Any]:
    docs_dir = project_root / "docs"
    documents = {
        name: (docs_dir / name).is_file() for name in REQUIRED_DOCUMENTS
    }
    missing = [name for name, exists in documents.items() if not exists]
    return {
        "status": "passed" if not missing else "failed",
        "required": list(REQUIRED_DOCUMENTS),
        "documents": documents,
        "missing": missing,
    }


def run_tests(project_root: Path, skipped: bool) -> dict[str, Any]:
    if skipped:
        return {"status": "skipped", "command": ["pytest", "-q"]}

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "command": [sys.executable, "-m", "pytest", "-q"],
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def write_state(state_file: Path, state: dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    state_file = resolve_path(args.state_file, project_root)
    started_at = utc_now()

    state: dict[str, Any] = {
        "workflow": "AI Expense Advisor CI/CD Orchestrator",
        "status": "running",
        "started_at": started_at,
        "project_root": str(project_root),
    }

    try:
        deliverables = check_deliverables(project_root)
        tests = run_tests(project_root, args.skip_tests)
        state["checks"] = {"deliverables": deliverables, "tests": tests}
        state["status"] = (
            "passed"
            if deliverables["status"] == "passed"
            and tests["status"] in {"passed", "skipped"}
            else "failed"
        )
        return_code = 0 if state["status"] == "passed" else 1
    except (OSError, subprocess.SubprocessError) as exc:
        state["status"] = "failed"
        state["error"] = str(exc)
        return_code = 1
    finally:
        state["finished_at"] = utc_now()
        write_state(state_file, state)

    print(json.dumps(state, indent=2))
    print(f"Execution state logged to {state_file}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
