# mpremote-mcp

MCP server for MicroPython boards via [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html).

## Install

```bash
uvx mpremote-mcp
```

Or:

```bash
pip install mpremote-mcp
mpremote-mcp
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MPY_PORT` | auto-detect | Serial port override (e.g. `COM3`, `/dev/ttyACM0`) |
| `MPY_BAUD` | `115200` | Baud rate |

Auto-detection connects to the first USB serial device found.

### MCP client config example

```json
{
  "mcpServers": {
    "micropython": {
      "command": "uvx",
      "args": ["mpremote-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `exec` | Execute MicroPython code via raw REPL |
| `eval` | Evaluate an expression and return result |
| `run` | Run a local .py file on device from RAM |
| `device_info` | Board name, MicroPython version, memory info |
| `list_files` | List files/directories on device |
| `read_file` | Read file from device |
| `write_file` | Write file to device |
| `mkdir` | Create directory |
| `rmdir` | Remove directory |
| `rm` | Remove file |
| `touch` | Create empty file |
| `df` | Filesystem storage stats |
| `mip_install` | Install MicroPython package |
| `rtc_get` | Read device real-time clock |
| `rtc_set` | Sync device RTC to host time |
| `soft_reset` | Soft-reset (Ctrl-D equivalent) |
| `hard_reset` | Hard reset (machine.reset()) |
| `enter_bootloader` | Enter USB bootloader for flashing |
