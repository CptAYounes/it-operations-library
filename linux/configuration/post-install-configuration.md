# Linux post-install configuration

A fresh installer boot is a starting point, not a usable baseline. This procedure turns it into a system whose identity, storage, time, updates, access and exposed services are known. Debian 13 commands are used where the distribution matters.

Work from a local or out-of-band console until remote access has been proven. Capture the before-state first; if an expected command or configuration manager is absent, identify the installed stack rather than adding another one by reflex.

## Establish the before-state

These checks are read-only and do not require `sudo` for their basic output:

```bash
cat /etc/os-release
uname -r
hostnamectl
systemctl is-system-running
systemctl --failed --no-pager
lsblk -f
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
ip -brief address
ip route
ss -lntup
timedatectl
```

Record anomalies such as a degraded system, an unexpected mount, more than one default route, the wrong time zone or an unexplained listener. Process information in `ss` and full logs may require additional permission.

## 1. Confirm identity and naming

Choose a hostname that complies with the local naming scheme and does not encode secrets or a person's full name.

Read the current values:

```bash
hostnamectl status
getent hosts "$(hostname)"
cat /etc/hosts
```

On a systemd host, this is the normal state-changing operation:

```bash
sudo hostnamectl set-hostname new-hostname
```

Review `/etc/hosts` if local static resolution is deliberately used. Do not add an address merely to silence a lookup warning without understanding whether DNS, DHCP or cloud-init owns the name. After a change, start a new shell and check `hostnamectl`, `hostname --fqdn` where a domain is expected, and application certificates or cluster membership that depend on the old name.

## 2. Correct time before package or TLS work

```bash
timedatectl status
timedatectl show -p Timezone -p NTPSynchronized -p NTP
systemctl status systemd-timesyncd --no-pager
```

Debian 13 may use `systemd-timesyncd`, but another NTP implementation can legitimately own synchronisation. Do not run competing time daemons.

Examples that change state:

```bash
sudo timedatectl set-timezone Europe/London
sudo timedatectl set-ntp true
```

Use the time zone required for operations; UTC often simplifies servers, while local time may be appropriate for a workstation. Confirm `NTPSynchronized=yes` after allowing time for synchronisation. A correct-looking wall clock is not proof that the configured source is healthy.

## 3. Review storage and persistent mounts

```bash
lsblk -o NAME,TYPE,FSTYPE,FSVER,SIZE,UUID,MOUNTPOINTS
findmnt --verify
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
df -hT
df -ih
```

Before changing `/etc/fstab`, confirm filesystem UUIDs with `lsblk` or `blkid`, make a recoverable copy, and arrange console access. A bad root or boot entry can prevent the next boot. Prefer `UUID=` or another intended stable identifier over a changeable `/dev/sdX` name.

After editing, check syntax and attempt only the specific planned mount. `sudo mount -a` can trigger every currently unmounted entry, including remote or removable filesystems, so it is not a harmless syntax test. Do not run `fsck` against a mounted filesystem; see [disk and filesystem investigation](../storage/disk-filesystem-investigation.md).

## 4. Inspect repositories, then update deliberately

Read-only Debian queries:

```bash
apt-cache policy
apt list --upgradable
dpkg-query -W -f='${binary:Package}\t${Version}\n'
```

Inspect `/etc/apt/sources.list` and `/etc/apt/sources.list.d/`. Debian 13 installations commonly use deb822 `.sources` files. Repositories should point to the intended release, use HTTPS where provided, and retain signature verification. Third-party repositories expand the trust and patching surface; document why each one exists.

Only after confirming backup/rollback, free space, repository identity and service impact:

```bash
sudo apt update
apt list --upgradable
sudo apt upgrade
```

`apt update` refreshes local metadata; it does not install package upgrades. Review removals, new dependencies, held packages and whether services or the kernel will restart. Follow the full [package management guide](package-management.md) for simulation, recovery and release upgrades.

## 5. Accounts and privilege

```bash
getent passwd
getent group
id
getent group sudo
```

- Use named accounts rather than shared logins.
- Grant only the groups required for the role.
- Ensure there is a tested administrative and console recovery path before locking any build account.
- Do not edit `/etc/passwd`, `/etc/shadow` or `/etc/group` directly for routine changes.
- Remember that group changes normally require a new login session.

See [users, groups and permissions](users-groups-permissions.md) before using `usermod`, changing ownership recursively or writing a `sudoers` rule. Validate `sudoers` changes with `visudo`; a malformed rule can remove administrative access.

## 6. Network configuration

Start with observations:

```bash
ip -brief link
ip -brief address
ip route
ip -6 route
getent ahosts example.com
```

Identify the manager before editing files:

```bash
systemctl is-active NetworkManager
systemctl is-active systemd-networkd
```

Debian may instead use ifupdown through `/etc/network/interfaces`. Cloud images can be owned by cloud-init. Do not configure the same interface in multiple managers.

For a static address, verify the address, prefix, gateway, VLAN and DNS assignments, check for conflicts, and preserve a console session. Remote network changes can disconnect the host before they can be reverted. Validate the local subnet, gateway, DNS resolution and an application endpoint separately; [network diagnostics](../networking/network-diagnostics.md) provides a layered sequence.

## 7. Minimise exposed services

```bash
systemctl list-unit-files --type=service --state=enabled
systemctl --type=service --state=running
ss -lntup
```

An enabled unit is configured to start through a dependency or boot target; it may not be running now. A running service is not necessarily enabled. Map every listener to an intended service, address and owner before disabling anything.

Use the [systemd operations guide](../systemd/service-operations.md) to inspect dependencies and logs. Disable or remove an unneeded package only after confirming it is not a dependency or recovery mechanism. Validate the host's actual function after any service change.

## 8. Secure remote access without locking it out

If SSH is required:

1. keep the console or current session available;
2. confirm the server package and service name;
3. establish a separate named account and key;
4. validate effective configuration with `sshd -T` and syntax with `sshd -t` where the server is installed;
5. open only the intended firewall path;
6. test a second session from an expected client;
7. only then consider disabling weaker authentication methods.

Debian's service unit is normally `ssh.service`, while other distributions often use `sshd.service`. Follow [SSH configuration and troubleshooting](ssh-configuration-troubleshooting.md) and [firewall fundamentals](../networking/firewall-fundamentals.md) rather than copying a hardening snippet.

## 9. Logging, backup and monitoring

Check what the current boot is already reporting:

```bash
journalctl -b -p warning --no-pager
journalctl --disk-usage
```

Access can be restricted, and an empty query is not proof that the system has no warnings. Decide whether journal persistence and retention meet the host's support requirements. Do not increase retention without checking disk capacity and privacy implications.

Configure backups around the data and configuration that matter, not just the root filesystem. Record encryption-key and application-consistency requirements. Test a restore of representative data to an alternate location. Monitoring should at least cover service availability, storage capacity/inodes, resource pressure, backup status, time synchronisation and high-severity logs as appropriate to the host.

## Acceptance after a final reboot

Rebooting is a disruptive operation. Confirm authority, active users, running jobs and console access first. After any required reboot:

```bash
who -b
uptime
systemctl is-system-running
systemctl --failed --no-pager
journalctl -b -p warning --no-pager
findmnt --verify
ip -brief address
ip route
ss -lntup
```

A baseline passes when:

- the correct kernel and release boot from the expected storage;
- required mounts, swap, time and name resolution are correct;
- the intended network path and firewall exposure work;
- required services pass functional checks, not only `active` state;
- administrative and recovery access work from a fresh session;
- no unexplained failed units or repeated high-severity events remain;
- update, backup, monitoring and ownership arrangements are recorded.

Escalate if a change would risk the only access route, signatures fail, storage errors appear, required services have unknown dependencies, or the system remains degraded without an understood and accepted exception.
