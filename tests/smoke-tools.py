#!/usr/bin/env python3
"""Exercise safe success and validation paths for the diagnostic tools."""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"{' '.join(command)} returned {result.returncode}, expected {expected}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def accept_once(listener: socket.socket) -> None:
    connection, _ = listener.accept()
    connection.close()


def test_bash() -> None:
    scripts = sorted((ROOT / "scripts/bash").glob("*.sh"))
    run(["bash", "-n", *(str(script) for script in scripts)])
    run([str(ROOT / "scripts/bash/disk-check.sh"), "--warning", "100", "/"])
    run([str(ROOT / "scripts/bash/system-health.sh"), "--help"])

    if all(shutil.which(command) for command in ("ip", "getent", "ping")):
        run([str(ROOT / "scripts/bash/network-check.sh"), "--timeout", "1", "127.0.0.1"])
    else:
        print("SKIP: Bash network smoke check (ip, getent or ping unavailable)")


def test_python() -> None:
    scripts = ROOT / "scripts/python"
    run([sys.executable, "-m", "compileall", "-q", str(scripts)])

    inventory = run([sys.executable, str(scripts / "system_inventory.py"), "--json"])
    parsed = json.loads(inventory.stdout)
    for required in ("operating_system", "logical_cpus", "disk_total_bytes"):
        if required not in parsed:
            raise AssertionError(f"inventory JSON is missing {required}")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as log_file:
        log_file.write("2026-08-10T08:00:01Z INFO start\n")
        log_file.write("2026-08-10T08:00:02Z WARN delayed\n")
        log_file.write("2026-08-10T08:00:03Z ERROR failed\n")
        log_path = Path(log_file.name)
    try:
        summary = run([sys.executable, str(scripts / "log_summary.py"), str(log_path)])
        for expected_line in ("ERROR: 1", "WARNING: 1", "INFO: 1"):
            if expected_line not in summary.stdout:
                raise AssertionError(f"log summary is missing {expected_line}")
    finally:
        log_path.unlink(missing_ok=True)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    thread = threading.Thread(target=accept_once, args=(listener,), daemon=True)
    thread.start()
    try:
        result = run(
            [
                sys.executable,
                str(scripts / "port_check.py"),
                "--timeout",
                "1",
                "127.0.0.1",
                str(port),
            ]
        )
        if "Result: reachable" not in result.stdout:
            raise AssertionError("TCP smoke check did not report reachable")
    finally:
        listener.close()
        thread.join(timeout=2)

    if shutil.which("ping"):
        run(
            [
                sys.executable,
                str(scripts / "host_check.py"),
                "--timeout",
                "1",
                "127.0.0.1",
            ]
        )
    else:
        print("SKIP: Python host smoke check (ping unavailable)")

    run([sys.executable, str(scripts / "port_check.py"), "127.0.0.1", "70000"], expected=2)


def main() -> int:
    test_bash()
    test_python()
    print("Tool smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
