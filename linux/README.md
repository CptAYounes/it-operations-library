# Linux operations

This section collects installation, administration and fault-finding notes for a general-purpose Linux host. The examples favour Debian 13 and systemd, but distribution-specific commands are labelled rather than treated as universal.

Start with observation: identify the host, current state and impact before changing a package, service, network rule or filesystem. `sudo` indicates elevated execution, not whether a command changes state: unprivileged commands can also create or modify files. Rely on each procedure's explicit read-only or change boundary, and check privileged work against local change and access policy first.

## Build and configure

- [Linux installation checklist](installation/linux-installation-checklist.md) — detailed planning, installation and acceptance checks (L01)
- [Post-install configuration](configuration/post-install-configuration.md) — turn a new install into a known, supportable baseline (L02)
- [Users, groups and permissions](configuration/users-groups-permissions.md) — inspect and safely change access controls (L03)
- [Package management](configuration/package-management.md) — query, update and recover packages without treating upgrades casually (L04)
- [SSH configuration and troubleshooting](configuration/ssh-configuration-troubleshooting.md) — configure remote access while avoiding lockout (L11)

## Operate and investigate

- [systemd service operations](systemd/service-operations.md) — unit state, dependencies, overrides and recovery (L05)
- [`journalctl` and log investigation](logs/journalctl-log-investigation.md) — build a useful log query and preserve evidence (L06)
- [Boot troubleshooting](troubleshooting/boot-troubleshooting.md) — separate firmware, bootloader, kernel and userspace failures (L07)
- [Network diagnostics](networking/network-diagnostics.md) — work from link state through routing, DNS, transport and application checks (L08)
- [Disk and filesystem investigation](storage/disk-filesystem-investigation.md) — distinguish capacity, device and filesystem faults (L09)
- [Performance investigation](troubleshooting/performance-investigation.md) — correlate CPU, memory and I/O evidence instead of guessing from one metric (L10)
- [Firewall fundamentals](networking/firewall-fundamentals.md) — inspect Linux packet filtering and plan safe rule changes (L12)
- [Maintenance checklist](maintenance/maintenance-checklist.md) — routine review with change and reboot boundaries (L13)

For a shorter installation sign-off, use the top-level [Linux installation checklist](../checklists/linux-installation.md). It links back to the detailed installation procedure where reasoning or recovery steps are needed.

## Limits

Exact installer screens, package tools, network managers and recovery paths vary. Confirm the installed distribution and release with `/etc/os-release`, then use that release's documentation for bootloader, storage-encryption and upgrade details. On managed systems, local policy and the service owner's recovery plan take precedence over these general notes.
