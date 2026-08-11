#!/usr/bin/env python3
"""Run the mandatory repository and maintained secret-scanner release gate."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate repository content, then scan the worktree and complete Git history "
            "with Gitleaks."
        )
    )
    parser.add_argument(
        "--gitleaks",
        default=os.environ.get("GITLEAKS") or shutil.which("gitleaks"),
        help="path to the Gitleaks executable (or set GITLEAKS)",
    )
    return parser.parse_args()


def run(command: list[str], timeout: int) -> int:
    try:
        result = subprocess.run(command, cwd=ROOT, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"Release check timed out: {' '.join(command)}", file=sys.stderr)
        return 2
    if result.returncode:
        print(
            f"Release check failed with status {result.returncode}: {' '.join(command)}",
            file=sys.stderr,
        )
    return result.returncode


def main() -> int:
    args = parse_args()
    if not args.gitleaks:
        print(
            "Gitleaks is required for release validation; install it or pass --gitleaks PATH.",
            file=sys.stderr,
        )
        return 2

    gitleaks = Path(args.gitleaks).expanduser()
    if not gitleaks.is_file() or not os.access(gitleaks, os.X_OK):
        print(f"Gitleaks executable is unavailable: {gitleaks}", file=sys.stderr)
        return 2

    commands = (
        ([sys.executable, "tests/validate-repository.py"], 120),
        (
            [
                str(gitleaks),
                "dir",
                "--no-banner",
                "--redact",
                "--exit-code",
                "1",
                ".",
            ],
            180,
        ),
        (
            [
                str(gitleaks),
                "git",
                "--no-banner",
                "--redact",
                "--exit-code",
                "1",
                ".",
            ],
            180,
        ),
    )
    for command, timeout in commands:
        if run(command, timeout):
            return 1

    print("Release security gate passed: repository, worktree and Git history checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
