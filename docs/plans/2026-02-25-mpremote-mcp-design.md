# mpremote-mcp Design

## Overview

MCP server exposing MicroPython board interaction via mpremote's SerialTransport.
Published to PyPI as `mpremote-mcp`, runnable via `uvx mpremote-mcp` or `pip install mpremote-mcp`.

## Project Structure

```
mpremote-mcp/
├── mpremote_mcp.py
├── pyproject.toml
├── LICENSE (MIT)
├── .gitignore
└── .github/workflows/
    ├── ci.yml
    └── release.yml
```

Single-module package. Entry point: `mpremote-mcp = "mpremote_mcp:main"`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MPY_PORT` | auto-detect | Serial port override |
| `MPY_BAUD` | `115200` | Baud rate |

Auto-detection uses mpremote's built-in logic (first USB serial device).

## Tools

### Existing (from mcp_micropython.py)

- **exec** — Execute MicroPython code via raw REPL. `timeout: int = 30`.
- **device_info** — Board name, MicroPython version, memory info.
- **soft_reset** — Soft-reset (Ctrl-D equivalent).
- **enter_bootloader** — Enter USB bootloader mode for flashing.
- **list_files** — List files/dirs on device filesystem.
- **read_file** — Read file from device.
- **write_file** — Write file to device.

### New

- **eval** — Evaluate expression, return result. `timeout: int = 30`.
- **run** — Run local .py file on device from RAM. `timeout: int = 30`.
- **mkdir** — Create directory on device.
- **rmdir** — Remove directory on device.
- **rm** — Remove file on device.
- **touch** — Create empty file on device.
- **df** — Storage stats via `os.statvfs('/')`.
- **mip_install** — Install package via `mpremote.mip`.
- **rtc_get** — Read device real-time clock.
- **rtc_set** — Sync device RTC to host time.
- **hard_reset** — Hard reset via `machine.reset()`.

### Connection Pattern

Every tool opens a fresh SerialTransport, enters raw REPL, executes, closes.
No persistent connections.

## GitHub Actions

### ci.yml
- Triggers: push, pull_request, workflow_call
- Runs: ruff check, ruff format --check

### release.yml
- Triggers: push tags `v*`
- Job 1: calls ci.yml
- Job 2 (depends on job 1): build + publish to PyPI via Trusted Publishers (OIDC, no tokens)

## Dependencies

- fastmcp
- mpremote
- pyserial
