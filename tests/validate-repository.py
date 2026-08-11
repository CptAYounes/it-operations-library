#!/usr/bin/env python3
"""Run repository structure, CommonMark link and privacy checks."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from markdown_it import MarkdownIt
from markdown_it.common.utils import normalizeReference
from markdown_it.rules_inline import image as commonmark_image_rule
from markdown_it.rules_inline import link as commonmark_link_rule

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORIES = {
    "__pycache__",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv-validation",
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

HEADING_PATTERN = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
BARE_URL_PATTERN = re.compile(r"https?://[^\s<]+", re.IGNORECASE)
BINARY_SIGNATURES = (
    b"\x7fELF",
    b"MZ",
    b"%PDF-",
    b"\x89PNG\r\n\x1a\n",
    b"\xff\xd8\xff",
    b"GIF87a",
    b"GIF89a",
    b"PK\x03\x04",
    b"\x1f\x8b",
    b"SQLite format 3\x00",
    b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",
    b"!<arch>\n",
    b"!<thin>\n",
)
HIDDEN_HTML_ELEMENTS = {"script", "style", "template"}
HTML_TARGET_ATTRIBUTES = {
    "a": {"href"},
    "area": {"href"},
    "audio": {"src"},
    "base": {"href"},
    "blockquote": {"cite"},
    "button": {"formaction"},
    "del": {"cite"},
    "embed": {"src"},
    "form": {"action"},
    "iframe": {"src"},
    "img": {"src", "srcset"},
    "input": {"formaction", "src"},
    "ins": {"cite"},
    "link": {"href"},
    "object": {"data"},
    "q": {"cite"},
    "script": {"src"},
    "source": {"src", "srcset"},
    "track": {"src"},
    "video": {"poster", "src"},
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"),
    re.compile(r"-----BEGIN PGP " r"PRIVATE KEY BLOCK-----"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"\bsk_live_[0-9A-Za-z]{20,}\b"),
    re.compile(r"\bsk-proj-[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"\bhf_[0-9A-Za-z]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
)
HIGH_RISK_EXTENSIONS = {
    ".der",
    ".jks",
    ".key",
    ".keystore",
    ".kdbx",
    ".p12",
    ".pfx",
    ".pkcs12",
}
HIGH_RISK_FILENAMES = {
    ".env",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
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


def security_files(visible: list[Path], errors: list[str]) -> list[Path]:
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            timeout=30,
        )
        if result.returncode:
            errors.append("unable to enumerate Git-tracked files for the security scan")
            return visible
        tracked = [
            ROOT / os.fsdecode(relative)
            for relative in result.stdout.split(b"\0")
            if relative
        ]
    else:
        tracked = [
            path
            for path in ROOT.rglob("*")
            if (path.is_file() or path.is_symlink()) and ".git" not in path.parts
        ]
    return sorted(
        set(visible).union(
            path for path in tracked if path.is_file() or path.is_symlink()
        )
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
    return unquote(raw_target.strip())


def heading_fragments(path: Path) -> set[str]:
    searchable, _ = markdown_without_fenced_code(path.read_text(encoding="utf-8"))
    fragments: set[str] = set()
    occurrences: dict[str, int] = {}
    for match in HEADING_PATTERN.finditer(searchable):
        heading = re.sub(r"<[^>]+>", "", match.group(1))
        heading = re.sub(r"[`*_~]", "", heading).casefold().strip()
        base = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        base = re.sub(r"-+", "-", base)
        count = occurrences.get(base, 0)
        fragment = base if count == 0 else f"{base}-{count}"
        occurrences[base] = count + 1
        fragments.add(fragment)
    return fragments


def normalise_reference_label(label: str) -> str:
    return str(normalizeReference(label)).casefold()


def balanced_label_end(content: str, start: int) -> int:
    if start >= len(content) or content[start] != "[":
        return -1
    depth = 1
    position = start + 1
    while position < len(content):
        character = content[position]
        if character == "\\" and position + 1 < len(content):
            position += 2
            continue
        if character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                return position
        position += 1
    return -1


def character_is_escaped(content: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and content[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def balanced_label_ends(content: str) -> dict[int, int]:
    """Return matching closing brackets for every balanced, unescaped opener."""
    ends: dict[int, int] = {}
    stack: list[int] = []
    position = 0
    while position < len(content):
        character = content[position]
        if character == "\\" and position + 1 < len(content):
            position += 2
            continue
        if character == "[":
            stack.append(position)
        elif character == "]" and stack:
            ends[stack.pop()] = position
        position += 1
    return ends


def explicit_reference_candidates(content: str) -> list[tuple[str, int, int]]:
    candidates: list[tuple[str, int, int]] = []
    label_ends = balanced_label_ends(content)
    position = 0
    while position < len(content):
        character = content[position]
        if character == "\\" and position + 1 < len(content):
            position += 2
            continue
        if character != "[":
            position += 1
            continue

        first_end = label_ends.get(position, -1)
        if first_end < 0:
            position += 1
            continue
        second_start = first_end + 1
        if second_start >= len(content) or content[second_start] != "[":
            position += 1
            continue
        second_end = label_ends.get(second_start, -1)
        if second_end < 0:
            position += 1
            continue
        label = content[second_start + 1 : second_end]
        if not label:
            label = content[position + 1 : first_end]
        candidate_start = position
        if (
            position > 0
            and content[position - 1] == "!"
            and not character_is_escaped(content, position - 1)
        ):
            candidate_start -= 1
        candidates.append((label, candidate_start, second_end + 1))
        # Keep scanning inside the candidate. CommonMark permits images inside
        # link text, so jumping past an outer reference can hide a nested image
        # reference that needs its own definition.
        position += 1
    return candidates


def commonmark_link_spans(
    content: str,
    references: dict[str, Any],
    required_target: str | None = None,
) -> set[tuple[int, int, str]]:
    parser = MarkdownIt("commonmark")
    matching_spans: set[tuple[int, int, str]] = set()
    image_source_spans: set[tuple[int, int]] = set()
    image_parse_depth = 0

    def traced_rule(rule: Any, target_type: str, attribute: str) -> Any:
        def traced(state: Any, silent: bool) -> bool:
            nonlocal image_parse_depth
            start = state.pos
            token_count = len(state.tokens)
            parent_image_depth = image_parse_depth
            if target_type == "image":
                image_parse_depth += 1
            try:
                matched = bool(rule(state, silent))
            finally:
                if target_type == "image":
                    image_parse_depth -= 1
            if matched and not silent and parent_image_depth == 0:
                for token in state.tokens[token_count:]:
                    if token.type != target_type:
                        continue
                    if target_type == "image":
                        image_source_spans.add((start, state.pos))
                    if (
                        required_target is None
                        or token.attrGet(attribute) == required_target
                    ):
                        matching_spans.add((start, state.pos, target_type))
                    break
            return matched

        return traced

    parser.inline.ruler.at(
        "link", traced_rule(commonmark_link_rule, "link_open", "href")
    )
    parser.inline.ruler.at(
        "image", traced_rule(commonmark_image_rule, "image", "src")
    )
    output_tokens: list[Any] = []
    parser.inline.parse(
        content,
        parser,
        {"references": references},
        output_tokens,
    )
    # markdown-it stores parsed inline children inside an image token rather
    # than emitting them beside the outer token. Re-parse each image label so
    # links and images nested in alt text retain source spans for exact
    # candidate confirmation and overlap checks.
    for image_start, _ in tuple(image_source_spans):
        label_start = image_start + 1
        label_end = balanced_label_end(content, label_start)
        if label_end < 0:
            continue
        label_content_start = label_start + 1
        label_content = content[label_content_start:label_end]
        for nested_start, nested_end, nested_type in commonmark_link_spans(
            label_content, references, required_target
        ):
            matching_spans.add(
                (
                    label_content_start + nested_start,
                    label_content_start + nested_end,
                    nested_type,
                )
            )
    return matching_spans


def commonmark_reference_key(raw_label: str) -> str | None:
    # CommonMark caps a link label at 999 source characters. markdown-it-py
    # accepts longer definitions, so enforce the specification before using a
    # synthetic definition to probe the candidate.
    if len(raw_label) > 999:
        return None
    sentinel = "urn:repository-validator:undefined-reference"
    reference_key = str(normalizeReference(raw_label))
    definition_environment: dict[str, object] = {}
    MarkdownIt("commonmark").parse(
        f"[{raw_label}]: {sentinel}\n", definition_environment
    )
    definitions = definition_environment.get("references", {})
    if not isinstance(definitions, dict) or reference_key not in definitions:
        return None
    return reference_key


def confirmed_commonmark_reference_spans(
    content: str, candidates: list[tuple[str, int, int]]
) -> set[tuple[int, int]]:
    # Defining and reparsing the whole inline source once per candidate is
    # quadratic for a paragraph containing many independent references. Split
    # overlapping source intervals into separate batches, then confirm every
    # non-overlapping batch in one parser pass. Overlapping/nested candidates
    # stay in different batches so one synthetic outer link cannot mask an
    # inner image/link candidate.
    batches: list[list[tuple[str, int, int]]] = []
    batch_ends: list[int] = []
    for candidate in sorted(candidates, key=lambda item: (item[1], item[2])):
        _, start, end = candidate
        for index, previous_end in enumerate(batch_ends):
            if previous_end <= start:
                batches[index].append(candidate)
                batch_ends[index] = end
                break
        else:
            batches.append([candidate])
            batch_ends.append(end)

    sentinel = "urn:repository-validator:undefined-reference"
    confirmed: set[tuple[int, int]] = set()
    for batch in batches:
        synthetic_references = {
            reference_key: {"href": sentinel, "title": ""}
            for reference_key, _, _ in batch
        }
        matching_spans = {
            (start, end)
            for start, end, _ in commonmark_link_spans(
                content, synthetic_references, sentinel
            )
        }
        confirmed.update(
            (start, end)
            for _, start, end in batch
            if (start, end) in matching_spans
        )
    return confirmed


def undefined_reference_labels(text: str, definition_labels: set[str]) -> set[str]:
    labels: set[str] = set()
    environment: dict[str, object] = {}
    tokens = MarkdownIt("commonmark").parse(text, environment)
    references = environment.get("references", {})
    if not isinstance(references, dict):
        references = {}
    for token in tokens:
        if token.type == "inline":
            actual_spans = commonmark_link_spans(token.content, references)
            candidate_labels: list[tuple[str, str, int, int]] = []
            reference_keys: dict[str, str | None] = {}
            for raw_label, start, end in explicit_reference_candidates(token.content):
                label = normalise_reference_label(raw_label)
                if label in definition_labels:
                    continue
                is_image = token.content[start : start + 1] == "!"
                if any(
                    start < actual_end
                    and actual_start < end
                    and not (
                        actual_start <= start
                        and end <= actual_end
                        and (is_image or actual_type == "image")
                    )
                    for actual_start, actual_end, actual_type in actual_spans
                ):
                    continue
                if raw_label not in reference_keys:
                    reference_keys[raw_label] = commonmark_reference_key(raw_label)
                reference_key = reference_keys[raw_label]
                if reference_key is not None:
                    candidate_labels.append((label, reference_key, start, end))
            confirmed_spans = confirmed_commonmark_reference_spans(
                token.content,
                [
                    (reference_key, start, end)
                    for _, reference_key, start, end in candidate_labels
                ],
            )
            labels.update(
                label
                for label, _, start, end in candidate_labels
                if (start, end) in confirmed_spans
            )
    return labels


class LinkHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: set[str] = set()
        self.anchor_depth = 0
        self.hidden_depth = 0

    def open_anchor(self) -> None:
        if self.hidden_depth == 0:
            # HTML5 implicitly closes an active anchor before opening another.
            # Model one active anchor rather than nesting counters so text after
            # the inner closing tag is visible to bare-URL checks.
            self.anchor_depth = 1

    def close_anchor(self) -> None:
        if self.hidden_depth == 0:
            self.anchor_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        folded_tag = tag.casefold()
        if folded_tag == "a":
            self.open_anchor()
        if folded_tag in HIDDEN_HTML_ELEMENTS:
            self.hidden_depth += 1
        target_attributes = HTML_TARGET_ATTRIBUTES.get(folded_tag)
        if target_attributes is None:
            return
        for name, value in attrs:
            folded_name = name.casefold()
            if folded_name not in target_attributes or not value:
                continue
            if folded_name == "srcset":
                self.targets.update(srcset_targets(value))
            else:
                self.targets.add(value)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        # HTML5 ignores the self-closing flag on non-void elements such as
        # a/script/style/template. Calling the default end-tag handler would
        # expose text that a browser keeps inside the element.
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        folded_tag = tag.casefold()
        if folded_tag in HIDDEN_HTML_ELEMENTS:
            self.hidden_depth = max(0, self.hidden_depth - 1)
        elif folded_tag == "a":
            self.close_anchor()

    def handle_data(self, data: str) -> None:
        if self.anchor_depth or self.hidden_depth:
            return
        self.targets.update(
            match.group(0).rstrip(".,;:!?)]}")
            for match in BARE_URL_PATTERN.finditer(data)
        )


def srcset_targets(value: str) -> set[str]:
    targets: set[str] = set()
    whitespace = " \t\n\f\r"
    position = 0
    while position < len(value):
        while position < len(value) and (
            value[position] in whitespace or value[position] == ","
        ):
            position += 1
        if position >= len(value):
            break

        start = position
        while position < len(value) and value[position] not in whitespace:
            position += 1
        target = value[start:position]
        if target.endswith(","):
            target = target.rstrip(",")
            if target:
                targets.add(target)
            continue
        if target:
            targets.add(target)

        parentheses = 0
        while position < len(value):
            character = value[position]
            if character == "(":
                parentheses += 1
            elif character == ")" and parentheses:
                parentheses -= 1
            elif character == "," and not parentheses:
                position += 1
                break
            position += 1
    return targets


def html_targets(content: str) -> set[str]:
    parser = LinkHTMLParser()
    parser.feed(content)
    parser.close()
    return parser.targets


def markdown_targets(text: str) -> tuple[set[str], set[str]]:
    environment: dict[str, object] = {}
    tokens = MarkdownIt("commonmark").parse(text, environment)
    targets: set[str] = set()
    for token in tokens:
        if token.type == "html_block":
            targets.update(html_targets(token.content))
        inline_html_parser = LinkHTMLParser()
        for child in token.children or []:
            if child.type == "link_open":
                target = child.attrGet("href")
                if target:
                    targets.add(str(target))
                inline_html_parser.open_anchor()
                continue
            if child.type == "link_close":
                inline_html_parser.close_anchor()
                continue
            elif child.type == "image":
                target = child.attrGet("src")
            elif child.type == "html_inline":
                inline_html_parser.feed(child.content)
                targets.update(inline_html_parser.targets)
                continue
            elif (
                child.type == "text"
                and inline_html_parser.anchor_depth == 0
                and inline_html_parser.hidden_depth == 0
            ):
                targets.update(
                    match.group(0).rstrip(".,;:!?)]}")
                    for match in BARE_URL_PATTERN.finditer(child.content)
                )
                continue
            else:
                continue
            if target:
                targets.add(str(target))
        inline_html_parser.close()
        targets.update(inline_html_parser.targets)

    references = environment.get("references", {})
    reference_labels: set[str] = set()
    if isinstance(references, dict):
        for label, definition in references.items():
            reference_labels.add(normalise_reference_label(str(label)))
            if isinstance(definition, dict) and definition.get("href"):
                targets.add(str(definition["href"]))
    return targets, reference_labels


def check_link_target(path: Path, target: str, errors: list[str]) -> None:
    relative = path.relative_to(ROOT)
    target = normalise_link(target)
    if not target:
        return

    parsed = urlparse(target)
    if parsed.scheme or target.startswith("//"):
        errors.append(f"external link requires a separate bounded check: {relative} -> {target}")
        return

    link_path, _, fragment = target.partition("#")
    link_path = link_path.split("?", 1)[0]
    if link_path.startswith("/"):
        errors.append(f"absolute local link: {relative} -> {target}")
        return

    candidate = (path.parent / link_path).resolve() if link_path else path.resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        errors.append(f"link leaves repository: {relative} -> {target}")
        return
    if not candidate.exists():
        errors.append(f"broken relative link: {relative} -> {target}")
        return
    if (
        fragment
        and candidate.is_file()
        and candidate.suffix.casefold() == ".md"
        and fragment.casefold() not in heading_fragments(candidate)
    ):
        errors.append(f"broken Markdown fragment: {relative} -> {target}")


def check_markdown(path: Path, errors: list[str]) -> None:
    relative = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.endswith((" ", "\t")):
            errors.append(f"trailing whitespace: {relative}:{line_number}")

    _, open_fence = markdown_without_fenced_code(text)
    if open_fence:
        errors.append(f"unclosed fenced code block: {relative}")

    targets, definition_labels = markdown_targets(text)
    for target in targets:
        check_link_target(path, target, errors)

    for label in sorted(undefined_reference_labels(text, definition_labels)):
        errors.append(f"undefined Markdown reference: {relative} -> [{label}]")


def check_scripts(files: list[Path], errors: list[str]) -> None:
    for path in files:
        if path.suffix in {".sh", ".py"} and not os.access(path, os.X_OK):
            errors.append(f"script is not executable: {path.relative_to(ROOT)}")


def check_secrets(files: list[Path], errors: list[str]) -> None:
    for path in files:
        relative = path.relative_to(ROOT)
        suffix = path.suffix.casefold()
        if path.is_symlink():
            errors.append(f"symbolic link requires manual security review: {relative}")
            continue
        if path.name.casefold() in HIGH_RISK_FILENAMES or suffix in HIGH_RISK_EXTENSIONS:
            errors.append(f"high-risk credential or key container: {relative}")
            continue
        content = path.read_bytes()
        if b"\x00" in content or any(
            content.startswith(signature) for signature in BINARY_SIGNATURES
        ):
            errors.append(f"unreviewed binary file: {relative}")
            continue
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"unreviewed binary file: {relative}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret material: {relative}")


def main() -> int:
    errors: list[str] = []
    files = visible_files()
    files_for_security = security_files(files, errors)
    check_expected(errors)
    check_names(files, errors)
    check_scripts(files, errors)
    check_secrets(files_for_security, errors)

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
        f"{len(markdown_files)} Markdown files, no broken links, and no unreviewed binary files "
        "or secret signatures in tracked/visible candidates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
