"""MCP server for MicroPython boards via mpremote serial transport."""

import logging
import os
import stat
import sys
import time

import serial.tools.list_ports
from fastmcp import FastMCP
from mpremote.transport_serial import SerialTransport
from mpremote.transport import TransportError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("mpremote-mcp")

mcp = FastMCP(
    "micropython",
    instructions="Interact with a MicroPython board over serial. "
    "Use exec to run code, list_files/read_file/write_file for filesystem ops, "
    "device_info for board details, soft_reset to reset the board.",
)

MPY_PORT = os.environ.get("MPY_PORT")
MPY_BAUD = int(os.environ.get("MPY_BAUD", "115200"))


def _find_device() -> str:
    """Find MicroPython device: explicit port > auto-detect first USB serial."""
    if MPY_PORT:
        return MPY_PORT
    for p in sorted(serial.tools.list_ports.comports()):
        if p.vid is not None and p.pid is not None:
            log.info("Auto-detected device on %s (VID=0x%04X)", p.device, p.vid)
            return p.device
    raise RuntimeError("No MicroPython device found. Set MPY_PORT or connect a device.")


def _open(soft_reset=False) -> SerialTransport:
    """Open serial connection and enter raw REPL."""
    port = _find_device()
    t = SerialTransport(port, baudrate=MPY_BAUD)
    t.enter_raw_repl(soft_reset=soft_reset)
    return t


def _close(t: SerialTransport):
    """Exit raw REPL and close serial connection."""
    try:
        t.exit_raw_repl()
    except Exception:
        pass
    t.close()


@mcp.tool()
def exec(code: str, timeout: int = 30) -> str:
    """Execute MicroPython code on the board and return stdout.

    Args:
        code: Python code to execute on the device.
        timeout: Timeout in seconds waiting for output (default 30).
    """
    t = _open()
    try:
        t.exec_raw_no_follow(code)
        ret, ret_err = t.follow(timeout=timeout)
        if ret_err:
            from mpremote.transport import TransportExecError
            raise TransportExecError(ret, ret_err.decode())
        return ret.decode(errors="replace")
    finally:
        _close(t)


@mcp.tool()
def enter_bootloader() -> str:
    """Reset the board into USB bootloader mode for flashing."""
    port = _find_device()
    try:
        t = SerialTransport(port, baudrate=MPY_BAUD)
        t.enter_raw_repl(soft_reset=False)
        try:
            t.exec_raw_no_follow("import machine; machine.bootloader()")
            time.sleep(0.5)
        except Exception:
            pass
        try:
            t.close()
        except Exception:
            pass
    except Exception as e:
        log.info("enter_bootloader serial exception (expected): %s", e)
    return "Board entering bootloader mode. USB disconnected. Ready for flashing."


@mcp.tool()
def soft_reset() -> str:
    """Soft-reset the MicroPython board (equivalent to Ctrl-D)."""
    t = _open(soft_reset=True)
    try:
        result = t.exec("print('reset ok')")
        return result.decode(errors="replace")
    finally:
        _close(t)


@mcp.tool()
def list_files(path: str = "/") -> str:
    """List files and directories on the device filesystem.

    Args:
        path: Directory path to list (default: root "/").
    """
    t = _open()
    try:
        entries = t.fs_listdir(path)
        lines = []
        for entry in entries:
            name = entry[0]
            mode = entry[1]
            size = entry[3]
            kind = "dir" if stat.S_ISDIR(mode) else "file"
            lines.append(f"{kind:4s}  {size:>8d}  {name}")
        return "\n".join(lines) if lines else "(empty)"
    finally:
        _close(t)


@mcp.tool()
def read_file(path: str) -> bytes:
    """Read a file from the device filesystem.

    Args:
        path: File path on the device (e.g. "/main.py").
    """
    t = _open()
    try:
        return t.fs_readfile(path)
    finally:
        _close(t)


@mcp.tool()
def write_file(path: str, content: bytes) -> str:
    """Write content to a file on the device filesystem.

    Args:
        path: Destination file path on the device (e.g. "/main.py").
        content: File content to write.
    """
    t = _open()
    try:
        t.fs_writefile(path, content)
        return f"Wrote {len(content)} bytes to {path}"
    finally:
        _close(t)


@mcp.tool()
def device_info() -> str:
    """Get board name, MicroPython version, and memory info."""
    code = """\
import sys, os, gc
gc.collect()
print("platform:", sys.platform)
print("version:", sys.version)
print("implementation:", sys.implementation)
uname = os.uname()
print("machine:", uname.machine)
print("sysname:", uname.sysname)
print("release:", uname.release)
gc.collect()
print("mem_free:", gc.mem_free())
print("mem_alloc:", gc.mem_alloc())
"""
    t = _open()
    try:
        result = t.exec(code)
        return result.decode(errors="replace")
    finally:
        _close(t)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
