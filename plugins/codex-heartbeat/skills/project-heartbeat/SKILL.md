---
name: project-heartbeat
description: Use when the user wants Codex to set up, review, or maintain recurring heartbeat-style work across one or more projects, repositories, or sub-project folders. This skill creates small HEARTBEAT.codex.md files, bounded automation prompts, and safe continuation rules inspired by OpenClaw heartbeat checklists.
---

# Project Heartbeat

Use this skill to help Codex keep multiple projects moving through short, bounded, recurring check-ins.

## Core Idea

A project heartbeat is not permission to work forever. It is a tiny operating contract that tells a future Codex run:

- what project or sub-project to inspect
- what tasks are eligible now
- what validation must be run before reporting progress
- when to stop and ask the user
- what to say when nothing needs attention

Prefer a plugin-backed heartbeat when the user wants reusable project configuration. Prefer a one-off Codex reminder or thread heartbeat when the user only wants this conversation to wake up later.

## Workflow

1. Find the scope.
   - Identify project roots and sub-project folders.
   - Look for existing `HEARTBEAT.codex.md`, `codex-heartbeat.config.json`, `AGENTS.md`, `README.md`, `package.json`, `pyproject.toml`, and task files.
   - Do not include generated folders, dependency folders, or secrets directories.

2. Write or update `codex-heartbeat.config.json`.
   - Keep one `projects[]` entry per project or sub-project.
   - Each entry needs `name`, `path`, `cadence`, and `tasks`.
   - Use short task prompts with concrete validators.
   - Add `stopIf` rules for secrets, destructive actions, external credentials, repeated failures, unclear ownership, or required product decisions.

3. Render heartbeat files.
   - Run `python3 plugins/codex-heartbeat/scripts/render_heartbeats.py --config codex-heartbeat.config.json` from the workspace root when the plugin lives in `plugins/codex-heartbeat`.
   - If the plugin is installed elsewhere, run the same script from that plugin path and pass the config file explicitly.
   - Review generated `HEARTBEAT.codex.md` files before creating automations.

4. Create or update Codex automations when the user asks for recurring execution.
   - For work across several workspaces, prefer cron automations with each project path as the workspace directory.
   - For continuing the current local thread, use a Codex heartbeat automation attached to the thread.
   - The automation prompt should instruct Codex to read that project’s `HEARTBEAT.codex.md`, do only due safe work, run validators, and respond `HEARTBEAT_OK` when nothing needs attention.

5. Keep runs bounded.
   - One heartbeat should normally finish one small task or produce one clear blocked status.
   - Do not commit, push, deploy, delete data, rotate credentials, or contact external services unless the heartbeat file explicitly allows it and the user has already granted the necessary authority.
   - If a validator fails twice for the same reason, stop and ask.

## Response Contract

When nothing is due or nothing needs attention, reply with:

```text
HEARTBEAT_OK
```

When work was done, report:

- project name
- task completed or advanced
- files changed
- validation run and result
- next eligible task or blocker

When blocked, ask one concise question and include the exact missing input.

## Suggested Config

```json
{
  "defaults": {
    "cadence": "30m",
    "ack": "HEARTBEAT_OK",
    "stopIf": [
      "Secrets, credentials, production data, billing, or destructive actions are required.",
      "The same validator fails twice for the same reason.",
      "The next step depends on a product or architecture decision."
    ]
  },
  "projects": [
    {
      "name": "main-app",
      "path": ".",
      "cadence": "30m",
      "tasks": [
        {
          "name": "continue-next-safe-task",
          "interval": "30m",
          "prompt": "Review the local task list and advance one small safe task. Run the narrowest relevant validator."
        }
      ]
    }
  ]
}
```

## Automation Prompt Template

Use this shape for each project automation:

```text
In <project path>, read HEARTBEAT.codex.md and follow it strictly. Work on at most one due safe task. Run the listed validator when code changes. If nothing is due, reply HEARTBEAT_OK. If blocked, ask one concise question and stop.
```
