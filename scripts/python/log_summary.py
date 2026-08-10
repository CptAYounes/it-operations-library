#!/usr/bin/env python3
"""Count common severity labels in a bounded portion of a text log."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

LEVEL_PATTERN = re.compile(r"\b(CRITICAL|FATAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE)\b", re.IGNORECASE)
TIMESTAMP_PATTERNS = (
    re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b"),
    re.compile(r"\b[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b"),
)


def positive_lines(value: str) -> int:
    try:
        lines = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("max-lines must be an integer") from exc
    if not 1 <= lines <= 1_000_000:
        raise argparse.ArgumentTypeError("max-lines must be between 1 and 1000000")
    return lines


def normalise_level(level: str) -> str:
    level = level.upper()
    if level == "FATAL":
        return "CRITICAL"
    if level in {"WARN", "WARNING"}:
        return "WARNING"
    return level


def timestamp_from(line: str) -> str | None:
    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(0)
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarise severity labels without printing log message contents."
    )
    parser.add_argument("log_file", type=Path, help="plain-text log file to inspect")
    parser.add_argument(
        "--max-lines",
        type=positive_lines,
        default=100_000,
        help="maximum number of lines to read from the start (default: 100000)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path: Path = args.log_file

    if not path.is_file():
        print(f"Error: not a readable regular file: {path}", file=sys.stderr)
        return 1

    counts: Counter[str] = Counter()
    lines_read = 0
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    truncated = False

    try:
        with path.open("r", encoding="utf-8", errors="replace") as log_file:
            for line in log_file:
                if lines_read >= args.max_lines:
                    truncated = True
                    break
                lines_read += 1
                for match in LEVEL_PATTERN.finditer(line):
                    counts[normalise_level(match.group(1))] += 1
                timestamp = timestamp_from(line)
                if timestamp:
                    first_timestamp = first_timestamp or timestamp
                    last_timestamp = timestamp
    except OSError as exc:
        print(f"Error: could not read {path}: {exc}", file=sys.stderr)
        return 1

    print(f"File: {path}")
    print(f"Lines read: {lines_read}")
    print(f"Input truncated: {'yes' if truncated else 'no'}")
    print(f"First recognised timestamp: {first_timestamp or 'none'}")
    print(f"Last recognised timestamp: {last_timestamp or 'none'}")
    for level in ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"):
        print(f"{level}: {counts[level]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
