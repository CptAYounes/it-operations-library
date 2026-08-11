# W05 — Windows boot troubleshooting

A boot failure becomes easier to reason about when it is assigned to a stage. Do not start by rebuilding boot files: first decide whether the failure is before firmware hand-off, in Windows Boot Manager, during kernel/device startup, or only at sign-in.

**Applies to:** Windows 11 and Windows Server 2022/2025. Windows client and Server with Desktop Experience can show graphical recovery screens; Server Core recovery remains command-oriented. Windows Server does not have every client reset option.

## Protect evidence and recovery access

Before a repair, record:

- exact screen, message and stop code;
- last known successful boot and last change;
- whether firmware still detects the target disk;
- BitLocker/device-encryption state and recovery-key location;
- firmware boot mode and storage-controller mode;
- recovery media/backup availability;
- whether data or service availability makes further attempts unsafe.

Repeated hard power-offs can compound filesystem or update damage. If the disk reports hardware failure, makes abnormal noise, disappears intermittently, or contains irreplaceable data, stop repair attempts and escalate to the storage/data-recovery owner.

## Locate the failing stage

```text
Power applied
    |
    +-- No POST / no firmware display ----> hardware/firmware path
    |
    +-- Firmware cannot see boot disk ----> connection/controller/device path
    |
    +-- "No boot device" / BCD error -----> boot selection or boot files
    |
    +-- Windows logo/spinner then stop ----> kernel, update or boot driver
    |
    +-- Sign-in shown but session fails ---> profile, shell, policy or service
```

A blank screen after sign-in is not automatically a boot-loader fault. Likewise, a BitLocker recovery prompt may be a response to a firmware/boot measurement change rather than disk corruption.

## Stage 1: firmware and boot target

These checks are read-only observations made in firmware setup or its one-time boot menu:

1. Is the expected disk detected with a plausible model/capacity?
2. Is **Windows Boot Manager** present and ahead of removable/network boot?
3. Is the system still using the recorded UEFI/legacy mode?
4. Did storage mode change between RAID/VMD/AHCI?
5. Did Secure Boot, TPM or firmware update immediately precede the fault?

Do not switch controller mode, clear TPM, reset firmware defaults or disable Secure Boot as generic fixes. Those changes can trigger BitLocker recovery or make the OS unbootable. Restore only a known prior setting, one at a time, with the recovery key available.

If the disk is absent in firmware, Windows repair tools cannot fix detection. Check power/data connection, slot, controller configuration and vendor diagnostics before modifying BCD or partitions.

## Stage 2: use the recovery menu conservatively

Enter Windows Recovery Environment (WinRE) through **Settings > System > Recovery > Advanced startup** while Windows still starts, from installation media via **Repair your computer**, or through automatic recovery after failed boots. Manufacturer keys and menus vary.

WinRE may request a BitLocker recovery key before it can access the Windows volume. Stop if the authorised key is unavailable. Do not format or reinstall around encryption.

Try in this order when appropriate:

1. **Startup Repair** — automated boot/startup diagnosis; preserve its result/log.
2. **Startup Settings** — Safe Mode or low-resolution boot to isolate a driver/startup component.
3. **Uninstall Updates** — only when timing and evidence point to a recent quality/feature update.
4. **System Restore** — only if a suitable restore point exists and application/settings rollback is acceptable.
5. Command Prompt for targeted, evidenced offline checks.

See [W12 — Recovery options](recovery-options.md) for the scope and data effect of each choice.

## Identify the offline Windows volume

In WinRE, `X:` is normally the temporary recovery environment, not the installed OS. Drive letters can differ from normal Windows.

**Read-only — WinRE Command Prompt:**

```text
diskpart
list disk
list volume
exit
```

Then inspect candidate volumes without writing to them:

```text
dir C:\Windows
dir D:\Windows
dir E:\Windows
```

Also identify the EFI System Partition (small FAT32 volume on a UEFI/GPT system) and the Windows volume by size, filesystem and contents. Do not format, clean or convert a disk during diagnosis.

## Inspect boot configuration before rebuilding it

From an online elevated command prompt or WinRE:

```text
bcdedit /enum all
```

This is **read-only**. In WinRE, the default store being examined may not be the installed system's store; use an explicitly identified BCD store when necessary. Record firmware boot entry, Windows Boot Manager, loader identifier, device/osdevice and path.

A normal UEFI installation uses the EFI System Partition and `\EFI\Microsoft\Boot\bootmgfw.efi`; BIOS/MBR arrangements differ. Do not copy a BIOS repair recipe onto a UEFI/GPT system.

## Check filesystem and operating-system files

Start with non-repairing checks where the running state permits them.

**Non-fixing initial NTFS check:**

```text
chkdsk C:
```

Without a repair switch, CHKDSK reports filesystem status rather than requesting a fix. It still writes diagnostic event/log evidence, and an active volume can produce transient observations; preserve the timestamp and result rather than treating one line as a confirmed cause. `chkdsk C: /scan` is a controlled-change branch, not a read-only substitute: supported online repair can occur unless `/forceofflinefix` is used, and that option queues detected defects for an offline repair. Obtain backup and outage authority before either path.

**Non-repairing component-store scan of the running Windows image:**

```text
DISM.exe /Online /Cleanup-Image /ScanHealth
```

`/ScanHealth` does not run `/RestoreHealth`, but it is not strictly read-only: DISM records diagnostic state and writes servicing logs while scanning the online image. Preserve the exit code and relevant log window.

From WinRE, if the Windows installation is `D:\Windows`:

```text
sfc.exe /scannow /offbootdir=D:\ /offwindir=D:\Windows
```

SFC is a **repair** even though it is diagnostic-looking; it can replace protected files. Confirm drive letters and use the Windows volume rather than `X:`. If the installation has a separate system/boot partition, `/offbootdir` may need that partition. Capture the output and CBS log before further changes.

`chkdsk /f`, `/scan`, `/spotfix` and `/r` can modify or schedule changes to filesystem state; `/r` also performs a long surface/readability scan. Use them only after storage health, backup, outage impact and rollback are considered. A failing physical disk should be imaged/replaced, not stressed by repeated repair scans.

## Recreate UEFI boot files only with evidence

If the Windows installation is intact, the UEFI firmware sees the disk, and boot files/BCD are missing or corrupt, `bcdboot` can recreate boot files. This is an **offline change** and the wrong target can alter another installation.

Example only, after assigning `S:` to the confirmed EFI System Partition and identifying Windows as `D:`:

```text
bcdboot D:\Windows /s S: /f UEFI
```

Validate that `D:\Windows` is the intended installation and `S:` is the FAT32 EFI System Partition on the same intended system disk. Record existing BCD state first. Do not use `/f ALL` without a reason.

`bootrec /fixmbr` applies to BIOS/MBR scenarios and is not a universal UEFI repair. `bootrec /fixboot` commonly produces access/target problems when copied into modern UEFI recipes. Prefer diagnosing the actual firmware/partition layout and using the documented `bcdboot` path rather than running every `bootrec` switch.

## Driver, update and Safe Mode branches

If normal boot fails but Safe Mode works:

- compare the last driver/update/software change;
- inspect Device Manager and System log;
- disable a non-essential startup item or roll back one evidenced driver change;
- avoid removing boot-critical storage/security drivers remotely or in bulk.

If failure began during servicing, use **Uninstall Updates** in WinRE only after recording the update/build. Offline DISM actions such as `/RevertPendingActions` alter servicing state and are last-resort recovery operations; use only against the confirmed offline image and after consulting the applicable Microsoft recovery guidance.

For a stop code, preserve the code, parameters if shown, dump path and change timeline. A bugcheck identifies a failure condition, not necessarily the guilty component. Hardware diagnostics, dump analysis and driver history may be required.

## Sign-in and post-boot symptoms

When the sign-in screen appears, the firmware and basic boot chain have largely completed. Check:

- whether another authorised account can sign in;
- free space and profile-service events;
- display output/low-resolution mode for a black screen;
- shell, policy and logon-script behaviour;
- remote versus console behaviour.

Do not delete a user profile to repair a sign-in symptom until its data is backed up and profile corruption is supported by evidence.

## Escalate or stop when

- the disk is intermittently absent, fails vendor diagnostics or contains unbacked-up critical data;
- BitLocker recovery material is unavailable;
- controller/RAID repair or firmware change is required;
- several Windows installations/EFI partitions make the target ambiguous;
- repeated rollback or repair attempts fail;
- the cause may be malicious change or credential compromise;
- the next action is Reset, reimage or reinstall without a verified backup.

## Validate recovery

After a successful change:

- boot twice from the internal disk with recovery media removed;
- confirm edition/build, storage volumes and encryption state;
- review System log for repeating boot, disk and controller errors;
- test sign-in, network and required service/application function;
- rerun update/driver validation when they were involved;
- restore the intended boot order and record exactly what fixed the fault.

“Startup Repair completed” is not the validation. A normal second boot and functional checks are.
