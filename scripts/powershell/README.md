# PowerShell diagnostic tools

The PowerShell tools collect evidence; they do not repair faults or change configuration. All four require PowerShell 7.4 or later (`pwsh`), not the Windows PowerShell 5.1 inbox runtime. Windows-only scripts use CIM and built-in service cmdlets. `Test-NetworkHealth.ps1` is cross-platform.

All four scripts were parsed with PowerShell 7.6.4 on Debian GNU/Linux 13, and `Test-NetworkHealth.ps1` was executed there. Windows-only logic was checked with mocked CIM/service data, but the system, service and disk scripts have not been executed against native Windows providers. Validate them on the intended Windows build before operational use.

Output blocks are illustrative and use synthetic names, addresses and capacities.

The examples assume the current directory is `scripts/powershell`. Run from a PowerShell prompt. If local policy permits scripts, a typical invocation is:

```powershell
pwsh -NoProfile -File ./Get-SystemHealth.ps1
```

Do not weaken an organisation's execution policy merely to run these tools.

Normal use does not request elevation, but local policy can restrict CIM, service and volume queries. The network tool also requires permission to make DNS, ICMP and TCP probes to the selected target. Treat access denied as incomplete evidence rather than rerunning with broader privilege by reflex.

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

- Exit `0` means no threshold warning, `1` means a capacity or service warning, and `2` means collection could not complete.
- Service names are literal; wildcard characters are rejected. A requested service that is not found is a warning, while access/provider failure makes collection incomplete.
- Missing processor, memory or fixed-volume data cannot produce a healthy result, and the actual system volume must be present.
- CPU load is a point-in-time CIM value, not a sustained performance baseline.

## `Test-NetworkHealth.ps1`

Performs DNS resolution, a bounded ICMP check and, when requested, a TCP connection.

```powershell
./Test-NetworkHealth.ps1 -Target example.org -Port 443 -TimeoutSeconds 3
```

```text
Target: example.org
Resolved address: 192.0.2.10
TCP 192.0.2.10:443: connection succeeded
ICMP 192.0.2.10: reply in 24 ms
Status: reachable
```

A reachable TCP port on any resolved address returns `0` even if ICMP is filtered; a negative or timed-out requested check returns `1`, and an invalid option combination returns `2`. One overall timeout covers DNS and all resolved addresses, without allowing an unresponsive first address to consume the whole check. The tool does not negotiate TLS or send an application request, so it cannot establish application health. Use only against systems you are authorised to check.

## `Get-ServiceHealth.ps1`

Reports Windows service state and configured start mode.

```powershell
./Get-ServiceHealth.ps1 -Name W32Time,Dnscache
```

```text
Service: W32Time | display: Windows Time | status: Running | start: Manual | result: healthy
Service: Dnscache | display: DNS Client | status: Running | start: Auto | result: healthy
```

A stopped or missing service returns `1`; access/provider failure, an incomplete configuration query, rejected wildcard/empty input or an unsupported platform returns `2`. Literal Windows service names are passed through without an artificial character whitelist. Not every installed service should run continuously; compare the result with its trigger and start mode before treating it as a fault.

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
