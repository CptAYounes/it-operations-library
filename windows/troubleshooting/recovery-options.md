# W12 — Windows recovery options

Recovery should preserve the most data and configuration that the fault allows. “Reset” and “reinstall” are not synonyms, and a recovery option visible on Windows 11 may not exist on Windows Server.

**Applies to:** supported Windows 11 releases and Windows Server 2022/2025. GUI paths refer to Windows 11 or Server with Desktop Experience where the option exists. Server Core is command/remote/recovery-media oriented. Server recovery normally relies on role/application backups, system-state or bare-metal recovery, vendor tooling and installation media—not the Windows 11 **Reset this PC** workflow.

## First protect access and evidence

Before entering recovery:

- record exact symptom, time, stop/error code and last change;
- confirm data backup and perform a read check or test restore;
- locate the BitLocker/device-encryption recovery key without copying it into public notes;
- identify Windows product, edition, architecture and build;
- identify storage/controller/RAID requirements and installation media;
- record applications, certificates, accounts and network configuration that may need restoration;
- define who authorises data loss, downtime and security rollback.

If hardware is failing or critical data is not backed up, stop and choose data preservation/escalation before filesystem or reset activity.

## Check available recovery state

From an elevated running Windows session:

```text
reagentc /info
```

This is **read-only**. It reports Windows RE status and configured location where the feature is present. Do not publish recovery partition identifiers without review.

`reagentc /enable` and `/disable` are **changes**. Enabling WinRE is not a substitute for a backup and should not be attempted until partition layout and BitLocker implications are understood.

Open Windows 11 recovery settings at **Settings > System > Recovery**. **Advanced startup > Restart now** reboots into WinRE and interrupts service. On Server, use the supported boot/install media or recovery path for the deployed edition; available menus differ.

## Choose by disruption

| Option | Typical target | Keeps personal data? | Removes apps/settings? | Main boundary |
|---|---|---:|---:|---|
| Startup Settings / Safe Mode | Driver/startup isolation | Yes | No | Diagnostic; changes made in Safe Mode still persist |
| Startup Repair | Boot/startup files | Normally | Not intended | Automated changes; may not fix hardware or OS-wide corruption |
| Uninstall latest update | Recent servicing regression | Normally | Rolls back update | Security/build rollback; uninstall window/package may be absent |
| System Restore | Recent driver/config/app change | User files normally | Rolls system state/apps back | Requires a suitable restore point; not a data backup |
| System Image Recovery / bare-metal restore | Failed OS/disk with a known-good image or bare-metal backup | Restores captured state | Replaces newer state | **Destructive** to target/newer data |
| Reset this PC — Keep my files | Windows 11 OS corruption | Designed to retain personal files | Yes | Client feature; still back up first |
| Reset this PC — Remove everything | Disposal or unrecoverable client install | No | Yes | **Destructive**; cleaning/data-erasure guarantees need separate verification |
| Repair install/in-place upgrade | Running client OS component damage | Usually | Intended to retain apps/data | Needs compatible edition/language/build and Windows able to run Setup |
| Clean installation | Unrecoverable/replace/redeploy | No on erased target | Yes | **Destructive**; use [W01](../installation/windows-installation-checklist.md) |

“Normally retains” is not a backup guarantee. Encryption, failing storage, wrong target or interrupted recovery can still cause loss.

## Low-disruption options

### Startup Settings and Safe Mode

Use Safe Mode when Windows reaches WinRE but normal startup is blocked by a driver, startup service or shell component. It starts a reduced set of drivers/services. Safe Mode with Networking adds network components but should not be chosen when network access is unnecessary.

If Safe Mode works, collect logs and reverse one evidenced recent change. Do not remove boot-critical storage/security drivers or bulk-disable services. See [W05 — Boot troubleshooting](boot-troubleshooting.md).

### Startup Repair

In WinRE choose **Troubleshoot > Advanced options > Startup Repair** where offered. It is an **offline repair**. Record its result and any log reference. Failure does not prove the Windows installation must be erased; check firmware detection, disk health, BCD and update/driver evidence next.

### Uninstall Updates

WinRE may offer uninstall of the latest quality update and, where rollback state exists, the latest feature update. Use it only when failure timing supports the update as a cause. Record the current/target build and plan how the update will be held and reintroduced safely.

This is a **change** and can re-expose fixed vulnerabilities. Server servicing and managed update rollback must follow the applicable role/change process.

### System Restore

System Restore reverts protected system files, registry, drivers and installed applications/settings to a restore point. It is not a user-file backup, is not enabled/configured on every installation, and can remove software installed after the restore point.

Review **Scan for affected programs** where available. Back up data first, select a point before the evidenced change, and validate applications/security/update state afterwards.

## Client repair install

When Windows 11 still boots, a compatible Windows Setup or a Settings-based reinstall option on supported builds may repair the Windows component set while retaining files, settings and applications. Availability and labels change by release.

Before proceeding:

- match edition, language and architecture;
- use official, sufficiently current media;
- ensure free space and stable power;
- back up and secure BitLocker recovery material;
- remove only software the compatibility report specifically requires;
- record current build and application validation list.

An in-place repair is a substantial **change**, takes time/restarts and is not suitable for hardware failure, malware containment or an OS that cannot start Setup. Windows Server in-place repair/upgrade support depends on edition, roles and supported upgrade paths; use server-specific Microsoft guidance and backups rather than assuming the client workflow.

## Reset this PC (Windows 11)

Windows 11 provides **Settings > System > Recovery > Reset PC**, with choices that can include:

- **Keep my files** — reinstalls Windows and removes applications/settings while designed to retain user files;
- **Remove everything** — removes personal files, applications and settings;
- **Cloud download** — downloads a fresh Windows image and requires suitable network/data;
- **Local reinstall** — uses local recovery files and can fail if those files are damaged.

Review the final **Ready to reset** summary; it is more authoritative for that build than a memorised screen sequence. Export application/licence/configuration information and back up all data even for **Keep my files**.

**Remove everything is destructive.** “Clean data/drive” choices take longer and make casual file recovery harder, but disposal requirements may demand organisation-approved sanitisation or physical destruction. Do not claim a consumer reset satisfies a specific data-erasure standard without verification.

Reset this PC is not the baseline recovery method for Windows Server.

## System image and bare-metal recovery

Use a known, tested backup/image when the OS or disk must be reconstructed to a recorded point. Recovery overwrites target state and may restore old credentials, vulnerabilities, machine identity or application data.

Before restore:

- confirm backup identity, date, integrity and encryption key;
- identify target disk/controller and capacity constraints;
- preserve data newer than the backup where possible;
- isolate duplicate machine identities/network presence until validated;
- plan updates, password/certificate rotation and application consistency;
- ensure application-aware recovery for transactional workloads.

For Windows Server, Windows Server Backup (if installed), system-state recovery, bare-metal recovery and role-specific restore have different scopes. Follow the exact backup product/role procedure. A VM snapshot alone is not automatically application-consistent or an independent backup.

## Command Prompt in WinRE

Command Prompt is a tool, not a recovery method. In WinRE, `X:` normally belongs to the recovery image and installed Windows can have another letter.

**Read-only identification:**

```text
diskpart
list disk
list volume
exit
```

Then verify candidate paths with `dir <letter>:\Windows`. Do not use `clean`, `format`, partition deletion or registry edits as exploratory commands. Offline SFC, CHKDSK repair, DISM servicing and BCDBoot all modify the selected installation; use the targeted conditions and safeguards in [W05](boot-troubleshooting.md) and [W09](../storage/storage-filesystem-diagnostics.md).

## Clean installation

Choose a clean installation when policy requires rebuild, the OS cannot be trusted/repaired, storage is replaced, or other recovery options are unsuitable. It removes applications/configuration and erases data when partitions are deleted. Follow [W01 — Install Windows safely](../installation/windows-installation-checklist.md), including target-disk identification and post-install validation.

For suspected compromise, recovery must also address containment, credential/key rotation, evidence preservation and trusted media. Restoring the same vulnerable state is not enough.

## Recovery validation

Recovery is complete only when:

- [ ] Windows boots twice without recovery media;
- [ ] product/edition/build, activation and firmware boot mode are expected;
- [ ] storage/filesystem and encryption state are healthy/owned;
- [ ] updates, drivers and security controls are current for the restored state;
- [ ] network, sign-in, required services and application transactions succeed;
- [ ] restored data is checked for correctness and recency;
- [ ] backup/recovery operation and any lost interval are recorded;
- [ ] temporary boot changes/media/network isolation are removed as planned;
- [ ] the trigger fault does not recur in logs or functional tests.

If recovery fails, retain the exact stage and error. Do not loop through resets/restores against a possibly failing disk without reconsidering the diagnosis.
