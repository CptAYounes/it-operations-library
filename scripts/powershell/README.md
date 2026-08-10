# PowerShell diagnostic tools

The PowerShell tools collect evidence; they do not repair faults or change configuration. Windows-only scripts use CIM and built-in service cmdlets. `Test-NetworkHealth.ps1` is cross-platform under PowerShell 7.

All four scripts were parsed with PowerShell 7.6.4 on Debian GNU/Linux 13. `Test-NetworkHealth.ps1` was also executed there. The CIM-based system, service and disk scripts have not been executed on Windows in this repository build, so their Windows behaviour should be validated in a lab before relying on them operationally.

Output blocks are illustrative and use synthetic names, addresses and capacities.

The examples assume the current directory is `scripts/powershell`. Run from a PowerShell prompt. If local policy permits scripts, a typical invocation is:

```powershell
pwsh -NoProfile -File ./Get-SystemHealth.ps1
```

Do not weaken an organisation's execution policy merely to run these tools.

## `Get-SystemHealth.ps1`

Collects Windows uptime, CPU load, available memory, fixed-volume free space and optional service state.

```powershell
./Get-SystemHealth.ps1 -DiskWarningPercent 15 -ServiceName W32Time,Dnscache
```

Example shape:

```text
Computer: LAB-WS01
Uptime: 4d 07h 12m
CPU load: 8%
Memory free: 61.2% (warning below 10%)
Volume C: | 48.3% free (118.6 GiB; warning below 15%)
Service W32Time: Running
Status: healthy
```

Exit `0` means no threshold warning, `1` means a capacity or service warning, and `2` means collection could not complete. CPU load is a point-in-time CIM value rather than a sustained performance baseline.

## `Test-NetworkHealth.ps1`

Performs DNS resolution, a bounded ICMP check and, when requested, a TCP connection.

```powershell
./Test-NetworkHealth.ps1 -Target example.org -Port 443 -TimeoutSeconds 3
```

```text
Target: example.org
Resolved address: 192.0.2.10
ICMP: reply in 24 ms
TCP 443: connection succeeded
Status: reachable
```

A reachable TCP port returns `0` even if ICMP is filtered; a negative requested check returns `1`, and the explicit invalid `-SkipPing` combination returns `2`. The tool does not negotiate TLS or send an application request, so it cannot establish application health. Use only against systems you are authorised to check.

## `Get-ServiceHealth.ps1`

Reports Windows service state and configured start mode.

```powershell
./Get-ServiceHealth.ps1 -Name W32Time,Dnscache
```

```text
Service: W32Time | display: Windows Time | status: Running | start: Manual | result: healthy
Service: Dnscache | display: DNS Client | status: Running | start: Auto | result: healthy
```

A stopped service returns `1`; a service name rejected inside the script or an unsupported platform returns `2`. PowerShell parameter-binding/validation errors happen before the script body and normally return `1`. Not every installed service should run continuously; compare the result with its trigger and start mode before treating it as a fault.

## `Get-DiskHealth.ps1`

Checks free capacity on fixed Windows volumes.

```powershell
./Get-DiskHealth.ps1 -Drive C: -FreeWarningPercent 15
```

```text
Free-space warning threshold: 15%
Volume: C: | free: 118.6 GiB of 237.9 GiB (49.9%) | status: healthy
```

Exit `0` means every selected volume is above the threshold. Exit `1` identifies a low-capacity volume or requested drive that was not found; `2` means collection could not complete. This script does not inspect SMART data, Storage Spaces health, filesystem errors or storage latency. Capacity is only one part of disk health.
