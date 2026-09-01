#!/usr/bin/env python3
"""Convert a pytest JUnit XML report into a client-friendly Markdown report."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Markdown test execution report.")
    parser.add_argument("--junitxml", type=Path, required=True, help="Pytest JUnit XML input.")
    parser.add_argument("--output", type=Path, required=True, help="Markdown output path.")
    return parser.parse_args()


def markdown_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def test_status(test_case: ET.Element) -> str:
    if test_case.find("failure") is not None or test_case.find("error") is not None:
        return "FAIL"
    if test_case.find("skipped") is not None:
        return "SKIPPED"
    return "PASS"


def generate_report(input_path: Path, output_path: Path) -> None:
    root = ET.parse(input_path).getroot()
    test_cases = list(root.iter("testcase"))
    statuses = [test_status(test_case) for test_case in test_cases]
    passed = statuses.count("PASS")
    failed = statuses.count("FAIL")
    skipped = statuses.count("SKIPPED")

    lines = [
        "# AI Expense Advisor Test Execution Report",
        "",
        "## Executive Summary",
        "",
        f"The automated API validation suite executed **{len(test_cases)} test cases**: "
        f"**{passed} passed**, **{failed} failed**, and **{skipped} skipped**.",
        "",
        "The coverage includes the positive transaction ingestion and retrieval flow, "
        "health validation, malformed payload handling, missing-resource 404 behavior, "
        "and invalid request-parameter handling.",
        "",
        "## Test Results",
        "",
        "| Test case | Class | Status | Duration (s) |",
        "| --- | --- | --- | ---: |",
    ]

    for test_case, status in zip(test_cases, statuses):
        name = markdown_cell(test_case.get("name", "Unnamed test"))
        classname = markdown_cell(test_case.get("classname", ""))
        duration = test_case.get("time", "0")
        lines.append(f"| {name} | {classname} | **{status}** | {duration} |")

    lines.extend(
        [
            "",
            "## Validation Assessment",
            "",
            "The report demonstrates that expected API behavior and negative error-handling "
            "paths are validated individually. Failures remain visible in the generated "
            "JUnit and HTML artifacts, while this Markdown summary is suitable for "
            "Confluence publication.",
            "",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    generate_report(args.junitxml, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())