---
sidebar_position: 5
title: MCP Server
description: Expose every Piyu registry model as Model Context Protocol tools for Cursor, Claude, and tryon-studio
keywords:
  - MCP
  - Model Context Protocol
  - FastMCP
  - Cursor
  - Claude
  - piyu
---

# MCP Server

Piyu ships a [Model Context Protocol](https://modelcontextprotocol.io) server under `mcp-server/`. Every model in `tryon.cli.registry` becomes an MCP tool automatically — the same surface as the `piyu` CLI, via `tryon.cli.runner.invoke_model()`.

**Current release:** works with Piyu **v0.0.3+** (`pip install -U piyu`).

## Why it matters

- Agents in **Cursor**, **Claude Desktop**, or **[tryon-studio](https://github.com/piyu/tryon-studio)** can call try-on, generate, edit, video, understand, and bg-remove tools directly
- New registry models appear as tools with **zero hand-written MCP wrappers**
- CLI and MCP cannot drift — one runner, one registry

## Quick start

```bash
cd mcp-server
pip install -r requirements.txt   # includes fastmcp
cp ../env.template ../.env        # fill API keys you need
python server.py                  # stdio (default for most MCP clients)
# or:
python server.py --transport http --host 127.0.0.1 --port 8000
```

Discovery tools:

- `list_piyu_tools` — list services / models / tool names / env readiness
- `piyu_status` — configuration status report

Every generated tool accepts `dry_run` and `output_dir`, matching the CLI.

## Client config

See example configs in the repo:

- [`mcp-server/examples/cursor_mcp_config.json`](https://github.com/piyu/piyu/blob/main/mcp-server/examples/cursor_mcp_config.json)
- [`mcp-server/examples/claude_desktop_config.json`](https://github.com/piyu/piyu/blob/main/mcp-server/examples/claude_desktop_config.json)

Full tool tables and architecture notes: [`mcp-server/README.md`](https://github.com/piyu/piyu/blob/main/mcp-server/README.md).

## Related

- [Unified CLI](cli)
- [Adding a new model](../advanced/new-model-checklist)
- [Configuration](configuration)
