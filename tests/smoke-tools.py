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


def run(
    command: list[str],
    expected: int = 0,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
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


def test_bash() -> None:
    scripts = sorted((ROOT / "scripts/bash").glob("*.sh"))
    run(["bash", "-n", *(str(script) for script in scripts)])
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
        printf 'default via 192.0.2.1 dev eth0\n'
        ;;
    '-brief link show up')
        [[ $HANG_STAGE == link ]] && hang
        printf 'eth0 UP\n'
        ;;
    '-4 route get 192.0.2.10')
        [[ $HANG_STAGE == route ]] && hang
        printf '192.0.2.10 via 192.0.2.1 dev eth0\n'
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
printf '192.0.2.10 STREAM example.invalid\n'
""",
                encoding="utf-8",
            )
            fake_ip.chmod(0o755)
            fake_getent.chmod(0o755)
            for stage, target, expected, message in (
                ("default", [], 2, "unable to query the IPv4 default route"),
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
                    raise AssertionError(f"network {stage} query did not honour its timeout")
                child_pid = int(pid_file.read_text(encoding="utf-8").strip())
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    raise AssertionError(f"network {stage} timeout left its child running")

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
        print("SKIP: Bash network smoke check (ip, getent, ping or timeout unavailable)")

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
    else:
        print("SKIP: Bash systemd failure-path checks (active systemd or ip unavailable)")

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
    else:
        print("SKIP: Python host smoke check (ping unavailable)")

    run([sys.executable, str(scripts / "port_check.py"), "127.0.0.1", "70000"], expected=2)

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
        print("SKIP: PowerShell smoke checks (pwsh unavailable)")
        return

    scripts = ROOT / "scripts/powershell"
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

    system_prelude = r"""
$env:OS = 'Windows_NT'
$env:COMPUTERNAME = 'test-host'
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
    test_bash()
    test_python()
    test_powershell()
    print("Tool smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
