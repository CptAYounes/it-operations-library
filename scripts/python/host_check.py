#!/usr/bin/env python3
"""Resolve a host and perform one bounded ICMP reachability check."""

from __future__ import annotations

import argparse
import platform
import shutil
import socket
import subprocess
import sys


def positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc
    if not 0.2 <= timeout <= 30:
        raise argparse.ArgumentTypeError("timeout must be between 0.2 and 30 seconds")
    return timeout


def resolve(host: str, family: int) -> list[str]:
    records = socket.getaddrinfo(host, None, family, socket.SOCK_STREAM)
    return list(dict.fromkeys(str(record[4][0]) for record in records))


def ping_command(address: str, timeout: float, ipv6: bool) -> list[str]:
    system = platform.system()
    if system == "Windows":
        command = ["ping", "-n", "1", "-w", str(round(timeout * 1000))]
        if ipv6:
            command.append("-6")
    else:
        command = ["ping", "-n", "-c", "1", "-W", str(max(1, round(timeout)))]
        if ipv6:
            command.append("-6")
    return [*command, address]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve a host and make one bounded ICMP reachability check."
    )
    parser.add_argument("host", help="DNS name or IP address to check")
    parser.add_argument(
        "--timeout",
        type=positive_timeout,
        default=2.0,
        help="ICMP timeout in seconds (default: 2)",
    )
    parser.add_argument(
        "--ipv6", action="store_true", help="resolve and check an IPv6 address"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    family = socket.AF_INET6 if args.ipv6 else socket.AF_INET

    try:
        addresses = resolve(args.host, family)
    except socket.gaierror as exc:
        print(f"Error: could not resolve {args.host}: {exc}", file=sys.stderr)
        return 1

    if not addresses:
        print(f"Error: no matching address found for {args.host}", file=sys.stderr)
        return 1

    print(f"Host: {args.host}")
    print(f"Resolved address: {addresses[0]}")

    if shutil.which("ping") is None:
        print("Error: ping command is not available", file=sys.stderr)
        return 2

    command = ping_command(addresses[0], args.timeout, args.ipv6)
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=args.timeout + 2,
        )
    except subprocess.TimeoutExpired:
        print(f"ICMP: command exceeded {args.timeout + 2:.1f}s")
        print("Status: warning")
        return 1
    except OSError as exc:
        print(f"Error: could not run ping: {exc}", file=sys.stderr)
        return 2

    if result.returncode == 0:
        print("ICMP: reply received")
        print("Status: reachable")
        return 0

    print("ICMP: no reply received")
    print("Status: warning (ICMP may be filtered)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
