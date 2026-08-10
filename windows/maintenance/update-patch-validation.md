# W04 — Update and patch validation

Installing an update is only half the job. Validation proves which update was applied, whether a restart is still pending, and whether the system's required functions survived the change.

**Applies to:** supported Windows 11 and Windows Server 2022/2025. Windows 11 uses **Settings > Windows Update**. Server with Desktop Experience may use its configured GUI/management platform; Server Core provides `sconfig` and PowerShell/remote management routes. WSUS, Windows Update for Business and other managed platforms can override local controls.

## Define the patch event

Record:

- host and Windows edition/build;
- update source and policy channel;
- planned KB/build or update classification;
- affected applications/roles and their owner;
- backup/recovery route and maintenance authority;
- restart expectation and a functional test list;
- known hold, safeguard or compatibility notice.

Do not treat “Check for updates” as permission to install previews, drivers, firmware or a feature upgrade. Each has a different rollback and support risk.

## Pre-update checks

### Establish state

**Read-only:**

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
Get-CimInstance Win32_OperatingSystem | Select-Object LastBootUpTime
Get-Volume | Where-Object DriveLetter | Select-Object DriveLetter, HealthStatus, SizeRemaining, Size
```

Check that the system drive has suitable free space, time synchronisation is healthy, the host is on stable power, and no storage/filesystem warning is unresolved. A patch attempt is a poor diagnostic for an already unstable machine.

Capture service/application state with tests that matter to this host: listening port, sign-in, transaction, local application launch, scheduled job or management check. “Ping works” is not enough proof for an application server.

### Check restart indicators

These registry checks are **read-only** and are useful signals, not a universal Microsoft-supported “pending reboot API.” Installers can maintain their own state.

```powershell
$rebootSignals = [ordered]@{
    ComponentBasedServicing = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'
    WindowsUpdate = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
    PendingFileRename = $null -ne (Get-ItemPropertyValue -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager' -Name PendingFileRenameOperations -ErrorAction SilentlyContinue)
}
[pscustomobject]$rebootSignals
```

If a previous update is awaiting restart, finish and validate it before introducing another unrelated change.

### Confirm recovery

For a client, check WinRE availability with `reagentc /info` and confirm the BitLocker recovery-key location. For a server, confirm the approved backup/bare-metal or reinstall route. Do not suspend BitLocker by default; do so only when vendor instructions require it and the recovery key is secured.

## Install through the owned channel

Use the organisation's update service when one exists. On a standalone Windows 11 device, use **Settings > Windows Update**. On Server Core, `sconfig` is a supported interactive tool on current Server releases. Avoid scripting against undocumented `UsoClient` switches; their behaviour is not a stable administration interface.

While the update runs:

- retain exact error codes rather than paraphrasing them;
- do not power off during firmware or servicing stages;
- note each restart and whether it was expected;
- do not repeatedly press “Retry” without checking disk, network, policy and servicing evidence.

A long percentage pause alone is not proof of a hang. Check disk/CPU activity, update logs and the change's documented timing before forcing a shutdown.

## Confirm installed build and packages

After the final restart:

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption, Version, BuildNumber, LastBootUpTime

Get-HotFix |
    Sort-Object InstalledOn -Descending |
    Select-Object -First 20 HotFixID, Description, InstalledOn
```

`Get-HotFix` reads the Win32_QuickFixEngineering view and does **not** enumerate every update type. Cross-check the Windows Update history/management platform and component packages where necessary.

**Read-only — component packages:**

```text
DISM.exe /Online /Get-Packages /Format:Table
```

Use a targeted search/export rather than pasting a full package inventory into a public issue; it can expose build and language details.

## Review servicing evidence

Windows Update history is the first summary. For event detail, filter around the actual patch window:

```powershell
$start = (Get-Date).AddHours(-4)
Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = $start
    Level     = 1,2,3
} | Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message
```

Also inspect **Applications and Services Logs > Microsoft > Windows > WindowsUpdateClient > Operational** where enabled. Event IDs are meaningful only with provider, log, build and message; do not maintain a context-free list of “Windows update event IDs.”

For Windows Update log analysis, current Windows generates a readable log from ETL traces:

```powershell
Get-WindowsUpdateLog -LogPath "$env:USERPROFILE\Desktop\WindowsUpdate.log"
```

This creates a file and may require access to symbol data. Review it for hostnames, URLs and identifiers before sharing.

## Functional validation

Repeat the pre-update tests and compare results:

- [ ] expected build/KB/package is present through more than one suitable view;
- [ ] update history contains no unexplained failure;
- [ ] no restart signal remains without explanation;
- [ ] required services are running and stable;
- [ ] application/role test succeeds, not just basic connectivity;
- [ ] storage free space and health remain acceptable;
- [ ] network, remote management and scheduled work still function;
- [ ] System/Application logs have no repeating new critical/error pattern;
- [ ] a second normal restart succeeds if policy requires it.

Monitor for a period proportionate to the host and update. Immediate success does not reveal every delayed driver, scheduled-task or memory-leak regression.

## Troubleshoot before repairing

If installation fails:

1. preserve the code, KB, timestamp and update source;
2. check free space, time, network/proxy, policy and pending restart;
3. compare Windows Update history and operational events;
4. run a read-only component-store scan if corruption is plausible:

```text
DISM.exe /Online /Cleanup-Image /ScanHealth
```

`/ScanHealth` scans and records component-store corruption; it can take time but does not perform `/RestoreHealth` repairs. Only after evidence supports corruption should an administrator consider:

```text
DISM.exe /Online /Cleanup-Image /RestoreHealth
sfc.exe /scannow
```

These are **changes/repairs**, require elevation and can use Windows Update or a specified compatible repair source. Run DISM repair before SFC when servicing-store corruption is involved, capture the result, restart if directed, and rerun the failed validation.

Do not delete `SoftwareDistribution`, reset ACLs or rename servicing folders as a reflex. Those actions discard useful state and can mask policy/source faults.

## Rollback boundary

Uninstalling a quality update, rolling back a feature update or using WinRE is a **change** with security and availability consequences. Confirm:

- the update is a plausible cause from timing and evidence;
- the uninstall window/package still exists;
- the vulnerability exposure created by removal;
- BitLocker/recovery access;
- a plan to pause only the affected deployment while the cause is resolved.

Use **Settings > Windows Update > Update history > Uninstall updates** where supported, or the approved managed/WinRE route. Windows Server and feature-update rollback options differ from Windows 11. See [W12 — Recovery options](../troubleshooting/recovery-options.md) before offline recovery.

Record the post-rollback build and repeat every functional test. “It boots” is not a complete rollback validation.
