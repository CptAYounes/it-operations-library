# Linux installation checklist

Use this procedure for a clean Linux installation on a physical machine or virtual machine. It is deliberately more detailed than the [short installation sign-off checklist](../../checklists/linux-installation.md): decisions made before the installer starts are often the hardest ones to reverse.

The worked examples use Debian 13 (Trixie) with UEFI firmware and systemd. Other distributions may name installer tasks, repositories and bootloader tools differently.

> **Data-loss boundary:** selecting a target disk, creating a partition table, formatting, configuring RAID or installing a bootloader can make existing data unbootable or permanently destroy it. Match disks by model, size and stable identifier—not by a remembered `/dev/sdX` name. Stop if the ownership of any data is uncertain.

## Installation record

Record enough information to reproduce or review the build. Do not publish serial numbers, recovery keys, internal addresses or account details.

| Item | Decision/evidence |
|---|---|
| Purpose and owner | |
| Distribution, release and architecture | |
| Installer image filename | |
| Image source and checksum | |
| Physical or virtual target | |
| Firmware mode (UEFI/legacy) | |
| Boot mode (Secure Boot state, if relevant) | |
| Target disk model, capacity and stable ID | |
| Partition, filesystem and encryption plan | |
| Hostname and network method | |
| Initial administrator account | |
| Package/profile selection | |
| Backup or rollback route | |

## 1. Before touching the target

### Confirm requirements

- [ ] Confirm the machine's purpose: desktop, server, appliance, lab host or VM.
- [ ] Confirm CPU architecture and that the chosen release supports the hardware.
- [ ] Check memory, disk capacity, network adapter and any required vendor firmware.
- [ ] Decide whether graphical packages are needed. A smaller server installation has fewer packages to patch, but it is not automatically secure.
- [ ] Confirm the maintenance window, outage authority and recovery contact for a machine that already provides a service.
- [ ] Back up required data and application configuration to a different device or service.
- [ ] Verify that the backup can be read. A successful copy command alone is not a restore test.
- [ ] Record the current boot mode, storage layout and network settings if this is a rebuild.
- [ ] Obtain encryption recovery material and a secure storage location before enabling full-disk encryption.

On a running Linux system, these checks are read-only:

```bash
uname -m
cat /etc/os-release
lsblk -e7 -o NAME,PATH,MODEL,SERIAL,SIZE,TYPE,FSTYPE,MOUNTPOINTS
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
ip -brief link
ip -brief address
ip route
```

`SERIAL` is useful for local disk identification but should be removed from public evidence. Device names can change between boots or when controllers are reordered.

### Obtain and verify the installer

Download the installer only from the distribution's official site or an approved internal mirror. Verify both authenticity and integrity using the method published for that release. A bare checksum detects a damaged download; it proves origin only when the checksum list or image is also authenticated.

Example integrity check, using the value published by Debian for the exact image:

```bash
sha256sum debian-13.x.x-amd64-netinst.iso
```

- [ ] The filename and architecture match the planned build.
- [ ] The calculated digest exactly matches the authenticated published digest.
- [ ] The installation medium boots on a non-critical test machine or VM where practical.

> Writing an image to a whole USB device is destructive. Graphical imaging tools and commands such as `dd` can overwrite the wrong disk without a useful confirmation prompt. Re-identify the destination immediately before writing and never copy a documentation example containing a placeholder device into a shell.

## 2. Plan storage before opening the installer

There is no single correct partition scheme. Keep it no more complex than the recovery requirements justify.

| Component | Typical decision | Points to check |
|---|---|---|
| Partition table | GPT for modern UEFI systems | Legacy BIOS compatibility may require a different boot arrangement. |
| EFI System Partition | FAT32, mounted at `/boot/efi` | Reuse only when its ownership and contents are understood; do not format another OS's ESP casually. |
| Root `/` | ext4 is a conservative Debian default | Allow space for the OS, packages, logs and temporary files. |
| Swap | partition, logical volume, file or none | Size depends on workload and hibernation; hibernation usually needs additional planning. |
| `/home` or data | separate only for a reason | Separation can simplify reinstalls but can also strand free space in the wrong filesystem. |
| Encryption | LUKS, where the threat model requires it | Plan unlock, remote reboot and recovery-key handling. Encryption does not replace backups. |
| LVM/RAID | only when operationally justified | Record member disks and recovery procedure. RAID improves availability; it is not a backup. |

Before accepting installer changes:

- [ ] Match the selected target against model, capacity and stable ID in the installation record.
- [ ] Confirm every partition the installer proposes to delete or format.
- [ ] Confirm where the bootloader and EFI files will be installed.
- [ ] Check alignment, mount points, filesystem types and encryption boundaries.
- [ ] For dual boot, make a separate recovery plan and confirm the other operating system is cleanly shut down.
- [ ] For a VM, confirm the virtual disk—not an attached data disk—is selected.
- [ ] Take an approved VM snapshot only if the platform and workload support consistent rollback; a snapshot is not a substitute for a backup.

Stop and escalate if disk identity is ambiguous, an unexpected RAID/LVM/LUKS signature appears, the installer reports I/O errors, or required data has not been verified elsewhere.

## 3. Firmware and boot preparation

- [ ] Use UEFI unless a documented compatibility requirement calls for legacy/CSM mode.
- [ ] Confirm the storage controller mode. Changing between AHCI and vendor RAID modes may stop an existing OS from booting.
- [ ] Put the installation medium first for this boot rather than permanently weakening the boot order where possible.
- [ ] Keep Secure Boot enabled when the chosen distribution and required drivers support it. Record and justify any exception.
- [ ] Check the hardware clock and firmware date; large errors can break TLS and package validation later.
- [ ] Do not update firmware during the OS installation unless a known fault requires it and the vendor recovery method is understood.

## 4. Work through the Debian 13 installer

Installer wording differs between the graphical, text and automated paths, but the decisions remain similar.

### Locale, identity and accounts

- [ ] Select the required language, locale, keyboard and time zone.
- [ ] Choose a valid hostname that follows local naming rules and does not expose unnecessary location or owner details.
- [ ] Configure the domain field only when there is a real DNS/search-domain requirement.
- [ ] Create a named administrative user; do not use a shared personal account for a multi-user host.
- [ ] Use a strong, unique passphrase and arrange secure recovery according to local policy.
- [ ] Understand the Debian installer choice: leaving the root password blank normally disables direct root login and gives the first user `sudo` access; setting a root password changes that model.

### Network and repositories

- [ ] Confirm the installer sees the expected interface and link.
- [ ] Prefer DHCP during installation unless a static address has been assigned and checked for conflicts.
- [ ] Record VLAN, proxy, static address, prefix, gateway and DNS values when they are required.
- [ ] If proprietary firmware is offered, confirm it is required, permitted and sourced through the installer/repository rather than an unknown download.
- [ ] Select an appropriate official or approved package mirror.
- [ ] Do not treat a mirror failure as permission to disable signature checking. Fix time, DNS, routing or proxy access first.

### Partition and install

- [ ] Re-read the final partition summary before selecting **Finish partitioning and write changes to disk**.
- [ ] Confirm any encryption passphrase before the operation becomes irreversible.
- [ ] Record the resulting LUKS, LVM or RAID design without recording secrets.
- [ ] Select only package tasks the host needs. On a Debian server this may be **SSH server** and **standard system utilities** without a desktop environment.
- [ ] If SSH is selected, plan its firewall and authentication controls; installing the server is not the same as making remote access safe.
- [ ] Install the bootloader to the planned system disk/EFI partition.
- [ ] Remove installation media when prompted and retain installer logs if the build failed.

## 5. First boot: prove the installed system

Start locally or through a trusted console. Do not depend on SSH until local access and the network configuration are known to work.

```bash
cat /etc/os-release
uname -r
uname -m
hostnamectl
systemctl is-system-running
systemctl --failed --no-pager
lsblk -f
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
ip -brief link
ip -brief address
ip route
```

Expected results are contextual, not just “the command ran”:

- [ ] The installed release and architecture are the ones planned.
- [ ] The system boots in the intended UEFI/legacy mode and no installer medium is required.
- [ ] Root and any separate filesystems are mounted from the expected devices.
- [ ] Swap and encryption behave as designed.
- [ ] No required mount is missing or unexpectedly read-only.
- [ ] `systemctl is-system-running` reports `running` or an understood `degraded` state.
- [ ] Failed units are investigated rather than silently ignored.
- [ ] The expected interface has the assigned address and route.
- [ ] Local login and approved privilege escalation work.

A `degraded` system is not automatically unusable, but it is not a clean acceptance result. Identify the failed unit and its impact.

## 6. Establish the package and time baseline

The following Debian 13 queries are read-only:

```bash
apt-cache policy
apt list --upgradable
systemctl status systemd-timesyncd --no-pager
# If systemd-timesyncd is in use:
timedatectl show -p Timezone -p NTPSynchronized
```

Updating package indexes and installing upgrades change system state. Review repository configuration, connectivity, free space, release notes and reboot requirements first, then use the [package management guide](../configuration/package-management.md) and [post-install configuration procedure](../configuration/post-install-configuration.md).

- [ ] Package sources refer to the intended Debian release and approved components.
- [ ] Signature verification is enabled; no workaround disables repository trust.
- [ ] Time zone is correct and clock synchronisation reaches a trusted source.
- [ ] Security and normal updates have been reviewed and applied under the appropriate change boundary.
- [ ] The host has been rebooted if required, and the new kernel/boot path has been validated.

## 7. Access, services and security acceptance

- [ ] List listening sockets and account for each exposed service:

```bash
ss -lntup
```

Process details may be hidden without privilege. An absent process name does not mean no listener exists.

- [ ] Confirm only required services are enabled and running.
- [ ] Validate SSH locally before opening network access; follow the [SSH configuration guide](../configuration/ssh-configuration-troubleshooting.md).
- [ ] Inspect the active firewall system and policy before changing rules; follow [firewall fundamentals](../networking/firewall-fundamentals.md).
- [ ] Remove or lock temporary build accounts only after a permanent recovery route is proven.
- [ ] Confirm file ownership and permissions for application data and administrative keys.
- [ ] Configure monitoring, backup and log retention appropriate to the host's purpose.
- [ ] Test a backup read or restore in a safe location rather than relying only on job status.

## 8. Final validation and handover

Run a short observation window after the last reboot:

```bash
systemctl --failed --no-pager
journalctl -b -p warning --no-pager
uptime
free -h
findmnt --verify
```

`journalctl` visibility depends on permissions; record that limitation instead of treating an empty result as proof that no errors exist. `findmnt --verify` checks `/etc/fstab` parsability and usability but does not prove every remote or removable mount will be available during the next boot.

- [ ] Boot, login, privilege escalation, time, DNS and default routing pass.
- [ ] Required applications and services pass a functional test, not just a process-state check.
- [ ] No unexplained failed units, filesystem errors or repeated high-priority log events remain.
- [ ] The next reboot has a tested console or recovery route.
- [ ] Build decisions, package state, exceptions and outstanding work are recorded.
- [ ] Sensitive values and unique identifiers are redacted from publishable evidence.
- [ ] The service owner or handover recipient knows the backup, recovery and escalation paths.

## Escalate rather than improvise when

- storage identity, existing data ownership or encryption recovery is uncertain;
- hardware reports repeated media, memory or I/O errors;
- boot requires an unplanned firmware-mode or controller-mode change;
- repository signatures cannot be verified;
- network addressing conflicts with an existing host;
- the only remaining action could remove console/SSH access;
- filesystem repair, RAID reconstruction or bootloader recovery is required without a verified backup;
- the build cannot meet its security, backup or service acceptance criteria.

An installation is complete only when the installed system can boot from its own storage, provide its intended service, survive the required reboot and be recovered by someone other than the installer using the recorded information.
