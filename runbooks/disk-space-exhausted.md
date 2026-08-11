# Disk space exhausted

Treat a full filesystem as both an availability risk and a clue. Deleting the largest visible file may briefly clear the alert while leaving the writer, inode shortage or retention fault untouched.

## First five minutes

1. Confirm the affected volume/filesystem, threshold, trend and impact.
2. Check whether capacity or inode/file-count exhaustion is the limit.
3. Record recent changes, failed jobs and which process is reporting write errors.
4. Avoid rebooting and do not recursively delete logs, temporary trees or unknown data.

Windows capacity view:

```powershell
Get-Volume | Select-Object DriveLetter, FileSystem, HealthStatus, Size, SizeRemaining
Get-ChildItem C:\Path -Force -ErrorAction Stop |
    Sort-Object Length -Descending |
    Select-Object -First 20 FullName, Length
```

The second command lists only immediate files; recursive scanning can be slow and access-controlled. Use an approved storage tool for large trees.

Linux starting points:

```bash
df -hT
df -ih
sudo du -x -d 1 /var 2>/dev/null | sort -n
sudo lsof +L1
```

With GNU `du`, `-x` stays on the filesystem containing `/var` and `-d 1` reports only the first directory level. The `2>/dev/null` redirection hides permission and traversal errors, so treat missing paths as unknown rather than empty. `du` still needs appropriate permission and may increase I/O load. `lsof +L1` finds deleted files still held open, which can explain a mismatch between `df` and visible files. See the [Linux storage guide](../linux/storage/disk-filesystem-investigation.md) or [Windows storage guide](../windows/storage/storage-filesystem-diagnostics.md).

## Decide what is safe

Identify ownership, retention and recovery value before removing or moving anything. Prefer supported actions such as correcting a failed log rotation, clearing an application's documented cache, extending an approved volume, or moving data through its lifecycle process. Compressing active logs, truncating open files, deleting package databases or relocating application data ad hoc can cause corruption or make recovery harder.

For critically low space, agree which service can be paused or which known expendable data can be removed. Record every path and quantity affected. If a runaway writer is involved, containing it may be more important than freeing space.

## Escalate when

- the volume contains databases, backups, audit/security logs or unknown customer data;
- ownership or retention requirements are unclear;
- storage reports I/O errors or read-only remounts;
- expansion, downtime or service shutdown needs approval;
- space returns quickly after cleanup;
- backup/recovery capability is also impaired.

## Validate

Recheck free capacity and inodes, then test the previously failing write or service operation. Confirm the writer/rotation fault is controlled, monitoring clears, scheduled work can continue and expected retention remains intact. Record before/after capacity, identified growth source, action, validation and follow-up threshold or retention changes.
