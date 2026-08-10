# W07 — Windows service troubleshooting

A service showing **Stopped** is not automatically faulty. It may be demand-started, triggered, disabled by design, or a secondary symptom of a dependency, account, storage or network failure. Begin with the required service outcome and its expected startup model.

**Applies to:** Windows 11 and Windows Server 2022/2025. `services.msc` is available on Windows client and Server with Desktop Experience. Use PowerShell, `sc.exe`, Server Manager or remote tools for Server Core.

## Immediate checks

Record service **name** (not only display name), host, symptom, impact, last known good time and recent change.

**Read-only:**

```powershell
Get-Service -Name 'ExampleService' |
    Select-Object Name, DisplayName, Status, StartType, ServicesDependedOn, DependentServices

Get-CimInstance Win32_Service -Filter "Name='ExampleService'" |
    Select-Object Name, State, StartMode, StartName, PathName, ProcessId, ExitCode
```

Replace `ExampleService` with a validated service name. A display name can be localised and may not work with every tool.

From Command Prompt or PowerShell:

```text
sc.exe queryex ExampleService
sc.exe qc ExampleService
```

In Windows PowerShell, `sc` is an alias for `Set-Content`; write `sc.exe` explicitly when invoking Service Control.

Check whether the service is actually expected to be continuously running. Trigger-start services commonly stop when idle.

## Observe the failure once

If authority and impact permit, make one controlled start attempt while watching time and error output:

```powershell
Start-Service -Name 'ExampleService' -PassThru
```

This is a **change**. Starting a database, agent or dependent service can consume resources or process queued work. Do not repeatedly start it during a crash loop.

Capture the full exception or Service Control error number. Immediately query state and events around that timestamp:

```powershell
$start = (Get-Date).AddMinutes(-10)
Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Service Control Manager'
    StartTime    = $start
} | Select-Object TimeCreated, Id, LevelDisplayName, Message
```

Then inspect the service/application's own operational or application log. Service Control Manager records the wrapper/start outcome; the application's log often contains the internal reason.

## Follow the likely branch

### Dependency not running

```powershell
Get-Service -Name 'ExampleService' -RequiredServices
Get-Service -Name 'ExampleService' -DependentServices
```

Investigate the failed dependency as its own service. Do not edit dependency lists to make the error disappear; ordering often reflects a real requirement.

### Logon failure

Read `StartName` from `Win32_Service` and check the corresponding Service Control Manager event. Do not display, reset or embed a password in command history. Verify:

- account is enabled and not locked/expired;
- **Log on as a service** right and policy source;
- credential rotation was coordinated with the service owner;
- managed service account/domain connectivity requirements;
- file, registry, certificate/private-key and network permissions.

Changing the service account is a security-sensitive **change** and may cause lockouts. Use the approved credential-management route.

### Executable or configuration failure

Review `PathName` carefully. Confirm the executable and configuration paths exist, the binary is from the expected signer/source, and the service account can read required files. Quote parsing in service paths is security-sensitive; do not “fix” it by editing the registry without vendor documentation and a rollback.

Check disk capacity, certificate validity, ports, database/dependency endpoints and application-specific configuration. A missing DLL or invalid parameter belongs to the application's support path, not a generic service restart loop.

### Starts, then stops

Correlate process ID and child processes:

```powershell
$svc = Get-CimInstance Win32_Service -Filter "Name='ExampleService'"
$svc | Select-Object Name, State, ProcessId, ExitCode
if ($svc.ProcessId -ne 0) { Get-Process -Id $svc.ProcessId }
```

A service that completes a scheduled task and stops may be healthy. For a daemon-style service, examine its own log, crash events, resource limits and recovery configuration.

### Running but unhealthy

“Running” only means the Service Control Manager sees the process in that state. Test the actual function:

- expected listener with `Get-NetTCPConnection`/`Test-NetConnection`;
- local API or health endpoint;
- application transaction or query;
- dependency reachability;
- queue/backlog and response time;
- required identity and certificate.

A port that accepts TCP is stronger than process state but still does not prove correct application behaviour.

## Check process and port ownership

```powershell
Get-CimInstance Win32_Service | Where-Object ProcessId -ne 0 |
    Sort-Object ProcessId |
    Select-Object Name, State, ProcessId, StartName

Get-NetTCPConnection -State Listen |
    Sort-Object LocalPort |
    Select-Object LocalAddress, LocalPort, OwningProcess
```

Shared-service hosts can run several services in one process. Do not kill an `svchost.exe` PID just because one hosted service is suspect.

## Safe corrective actions

Choose one based on evidence:

- start a required stopped service;
- correct a documented missing dependency/resource;
- restore a known-good application configuration;
- repair permissions through the owning product/policy;
- update or roll back the specific application/driver change;
- restart the service during an approved interruption.

```powershell
Restart-Service -Name 'ExampleService'
```

A restart is a **change** and creates downtime for that service. It can clear the symptom without finding the cause, so capture logs/state first and validate afterwards.

Changing startup type is not a generic repair:

```powershell
Set-Service -Name 'ExampleService' -StartupType Automatic
```

This **change** should match documented service design. Automatic, Automatic (Delayed Start), Manual/triggered and Disabled are not interchangeable.

## Actions to avoid as first response

- repeated restarts without capturing failure evidence;
- `taskkill /F` against shared or critical processes;
- deleting service registry keys or recreating a vendor service manually;
- broad permissions such as Everyone:Full Control;
- disabling antivirus/firewall instead of checking a specific rule/block;
- extending every service timeout to hide slow startup;
- changing account, dependencies and binary path together.

## Escalate when

- the service is part of identity, storage, security, clustering or another critical Windows role;
- credentials, certificates or domain policy require another owner;
- the process crashes and dump analysis/vendor support is needed;
- changes would interrupt other services or users;
- malware/tampering is plausible;
- restart fixes the symptom repeatedly but the cause remains unknown.

## Validate recovery

- [ ] expected startup model and current state are documented;
- [ ] the service remains stable beyond its previous failure interval;
- [ ] the real application/role function succeeds;
- [ ] dependent and downstream services recover;
- [ ] no repeating new event/error appears;
- [ ] start/restart after the next planned reboot is validated when relevant;
- [ ] change, evidence and rollback are recorded.

The closing statement should describe the function restored, not merely “service is running.”
