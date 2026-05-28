# Codex Heartbeat Marketplace

This repository is shaped for installation through the Codex plugin UI.

It contains one plugin:

- `codex-heartbeat`: safe recurring project check-ins with `HEARTBEAT.codex.md` contracts, bounded task prompts, validators, and idle `HEARTBEAT_OK` responses.

## Install In Codex UI

1. Open Codex.
2. Open Settings.
3. Go to Plugins.
4. Add a marketplace from this GitHub repository URL.
5. Find `Codex Heartbeat`.
6. Click Install or Enable.
7. Start a new Codex thread and ask:

```text
Set up heartbeats for this repo.
```

Codex discovers the plugin through:

```text
.agents/plugins/marketplace.json
```

The marketplace entry points to:

```text
plugins/codex-heartbeat
```

## Install With Codex CLI

If the UI asks you to add the marketplace manually, clone this repository and register its marketplace root:

```bash
git clone https://github.com/<owner>/codex-heartbeat-plugin.git
cd codex-heartbeat-plugin
codex plugin marketplace add .
codex plugin add codex-heartbeat@codex-heartbeat-marketplace
```

Then start a new Codex thread so the plugin skills are loaded.

## Plugin Contents

- `plugins/codex-heartbeat/.codex-plugin/plugin.json`: plugin manifest
- `plugins/codex-heartbeat/skills/project-heartbeat/SKILL.md`: Codex workflow instructions
- `plugins/codex-heartbeat/scripts/render_heartbeats.py`: renderer for `HEARTBEAT.codex.md`
- `plugins/codex-heartbeat/examples/codex-heartbeat.config.example.json`: starter config

## Quick Use

Create `codex-heartbeat.config.json` in the workspace you want to manage, then render heartbeat files:

```bash
python3 plugins/codex-heartbeat/scripts/render_heartbeats.py --config codex-heartbeat.config.json
```

Ask Codex:

```text
Use project-heartbeat to create Codex automations for the projects in codex-heartbeat.config.json.
```

## Safety Notes

- Keep heartbeat tasks small.
- Do not put secrets in heartbeat files.
- Do not let recurring runs commit, push, deploy, or delete data unless the user has explicitly granted that authority.
- Treat `HEARTBEAT_OK` as the quiet idle response.
