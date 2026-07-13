# SevOne MCP Server — Quick Start Guide

This guide covers setting up the `sevone-api` MCP server locally for use with **IBM Bob Insiders** (stdio transport).

For remote/multi-client deployments over HTTP, see [SSE_SETUP.md](SSE_SETUP.md).

## Prerequisites

- Python 3.10+
- IBM Bob Insiders installed
- SevOne NMS instance with API access and valid credentials

---

## Step 1 — Clone the repository

```bash
git clone <repo-url> ~/sevone-mcp-api
cd ~/sevone-mcp-api
```

> The directory path matters — you will reference it in all steps below. Adjust if you clone elsewhere.

---

## Step 2 — Create the virtual environment and install dependencies

```bash
cd ~/sevone-mcp-api
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

---

## Step 3 — Encrypt your SevOne password

Run the interactive encryption utility:

```bash
venv/bin/python3 scripts/encrypt_password.py
```

Follow the prompts to:
1. Generate a new encryption key (or provide an existing one)
2. Enter your SevOne password

Copy the output values — you will need them in the next step.

---

## Step 4 — Create the `.env` file

Create a `.env` file in the **project root** (same directory as `run_server.sh`):

```bash
SEVONE_HOSTNAME=your-sevone-hostname.com
SEVONE_USERNAME=your-username
SEVONE_PASSWORD_ENCRYPTED=<output from step 3>
SEVONE_ENCRYPTION_KEY=<output from step 3>
SEVONE_VERIFY_SSL=false
LOG_LEVEL=INFO
```

> **Important:** The `.env` file must be in the project root. The server finds it by looking in its working directory at startup.

---

## Step 5 — Make the launcher script executable

```bash
chmod +x ~/sevone-mcp-api/run_server.sh
```

> `run_server.sh` is used as the MCP command instead of calling the venv Python directly. This is required on macOS because IBM Bob (a GUI/Electron app) cannot spawn venv Python binaries that carry an adhoc code signature — they are silently killed before the MCP handshake completes. `/bin/bash` is a system binary Bob can always spawn; the script then sets the correct working directory and invokes the venv Python from within a normal shell context.

---

## Step 6 — Smoke test from the terminal

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | ~/sevone-mcp-api/run_server.sh 2>/dev/null
```

Expected output:
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{...},"serverInfo":{"name":"sevone-api","version":"..."}}}
```

If you see an error instead, check your `.env` file and that the venv was created correctly.

---

## Step 7 — Register in Bob's MCP config

Open `~/.bob/settings/mcp.json` (this is the file Bob Insiders reads — not the `Library/Application Support` paths) and add the `sevone-api` block inside `"mcpServers"`:

```json
{
  "mcpServers": {
    "sevone-api": {
      "type": "stdio",
      "command": "/bin/bash",
      "args": [
        "/Users/<you>/sevone-mcp-api/run_server.sh"
      ]
    }
  }
}
```

- Use `/bin/bash` as the `command`
- Pass the **full absolute path** to `run_server.sh` as the argument
- Do **not** set `cwd` — the script handles that itself

---

## Step 8 — Reload Bob

`Cmd + Shift + P` → **Developer: Reload Window**

The `sevone-api` server should appear as **connected** in the MCP panel.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Shows *disconnected*, log says `Connection closed` in <50ms | Bob cannot spawn the adhoc-signed venv Python binary directly | Ensure the config uses `/bin/bash run_server.sh`, not the Python binary directly |
| `SEVONE_ENCRYPTION_KEY not found` | `.env` missing or not in project root | Verify `.env` exists at the same level as `run_server.sh` |
| Server not listed in Bob at all | Entry missing from `~/.bob/settings/mcp.json` | Add the entry to `~/.bob/settings/mcp.json` (not to the `Library/Application Support` paths) |
| Log file is 0 bytes after reload | Process crashes before writing any output | Run the smoke test in Step 6 to see the real error |
| `Failed to decrypt password` | Wrong encryption key or corrupted encrypted password | Re-run `scripts/encrypt_password.py` and update `.env` |

---

## Key files reference

| File | Purpose |
|---|---|
| `run_server.sh` | Launcher script — sets `cwd` and invokes the venv Python. Always use this as the MCP command. |
| `.env` | Credentials (not committed to git). Must be in project root. |
| `~/.bob/settings/mcp.json` | Bob Insiders MCP registry. This is the file Bob actually reads. |
| `scripts/encrypt_password.py` | Interactive utility to generate the encryption key and encrypted password. |
| `src/server.py` | MCP server entry point. |
| `requirements.txt` | Python dependencies for the venv. |

---

## Next Steps

- Read [README.md](README.md) for full API documentation
- See [SSE_SETUP.md](SSE_SETUP.md) for remote/multi-client HTTP deployment
- Browse [api-docs/](api-docs/) for available SevOne API endpoints
