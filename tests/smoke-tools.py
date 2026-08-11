#!/usr/bin/env python3
"""Exercise safe success and validation paths for the diagnostic tools."""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRICT = False


def run(
    command: list[str],
    expected: int = 0,
    *,
    env: dict[str, str] | None = None,
    cwd: Path = ROOT,
    timeout: float = 20,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"{' '.join(command)} returned {result.returncode}, expected {expected}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def run_with_group_deadline(
    command: list[str],
    expected: int,
    deadline: float,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=deadline)
    except subprocess.TimeoutExpired as exc:
        process_rows = subprocess.run(
            ["ps", "-eo", "pid=,ppid=,pgid="],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.splitlines()
        relationships = {
            int(pid): (int(parent), int(group))
            for row in process_rows
            if len(fields := row.split()) == 3
            for pid, parent, group in [fields]
        }
        descendants = {process.pid}
        while True:
            discovered = {
                pid for pid, (parent, _) in relationships.items() if parent in descendants
            }
            if discovered <= descendants:
                break
            descendants.update(discovered)
        groups = {
            relationships[pid][1]
            for pid in descendants
            if pid in relationships and relationships[pid][1] > 0
        }
        groups.add(process.pid)
        for group in groups:
            try:
                os.killpg(group, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.communicate()
        stage = env.get("HANG_STAGE", "command")
        raise AssertionError(
            f"network {stage} query exceeded the {deadline}s outer deadline: {' '.join(command)}"
        ) from exc
    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if result.returncode != expected:
        raise AssertionError(
            f"{' '.join(command)} returned {result.returncode}, expected {expected}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def accept_once(listener: socket.socket) -> None:
    connection, _ = listener.accept()
    connection.close()


def skip_or_fail(message: str) -> None:
    if STRICT:
        raise AssertionError(message)
    print(f"SKIP: {message}")


def test_validator_regressions() -> None:
    with tempfile.TemporaryDirectory() as directory:
        copy_root = Path(directory) / "repo"
        shutil.copytree(
            ROOT,
            copy_root,
            ignore=shutil.ignore_patterns(
                ".git",
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
            ),
        )
        validator = copy_root / "tests/validate-repository.py"

        def assert_clean_copy() -> None:
            run([sys.executable, str(validator)], cwd=copy_root)

        assert_clean_copy()

        nested_image = "alt"
        for _ in range(8):
            nested_image = f"![{nested_image}](README.md)"
        nested_image_canary = copy_root / "nested-image-canary.md"
        nested_image_canary.write_text(f"# Nested image canary\n\n{nested_image}\n")
        try:
            nested_validation = subprocess.run(
                [sys.executable, str(validator)],
                cwd=copy_root,
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise AssertionError(
                "validator exceeded five seconds on eight nested images"
            ) from error
        if nested_validation.returncode != 0:
            raise AssertionError(
                "validator rejected a valid nested-image canary:\n"
                f"{nested_validation.stderr}"
            )
        nested_image_canary.unlink()
        assert_clean_copy()

        wide_reference_canary = copy_root / "wide-reference-canary.md"
        wide_reference_canary.write_text(
            "# Wide reference canary\n\n"
            + " ".join(
                f"[item {index}][wide-missing-{index}]" for index in range(400)
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            wide_validation = subprocess.run(
                [sys.executable, str(validator)],
                cwd=copy_root,
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise AssertionError(
                "validator exceeded five seconds on 400 independent references"
            ) from error
        if wide_validation.returncode != 1:
            raise AssertionError(
                "validator did not reject the wide undefined-reference canary:\n"
                f"{wide_validation.stderr}"
            )
        for expected_label in ("wide-missing-0", "wide-missing-399"):
            if (
                "undefined Markdown reference: wide-reference-canary.md -> "
                f"[{expected_label}]"
            ) not in wide_validation.stderr:
                raise AssertionError(
                    f"validator missed wide reference label: {expected_label}"
                )
        wide_reference_canary.unlink()
        assert_clean_copy()

        credential_container = copy_root / "canary.pfx"
        credential_container.write_bytes(b"synthetic validator canary")
        blocked_binary = run(
            [sys.executable, str(validator)], expected=1, cwd=copy_root
        )
        if "high-risk credential or key container" not in blocked_binary.stderr:
            raise AssertionError("validator accepted a high-risk credential container")
        credential_container.unlink()
        assert_clean_copy()

        unexpected_binary = copy_root / "canary.bin"
        unexpected_binary.write_bytes(b"\xff\xfe\x00\x01")
        blocked_binary = run(
            [sys.executable, str(validator)], expected=1, cwd=copy_root
        )
        if "unreviewed binary file" not in blocked_binary.stderr:
            raise AssertionError("validator accepted an unexpected binary artifact")
        unexpected_binary.unlink()
        assert_clean_copy()

        disguised_executable = copy_root / "cover.png"
        disguised_executable.write_bytes(
            b"\x7fELF\x02\x01\x01\x00" + (b"\x00" * 24)
        )
        blocked_binary = run(
            [sys.executable, str(validator)], expected=1, cwd=copy_root
        )
        if "unreviewed binary file" not in blocked_binary.stderr:
            raise AssertionError("validator trusted an executable payload by image suffix")
        disguised_executable.unlink()
        assert_clean_copy()

        ascii_archive = copy_root / "canary.a"
        archive_header = (
            b"member.txt/     "
            b"0           "
            b"0     "
            b"0     "
            b"100644  "
            b"5         "
            b"`\n"
        )
        if len(archive_header) != 60:
            raise AssertionError("synthetic ar member header is not 60 bytes")
        ascii_archive.write_bytes(b"!<arch>\n" + archive_header + b"hello\n")
        blocked_binary = run(
            [sys.executable, str(validator)], expected=1, cwd=copy_root
        )
        if "unreviewed binary file: canary.a" not in blocked_binary.stderr:
            raise AssertionError("validator accepted an ASCII-clean ar archive")
        ascii_archive.unlink()
        assert_clean_copy()

        thin_archive = copy_root / "canary-thin.a"
        thin_archive.write_bytes(
            b"!<thin>\n" + archive_header + b"ascii-member.txt/\n"
        )
        blocked_binary = run(
            [sys.executable, str(validator)], expected=1, cwd=copy_root
        )
        if "unreviewed binary file: canary-thin.a" not in blocked_binary.stderr:
            raise AssertionError("validator accepted an ASCII-clean GNU thin archive")
        thin_archive.unlink()
        assert_clean_copy()

        credential_file = copy_root / ".env"
        credential_file.write_text("SYNTHETIC_CANARY=not-a-secret\n", encoding="utf-8")
        blocked_name = run([sys.executable, str(validator)], expected=1, cwd=copy_root)
        if "high-risk credential or key container" not in blocked_name.stderr:
            raise AssertionError("validator accepted a high-risk credential filename")
        credential_file.unlink()
        assert_clean_copy()

        secret_signature = copy_root / "canary.txt"
        secret_signature.write_text(
            "-----BEGIN " "PRIVATE KEY-----\nsynthetic validation canary\n",
            encoding="utf-8",
        )
        blocked_secret = run(
            [sys.executable, str(validator)], expected=1, cwd=copy_root
        )
        if "possible secret material" not in blocked_secret.stderr:
            raise AssertionError("validator accepted a high-confidence secret signature")
        secret_signature.unlink()
        assert_clean_copy()

        for synthetic_token in ("hf_" + ("A" * 32), "sk-proj-" + ("A" * 40)):
            secret_signature.write_text(synthetic_token + "\n", encoding="utf-8")
            blocked_secret = run(
                [sys.executable, str(validator)], expected=1, cwd=copy_root
            )
            if "possible secret material" not in blocked_secret.stderr:
                raise AssertionError("validator accepted a current token-family canary")
            secret_signature.unlink()
            assert_clean_copy()

        run(["git", "init", "--quiet"], cwd=copy_root)
        for ignored_name in (
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
        ):
            ignored_directory = copy_root / ignored_name
            ignored_directory.mkdir()
            tracked_secret = ignored_directory / "canary.txt"
            tracked_secret.write_text(
                "-----BEGIN " "PRIVATE KEY-----\ntracked ignored-path canary\n",
                encoding="utf-8",
            )
            relative_secret = f"{ignored_name}/canary.txt"
            run(["git", "add", "--force", relative_secret], cwd=copy_root)
            blocked_tracked = run(
                [sys.executable, str(validator)], expected=1, cwd=copy_root
            )
            if f"possible secret material: {relative_secret}" not in blocked_tracked.stderr:
                raise AssertionError(
                    f"validator omitted tracked security content beneath {ignored_name}"
                )
            run(
                ["git", "rm", "--cached", "--quiet", relative_secret],
                cwd=copy_root,
            )
            tracked_secret.unlink()
            ignored_directory.rmdir()
            assert_clean_copy()

        broken_links = copy_root / "canary.md"
        overlong_reference_label = "x" * 1000
        deep_nested_missing = "[alt][deep-nested-image-missing]"
        for _ in range(8):
            deep_nested_missing = f"![{deep_nested_missing}](README.md)"
        broken_links.write_text(
            "# Canary\n\n"
            "[Missing fragment](README.md#not-a-heading)\n"
            "[Missing reference][undefined]\n"
            "[Outer [inner]][nested undefined]\n"
            "unclosed ` then [Missing][tick-missing]\n\n"
            "a < b [Missing][angle-missing] > c\n\n"
            "![Missing image][image-missing]\n\n"
            "[Valid reference][local]\n"
            "`[Code sample][code-only]`\n\n"
            "\\[Escaped text][escaped-only]\n\n"
            "<!-- [Comment text][comment-only] -->\n\n"
            '[Valid title](README.md "[Sample][title-only]")\n\n'
            "[Invalid nested label][a[b]c]\n\n"
            "[outer [not][reference]](README.md)\n\n"
            "[outer ![alt][nested-image-missing]](README.md)\n\n"
            "[outer ![nested-collapsed-missing][]](README.md)\n\n"
            "[outer ![alt][nested-reference-image-missing]][outer]\n\n"
            "![outer [alt][nested-link-in-image-missing]](README.md)\n\n"
            "![outer ![alt][nested-image-in-image-missing]](README.md)\n\n"
            + deep_nested_missing
            + "\n\n"
            "[a][overlap-only](README.md)\n\n"
            "![a][image-overlap-only](README.md)\n\n"
            "![outer [a][nested-link-overlap-only](README.md)](README.md)\n\n"
            "![outer ![a][nested-image-overlap-only](README.md)](README.md)\n\n"
            "[Overlong label][" + overlong_reference_label + "]\n\n"
            "[Outer [inner]](nested-missing.md)\n"
            "[Nested destination](missing_(nested).md)\n"
            "[Encoded destination](encoded%2Dmissing.md)\n"
            "[Valid angle destination](<README.md>)\n"
            "[External](https://example.com)\n\n"
            '<a href="html-missing.md">Missing HTML target</a>\n'
            '<a href="https://html-unreviewed.example">External HTML target</a>\n'
            '<iframe src="frame-missing.html"></iframe>\n'
            '<link href="style-missing.css" rel="stylesheet">\n'
            '<script src="script-missing.js"></script>\n'
            '<source src="source-missing.mp4" '
            'srcset="source-one-missing.png 1x, source-two-missing.png 2x">\n'
            '<img srcset="comma,name-missing.png 1x, data:image/png;base64,AAAA 2x">\n'
            '<object data="object-missing.bin"></object>\n'
            '<video src="video-missing.mp4" poster="poster-missing.png"></video>\n'
            '<form action="submit-missing"><button formaction="button-missing">Send</button></form>\n\n'
            '<a href="README.md missing-target.md">Literal-space target</a>\n'
            "[https://display-only.invalid](README.md)\n"
            '<a href="README.md">https://html-display-only.invalid</a>\n'
            "[HTTPS://uppercase-display-only.invalid](README.md)\n"
            '<a href="README.md">HtTpS://mixed-html-display-only.invalid</a>\n'
            "https://bare-unreviewed.example\n\n"
            "HTTPS://uppercase-bare-unreviewed.example/x\n\n"
            "<div>\nhttps://html-block-bare.invalid\n</div>\n\n"
            "<div>\n<a href=\"README.md\">outer <a href=\"README.md\">inner</a> HTTPS://nested-block-visible.invalid/x</a>\n</div>\n\n"
            "<script>https://script-data.invalid</script>\n\n"
            "Prefix <span>https://inline-visible.invalid/x</span> suffix\n\n"
            "Prefix <span>HtTpS://mixed-inline-visible.invalid/x</span> suffix\n\n"
            '<a href="README.md">outer <a href="README.md">inner</a> HTTPS://nested-raw-visible.invalid/x</a>\n\n'
            '<a href="README.md">outer [inner](README.md) HtTpS://nested-raw-markdown-visible.invalid/x</a>\n\n'
            '[outer <a href="README.md">inner</a> HTTPS://nested-markdown-raw-visible.invalid/x](README.md)\n\n'
            "Prefix <script>https://inline-script-data.invalid/x</script> suffix\n\n"
            "Prefix <style>https://inline-style-data.invalid/x</style> suffix\n\n"
            "Prefix <template>https://inline-template-data.invalid/x</template> suffix\n\n"
            "Prefix <script/>HTTPS://inline-selfclose-script.invalid/x</script> suffix\n\n"
            "Prefix <style/>HTTPS://inline-selfclose-style.invalid/x</style> suffix\n\n"
            "Prefix <template/>HTTPS://inline-selfclose-template.invalid/x</template> suffix\n\n"
            '<a href="README.md"/>HTTPS://inline-selfclose-anchor.invalid/x</a>\n\n'
            "[local]: README.md\n"
            "[outer]: README.md\n",
            encoding="utf-8",
        )
        blocked_links = run([sys.executable, str(validator)], expected=1, cwd=copy_root)
        for expected_error in (
            "broken Markdown fragment",
            "broken relative link: canary.md -> nested-missing.md",
            "broken relative link: canary.md -> missing_(nested).md",
            "broken relative link: canary.md -> encoded-missing.md",
            "broken relative link: canary.md -> html-missing.md",
            "broken relative link: canary.md -> frame-missing.html",
            "broken relative link: canary.md -> style-missing.css",
            "broken relative link: canary.md -> script-missing.js",
            "broken relative link: canary.md -> source-missing.mp4",
            "broken relative link: canary.md -> source-one-missing.png",
            "broken relative link: canary.md -> source-two-missing.png",
            "broken relative link: canary.md -> comma,name-missing.png",
            "broken relative link: canary.md -> object-missing.bin",
            "broken relative link: canary.md -> video-missing.mp4",
            "broken relative link: canary.md -> poster-missing.png",
            "broken relative link: canary.md -> submit-missing",
            "broken relative link: canary.md -> button-missing",
            "broken relative link: canary.md -> README.md missing-target.md",
            "undefined Markdown reference",
            "undefined Markdown reference: canary.md -> [nested undefined]",
            "undefined Markdown reference: canary.md -> [tick-missing]",
            "undefined Markdown reference: canary.md -> [angle-missing]",
            "undefined Markdown reference: canary.md -> [image-missing]",
            "undefined Markdown reference: canary.md -> [nested-image-missing]",
            "undefined Markdown reference: canary.md -> [nested-collapsed-missing]",
            "undefined Markdown reference: canary.md -> [nested-reference-image-missing]",
            "undefined Markdown reference: canary.md -> [nested-link-in-image-missing]",
            "undefined Markdown reference: canary.md -> [nested-image-in-image-missing]",
            "undefined Markdown reference: canary.md -> [deep-nested-image-missing]",
            "external link requires a separate bounded check: canary.md -> https://html-unreviewed.example",
            "external link requires a separate bounded check: canary.md -> https://bare-unreviewed.example",
            "external link requires a separate bounded check: canary.md -> HTTPS://uppercase-bare-unreviewed.example/x",
            "external link requires a separate bounded check: canary.md -> https://html-block-bare.invalid",
            "external link requires a separate bounded check: canary.md -> HTTPS://nested-block-visible.invalid/x",
            "external link requires a separate bounded check: canary.md -> https://inline-visible.invalid/x",
            "external link requires a separate bounded check: canary.md -> HtTpS://mixed-inline-visible.invalid/x",
            "external link requires a separate bounded check: canary.md -> HTTPS://nested-raw-visible.invalid/x",
            "external link requires a separate bounded check: canary.md -> HtTpS://nested-raw-markdown-visible.invalid/x",
            "external link requires a separate bounded check: canary.md -> HTTPS://nested-markdown-raw-visible.invalid/x",
            "external link requires a separate bounded check: canary.md -> data:image/png;base64,AAAA",
        ):
            if expected_error not in blocked_links.stderr:
                raise AssertionError(f"validator missed link failure: {expected_error}")
        if "undefined Markdown reference: canary.md -> [local]" in blocked_links.stderr:
            raise AssertionError("validator rejected a valid CommonMark reference link")
        for false_positive in (
            "code-only",
            "escaped-only",
            "comment-only",
            "title-only",
            "a[b]c",
            "reference",
            "overlap-only",
            "image-overlap-only",
            "nested-link-overlap-only",
            "nested-image-overlap-only",
            overlong_reference_label,
        ):
            if f"undefined Markdown reference: canary.md -> [{false_positive}]" in blocked_links.stderr:
                raise AssertionError(
                    f"validator falsely treated {false_positive} as reference syntax"
                )
        for linked_label in (
            "https://display-only.invalid",
            "https://html-display-only.invalid",
            "HTTPS://uppercase-display-only.invalid",
            "HtTpS://mixed-html-display-only.invalid",
            "https://script-data.invalid",
            "https://inline-script-data.invalid/x",
            "https://inline-style-data.invalid/x",
            "https://inline-template-data.invalid/x",
            "HTTPS://inline-selfclose-script.invalid/x",
            "HTTPS://inline-selfclose-style.invalid/x",
            "HTTPS://inline-selfclose-template.invalid/x",
            "HTTPS://inline-selfclose-anchor.invalid/x",
        ):
            if f"external link requires a separate bounded check: canary.md -> {linked_label}" in blocked_links.stderr:
                raise AssertionError(
                    f"validator treated linked display text as a bare URL: {linked_label}"
                )
        broken_links.unlink()
        assert_clean_copy()


def test_release_gate() -> None:
    with tempfile.TemporaryDirectory() as directory:
        fake_directory = Path(directory)
        fake_gitleaks = fake_directory / "gitleaks"
        invocation_log = fake_directory / "invocations"
        fake_gitleaks.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$*\" >> \"$GITLEAKS_LOG\"\n"
            "if [[ $1 == \"$FAIL_SCAN\" ]]; then exit 1; fi\n",
            encoding="utf-8",
        )
        fake_gitleaks.chmod(0o755)
        environment = os.environ.copy()
        environment["GITLEAKS_LOG"] = str(invocation_log)
        environment["FAIL_SCAN"] = ""
        run(
            [
                sys.executable,
                str(ROOT / "tests/validate-release.py"),
                "--gitleaks",
                str(fake_gitleaks),
            ],
            env=environment,
        )
        invocations = invocation_log.read_text(encoding="utf-8").splitlines()
        if len(invocations) != 2 or not invocations[0].startswith("dir ") or not invocations[1].startswith("git "):
            raise AssertionError("release gate did not scan both worktree and Git history")

        environment["FAIL_SCAN"] = "dir"
        run(
            [
                sys.executable,
                str(ROOT / "tests/validate-release.py"),
                "--gitleaks",
                str(fake_gitleaks),
            ],
            expected=1,
            env=environment,
        )
        missing_scanner = run(
            [
                sys.executable,
                str(ROOT / "tests/validate-release.py"),
                "--gitleaks",
                str(fake_directory / "missing-gitleaks"),
            ],
            expected=2,
            env=environment,
        )
        if "Gitleaks executable is unavailable" not in missing_scanner.stderr:
            raise AssertionError("release gate did not fail closed without Gitleaks")


def test_bash() -> None:
    scripts = sorted((ROOT / "scripts/bash").glob("*.sh"))
    run(["bash", "-n", *(str(script) for script in scripts)])
    shellcheck = shutil.which("shellcheck")
    if shellcheck:
        run([shellcheck, *(str(script) for script in scripts)])
    elif shutil.which("pipx"):
        run(
            ["pipx", "run", "shellcheck-py", *(str(script) for script in scripts)],
            timeout=180,
        )
    else:
        skip_or_fail("ShellCheck validation (shellcheck and pipx unavailable)")
    disk_command = [str(ROOT / "scripts/bash/disk-check.sh"), "--warning", "100", "/"]
    disk_result = run(disk_command)
    total_match = re.search(r"total: (\d+) KiB", disk_result.stdout)
    if total_match is None:
        raise AssertionError("disk check did not report a total in KiB")
    expected_total = total_match.group(1)

    for variable, value in (
        ("POSIXLY_CORRECT", "1"),
        ("DF_BLOCK_SIZE", "1M"),
        ("BLOCK_SIZE", "1M"),
    ):
        environment = os.environ.copy()
        environment[variable] = value
        result = run(disk_command, env=environment)
        if f"total: {expected_total} KiB" not in result.stdout:
            raise AssertionError(f"{variable} changed the documented KiB units")

    run([str(ROOT / "scripts/bash/system-health.sh"), "--help"])

    if all(shutil.which(command) for command in ("ip", "getent", "ping", "timeout")):
        run([str(ROOT / "scripts/bash/network-check.sh"), "--timeout", "1", "127.0.0.1"])

        with tempfile.TemporaryDirectory() as directory:
            fake_directory = Path(directory)
            fake_ip = fake_directory / "ip"
            fake_getent = fake_directory / "getent"
            fake_ping = fake_directory / "ping"
            fake_ip.write_text(
                """#!/usr/bin/env bash
hang() {
    printf '%s\n' "$$" > "$PID_FILE"
    trap '' TERM
    while :; do :; done
}
case "$*" in
    '-4 route show default')
        [[ $HANG_STAGE == default ]] && hang
        if [[ $MALFORM_STAGE == default ]]; then
            printf 'default via gateway.invalid dev eth0\n'
        elif [[ $MALFORM_STAGE == default-prefix ]]; then
            printf 'defaultfoo via 192.0.2.1 dev eth0\n'
        elif [[ $MALFORM_STAGE == default-prefix-mixed ]]; then
            printf 'defaultfoo via 192.0.2.1 dev eth0\n'
            printf 'default via 192.0.2.1 dev eth0\n'
        else
            printf 'default via 192.0.2.1 dev eth0\n'
        fi
        [[ $FAIL_STAGE == default ]] && exit 7
        exit 0
        ;;
    '-brief link show up')
        [[ $HANG_STAGE == link ]] && hang
        printf 'eth0 UP\n'
        ;;
    '-4 route get 192.0.2.10')
        [[ $HANG_STAGE == route ]] && hang
        if [[ -n $ROUTE_TYPE ]]; then
            printf '%s 192.0.2.10 dev eth0\n' "$ROUTE_TYPE"
        elif [[ $MALFORM_STAGE == route ]]; then
            printf 'garbage route output\n'
        else
            printf '192.0.2.10 via 192.0.2.1 dev eth0\n'
        fi
        [[ $FAIL_STAGE == route ]] && exit 7
        exit 0
        ;;
    *) exit 1 ;;
esac
""",
                encoding="utf-8",
            )
            fake_getent.write_text(
                """#!/usr/bin/env bash
if [[ $HANG_STAGE == resolution ]]; then
    printf '%s\n' "$$" > "$PID_FILE"
    trap '' TERM
    while :; do :; done
fi
if [[ $MALFORM_STAGE == resolution ]]; then
    printf 'not-an-ip STREAM example.invalid\n'
else
    printf '192.0.2.10 STREAM example.invalid\n'
fi
[[ $FAIL_STAGE == resolution ]] && exit 7
exit 0
""",
                encoding="utf-8",
            )
            fake_ping.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            fake_ip.chmod(0o755)
            fake_getent.chmod(0o755)
            fake_ping.chmod(0o755)
            for stage, target, expected, message in (
                ("default", [], 2, "default-route query timed out"),
                ("link", ["example.invalid"], 2, "Interface query: unavailable"),
                ("resolution", ["example.invalid"], 1, "Resolution: timed out"),
                ("route", ["example.invalid"], 1, "Route: query timed out"),
            ):
                pid_file = fake_directory / f"{stage}.pid"
                environment = os.environ.copy()
                environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
                environment["HANG_STAGE"] = stage
                environment["PID_FILE"] = str(pid_file)
                started = time.monotonic()
                timed_out = run_with_group_deadline(
                    [str(ROOT / "scripts/bash/network-check.sh"), "--timeout", "1", *target],
                    expected=expected,
                    deadline=4,
                    env=environment,
                )
                elapsed = time.monotonic() - started
                if elapsed > 3 or message not in timed_out.stdout + timed_out.stderr:
                    raise AssertionError(
                        f"network {stage} query did not honour its timeout: "
                        f"elapsed={elapsed:.3f}s, stdout={timed_out.stdout!r}, "
                        f"stderr={timed_out.stderr!r}"
                    )
                child_pid = int(pid_file.read_text(encoding="utf-8").strip())
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    raise AssertionError(f"network {stage} timeout left its child running")

            for stage, message in (
                ("resolution", "Resolution: failed (collector status 7)"),
                ("route", "Route: unavailable (collector status 7)"),
            ):
                environment = os.environ.copy()
                environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
                environment["HANG_STAGE"] = ""
                environment["FAIL_STAGE"] = stage
                failed = run(
                    [
                        str(ROOT / "scripts/bash/network-check.sh"),
                        "--timeout",
                        "1",
                        "example.invalid",
                    ],
                    expected=1,
                    env=environment,
                )
                if message not in failed.stdout:
                    raise AssertionError(
                        f"network {stage} accepted plausible output from a failed collector"
                    )

            for stage, message in (
                ("resolution", "Resolution: invalid IPv4 address from collector"),
                ("route", "Route: malformed collector output"),
            ):
                environment = os.environ.copy()
                environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
                environment["HANG_STAGE"] = ""
                environment["FAIL_STAGE"] = ""
                environment["MALFORM_STAGE"] = stage
                malformed = run(
                    [
                        str(ROOT / "scripts/bash/network-check.sh"),
                        "--timeout",
                        "1",
                        "example.invalid",
                    ],
                    expected=1,
                    env=environment,
                )
                if message not in malformed.stdout or "Status: healthy" in malformed.stdout:
                    raise AssertionError(
                        f"network {stage} accepted malformed successful collector output"
                    )

            for malformed_stage, message in (
                ("default", "invalid IPv4 gateway"),
                ("default-prefix", "no single IPv4 default gateway"),
                ("default-prefix-mixed", "no single IPv4 default gateway"),
            ):
                environment = os.environ.copy()
                environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
                environment["HANG_STAGE"] = ""
                environment["FAIL_STAGE"] = ""
                environment["MALFORM_STAGE"] = malformed_stage
                malformed_default = run(
                    [str(ROOT / "scripts/bash/network-check.sh"), "--timeout", "1"],
                    expected=2,
                    env=environment,
                )
                if message not in malformed_default.stderr or "Status: healthy" in malformed_default.stdout:
                    raise AssertionError(
                        f"network check accepted malformed default-route output: {malformed_stage}"
                    )

            for route_type in ("local", "broadcast", "multicast", "anycast", "unicast"):
                environment = os.environ.copy()
                environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
                environment["HANG_STAGE"] = ""
                environment["FAIL_STAGE"] = ""
                environment["MALFORM_STAGE"] = ""
                environment["ROUTE_TYPE"] = route_type
                typed_route = run(
                    [
                        str(ROOT / "scripts/bash/network-check.sh"),
                        "--timeout",
                        "1",
                        "example.invalid",
                    ],
                    env=environment,
                )
                if f"Route: {route_type} 192.0.2.10 dev eth0" not in typed_route.stdout:
                    raise AssertionError(f"network check rejected valid {route_type} route output")

        with tempfile.TemporaryDirectory() as directory:
            fake_directory = Path(directory)
            fake_ip = fake_directory / "ip"
            fake_ip.write_text(
                "#!/usr/bin/env bash\n"
                "if [[ $* == '-4 route show default' ]]; then\n"
                "    printf 'default dev ppp0 scope link\\n'\n"
                "    exit 0\n"
                "fi\n"
                "exit 1\n",
                encoding="utf-8",
            )
            fake_ip.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
            on_link = run(
                [str(ROOT / "scripts/bash/network-check.sh"), "--timeout", "1"],
                expected=2,
                env=environment,
            )
            if "Supply an explicit target" not in on_link.stderr:
                raise AssertionError("on-link default route did not request an explicit target")
    else:
        skip_or_fail("Bash network smoke check (ip, getent, ping or timeout unavailable)")

    if Path("/run/systemd/system").is_dir() and shutil.which("ip"):
        with tempfile.TemporaryDirectory() as directory:
            fake_directory = Path(directory)
            fake_systemctl = fake_directory / "systemctl"
            fake_systemctl.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
            fake_systemctl.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
            health = run(
                [str(ROOT / "scripts/bash/system-health.sh")],
                expected=2,
                env=environment,
            )
            if "systemctl query failed" not in health.stdout:
                raise AssertionError("system health concealed a failed systemctl query")
            service = run(
                [str(ROOT / "scripts/bash/service-check.sh"), "example.service"],
                expected=2,
                env=environment,
            )
            if "systemctl query failed" not in service.stderr:
                raise AssertionError("service check concealed a failed systemctl query")

        with tempfile.TemporaryDirectory() as directory:
            fake_directory = Path(directory)
            fake_systemctl = fake_directory / "systemctl"
            fake_systemctl.write_text(
                "#!/usr/bin/env bash\n"
                "printf 'LoadState=\\nActiveState=\\nSubState=\\n'\n",
                encoding="utf-8",
            )
            fake_systemctl.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
            service = run(
                [str(ROOT / "scripts/bash/service-check.sh"), "example.service"],
                expected=2,
                env=environment,
            )
            if "incomplete systemctl response" not in service.stderr:
                raise AssertionError("service check accepted empty systemctl properties")

        with tempfile.TemporaryDirectory() as directory:
            fake_directory = Path(directory)
            fake_systemctl = fake_directory / "systemctl"
            fake_df = fake_directory / "df"
            fake_ip = fake_directory / "ip"
            fake_hostname = fake_directory / "hostname"
            fake_systemctl.write_text(
                "#!/usr/bin/env bash\n"
                "if [[ $1 == '--failed' ]]; then exit 0; fi\n"
                "if [[ $1 == 'show' ]]; then\n"
                "    if [[ $SERVICE_STATE == warning ]]; then\n"
                "        printf 'LoadState=loaded\\nActiveState=inactive\\nSubState=dead\\n'\n"
                "    else\n"
                "        printf 'LoadState=loaded\\nActiveState=active\\nSubState=running\\n'\n"
                "    fi\n"
                "    exit 0\n"
                "fi\n"
                "exit 1\n",
                encoding="utf-8",
            )
            fake_df.write_text(
                "#!/usr/bin/env bash\n"
                "printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\\n'\n"
                "printf '/dev/fake 100 10 90 10%% /\\n'\n",
                encoding="utf-8",
            )
            fake_ip.write_text(
                "#!/usr/bin/env bash\nprintf 'eth0 DOWN\\n'\n",
                encoding="utf-8",
            )
            fake_hostname.write_text(
                "#!/usr/bin/env bash\nprintf 'test-host\\n'\n",
                encoding="utf-8",
            )
            for executable in (fake_systemctl, fake_df, fake_ip, fake_hostname):
                executable.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
            environment["SERVICE_STATE"] = "healthy"

            healthy_system = run(
                [
                    str(ROOT / "scripts/bash/system-health.sh"),
                    "--disk-warning",
                    "100",
                    "--memory-warning",
                    "100",
                ],
                env=environment,
            )
            if "inventory only; carrier state not evaluated" not in healthy_system.stdout:
                raise AssertionError("system health presented administrative state as link health")
            run(
                [
                    str(ROOT / "scripts/bash/system-health.sh"),
                    "--disk-warning",
                    "1",
                    "--memory-warning",
                    "100",
                ],
                expected=1,
                env=environment,
            )
            run(
                [str(ROOT / "scripts/bash/disk-check.sh"), "--warning", "1", "/"],
                expected=1,
                env=environment,
            )
            run(
                [str(ROOT / "scripts/bash/service-check.sh"), "example.service"],
                env=environment,
            )
            environment["SERVICE_STATE"] = "warning"
            run(
                [str(ROOT / "scripts/bash/service-check.sh"), "example.service"],
                expected=1,
                env=environment,
            )
    else:
        skip_or_fail("Bash systemd failure-path checks (active systemd or ip unavailable)")

    with tempfile.TemporaryDirectory() as directory:
        fake_directory = Path(directory)
        fake_df = fake_directory / "df"
        fake_df.write_text(
            "#!/usr/bin/env bash\n"
            "printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\\n'\n"
            "printf '/dev/fake 100 10 90 10%% /\\n'\n"
            "exit 7\n",
            encoding="utf-8",
        )
        fake_df.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
        disk = run(
            [str(ROOT / "scripts/bash/disk-check.sh"), "--warning", "100", "/"],
            expected=2,
            env=environment,
        )
        if "df query failed" not in disk.stderr:
            raise AssertionError("disk check concealed a failed df query")
        health = run(
            [str(ROOT / "scripts/bash/system-health.sh")],
            expected=2,
            env=environment,
        )
        if "df query failed" not in health.stdout:
            raise AssertionError("system health concealed a failed df query")

        fake_df.write_text(
            "#!/usr/bin/env bash\n"
            "printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\\n'\n"
            "printf '/dev/fake 100 not-a-number 90 10%% /\\n'\n",
            encoding="utf-8",
        )
        invalid_disk = run(
            [str(ROOT / "scripts/bash/disk-check.sh"), "--warning", "100", "/"],
            expected=2,
            env=environment,
        )
        if "unexpected df output" not in invalid_disk.stderr:
            raise AssertionError("disk check accepted a nonnumeric used-capacity field")

        fake_df.write_text(
            "#!/usr/bin/env bash\n"
            "printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\\n'\n"
            "printf '/dev/fake 100 10 90 invalid%% /\\n'\n",
            encoding="utf-8",
        )
        invalid_health = run(
            [str(ROOT / "scripts/bash/system-health.sh")],
            expected=2,
            env=environment,
        )
        if "Disk / used: unavailable" not in invalid_health.stdout:
            raise AssertionError("system health accepted a malformed disk percentage")


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

    with tempfile.NamedTemporaryFile("wb", delete=False) as large_line_file:
        large_line_file.write(b"INFO\n" + (b"X" * 1000))
        large_line_path = Path(large_line_file.name)
    try:
        bounded = run(
            [
                sys.executable,
                str(scripts / "log_summary.py"),
                "--max-bytes",
                "50",
                str(large_line_path),
            ]
        )
        for expected_line in ("Bytes read: 5", "Lines read: 1", "Input truncated: yes"):
            if expected_line not in bounded.stdout:
                raise AssertionError(f"byte-bounded log summary is missing {expected_line}")
    finally:
        large_line_path.unlink(missing_ok=True)

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
        with tempfile.TemporaryDirectory() as directory:
            fake_directory = Path(directory)
            fake_ping = fake_directory / "ping"
            fake_ping.write_text(
                "#!/usr/bin/env bash\ntrap '' TERM\nwhile :; do :; done\n",
                encoding="utf-8",
            )
            fake_ping.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_directory}:{environment['PATH']}"
            started = time.monotonic()
            timed_ping = run(
                [
                    sys.executable,
                    str(scripts / "host_check.py"),
                    "--timeout",
                    "0.2",
                    "127.0.0.1",
                ],
                expected=1,
                env=environment,
            )
            elapsed = time.monotonic() - started
            if elapsed > 0.8 or "command exceeded 0.2s" not in timed_ping.stdout:
                raise AssertionError(
                    f"host ICMP deadline failed: elapsed={elapsed:.3f}s, "
                    f"stdout={timed_ping.stdout!r}"
                )
    else:
        skip_or_fail("Python host smoke check (ping unavailable)")

    run([sys.executable, str(scripts / "port_check.py"), "127.0.0.1", "70000"], expected=2)

    host_platform_check = f"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('host_module', {str(scripts / 'host_check.py')!r})
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
module.platform.system = lambda: 'Darwin'
sys.argv = ['host_check.py', '127.0.0.1']
if module.main() != 2:
    raise SystemExit('unsupported host platform did not return 2')
"""
    run([sys.executable, "-c", host_platform_check])

    port_deadline_check = f"""
import importlib.util
import sys
import time

spec = importlib.util.spec_from_file_location('port_module', {str(scripts / 'port_check.py')!r})
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
addresses = [
    (module.socket.AF_INET, module.socket.SOCK_STREAM, 0, '', ('192.0.2.10', 443)),
    (module.socket.AF_INET, module.socket.SOCK_STREAM, 0, '', ('192.0.2.10', 443)),
    (module.socket.AF_INET, module.socket.SOCK_STREAM, 0, '', ('192.0.2.11', 443)),
]
module.resolve = lambda *args, **kwargs: addresses

class SlowSocket:
    calls = 0
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def settimeout(self, timeout):
        self.timeout = timeout
    def connect(self, address):
        type(self).calls += 1
        if address[0] == '192.0.2.10':
            time.sleep(self.timeout + 0.01)
            raise TimeoutError('simulated black hole')

module.socket.socket = lambda *args, **kwargs: SlowSocket()
sys.argv = ['port_check.py', '--timeout', '0.2', 'example.invalid', '443']
started = time.monotonic()
result = module.main()
elapsed = time.monotonic() - started
if result != 0 or elapsed > 0.6 or SlowSocket.calls != 2:
    raise SystemExit(f'fair TCP deadline failed: rc={{result}}, elapsed={{elapsed}}, calls={{SlowSocket.calls}}')
"""
    run([sys.executable, "-c", port_deadline_check])

    for script_name, resolve_call in (
        ("host_check.py", "module.resolve('example.invalid', module.socket.AF_INET, 0.2)"),
        ("port_check.py", "module.resolve('example.invalid', 443, module.socket.AF_INET, 0.2)"),
    ):
        module_path = scripts / script_name
        timeout_check = f"""
import importlib.util
import time

spec = importlib.util.spec_from_file_location('checked_module', {str(module_path)!r})
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

def slow_resolution(*args, **kwargs):
    time.sleep(5)
    return []

module.socket.getaddrinfo = slow_resolution
started = time.monotonic()
try:
    {resolve_call}
except TimeoutError:
    pass
else:
    raise SystemExit('resolution did not time out')
if time.monotonic() - started > 1:
    raise SystemExit('resolution deadline was not bounded')
"""
        run([sys.executable, "-c", timeout_check])


def test_powershell() -> None:
    if not shutil.which("pwsh"):
        skip_or_fail("PowerShell smoke checks (pwsh unavailable)")
        return

    run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            "if ($PSVersionTable.PSVersion -lt [version]'7.4') { exit 1 }",
        ]
    )

    scripts = ROOT / "scripts/powershell"
    attempt_budget_check = f"""
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    {str(scripts / 'Test-NetworkHealth.ps1')!r},
    [ref]$tokens,
    [ref]$errors
)
$functions = $ast.FindAll({{
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $node.Name -in @('Get-RemainingMillisecond', 'Get-AddressAttemptMillisecond')
}}, $true)
foreach ($function in $functions) {{ Invoke-Expression $function.Extent.Text }}
$TimeoutSeconds = 2
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$firstShare = Get-AddressAttemptMillisecond -RemainingAddressCount 2
if ($firstShare -le 0 -or $firstShare -gt 1000) {{
    throw "first address received an unfair budget: $firstShare ms"
}}
"""
    run(["pwsh", "-NoProfile", "-Command", attempt_budget_check])

    run(
        [
            "pwsh",
            "-NoProfile",
            "-File",
            str(scripts / "Test-NetworkHealth.ps1"),
            "-Target",
            "127.0.0.1",
            "-TimeoutSeconds",
            "1",
        ]
    )

    try:
        ipv4_localhost = socket.getaddrinfo(
            "localhost", 0, socket.AF_INET, socket.SOCK_STREAM
        )
        ipv6_localhost = socket.getaddrinfo(
            "localhost", 0, socket.AF_INET6, socket.SOCK_STREAM
        )
    except OSError:
        ipv4_localhost = []
        ipv6_localhost = []

    if socket.has_ipv6 and ipv4_localhost and ipv6_localhost:
        listener = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        listener.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("::1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        thread = threading.Thread(target=accept_once, args=(listener,), daemon=True)
        thread.start()
        try:
            fallback = run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    str(scripts / "Test-NetworkHealth.ps1"),
                    "-Target",
                    "localhost",
                    "-Port",
                    str(port),
                    "-SkipPing",
                    "-TimeoutSeconds",
                    "2",
                ]
            )
            if "failed" not in fallback.stdout or "connection succeeded" not in fallback.stdout:
                raise AssertionError("PowerShell TCP check did not fall back to a later address")
        finally:
            listener.close()
            thread.join(timeout=2)
    else:
        skip_or_fail("PowerShell multi-address fallback check (dual-stack localhost unavailable)")

    system_prelude = r"""
$env:OS = 'Windows_NT'
$env:COMPUTERNAME = 'test-host'
$env:SystemDrive = 'C:'
function Get-Date { [datetime]'2026-08-10T12:00:00Z' }
function Get-CimInstance {
    param([string]$ClassName, [string]$Filter)
    switch ($ClassName) {
        'Win32_OperatingSystem' { [pscustomobject]@{ LastBootUpTime = [datetime]'2026-08-05T20:00:00Z'; TotalVisibleMemorySize = 1000; FreePhysicalMemory = 500 } }
        'Win32_Processor' { [pscustomobject]@{ LoadPercentage = 10 } }
        'Win32_LogicalDisk' { [pscustomobject]@{ DeviceID = 'C:'; Size = 100GB; FreeSpace = 50GB } }
    }
}
"""
    system_health = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            system_prelude + f"& '{scripts / 'Get-SystemHealth.ps1'}'; exit $LASTEXITCODE",
        ]
    )
    if "Uptime: 4d 16h 00m" not in system_health.stdout:
        raise AssertionError("system health rounded partial uptime days")

    empty_processor = system_prelude.replace(
        "'Win32_Processor' { [pscustomobject]@{ LoadPercentage = 10 } }",
        "'Win32_Processor' { @() }",
    )
    run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            empty_processor + f"& '{scripts / 'Get-SystemHealth.ps1'}'; exit $LASTEXITCODE",
        ],
        expected=2,
    )

    missing_system_volume = system_prelude.replace("DeviceID = 'C:'", "DeviceID = 'D:'")
    missing_system = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            missing_system_volume
            + f"& '{scripts / 'Get-SystemHealth.ps1'}'; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "not returned as a fixed volume" not in missing_system.stdout:
        raise AssertionError("system health accepted a missing system-volume record")

    for impossible_value in (
        system_prelude.replace("LoadPercentage = 10", "LoadPercentage = 150"),
        system_prelude.replace("FreePhysicalMemory = 500", "FreePhysicalMemory = 2000"),
        system_prelude.replace("FreeSpace = 50GB", "FreeSpace = 200GB"),
    ):
        run(
            [
                "pwsh",
                "-NoProfile",
                "-Command",
                impossible_value
                + f"& '{scripts / 'Get-SystemHealth.ps1'}'; exit $LASTEXITCODE",
            ],
            expected=2,
        )

    wildcard_service_prelude = system_prelude + r"""
function Get-Service {
    @(
        [pscustomobject]@{ Name = 'Alpha'; DisplayName = 'Alpha'; Status = 'Running' },
        [pscustomobject]@{ Name = 'Beta'; DisplayName = 'Beta'; Status = 'Stopped' }
    )
}
"""
    wildcard_services = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            system_prelude
            + f"& '{scripts / 'Get-SystemHealth.ps1'}' -ServiceName '*'; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "literal service names" not in wildcard_services.stderr:
        raise AssertionError("system health accepted a wildcard service name")

    ambiguous_services = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            wildcard_service_prelude
            + f"& '{scripts / 'Get-SystemHealth.ps1'}' -ServiceName Demo; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "expected one service record" not in ambiguous_services.stdout:
        raise AssertionError("system health accepted multiple records for a literal service")

    system_access_prelude = system_prelude + r"""
function Get-Service { throw 'Access denied' }
"""
    system_access = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            system_access_prelude
            + f"& '{scripts / 'Get-SystemHealth.ps1'}' -ServiceName Demo; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "collection failed" not in system_access.stdout or "Status: incomplete" not in system_access.stdout:
        raise AssertionError("system health treated service access failure as a warning")

    system_missing_prelude = system_prelude + r"""
function Get-Service {
    Write-Error 'Service was not found' -ErrorId NoServiceFoundForGivenName -Category ObjectNotFound -ErrorAction Stop
}
"""
    system_missing = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            system_missing_prelude
            + f"& '{scripts / 'Get-SystemHealth.ps1'}' -ServiceName Demo; exit $LASTEXITCODE",
        ],
        expected=1,
    )
    if "Service Demo: not found" not in system_missing.stdout or "Status: warning" not in system_missing.stdout:
        raise AssertionError("system health did not classify a missing service as a warning")

    system_dollar_service_prelude = system_prelude + r"""
function Get-Service {
    [pscustomobject]@{ Name = 'MSSQL$SQLEXPRESS'; DisplayName = 'SQL Server (SQLEXPRESS)'; Status = 'Running' }
}
"""
    run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            system_dollar_service_prelude
            + f"& '{scripts / 'Get-SystemHealth.ps1'}' -ServiceName 'MSSQL$SQLEXPRESS'; exit $LASTEXITCODE",
        ]
    )

    service_prelude = r"""
$env:OS = 'Windows_NT'
function Get-Service { [pscustomobject]@{ Name = 'Demo'; DisplayName = 'Demo'; Status = 'Running' } }
function Get-CimInstance { throw 'CIM unavailable' }
"""
    service = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            service_prelude + f"& '{scripts / 'Get-ServiceHealth.ps1'}' -Name Demo; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "configuration unavailable" not in service.stdout:
        raise AssertionError("service configuration failure was not reported as incomplete")

    service_access_prelude = r"""
$env:OS = 'Windows_NT'
function Get-Service { throw 'Access denied' }
"""
    service_access = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            service_access_prelude
            + f"& '{scripts / 'Get-ServiceHealth.ps1'}' -Name Demo; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "collection failed" not in service_access.stdout:
        raise AssertionError("service health treated access failure as a warning")

    service_missing_prelude = r"""
$env:OS = 'Windows_NT'
function Get-Service {
    Write-Error 'Service was not found' -ErrorId NoServiceFoundForGivenName -Category ObjectNotFound -ErrorAction Stop
}
"""
    service_missing = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            service_missing_prelude
            + f"& '{scripts / 'Get-ServiceHealth.ps1'}' -Name Demo; exit $LASTEXITCODE",
        ],
        expected=1,
    )
    if "Service Demo: not found" not in service_missing.stdout:
        raise AssertionError("service health did not classify a missing service as a warning")

    service_dollar_prelude = r"""
$env:OS = 'Windows_NT'
function Get-Service {
    [pscustomobject]@{ Name = 'MSSQL$SQLEXPRESS'; DisplayName = 'SQL Server (SQLEXPRESS)'; Status = 'Running' }
}
function Get-CimInstance { [pscustomobject]@{ StartMode = 'Auto' } }
"""
    dollar_service = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            service_dollar_prelude
            + f"& '{scripts / 'Get-ServiceHealth.ps1'}' -Name 'MSSQL$SQLEXPRESS'; exit $LASTEXITCODE",
        ]
    )
    if "Service: MSSQL$SQLEXPRESS" not in dollar_service.stdout:
        raise AssertionError("service health rejected a valid literal service name containing a dollar sign")

    wql_escape_prelude = r"""
$env:OS = 'Windows_NT'
function Get-Service {
    param([string]$Name)
    [pscustomobject]@{ Name = $Name; DisplayName = $Name; Status = 'Running' }
}
function Get-CimInstance {
    param([string]$ClassName, [string]$Filter)
    Write-Host "FILTER:$Filter"
    [pscustomobject]@{ StartMode = 'Auto' }
}
"""
    wql_escape_service = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            wql_escape_prelude
            + rf'''& '{scripts / 'Get-ServiceHealth.ps1'}' -Name 'O''Brien\Quoted"Service'; exit $LASTEXITCODE''',
        ]
    )
    expected_wql_filter = r'''FILTER:Name = 'O\'Brien\\Quoted\"Service' '''.rstrip()
    if expected_wql_filter not in wql_escape_service.stdout:
        raise AssertionError(
            "service health did not backslash-escape WQL string characters:\n"
            f"{wql_escape_service.stdout}"
        )

    wildcard_service = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            service_dollar_prelude
            + f"& '{scripts / 'Get-ServiceHealth.ps1'}' -Name '*'; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "invalid literal name" not in wildcard_service.stdout:
        raise AssertionError("service health accepted a wildcard service name")

    empty_service = run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            service_dollar_prelude
            + f"& '{scripts / 'Get-ServiceHealth.ps1'}' -Name ''; exit $LASTEXITCODE",
        ],
        expected=2,
    )
    if "invalid literal name" not in empty_service.stdout:
        raise AssertionError(
            "service health did not classify an empty name as invalid input"
        )

    disk_prelude = r"""
$env:OS = 'Windows_NT'
function Get-CimInstance { @() }
"""
    run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            disk_prelude + f"& '{scripts / 'Get-DiskHealth.ps1'}'; exit $LASTEXITCODE",
        ],
        expected=2,
    )

    impossible_disk_prelude = r"""
$env:OS = 'Windows_NT'
function Get-CimInstance { [pscustomobject]@{ DeviceID = 'C:'; Size = 100; FreeSpace = 200 } }
"""
    run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            impossible_disk_prelude
            + f"& '{scripts / 'Get-DiskHealth.ps1'}'; exit $LASTEXITCODE",
        ],
        expected=2,
    )


def main() -> int:
    global STRICT
    arguments = sys.argv[1:]
    if any(argument != "--strict" for argument in arguments) or len(arguments) > 1:
        print("Usage: python3 tests/smoke-tools.py [--strict]", file=sys.stderr)
        return 2
    STRICT = "--strict" in arguments
    test_validator_regressions()
    test_release_gate()
    test_bash()
    test_python()
    test_powershell()
    print("Tool smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
