# Disk and filesystem investigation

“Disk problem” may mean four different things: no free blocks, no free inodes, a slow/failing device, or damaged filesystem metadata. Identify which condition exists before deleting files, remounting or running repair tools.

> **Write boundary:** partitioning, formatting, RAID/LVM changes, mounting read-write and filesystem repair can destroy data. Never run a repair tool on a mounted filesystem unless that filesystem's official procedure explicitly supports it. Stop on uncertain device identity or repeated I/O errors.

## Map the storage stack

Start read-only:

```bash
lsblk -e7 -o NAME,PATH,MODEL,SIZE,TYPE,FSTYPE,FSVER,UUID,MOUNTPOINTS
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
findmnt --verify
cat /etc/fstab
df -hT
df -ih
```

Read the output as layers, for example:

```text
physical/NVMe device
  -> partition
    -> LUKS container
      -> LVM physical/logical volume
        -> filesystem
          -> mount point
```

An error at one layer can surface at another. Record model, capacity, filesystem and stable IDs locally, but redact serial numbers and private mount names from public evidence.

### What each query proves

- `lsblk` maps block devices known to the kernel; it does not prove media health.
- `findmnt` maps mounts and options; an expected mount may be absent.
- `findmnt --verify` checks `fstab` consistency and userspace usability; it does not contact every remote dependency reliably.
- `df -hT` reports filesystem block accounting, not the physical device's remaining flash or thin-pool capacity.
- `df -ih` detects inode exhaustion, which can prevent file creation even with free bytes.
- A read-only mount (`ro`) may be intentional or a protective response to errors; check the mount design and logs before remounting.

## Capacity investigation

Identify the affected filesystem, then stay on it while locating usage:

```bash
df -hT /affected/path
du -x -h --max-depth=1 /affected/path
```

`-x` prevents crossing into other mounted filesystems. `du` can be expensive on a large tree and may miss unreadable paths. Narrow the directory and schedule scans appropriately.

Large-file search, scoped to one filesystem:

```bash
find /affected/path -xdev -type f -size +1G -printf '%s %p\n'
```

The byte count is unsorted and filenames can contain unusual characters; treat output carefully in tooling. Do not delete solely because a file is large. Determine its owner, retention requirement and writer.

A mismatch where `df` shows much more usage than `du` can be caused by:

- a deleted file still open by a process;
- filesystem reserved blocks/metadata;
- inaccessible directories excluded from the scan;
- snapshots/subvolumes outside the visible tree;
- mount confusion (data written beneath an absent mount);
- sparse files and different block-accounting methods.

If `lsof` is installed and authorised to view the relevant processes:

```bash
sudo lsof +L1
```

Restarting the writer or truncating its descriptor may release a deleted open file, but can interrupt service or lose logs. Preserve evidence and use the application's supported rotation/reopen method.

### Inodes

```bash
df -ih /affected/path
find /affected/path -xdev -printf '%h\n' | sort | uniq -c | sort -n
```

The second pipeline can be costly and is only a starting point for a filesystem with many entries. A high count can come from caches, sessions, mail queues or runaway logging. Deleting unknown small files can corrupt application state just as easily as deleting one large file.

## Device and kernel evidence

```bash
journalctl -k -b -p warning --no-pager
journalctl -k --since '2 hours ago' --no-pager
```

Look for timeouts, link resets, medium errors, filesystem warnings, NVMe status, controller resets or the kernel remounting a filesystem read-only. One line rarely proves whether the device, cable/backplane, controller, power or filesystem is at fault; preserve the sequence and repetition.

When `smartctl` from `smartmontools` is available:

```bash
sudo smartctl --info --health --attributes /dev/device
sudo smartctl --xall /dev/device
```

SMART/NVMe fields are vendor- and device-specific. “PASSED” does not guarantee a healthy disk, and some USB/RAID controllers hide or translate data. Compare trends, error logs and vendor thresholds. Starting a self-test changes device activity and may affect latency; schedule it and confirm the correct device/controller syntax.

For NVMe, if `nvme-cli` is installed:

```bash
sudo nvme smart-log /dev/nvmeX
sudo nvme error-log /dev/nvmeX
```

Replace placeholders only after matching the device. Temperature, percentage-used and media/error counters need device documentation and trend context.

## Filesystem-specific observations

Identify type first:

```bash
findmnt -no SOURCE,FSTYPE,OPTIONS /affected/path
```

Different filesystems use different tools and recovery rules:

- ext2/3/4 use `e2fsck` while unmounted for repair;
- XFS uses `xfs_repair` offline for many repairs and `xfs_scrub` where supported;
- Btrfs has device, scrub and check tooling with distinct semantics; `btrfs check --repair` is not a routine command;
- ZFS has pool-level status/scrub and should be managed with ZFS procedures;
- network filesystems require client, network and server-side evidence.

Do not run a generic `fsck` command against an encryption container, whole disk, RAID member or LVM physical volume. The target is normally the assembled block device containing the filesystem.

A no-write dispatch preview is available on util-linux systems:

```bash
sudo /usr/sbin/fsck -N /dev/mapper/example
```

This only shows the intended checker; it does not validate the placeholder device or make a later repair safe.

## LVM, encryption and RAID visibility

When the host uses these layers and tools are installed, read-only status usually includes:

```bash
sudo pvs
sudo vgs
sudo lvs -a -o +devices
sudo cryptsetup status mapping-name
cat /proc/mdstat
sudo mdadm --detail /dev/mdX
```

Check thin-pool **data and metadata** usage separately; a filesystem can show free space while its underlying thin pool is exhausted. For MD RAID, “degraded” identifies lost redundancy, not automatically lost data, but rebuild decisions can overwrite the wrong member. Do not initialise, add, remove or force-assemble members without an exact topology and recovery plan.

## Mount and `fstab` faults

For a failed mount:

```bash
systemctl status path-to-mount.mount --no-pager --full
journalctl -b -u path-to-mount.mount --no-pager
findmnt --verify
lsblk -f
```

Systemd escapes mount paths into unit names; use `systemd-escape -p --suffix=mount /path/to/mount` to derive one. Check UUID, filesystem type, mount-point existence, dependency ordering, credentials for remote mounts and whether the underlying device is assembled/unlocked.

Do not use `mount -a` casually: it attempts all currently unmounted `fstab` entries and can hang on remote filesystems. Test the intended entry with console access and a timeout/recovery route appropriate to the mount type.

## Investigation sequence

1. Confirm symptom, impact and affected path.
2. Map path to mount, filesystem and underlying device.
3. Check block and inode capacity.
4. Review mount options and whether the expected filesystem is actually mounted.
5. Correlate kernel/device logs with the failure time.
6. Inspect the relevant storage layer (LUKS/LVM/RAID/thin pool).
7. Use filesystem/device-specific read-only diagnostics.
8. Preserve data before any repair if errors or corruption are possible.
9. Change one understood cause under an approved plan.

## Validate or escalate

After a safe correction, verify capacity/inodes, intended mount source/options, a controlled read and write through the application path, kernel logs, service function, backup jobs and monitoring. A test file should be created only in an approved path and removed after confirming its contents; free space alone does not prove durability.

Escalate immediately for repeated I/O/media errors, an unexpectedly read-only filesystem, missing encryption keys, ambiguous device identity, degraded RAID, thin-pool metadata exhaustion, corruption indicators, unavailable backups or any repair requiring forced assembly/overwrite. Record topology, timestamps, exact errors and read-only checks—never encryption keys or sensitive data filenames.
