#!/usr/bin/env python3
"""Synchronize project documentation to Confluence.

Environment variables required:
- CONFLUENCE_BASE_URL: Base Confluence URL, e.g. https://yourcompany.atlassian.net/wiki
- CONFLUENCE_USER_EMAIL: Atlassian account email used for basic auth
- CONFLUENCE_API_TOKEN: Atlassian API token for the account
- CONFLUENCE_SPACE_KEY: Confluence space key, e.g. ENG

Example:
    $env:CONFLUENCE_BASE_URL = "https://yourcompany.atlassian.net/wiki"
    $env:CONFLUENCE_USER_EMAIL = "you@example.com"
    $env:CONFLUENCE_API_TOKEN = "your-api-token"
    $env:CONFLUENCE_SPACE_KEY = "ENG"
    python scripts/confluence_sync.py --mode all
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests


REPORT_FILES = (
    "architecture.md",
    "design-review.md",
    "executive-summary.md",
    "impl-plan.md",
    "pr.md",
    "requirements.md",
    "test-report.md",
)


class ConfluenceSyncError(RuntimeError):
    """Raised when Confluence synchronization fails."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def get_required_env() -> Dict[str, str]:
    config = {
        "CONFLUENCE_BASE_URL": os.getenv("CONFLUENCE_BASE_URL", "").strip(),
        "CONFLUENCE_USER_EMAIL": os.getenv("CONFLUENCE_USER_EMAIL", "").strip(),
        "CONFLUENCE_API_TOKEN": os.getenv("CONFLUENCE_API_TOKEN", "").strip(),
        "CONFLUENCE_SPACE_KEY": os.getenv("CONFLUENCE_SPACE_KEY", "").strip(),
    }

    missing = [key for key, value in config.items() if not value]
    if missing:
        raise ConfluenceSyncError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return config


def build_session(email: str, token: str) -> requests.Session:
    session = requests.Session()
    session.auth = (email, token)
    session.headers.update({"Accept": "application/json"})
    return session


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    try:
        response = session.request(
            method=method,
            url=url,
            json=payload,
            params=params,
            timeout=30,
        )
    except requests.RequestException as exc:  # pragma: no cover - exercised at runtime
        raise ConfluenceSyncError(f"Confluence request failed for {method} {url}: {exc}") from exc

    if response.status_code >= 400:
        detail = " ".join(response.text.split())[:500] or "No response body"
        raise ConfluenceSyncError(
            f"Confluence request returned HTTP {response.status_code} for {method} {url}: {detail}",
            status_code=response.status_code,
        )

    if not response.content:
        return {}

    try:
        return response.json()
    except ValueError as exc:
        raise ConfluenceSyncError(
            "Confluence returned a non-JSON response "
            f"for {method} {url} (HTTP {response.status_code}); "
            "check the base URL, credentials, and API permissions."
        ) from exc


def markdown_to_storage_html(markdown_text: str) -> str:
    """Convert basic Markdown to Confluence Storage Format HTML."""
    lines = markdown_text.splitlines()
    html_lines: List[str] = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            close_list()
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading_match:
            close_list()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            html_lines.append(f"<h{level}>{html.escape(heading_text)}</h{level}>")
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)$", line)
        if bullet_match:
            bullet_text = bullet_match.group(1).strip()
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{html.escape(bullet_text)}</li>")
            continue

        close_list()
        html_lines.append(f"<p>{html.escape(line.strip())}</p>")

    close_list()
    return "\n".join(html_lines)


def get_page_by_title(
    session: requests.Session,
    base_url: str,
    space_key: str,
    title: str,
) -> Optional[Dict[str, Any]]:
    endpoint = f"{base_url.rstrip('/')}/rest/api/content"
    params = {
        "spaceKey": space_key,
        "title": title,
        "expand": "version,body.storage,ancestors",
        "limit": 1,
    }

    try:
        data = request_json(session, "GET", endpoint, params=params)
    except ConfluenceSyncError as exc:
        if exc.status_code == 404:
            print(
                f"Warning: Confluence page lookup returned 404 for '{title}'; "
                "the page will be created if possible.",
                file=sys.stderr,
            )
            return None
        raise

    results = data.get("results", [])
    if not results:
        return None

    return results[0]


def ensure_parent_page(
    session: requests.Session,
    base_url: str,
    space_key: str,
    parent_title: str,
) -> str:
    parent_page = get_page_by_title(session, base_url, space_key, parent_title)
    if parent_page:
        return str(parent_page["id"])

    payload = {
        "type": "page",
        "title": parent_title,
        "space": {"key": space_key},
        "body": {"storage": {"representation": "storage", "value": "<p>Project documentation</p>"}},
    }
    data = request_json(session, "POST", f"{base_url.rstrip('/')}/rest/api/content", payload=payload)
    return str(data["id"])


def build_page_payload(title: str, html_body: str, space_key: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"representation": "storage", "value": html_body}},
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]
    return payload


def create_or_update_page(
    session: requests.Session,
    base_url: str,
    space_key: str,
    title: str,
    markdown_content: str,
    parent_title: Optional[str] = None,
) -> Dict[str, Any]:
    page = get_page_by_title(session, base_url, space_key, title)

    if parent_title:
        parent_id = ensure_parent_page(session, base_url, space_key, parent_title)
    else:
        parent_id = None

    html_body = markdown_to_storage_html(markdown_content)

    if page:
        page_id = str(page["id"])
        version_number = int(page.get("version", {}).get("number", 0)) + 1
        payload = build_page_payload(title, html_body, space_key, parent_id=parent_id)
        payload["id"] = page_id
        payload["version"] = {"number": version_number}
        data = request_json(
            session,
            "PUT",
            f"{base_url.rstrip('/')}/rest/api/content/{page_id}",
            payload=payload,
        )
        return data

    payload = build_page_payload(title, html_body, space_key, parent_id=parent_id)
    data = request_json(session, "POST", f"{base_url.rstrip('/')}/rest/api/content", payload=payload)
    return data


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfluenceSyncError(f"Required file not found: {path}") from exc


def sync_requirements_page(session: requests.Session, base_url: str, space_key: str) -> str:
    requirements_path = Path("docs/requirements.md")
    content = read_file(requirements_path)
    page = create_or_update_page(
        session=session,
        base_url=base_url,
        space_key=space_key,
        title="AI Expense Advisor Requirements",
        markdown_content=content,
        parent_title="AI Expense Advisor Project Docs",
    )
    return page.get("title", "AI Expense Advisor Requirements")


def sync_execution_reports(session: requests.Session, base_url: str, space_key: str) -> List[str]:
    docs_dir = Path("docs")
    if not docs_dir.exists():
        raise ConfluenceSyncError("Docs directory not found: docs")

    synced_titles: List[str] = []
    report_files = [docs_dir / filename for filename in REPORT_FILES]
    for path in report_files:
        if not path.is_file():
            raise ConfluenceSyncError(f"Required report file not found: {path}")

        stem = path.stem
        title = " ".join(part.capitalize() for part in re.split(r"[-_\s]+", stem) if part)

        if stem.lower() == "requirements":
            title = "AI Expense Advisor Requirements"
        elif stem.lower() == "pr":
            title = "AI Expense Advisor Pull Request"
        elif stem.lower() == "impl-plan":
            title = "AI Expense Advisor Implementation Plan"
        elif stem.lower() == "design-review":
            title = "AI Expense Advisor Design Review"
        elif stem.lower() == "executive-summary":
            title = "Executive Summary"
        elif stem.lower() == "architecture":
            title = "Architecture"
        elif stem.lower() == "test-report":
            title = "AI Expense Advisor Test Execution Report"

        body = read_file(path)
        page = create_or_update_page(
            session=session,
            base_url=base_url,
            space_key=space_key,
            title=title,
            markdown_content=body,
            parent_title="AI Expense Advisor Project Docs",
        )
        synced_titles.append(page.get("title", title))

    return synced_titles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync project documentation to Confluence.")
    parser.add_argument(
        "--mode",
        choices=["requirements", "reports", "all"],
        default="all",
        help="Which documentation set to publish.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        config = get_required_env()
        base_url = config["CONFLUENCE_BASE_URL"]
        space_key = config["CONFLUENCE_SPACE_KEY"]
        session = build_session(config["CONFLUENCE_USER_EMAIL"], config["CONFLUENCE_API_TOKEN"])

        if args.mode in {"requirements", "all"}:
            title = sync_requirements_page(session, base_url, space_key)
            print(f"Requirements page synced: {title}")

        if args.mode in {"reports", "all"}:
            titles = sync_execution_reports(session, base_url, space_key)
            if titles:
                print("Report pages synced:")
                for title in titles:
                    print(f"- {title}")

        return 0

    except ConfluenceSyncError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - final safety net
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
