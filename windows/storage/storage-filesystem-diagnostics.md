# W09 — Windows storage and filesystem diagnostics

Capacity, filesystem integrity and physical media health are separate questions. A full volume can stop an application while the disk is healthy; a healthy-looking NTFS volume can sit on failing media; hardware RAID can hide individual disks from Windows.

**Applies to:** Windows 11 and Windows Server 2022/2025. Disk Management is available on client and Server with Desktop Experience. Use PowerShell, `diskpart`, Storage Spaces tools or vendor management on Server Core. Cmdlet detail varies with bus, controller and storage provider.

## Stop conditions

Stop write-heavy tests and escalate when a disk:

- disappears or reconnects intermittently;
- reports failed/predictive-failure status;
- makes abnormal mechanical noise;
- belongs to degraded RAID/Storage Spaces whose repair ownership is unclear;
- contains irreplaceable, unbacked-up or forensically significant data;
- is encrypted and the recovery key is unavailable.

Repeated `chkdsk /r` is not a recovery strategy for failing hardware. Preserve data/image first where appropriate.

## Build a read-only map

Run elevated PowerShell for complete visibility:

```powershell
Get-Disk | Sort-Object Number |
    Select-Object Number, FriendlyName, SerialNumber, BusType, PartitionStyle, OperationalStatus, HealthStatus, Size, IsBoot, IsSystem, IsOffline, IsReadOnly

Get-Partition | Sort-Object DiskNumber, Offset |
    Select-Object DiskNumber, PartitionNumber, DriveLetter, Type, Size, Offset

Get-Volume | Sort-Object DriveLetter |
    Select-Object DriveLetter, FileSystemLabel, FileSystem, HealthStatus, OperationalStatus, SizeRemaining, Size
```

Serial numbers must be redacted before publication. `HealthStatus = Healthy` is the storage provider's current report, not a guarantee that the media has no latent fault.

For Storage Spaces:

```powershell
Get-StoragePool
Get-VirtualDisk
Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, HealthStatus, OperationalStatus, Size
```

`Get-PhysicalDisk` may describe poolable/provider-visible devices, not every physical disk behind a RAID controller. Use the controller/OEM utility for controller cache, array and member-disk state.

## Capacity: find the writer before deleting

```powershell
Get-Volume | Where-Object DriveLetter |
    ForEach-Object {
        [pscustomobject]@{
            Drive       = "$($_.DriveLetter):"
            FileSystem  = $_.FileSystem
            FreeGiB     = [math]::Round($_.SizeRemaining / 1GB, 2)
            TotalGiB    = [math]::Round($_.Size / 1GB, 2)
            FreePercent = if ($_.Size) { [math]::Round(100 * $_.SizeRemaining / $_.Size, 1) }
        }
    }
```

If a volume is full, identify growth by owner, path and time. Common areas include logs, dumps, update caches, temporary files, application data and shadow copies, but never delete one merely because it is common. Clearing a runaway log without fixing retention or the writer makes the fault return and removes evidence.

Useful observations:

```text
fsutil volume diskfree C:
vssadmin list shadowstorage
```

`vssadmin list shadowstorage` is read-only. Resizing or deleting shadow storage is destructive to restore points/snapshots and needs backup/recovery ownership.

## Filesystem checks: scan before repair

Identify the filesystem first. `chkdsk` behaviour and repair options are chiefly relevant to NTFS/FAT family volumes; ReFS uses its own integrity and repair model and does not rely on the same offline CHKDSK workflow.

Run CHKDSK, `fsutil` and `Repair-Volume` from an administrator terminal. The commands below may be read-only, diagnostic-state-writing or repairing; each boundary is stated separately.

**Non-fixing initial NTFS status check:**

```text
chkdsk C:
```

Without a repair switch, CHKDSK reports status rather than requesting a fix. It still writes diagnostic event/log evidence, and an active volume can produce transient observations.

**Controlled online scan:**

```text
chkdsk C: /scan
```

PowerShell scan path:

```powershell
Repair-Volume -DriveLetter C -Scan
```

`chkdsk /scan` writes diagnostic state and can perform supported online repair. With CHKDSK, `/forceofflinefix` prevents online repair but queues detected defects for offline fixing. `Repair-Volume -Scan` scans and reports corruption without requesting repair, although the scan still records diagnostic state. Confirm backup, target and change/outage authority before CHKDSK `/scan`; capture the result of either command and investigate hardware/provider events before further repair.

Check NTFS dirty state:

```text
fsutil dirty query C:
```

This is read-only. A dirty bit says the volume needs checking; it does not identify why.

### Repair levels

- `chkdsk C: /scan` — **controlled online change**, may perform supported online repair; `/forceofflinefix` instead queues detected defects for offline repair.
- `Repair-Volume -DriveLetter C -Scan` — **controlled scan**, reports corruption without requesting repair but records diagnostic state.
- `chkdsk C: /spotfix` or `Repair-Volume -SpotFix` — **change**, briefly takes NTFS volume offline where supported.
- `chkdsk C: /f` — **change**, fixes logical filesystem errors; system volume normally schedules at restart.
- `chkdsk C: /r` — **change and highly disruptive**, includes `/f` and attempts to locate readable data in bad sectors; can take a long time and stress failing media.
- `chkdsk C: /offlinescanandfix` — **offline change**, takes volume offline for scan/repair.

Back up, identify the correct volume and arrange downtime before repair. If physical failure is suspected, preserve/replace the device rather than treating a successful filesystem repair as hardware recovery.

## Physical/media observations

```powershell
Get-PhysicalDisk |
    Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus, CannotPool

Get-PhysicalDisk | Get-StorageReliabilityCounter |
    Select-Object DeviceId, Temperature, Wear, PowerOnHours, ReadErrorsTotal, WriteErrorsTotal
```

Reliability counters are not available through every USB bridge, RAID controller, virtual disk or storage driver. Missing/zero fields are unknown, not proof of zero wear/errors. Use vendor diagnostics and firmware/controller logs for definitive device detail.

For NVMe/SATA SMART, prefer the hardware/OEM supported tool and preserve raw values with model-specific interpretation. SMART attributes are vendor-specific; a single generic threshold table is unreliable.

## Event evidence

Query the relevant window in System log rather than relying on a universal ID list:

```powershell
$start = (Get-Date).AddHours(-6)
Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = $start
    Level     = 1,2,3
} | Where-Object ProviderName -Match 'disk|stor|ntfs|refs|volmgr|space' |
    Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message
```

Provider names and events vary by driver/build. Record device path, controller, operation, status/error and recurrence. A filesystem event downstream of controller resets does not make NTFS the root cause.

## Offline, encrypted and boot volumes

WinRE may assign different drive letters. `X:` normally belongs to the recovery environment. Use `diskpart` with `list disk` and `list volume` for **read-only identification**, then verify contents with `dir` before targeting a command.

BitLocker volumes need the authorised recovery route. Do not format an apparently inaccessible volume or publish recovery keys. Suspending protection, unlocking offline or changing protectors is a security-sensitive **change**.

Do not initialise an “Unknown/Not initialized” disk until its identity and data ownership are confirmed. `Initialize-Disk`, `Clear-Disk`, `diskpart clean`, format and partition deletion are **destructive** in an investigation.

## Performance versus integrity

High active time can come from workload, paging, queueing, controller retries or media latency. Capture latency/queue and process I/O using [W10 — Performance investigation](../troubleshooting/performance-investigation.md). Do not run a synthetic stress test on a degraded array or suspect disk.

## Validate the outcome

- [ ] expected disks, partitions and volumes are present;
- [ ] backup/restore path is confirmed before any repair;
- [ ] capacity is stable and the growth source/retention issue is addressed;
- [ ] filesystem scan is clean, or repair result and downtime are recorded;
- [ ] physical/controller/provider health has no unexplained warning;
- [ ] System log shows no repeating reset, I/O or filesystem error;
- [ ] required read/write/application test succeeds;
- [ ] encrypted volume protection and recovery ownership remain correct;
- [ ] restart/boot succeeds when the system volume was involved.

Filesystem consistency after `chkdsk` does not by itself close a physical-disk incident. Validate both layers.
