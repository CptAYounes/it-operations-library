# Linux maintenance checklist

Use this for a planned host review. It is not an instruction to upgrade, reboot or delete files automatically. Record exceptions and owners rather than forcing every system into one baseline.

## Before the window

- [ ] Confirm host/service, owner, maintenance scope and approved time window.
- [ ] Review active incidents, monitoring suppressions, recent changes and known risks.
- [ ] Confirm current user sessions, long-running jobs and dependent services.
- [ ] Confirm working console/out-of-band access before network, SSH, boot or firewall work.
- [ ] Verify the latest required backups completed and a representative restore/read test is current.
- [ ] Record rollback limits; package rollback does not necessarily reverse data/schema changes.
- [ ] Check the correct distribution/release and vendor maintenance guidance.

## Capture a read-only baseline

```bash
cat /etc/os-release
uname -r
uptime
systemctl is-system-running
systemctl --failed --no-pager
journalctl -b -p warning --since '24 hours ago' --no-pager
df -hT
df -ih
free -h
ip -brief address
ip route
ss -lntup
timedatectl show -p Timezone -p NTPSynchronized
```

- [ ] Explain any degraded state, failed unit, repeated warning or unexpected listener.
- [ ] Confirm required mounts are present and not unexpectedly read-only.
- [ ] Confirm storage has enough block, inode, `/boot` and EFI capacity for planned work.
- [ ] Compare CPU, memory, swap and I/O observations with a known baseline where available.
- [ ] Remove sensitive addresses, usernames and service details from publishable evidence.

## Packages and security updates

Debian 13 initial read-only inventory:

```bash
apt-cache policy
apt-mark showhold
dpkg --audit
```

- [ ] Repository suite, mirror and signing configuration match the intended release.
- [ ] Free space, backup, console and application compatibility checked.
- [ ] Security updates prioritised according to exposure and risk.
- [ ] Third-party packages/repositories still have a named purpose and supported update route.
- [ ] Metadata refresh approved before running `sudo apt update` (Debian-specific and state-changing).

After the approved metadata refresh, recalculate the proposed transaction:

```bash
apt list --upgradable
apt-get --simulate upgrade
```

- [ ] Proposed installs, removals, holds, service restarts and kernel/boot changes reviewed against the refreshed metadata.
- [ ] The exact transaction is approved before running `sudo apt upgrade`.
- [ ] Distribution release upgrades handled as a separate tested change.

Do not bypass a signature failure or run `autoremove`/`purge` without reviewing every proposed removal. Use [package management](../configuration/package-management.md) for interrupted transactions and validation.

## Accounts and access

- [ ] Named administrator and service accounts still have owners and a current need.
- [ ] Supplementary groups and `sudo` access match least privilege.
- [ ] Disabled/departed accounts, keys, tokens and scheduled jobs reviewed through the authorised identity process.
- [ ] SSH host/user key rotation and expiry policy checked without collecting private keys.
- [ ] A fresh approved SSH session passes before the known-good session is closed.
- [ ] Home, application and key-file permissions have no unexplained broad access.

Account locking does not terminate sessions or remove key-based/scheduled access. Follow [users and permissions](../configuration/users-groups-permissions.md) and [SSH configuration](../configuration/ssh-configuration-troubleshooting.md).

## Services, logs and scheduled work

```bash
systemctl list-unit-files --type=service --state=enabled
systemctl list-timers --all
journalctl --disk-usage
```

- [ ] Required services are enabled/running as designed and pass functional checks.
- [ ] Unneeded listeners/packages are assessed before removal; dependencies are understood.
- [ ] Timers/cron jobs have current owners, expected last results and no overlap issue.
- [ ] Log retention fits disk and evidence requirements; high-volume writers investigated.
- [ ] Time synchronisation and certificate validity are healthy.
- [ ] Monitoring agents and backup jobs report from the host and central system.

Do not vacuum logs only to recover space until evidence is preserved and the writer/retention cause is known.

## Storage, network and firewall

- [ ] Kernel logs checked for device resets, I/O errors or filesystem warnings.
- [ ] RAID/LVM/thin-pool/encryption health reviewed where present.
- [ ] Filesystem capacity and inode trends are acceptable for the next interval.
- [ ] Persistent mounts and `/etc/fstab` validate; no repair is run on a mounted filesystem.
- [ ] Interface errors/drops, routes, DNS and required endpoints pass.
- [ ] Firewall manager/owner, saved policy and active policy agree.
- [ ] Exposed ports match service purpose for both IPv4 and IPv6.
- [ ] Container/VM/VPN forwarding and NAT dependencies are accounted for.

Disk repair, rule flushes, network-manager restarts and remote route/address changes require their own recovery plan. See the [storage](../storage/disk-filesystem-investigation.md), [network](../networking/network-diagnostics.md) and [firewall](../networking/firewall-fundamentals.md) guides.

## Apply approved work

- [ ] One change group performed at a time with start/end time and operator recorded.
- [ ] Configuration validated with the application's parser before reload/restart.
- [ ] Service restarts performed only when impact and dependency order are understood.
- [ ] Any warning or deviation captured before retrying or applying a repair.
- [ ] Rollback invoked if stop conditions or acceptance limits are breached.

## Reboot decision

- [ ] Determine whether the running kernel/libraries/services require restart or reboot; do not rely on one indicator alone.
- [ ] Confirm users, jobs, redundancy, bootable kernel, mounts and console recovery.
- [ ] Reboot authorised and monitoring/alert handling coordinated.
- [ ] If reboot is deferred, record risk, owner and deadline.

A reboot changes state and can reveal latent boot, mount, encryption or network faults. It is not a generic troubleshooting step.

## Acceptance after maintenance

```bash
uname -r
uptime
systemctl is-system-running
systemctl --failed --no-pager
journalctl -b -p warning --no-pager
findmnt --verify
ip -brief address
ip route
ss -lntup
```

- [ ] Correct kernel/release and all expected mounts present after any reboot.
- [ ] Required services pass application-level checks from the expected client path.
- [ ] Network, DNS, time, SSH and firewall exposure match the before-state or approved change.
- [ ] No new repeated high-severity logs, storage errors or failed units.
- [ ] Backup and monitoring completed a fresh successful check-in.
- [ ] Temporary rules, accounts, files, snapshots and alert suppressions removed or assigned.
- [ ] Package/configuration versions, commands, evidence, results and exceptions recorded.
- [ ] Handover includes outstanding risk, owner, next action and escalation point.

**Outcome:** [ ] Pass  [ ] Pass with accepted exception  [ ] Rolled back  [ ] Escalated

Stop and escalate for data-integrity warnings, unknown privileged access, signature failure, unexpected package removal, loss of management path, failed recovery/backup, repeated post-change failure or any impact outside the approved maintenance scope.
