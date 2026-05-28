#!/usr/bin/env python3
"""Render project HEARTBEAT.codex.md files from codex-heartbeat.config.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit("Config root must be a JSON object.")
    if not isinstance(data.get("projects"), list) or not data["projects"]:
        raise SystemExit("Config must include a non-empty projects array.")
    return data


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise SystemExit("Expected a string or list of strings.")


def render_project(project: dict[str, Any], defaults: dict[str, Any]) -> str:
    name = require_str(project, "name")
    cadence = project.get("cadence", defaults.get("cadence", "30m"))
    ack = defaults.get("ack", "HEARTBEAT_OK")
    tasks = project.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise SystemExit(f"Project {name} must include a non-empty tasks array.")

    lines = [
        f"# Heartbeat: {name}",
        "",
        "Read this file during recurring Codex heartbeat or cron automation runs.",
        "Work on at most one due safe task per run.",
        "",
        f"- Cadence: {cadence}",
        f"- Ack when idle: `{ack}`",
    ]

    validators = as_list(project.get("validators", defaults.get("validators")))
    if validators:
        lines += ["", "## Validators", ""]
        lines += [f"- `{item}`" for item in validators]

    stop_if = as_list(project.get("stopIf", defaults.get("stopIf")))
    if stop_if:
        lines += ["", "## Stop And Ask", ""]
        lines += [f"- {item}" for item in stop_if]

    lines += ["", "## Tasks", "", "tasks:", ""]
    for task in tasks:
        if not isinstance(task, dict):
            raise SystemExit(f"Project {name} has a task that is not an object.")
        task_name = require_str(task, "name")
        interval = task.get("interval", cadence)
        prompt = require_str(task, "prompt")
        lines += [
            f"- name: {task_name}",
            f"  interval: {interval}",
            f"  prompt: {json.dumps(prompt)}",
        ]

    lines += [
        "",
        "## Completion Contract",
        "",
        f"- If nothing is due or no action is needed, reply `{ack}`.",
        "- If work is done, report changed files, validation, and the next safe step.",
        "- If blocked, ask one concise question and stop.",
        "",
    ]
    return "\n".join(lines)


def require_str(obj: dict[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Missing required string field: {key}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="codex-heartbeat.config.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    root = config_path.parent
    config = load_config(config_path)
    defaults = config.get("defaults", {})
    if not isinstance(defaults, dict):
        raise SystemExit("defaults must be an object when present.")

    summary: list[str] = []
    for project in config["projects"]:
        if not isinstance(project, dict):
            raise SystemExit("Each project must be an object.")
        name = require_str(project, "name")
        rel_path = require_str(project, "path")
        project_dir = (root / rel_path).resolve()
        try:
            project_dir.relative_to(root)
        except ValueError as exc:
            raise SystemExit(f"Project {name} path escapes config root: {rel_path}") from exc
        if not project_dir.exists():
            raise SystemExit(f"Project {name} path does not exist: {project_dir}")

        heartbeat_path = project_dir / "HEARTBEAT.codex.md"
        content = render_project(project, defaults)
        summary.append(f"{name}: {heartbeat_path}")
        if not args.dry_run:
            heartbeat_path.write_text(content, encoding="utf-8")

    mode = "Would write" if args.dry_run else "Wrote"
    print(f"{mode} {len(summary)} heartbeat file(s):")
    for item in summary:
        print(f"- {item}")


if __name__ == "__main__":
    main()
