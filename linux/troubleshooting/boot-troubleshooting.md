# Linux boot troubleshooting

A boot failure can occur before Linux is involved. First locate the last successful stage; changing the bootloader will not repair failed power-on self-test, and running filesystem repair will not fix a missing UEFI boot entry.

> **Recovery boundary:** bootloader installation, initramfs rebuilding, partition changes and filesystem repair can turn a recoverable host into an unbootable one or damage data. Preserve console access and backups, confirm device identity, and escalate when storage or encryption state is uncertain.

## Where does progress stop?

```text
Power/POST
   |
Firmware detects boot disk?
   |
UEFI entry / bootloader menu?
   |
Kernel and initramfs messages?
   |
Root filesystem mounted?
   |
systemd target / login?
   |
Required application available?
```

Record the exact last message, screen/photo time, recent changes and whether the failure repeats. A blank display can be a graphics-output problem while the system continues to boot; check network/console evidence only if doing so is authorised and expected.

## 1. No POST or no firmware disk

This is not yet a Linux fault.

- Confirm power, display input, diagnostic LEDs/beeps and physical connections.
- Check whether firmware sees the expected disk by model and capacity.
- Record firmware mode, Secure Boot and storage-controller mode.
- If hardware was changed, return to the known baseline one change at a time.
- Do not initialise, format or accept a firmware RAID conversion prompt to “make the disk visible.”

Escalate to hardware/storage diagnosis for missing media, repeated controller errors or a disk that appears intermittently.

## 2. Firmware sees the disk but no bootloader starts

Check in firmware:

- expected UEFI boot entry and order;
- UEFI versus legacy/CSM mode;
- Secure Boot state;
- whether the EFI system partition belongs to this installation;
- recent firmware reset/update or disk/controller move.

A bootable rescue image can inspect without immediately writing:

```bash
lsblk -e7 -o NAME,PATH,MODEL,SIZE,TYPE,FSTYPE,FSVER,UUID,MOUNTPOINTS
blkid
```

Do not assume `/dev/sda` is the system disk. If full-disk encryption, LVM, MD RAID, ZFS or another storage layer is present, use its documented assembly/unlock process and avoid write actions until the layout is recorded.

Bootloader recovery is distribution- and firmware-specific. On Debian/GRUB it may involve mounting the installed root and EFI filesystems, bind-mounting runtime filesystems, entering a chroot, and running `grub-install`/`update-grub`. Those commands write boot state; do not use a generic command block without confirming UEFI mode, mount points, target architecture and multi-boot ownership.

## 3. Bootloader appears, kernel does not start

At the GRUB menu, retain the normal entry and note whether an older installed kernel or recovery entry boots. A one-time edit affects only that attempt and can help isolate:

- incorrect `root=` or `resume=` identifiers;
- a newly set kernel parameter;
- graphics mode setting;
- a bad current kernel/initramfs versus a wider storage fault.

Do not make `nomodeset`, disabled security controls or other diagnostic parameters permanent simply because they reach a login. They narrow the fault and can reduce function or security.

From a working older kernel:

```bash
uname -r
cat /proc/cmdline
ls -lh /boot
findmnt --target /boot
findmnt --target /boot/efi
journalctl -k -b --no-pager
```

Check package state and free space before rebuilding. On Debian, these are state-changing recovery operations:

```bash
sudo update-initramfs -u -k all
sudo update-grub
```

Run them only after the cause is understood (for example, an interrupted kernel package operation or missing generated files), with a console and rollback kernel available.

## 4. Initramfs cannot find or mount root

Common evidence includes a timeout waiting for a UUID, an emergency shell, missing crypt/LVM/RAID devices or filesystem errors.

Read-only observations where available:

```bash
cat /proc/cmdline
lsblk -f
blkid
cat /etc/fstab
cat /etc/crypttab
```

From an initramfs shell, tool availability is limited. Compare:

- kernel `root=` identifier;
- actual filesystem UUID/PARTUUID;
- `/etc/fstab` and `/etc/crypttab` identifiers;
- required storage driver/module and initramfs contents;
- LUKS, LVM or RAID member visibility;
- controller mode versus the installed configuration.

Do not repeatedly attempt writes against a disk reporting I/O errors. Preserve power and escalate for imaging/data recovery where the data matters.

### Filesystem checks

A filesystem can be damaged, but “run fsck” is not a universal first step.

- Identify the exact filesystem type and device.
- Ensure it is unmounted; a rescue environment is often required for root.
- Check backup and storage-health evidence first.
- Use the filesystem-specific check/repair tool and release documentation.
- Never apply an ext-family `fsck` command to XFS, Btrfs, ZFS, LUKS container or an assembled RAID device by guesswork.
- Avoid automatic “yes to all” repair where data-loss decisions need review.

`fsck -N` shows what would be invoked without executing a check, but correct device selection still matters:

```bash
sudo /usr/sbin/fsck -N /dev/mapper/example-root
```

Treat the placeholder literally as a placeholder, not a device to copy.

## 5. Kernel starts but systemd does not reach the expected target

If a shell or alternate target is available:

```bash
systemctl is-system-running
systemctl --failed --no-pager
systemctl get-default
systemd-analyze critical-chain
journalctl -b -p warning --no-pager
journalctl -b -1 -p warning --no-pager
```

Likely fault domains include:

- a required `/etc/fstab` mount waiting or failing;
- an invalid unit/drop-in or dependency cycle;
- a service start timeout;
- exhausted root, `/var`, inode or journal space;
- failed local filesystem;
- broken package/configuration change;
- graphics/display-manager failure while text login still works.

A one-boot kernel parameter such as `systemd.unit=rescue.target` or `systemd.unit=emergency.target` can reduce what starts. Emergency mode provides fewer mounts and services; rescue mode normally brings up more of the local system. Both change the boot environment and may bypass application safeguards, so use console access and a documented recovery plan.

If `/etc/fstab` is suspected, inspect it and run:

```bash
findmnt --verify
systemd-analyze verify /etc/systemd/system/*.mount
```

Globs can include no files or many files depending on the shell. `findmnt --verify` does not prove a remote server will be reachable at boot. Correct one known-bad entry at a time, retain the original, and test the next boot under observation.

## 6. Login appears but the service is unavailable

The OS may have booted successfully even though the workload did not.

```bash
systemctl status example.service --no-pager --full
journalctl -u example.service -b --no-pager
ss -lntup
```

Follow [systemd service operations](../systemd/service-operations.md) and test the application through its expected path. Do not classify an application dependency failure as an OS boot failure unless evidence connects them.

## Compare the failed and last known-good boots

```bash
journalctl --list-boots
journalctl -b -1 -p warning -o short-iso-precise --no-pager
journalctl -b 0 -p warning -o short-iso-precise --no-pager
```

Look for the first divergence around storage discovery, mounts, unit ordering or kernel errors. Previous boots exist only if retained; absence is a visibility limitation.

## Validate recovery

After an approved correction:

- [ ] Boot without rescue media or one-time diagnostic parameters.
- [ ] Confirm expected firmware mode, kernel and command line.
- [ ] Confirm all required filesystems and swap are present and writable as designed.
- [ ] Check failed units and high-priority messages for the new boot.
- [ ] Validate network, time and the required application function.
- [ ] Perform a second normal reboot when the change policy requires proof of repeatability.
- [ ] Keep an older known-good kernel/recovery route until the fix has passed its observation period.
- [ ] Record exact fault stage, evidence, change, validation and remaining risk.

Escalate immediately for uncertain disk identity, unavailable encryption keys, I/O/media errors, suspected data corruption, firmware/RAID changes, Secure Boot signing problems, multi-boot ownership uncertainty, or a repair that would write to storage without a verified backup.
