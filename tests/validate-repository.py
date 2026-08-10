#!/usr/bin/env python3
"""Run dependency-free repository structure, Markdown and privacy checks."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORIES = {
    "__pycache__",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vscode",
    "htmlcov",
    "node_modules",
    "output",
    "test-output",
    "venv",
}

EXPECTED_FILES = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "hardware/README.md",
    "hardware/building/pc-build-planning.md",
    "hardware/building/physical-assembly.md",
    "hardware/diagnostics/no-post-troubleshooting.md",
    "hardware/firmware/bios-uefi-configuration.md",
    "hardware/memory/ram-troubleshooting.md",
    "hardware/storage/storage-diagnostics.md",
    "hardware/thermals/cpu-thermal-troubleshooting.md",
    "hardware/diagnostics/power-fault-methodology.md",
    "hardware/diagnostics/fault-isolation.md",
    "windows/README.md",
    "windows/installation/windows-installation-checklist.md",
    "windows/configuration/post-install-configuration.md",
    "windows/configuration/driver-device-validation.md",
    "windows/maintenance/update-patch-validation.md",
    "windows/troubleshooting/boot-troubleshooting.md",
    "windows/event-logs/event-viewer-practical-guide.md",
    "windows/services/service-troubleshooting.md",
    "windows/networking/network-diagnostics.md",
    "windows/storage/storage-filesystem-diagnostics.md",
    "windows/troubleshooting/performance-investigation.md",
    "windows/configuration/powershell-administration-reference.md",
    "windows/troubleshooting/recovery-options.md",
    "linux/README.md",
    "linux/installation/linux-installation-checklist.md",
    "linux/configuration/post-install-configuration.md",
    "linux/configuration/users-groups-permissions.md",
    "linux/configuration/package-management.md",
    "linux/systemd/service-operations.md",
    "linux/logs/journalctl-log-investigation.md",
    "linux/troubleshooting/boot-troubleshooting.md",
    "linux/networking/network-diagnostics.md",
    "linux/storage/disk-filesystem-investigation.md",
    "linux/troubleshooting/performance-investigation.md",
    "linux/configuration/ssh-configuration-troubleshooting.md",
    "linux/networking/firewall-fundamentals.md",
    "linux/maintenance/maintenance-checklist.md",
    "networking/README.md",
    "networking/tcp-ip/practical-reference.md",
    "networking/tcp-ip/ipv4-addressing-subnetting.md",
    "networking/routing/default-gateway-routing.md",
    "networking/dns/dns-troubleshooting.md",
    "networking/dhcp/dhcp-troubleshooting.md",
    "networking/tcp-ip/arp-local-communication.md",
    "networking/switching/switching-fundamentals.md",
    "networking/vlans/vlan-fundamentals.md",
    "networking/firewalls/firewall-troubleshooting.md",
    "networking/reference/tcp-udp-ports.md",
    "networking/diagnostics/layered-connectivity-troubleshooting.md",
    "networking/reference/windows-linux-network-commands.md",
    "monitoring/README.md",
    "monitoring/host-monitoring/what-to-monitor.md",
    "monitoring/performance/thresholds-baselines.md",
    "monitoring/alerting/alert-fault-symptom.md",
    "monitoring/performance/normal-behaviour.md",
    "monitoring/logs/log-monitoring-fundamentals.md",
    "monitoring/alerting/alert-response-workflow.md",
    "operations/README.md",
    "operations/incidents/incident-handling.md",
    "operations/incidents/incident-prioritisation.md",
    "operations/escalation/technical-escalation.md",
    "operations/handovers/shift-handover.md",
    "operations/changes/change-management.md",
    "operations/changes/maintenance-windows.md",
    "operations/patching/patch-management.md",
    "operations/backup/backup-verification.md",
    "operations/recovery/recovery-verification.md",
    "operations/incidents/root-cause-vs-immediate-fix.md",
    "operations/maintenance/service-validation.md",
    "operations/documentation/technical-documentation-standards.md",
    "troubleshooting/README.md",
    "runbooks/README.md",
    "runbooks/host-unreachable.md",
    "runbooks/os-will-not-boot.md",
    "runbooks/service-not-running.md",
    "runbooks/disk-space-exhausted.md",
    "runbooks/high-cpu.md",
    "runbooks/high-memory.md",
    "runbooks/dns-resolution-failure.md",
    "runbooks/network-connectivity-failure.md",
    "runbooks/ssh-rdp-unavailable.md",
    "runbooks/unexpected-reboot.md",
    "checklists/README.md",
    "checklists/new-system-build.md",
    "checklists/windows-installation.md",
    "checklists/linux-installation.md",
    "checklists/hardware-diagnostics.md",
    "checklists/patching.md",
    "checklists/backup-verification.md",
    "checklists/shift-handover.md",
    "templates/README.md",
    "templates/troubleshooting-record.md",
    "templates/incident-record.md",
    "templates/change-record.md",
    "templates/system-build-record.md",
    "templates/shift-handover.md",
    "scripts/README.md",
    "scripts/bash/README.md",
    "scripts/bash/system-health.sh",
    "scripts/bash/disk-check.sh",
    "scripts/bash/service-check.sh",
    "scripts/bash/network-check.sh",
    "scripts/powershell/README.md",
    "scripts/powershell/Get-SystemHealth.ps1",
    "scripts/powershell/Test-NetworkHealth.ps1",
    "scripts/powershell/Get-ServiceHealth.ps1",
    "scripts/powershell/Get-DiskHealth.ps1",
    "scripts/python/README.md",
    "scripts/python/host_check.py",
    "scripts/python/port_check.py",
    "scripts/python/system_inventory.py",
    "scripts/python/log_summary.py",
)

LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
)
POWERSHELL_NAMES = {
    "Get-SystemHealth.ps1",
    "Test-NetworkHealth.ps1",
    "Get-ServiceHealth.ps1",
    "Get-DiskHealth.ps1",
}
PLANNED_PYTHON_NAMES = {
    "host_check.py",
    "port_check.py",
    "system_inventory.py",
    "log_summary.py",
}


def visible_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and IGNORED_DIRECTORIES.isdisjoint(path.parts)
    )


def check_expected(errors: list[str]) -> None:
    for relative in EXPECTED_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        elif path.stat().st_size < 200:
            errors.append(f"required file is unexpectedly small: {relative}")


def check_names(files: list[Path], errors: list[str]) -> None:
    for path in files:
        relative = path.relative_to(ROOT)
        for directory in relative.parts[:-1]:
            if directory != directory.lower() or " " in directory or "_" in directory:
                errors.append(f"non-canonical directory name: {relative}")
                break

        name = path.name
        if (
            name in {"README.md", "LICENSE", "CONTRIBUTING.md"}
            or name in POWERSHELL_NAMES
            or name in PLANNED_PYTHON_NAMES
        ):
            continue
        if path.suffix in {".md", ".sh", ".py"} and (
            name != name.lower() or " " in name or "_" in name
        ):
            errors.append(f"non-canonical file name: {relative}")


def markdown_without_fenced_code(text: str) -> tuple[str, bool]:
    output: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            output.append("\n")
        elif in_fence:
            output.append("\n")
        else:
            output.append(line)
    return "".join(output), in_fence


def normalise_link(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif " " in target:
        target = target.split(" ", 1)[0]
    return unquote(target)


def check_markdown(path: Path, errors: list[str]) -> None:
    relative = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.endswith((" ", "\t")):
            errors.append(f"trailing whitespace: {relative}:{line_number}")

    searchable, open_fence = markdown_without_fenced_code(text)
    if open_fence:
        errors.append(f"unclosed fenced code block: {relative}")

    for match in LINK_PATTERN.finditer(searchable):
        target = normalise_link(match.group(1))
        if not target or target.startswith("#"):
            continue
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("//"):
            continue

        link_path = target.split("#", 1)[0].split("?", 1)[0]
        if not link_path:
            continue
        if link_path.startswith("/"):
            errors.append(f"absolute local link: {relative} -> {target}")
            continue

        candidate = (path.parent / link_path).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            errors.append(f"link leaves repository: {relative} -> {target}")
            continue
        if not candidate.exists():
            errors.append(f"broken relative link: {relative} -> {target}")


def check_scripts(files: list[Path], errors: list[str]) -> None:
    for path in files:
        if path.suffix in {".sh", ".py"} and not os.access(path, os.X_OK):
            errors.append(f"script is not executable: {path.relative_to(ROOT)}")


def check_secrets(files: list[Path], errors: list[str]) -> None:
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret material: {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []
    files = visible_files()
    check_expected(errors)
    check_names(files, errors)
    check_scripts(files, errors)
    check_secrets(files, errors)

    markdown_files = [path for path in files if path.suffix == ".md"]
    for path in markdown_files:
        check_markdown(path, errors)

    if errors:
        print(f"Repository validation failed with {len(errors)} issue(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Repository validation passed: {len(EXPECTED_FILES)} required files, "
        f"{len(markdown_files)} Markdown files, no broken relative links or secret signatures."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
