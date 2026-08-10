# W11 — PowerShell administration reference

This is a field reference for inspecting Windows systems without turning every query into an opaque one-liner. Examples are read-only unless marked otherwise.

**Platform:** Windows 11 and Windows Server 2022/2025. Windows PowerShell 5.1 is built into these Windows versions. PowerShell 7 is a separate, side-by-side product; some Windows-only modules use .NET Framework or are not fully compatible with PowerShell 7. Verify `$PSVersionTable`, module compatibility and the local help before relying on a command.

Windows cmdlets in this guide were not executed on the Linux authoring host. Syntax can be parsed cross-platform, but provider, CIM class and cmdlet behaviour must be validated on the intended Windows edition/build.

## Establish the session

```powershell
$PSVersionTable
Get-ExecutionPolicy -List
whoami.exe /all
```

`whoami /all` can expose account/domain/group information. Keep the output private. An “Administrator” account does not mean every process is elevated under UAC; confirm the current token and open an elevated session only when required.

Execution policy helps prevent accidental script execution; it is not a security boundary. Do not set it to `Bypass` system-wide as a troubleshooting reflex. Use signed/trusted scripts and the narrowest approved scope.

## Discover before guessing

```powershell
Get-Command -Name '*NetIP*'
Get-Command Get-NetIPConfiguration -Syntax
Get-Help Get-NetIPConfiguration -Full
Get-Help about_Quoting_Rules
Get-Module -ListAvailable
```

Local help may be incomplete until an administrator runs `Update-Help`; `Get-Help <command> -Online` opens the matching online documentation where supported. Check examples against the installed module version.

Use `Get-Member` to learn what an object actually contains:

```powershell
Get-Service | Select-Object -First 1 | Get-Member
```

PowerShell passes objects through the pipeline. Keep them as objects until final display/export; `Format-Table` produces formatting data and should normally be the last pipeline stage.

## Select, filter and sort

```powershell
Get-Service |
    Where-Object Status -eq 'Running' |
    Sort-Object DisplayName |
    Select-Object Name, DisplayName, Status
```

Filter at the source when the cmdlet supports it, especially for event logs and CIM:

```powershell
Get-CimInstance Win32_Service -Filter "State='Stopped'" |
    Select-Object Name, StartMode, StartName, ExitCode
```

Calculated properties make units explicit:

```powershell
Get-Volume | Where-Object DriveLetter |
    Select-Object DriveLetter, FileSystem,
        @{Name='FreeGiB'; Expression={[math]::Round($_.SizeRemaining / 1GB, 2)}},
        @{Name='SizeGiB'; Expression={[math]::Round($_.Size / 1GB, 2)}}
```

## Common read-only inventory

### Operating system and firmware

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption, Version, BuildNumber, OSArchitecture, LastBootUpTime
Get-CimInstance Win32_ComputerSystem |
    Select-Object Manufacturer, Model, Domain, PartOfDomain, TotalPhysicalMemory
Get-CimInstance Win32_BIOS |
    Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate
```

BIOS serial properties are intentionally omitted because they are identifying data. VM firmware classes may return synthetic or incomplete values.

### Services and processes

```powershell
Get-Service | Sort-Object Status, DisplayName
Get-CimInstance Win32_Service |
    Select-Object Name, State, StartMode, StartName, ProcessId, ExitCode
Get-Process |
    Sort-Object CPU -Descending |
    Select-Object -First 15 Name, Id, CPU, WorkingSet64, HandleCount
```

`CPU` is cumulative processor time, not instantaneous percentage.

### Network

```powershell
Get-NetAdapter
Get-NetIPConfiguration -Detailed
Get-NetRoute
Get-DnsClientServerAddress
Get-NetTCPConnection -State Listen
Test-NetConnection -ComputerName 'example.net' -Port 443 -InformationLevel Detailed
Resolve-DnsName 'example.net'
```

Addresses, suffixes and routes can reveal internal design. Redact captures before publication.

### Storage

```powershell
Get-Disk
Get-Partition
Get-Volume
Get-PhysicalDisk
```

Storage-provider health is not a substitute for controller/vendor diagnostics, especially behind RAID or USB bridges.

### Updates and event logs

```powershell
Get-HotFix | Sort-Object InstalledOn -Descending
Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = (Get-Date).AddHours(-1)
    Level     = 1,2,3
} | Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message
```

`Get-HotFix` does not list every servicing/package type. Event IDs need provider and message context.

### Files and hashes

```powershell
Get-ChildItem -LiteralPath 'C:\Evidence' -File -Recurse
Get-Item -LiteralPath 'C:\Evidence\sample.txt' | Select-Object FullName, Length, LastWriteTimeUtc
Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Evidence\sample.txt'
Select-String -LiteralPath 'C:\Logs\app.log' -Pattern 'timeout','failed'
```

A file hash proves byte identity when compared with a trusted expected hash; it does not establish that the file is safe.

## Quoting and paths

Use `-LiteralPath` when a path may contain `[` `]` `*` or `?`. Single quotes prevent variable expansion; double quotes expand variables:

```powershell
$name = 'example'
'$name'          # literal text
"Name: $name"   # expanded
```

Use the call operator for a quoted executable path:

```powershell
& 'C:\Program Files\Example\tool.exe' '--status'
```

Do not assemble a command string from untrusted input and pass it to `Invoke-Expression`. Prefer parameter binding and validated values.

## Export evidence without flattening it too early

```powershell
$data = Get-Service | Select-Object Name, DisplayName, Status, StartType
$data | Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath 'C:\Evidence\services.csv'
$data | ConvertTo-Json -Depth 3 | Set-Content -Encoding UTF8 -LiteralPath 'C:\Evidence\services.json'
```

Both commands create/overwrite output and are therefore file **changes**, although source state is read-only. Protect and review exports for service/account/host details.

For CLIXML round-tripping of PowerShell objects:

```powershell
$data | Export-Clixml -LiteralPath 'C:\Evidence\services.clixml'
$restored = Import-Clixml -LiteralPath 'C:\Evidence\services.clixml'
```

Exported credentials or secure strings have different machine/user protection semantics and must not be treated as portable secret storage. Do not export secrets for convenience.

## Error handling that preserves failure

```powershell
try {
    $result = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    $result | Select-Object Caption, Version, BuildNumber
}
catch {
    Write-Error "Operating-system query failed: $($_.Exception.Message)"
    throw
}
```

Many cmdlets emit non-terminating errors by default. `-ErrorAction Stop` lets `catch` handle them. Avoid `-ErrorAction SilentlyContinue` unless absence is expected and the script records how it distinguished absence from failure.

Check success deliberately:

```powershell
$result = Test-NetConnection -ComputerName 'example.net' -Port 443 -WarningAction SilentlyContinue
if (-not $result.TcpTestSucceeded) {
    throw 'TCP 443 test did not succeed.'
}
```

## Changes and ShouldProcess

Before a state-changing cmdlet, inspect help for `-WhatIf` and `-Confirm`:

```powershell
Get-Help Restart-Service -Full
Restart-Service -Name 'ExampleService' -WhatIf
```

`-WhatIf` previews only commands that implement `ShouldProcess`; it is not a universal sandbox and cannot predict every downstream effect. Validate target scope, recovery path and authority before replacing `-WhatIf` with execution.

Commands such as `Set-NetIPAddress`, `Remove-Item`, `Stop-Process -Force`, `Restart-Computer`, `Clear-Disk`, `Disable-NetAdapter` and service-account changes are not suitable for a generic copy/paste sequence.

## Remoting boundaries

```powershell
Test-WSMan -ComputerName 'server.example.net'
```

This tests whether WS-Management responds; it does not prove the user is authorised or that the final command will work. PowerShell remoting setup depends on client/server, domain/workgroup, network profile, HTTPS/Kerberos design and policy.

`Enable-PSRemoting`, TrustedHosts changes, firewall rules and WinRM listener creation are security-relevant **changes**. Do not enable them from a general reference. Prefer domain authentication or properly validated HTTPS design; do not add `*` to TrustedHosts merely to suppress an authentication error.

When remoting is already approved:

```powershell
Invoke-Command -ComputerName 'server.example.net' -ScriptBlock {
    Get-CimInstance Win32_OperatingSystem |
        Select-Object Caption, Version, LastBootUpTime
}
```

Avoid embedding credentials. Use the authorised identity/secret-management route and remember that remote output is deserialised.

## Logging and privacy

`Start-Transcript` can support accountability but can also capture commands, paths, output and accidentally typed secrets. Transcription policy and protected storage should be defined before enabling it. Shell history, exports and error messages deserve the same care.

When sharing output, remove or mask usernames, host/domain names, addresses, serials, certificate identifiers, activation details, tokens and recovery material. Keep an untouched restricted original when evidence integrity matters and publish only a labelled sanitised extract.
