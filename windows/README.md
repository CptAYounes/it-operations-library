# Windows operations notes

This section covers installing, checking and recovering current Windows clients and servers. It is arranged around practical jobs rather than the layout of Control Panel.

## Platform and command scope

The procedures target supported Windows 11 releases and Windows Server 2022/2025. Build-specific behaviour, hardware support and servicing status still need to be checked against Microsoft's current documentation before a change. Windows 10 examples are not the baseline because its general support lifecycle has ended.

GUI paths are written for Windows 11 and **Windows Server with Desktop Experience**. Server Core has no equivalent desktop workflow; use the stated PowerShell, command-line or `sconfig` route. Features also vary by edition:

- Windows Home cannot join an Active Directory domain and omits some management tools found in Pro and Enterprise.
- BitLocker management, Group Policy, Hyper-V, Remote Desktop hosting and business update controls depend on edition and installed features. Some Home devices expose **Device encryption** instead of the full BitLocker interface.
- Windows Server does not provide every client recovery or Settings feature. In particular, do not assume that **Reset this PC** exists on a server.
- PowerShell examples use built-in Windows modules. Windows PowerShell 5.1 and PowerShell 7 do not load every Windows module in exactly the same way.

Command forms have been reviewed as documentation, but the Windows-specific cmdlets were not execution-tested on this Linux authoring host. Treat sample output and available properties as version-dependent.

## Safety labels

These notes put observation before repair. Labels mean:

- **Read-only** — queries current state and should not change system configuration.
- **Change** — alters configuration, starts/stops a component, or may interrupt a connection.
- **Offline/WinRE** — runs against a non-booted installation or from Windows Recovery Environment. Drive letters may differ from normal Windows.
- **Destructive** — can remove data, applications, configuration or boot metadata. Verify the target, backup and authority first.

A read-only command can still expose usernames, hostnames, addresses or application data. Review captured output before publishing it.

## Contents

| ID | Guide | Main use |
|---|---|---|
| W01 | [Install Windows](installation/windows-installation-checklist.md) | Prepare, perform and validate a clean installation |
| W02 | [Post-install configuration](configuration/post-install-configuration.md) | Establish a supportable baseline |
| W03 | [Driver and device validation](configuration/driver-device-validation.md) | Resolve missing, failed or unexpected devices |
| W04 | [Update and patch validation](maintenance/update-patch-validation.md) | Prove that an update completed and the host still works |
| W05 | [Boot troubleshooting](troubleshooting/boot-troubleshooting.md) | Locate a failure between firmware and sign-in |
| W06 | [Event Viewer practical guide](event-logs/event-viewer-practical-guide.md) | Find and preserve relevant Windows events |
| W07 | [Service troubleshooting](services/service-troubleshooting.md) | Investigate a stopped or unhealthy service |
| W08 | [Network diagnostics](networking/network-diagnostics.md) | Isolate local, routing, DNS and port faults |
| W09 | [Storage and filesystem diagnostics](storage/storage-filesystem-diagnostics.md) | Check capacity, device and filesystem health |
| W10 | [Performance investigation](troubleshooting/performance-investigation.md) | Gather evidence for CPU, memory, disk and latency symptoms |
| W11 | [PowerShell administration reference](configuration/powershell-administration-reference.md) | Use PowerShell safely for common observations |
| W12 | [Recovery options](troubleshooting/recovery-options.md) | Choose the least disruptive suitable recovery route |

For a short installation release gate, use the repository-level [Windows installation checklist](../checklists/windows-installation.md). It links back to W01 for the full method.
