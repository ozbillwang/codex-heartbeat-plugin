# Codex Heartbeat

A small Codex plugin for keeping several projects or sub-projects moving through safe recurring check-ins.

It borrows the useful part of OpenClaw heartbeat: tiny `HEARTBEAT.md`-style checklists, per-task intervals, an idle ack (`HEARTBEAT_OK`), and strict stop rules. Codex automations provide the wake-up schedule; this plugin provides the repeatable project contract and setup workflow.

## What It Includes

- `skills/project-heartbeat/SKILL.md`: Codex instructions for creating and running project heartbeats.
- `scripts/render_heartbeats.py`: renders `HEARTBEAT.codex.md` files from a JSON config.
- `.codex-plugin/plugin.json`: Codex plugin manifest.

## Quick Start

Create `codex-heartbeat.config.json` in the workspace you want to manage. A generic starter is available at `examples/codex-heartbeat.config.example.json`:

```json
{
  "defaults": {
    "cadence": "30m",
    "ack": "HEARTBEAT_OK",
    "validators": ["npm test"],
    "stopIf": [
      "Secrets, credentials, production data, billing, or destructive actions are required.",
      "The same validator fails twice for the same reason.",
      "The next step depends on a product or architecture decision."
    ]
  },
  "projects": [
    {
      "name": "main-project",
      "path": ".",
      "cadence": "30m",
      "tasks": [
        {
          "name": "continue-next-safe-task",
          "interval": "30m",
          "prompt": "Review the local task list and advance one small safe task. Run the narrowest relevant validator."
        }
      ]
    },
    {
      "name": "docs",
      "path": "docs",
      "cadence": "2h",
      "validators": ["npm run lint:docs"],
      "tasks": [
        {
          "name": "docs-maintenance",
          "interval": "2h",
          "prompt": "Improve or verify one stale documentation item. Keep edits small and cite the source file."
        }
      ]
    }
  ]
}
```

Render heartbeat files from a workspace that has this plugin checked out under `plugins/codex-heartbeat`:

```bash
python3 plugins/codex-heartbeat/scripts/render_heartbeats.py --config codex-heartbeat.config.json
```

Ask Codex:

```text
Use project-heartbeat to create Codex automations for the projects in codex-heartbeat.config.json.
```

For multiple independent projects, use cron automations with each project path as the workspace. For continuing the current conversation, use a Codex heartbeat automation.

## Automation Prompt Shape

```text
In <project path>, read HEARTBEAT.codex.md and follow it strictly. Work on at most one due safe task. Run the listed validator when code changes. If nothing is due, reply HEARTBEAT_OK. If blocked, ask one concise question and stop.
```

## Publishing To GitHub

Publish this folder as a Codex plugin repository, or keep it under a larger repo and point your marketplace entry at the folder that contains `.codex-plugin/plugin.json`.

Required plugin entry point:

```text
.codex-plugin/plugin.json
```

For local marketplace testing from a larger repo, create an entry that points to this plugin folder.

## Safety Notes

- Keep heartbeat tasks small.
- Do not put secrets in heartbeat files.
- Do not let recurring runs commit, push, deploy, or delete data unless the user has explicitly granted that authority.
- Treat `HEARTBEAT_OK` as the quiet idle response.
