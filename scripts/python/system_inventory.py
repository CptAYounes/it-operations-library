#!/usr/bin/env python3
"""Print a privacy-conscious local system inventory."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import shutil
import socket
import sys
from pathlib import Path
from typing import TypedDict


class Inventory(TypedDict):
    hostname: str
    operating_system: str
    release: str
    architecture: str
    logical_cpus: int | None
    memory_bytes: int | None
    disk_path: str
    disk_total_bytes: int
    disk_free_bytes: int


def linux_memory() -> int | None:
    try:
        with Path("/proc/meminfo").open(encoding="ascii") as meminfo:
            for line in meminfo:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def windows_memory() -> int | None:
    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    try:
        windll = getattr(ctypes, "windll", None)
        if windll is not None and windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return int(status.total_physical)
    except (AttributeError, OSError):
        pass
    return None


def total_memory() -> int | None:
    if platform.system() == "Linux":
        return linux_memory()
    if platform.system() == "Windows":
        return windows_memory()
    return None


def human_bytes(value: int | None) -> str:
    if value is None:
        return "unavailable"
    amount = float(value)
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show a local inventory without serial numbers, MAC addresses or IP addresses."
    )
    parser.add_argument(
        "--disk-path",
        default=os.path.abspath(os.sep),
        help="path whose filesystem should be measured (default: system root)",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    disk_path = Path(args.disk_path).expanduser()

    if not disk_path.exists():
        print(f"Error: disk path does not exist: {disk_path}", file=sys.stderr)
        return 1

    try:
        disk = shutil.disk_usage(disk_path)
    except OSError as exc:
        print(f"Error: could not inspect {disk_path}: {exc}", file=sys.stderr)
        return 1

    inventory: Inventory = {
        "hostname": socket.gethostname(),
        "operating_system": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "logical_cpus": os.cpu_count(),
        "memory_bytes": total_memory(),
        "disk_path": str(disk_path),
        "disk_total_bytes": disk.total,
        "disk_free_bytes": disk.free,
    }

    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
        return 0

    print(f"Hostname: {inventory['hostname']}")
    print(f"Operating system: {inventory['operating_system']} {inventory['release']}")
    print(f"Architecture: {inventory['architecture']}")
    print(f"Logical CPUs: {inventory['logical_cpus'] or 'unavailable'}")
    print(f"Physical memory: {human_bytes(inventory['memory_bytes'])}")
    print(f"Disk path: {inventory['disk_path']}")
    print(f"Disk total: {human_bytes(inventory['disk_total_bytes'])}")
    print(f"Disk free: {human_bytes(inventory['disk_free_bytes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
