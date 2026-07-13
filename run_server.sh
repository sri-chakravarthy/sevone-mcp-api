#!/bin/bash
# Launcher script for SevOne MCP server
# Used by Bob MCP config to avoid macOS code-signing issues with venv Python binaries
cd "$(dirname "$0")"
exec ./venv/bin/python3 src/server.py "$@"
