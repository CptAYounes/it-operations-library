#!/usr/bin/env python3
"""Attempt a bounded TCP connection to a host and port."""

from __future__ import annotations

import argparse
import socket
import sys
import threading
import time
from typing import Any


def port_number(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def timeout_value(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc
    if not 0.1 <= timeout <= 30:
        raise argparse.ArgumentTypeError("timeout must be between 0.1 and 30 seconds")
    return timeout


def resolve(host: str, port: int, family: int, timeout: float) -> list[tuple[Any, ...]]:
    addresses: list[tuple[Any, ...]] | None = None
    resolution_error: OSError | None = None
    completed = threading.Event()

    def worker() -> None:
        nonlocal addresses, resolution_error
        try:
            addresses = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)
        except OSError as exc:
            resolution_error = exc
        finally:
            completed.set()

    threading.Thread(target=worker, daemon=True).start()
    if not completed.wait(timeout):
        raise TimeoutError(f"resolution exceeded {timeout:.1f}s")
    if resolution_error is not None:
        raise resolution_error
    return addresses or []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Attempt a TCP connection without sending application data."
    )
    parser.add_argument("host", help="DNS name or IP address")
    parser.add_argument("port", type=port_number, help="TCP port, 1-65535")
    parser.add_argument(
        "--timeout",
        type=timeout_value,
        default=3.0,
        help="overall timeout for resolution and all address attempts (default: 3)",
    )
    parser.add_argument(
        "--family",
        choices=("any", "ipv4", "ipv6"),
        default="any",
        help="address family to use (default: any)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    families = {"any": socket.AF_UNSPEC, "ipv4": socket.AF_INET, "ipv6": socket.AF_INET6}
    deadline = time.monotonic() + args.timeout

    try:
        addresses = resolve(
            args.host,
            args.port,
            families[args.family],
            max(0.0, deadline - time.monotonic()),
        )
    except TimeoutError as exc:
        print(f"Error: could not resolve {args.host}: {exc}", file=sys.stderr)
        return 1
    except socket.gaierror as exc:
        print(f"Error: could not resolve {args.host}: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    seen: set[tuple[int, tuple[object, ...]]] = set()
    unique_addresses: list[tuple[Any, ...]] = []

    for family, socket_type, protocol, _, socket_address in addresses:
        key = (family, socket_address)
        if key in seen:
            continue
        seen.add(key)
        unique_addresses.append(
            (family, socket_type, protocol, "", socket_address)
        )

    for index, (family, socket_type, protocol, _, socket_address) in enumerate(
        unique_addresses
    ):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            errors.append(f"overall timeout of {args.timeout:.1f}s exhausted")
            break
        remaining_candidates = len(unique_addresses) - index
        attempt_timeout = remaining / remaining_candidates

        started = time.monotonic()
        try:
            with socket.socket(family, socket_type, protocol) as connection:
                connection.settimeout(attempt_timeout)
                connection.connect(socket_address)
            elapsed_ms = (time.monotonic() - started) * 1000
            print(f"Host: {args.host}")
            print(f"Port: {args.port}/tcp")
            print(f"Address: {socket_address[0]}")
            print("Result: reachable")
            print(f"Connection time: {elapsed_ms:.1f} ms")
            return 0
        except (OSError, TimeoutError) as exc:
            errors.append(f"{socket_address[0]}: {exc}")

    print(f"Host: {args.host}")
    print(f"Port: {args.port}/tcp")
    print("Result: unreachable")
    if errors:
        print(f"Last error: {errors[-1]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
