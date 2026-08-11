# Storage Diagnostics

A storage complaint usually belongs to one of four layers:

1. **detection** — firmware or the OS cannot see the device;
2. **device/media health** — the controller reports errors, wear or failed reads/writes;
3. **layout/filesystem** — partitions, RAID metadata, encryption or the filesystem is damaged;
4. **performance/application** — the device is present but I/O is slow or blocked.

Keep these layers separate. Formatting a device does not fix a missing power cable; replacing a disk does not fix a full filesystem or a saturated controller.

## Data-safety gate

Before a write test, firmware update, repair command, reinitialisation or cable swap:

- identify the correct physical and logical device;
- record the storage topology, including RAID/controller membership and encryption;
- check backup status and whether a restore has actually been proven;
- capture current errors and health data;
- establish whether the device contains the only copy of important data;
- obtain authority for downtime or state-changing work.

Stop normal writes and escalate for recovery when a device clicks or repeatedly disappears, has liquid/impact damage, reports rapidly increasing uncorrectable errors, or contains irreplaceable data without a verified backup. Repeated power cycles and filesystem repairs can reduce recovery options.

## Establish scope without changing state

### Firmware and physical topology

Confirm whether firmware detects the device at every cold start. For RAID/HBA-attached storage, also check the controller interface and management logs. Record the port, bay or slot and logical volume mapping without exposing serial numbers.

A device absent from firmware points below the filesystem. A device visible to a controller but absent from the OS can instead indicate driver, mode, policy or logical-volume configuration.

### Windows

Run from PowerShell; these commands are read-only:

```powershell
Get-Disk | Format-Table Number, FriendlyName, BusType, OperationalStatus, HealthStatus, Size
Get-PhysicalDisk | Format-Table FriendlyName, MediaType, OperationalStatus, HealthStatus, Size
Get-Volume | Format-Table DriveLetter, FileSystem, HealthStatus, SizeRemaining, Size
Get-PhysicalDisk | Get-StorageReliabilityCounter
```

Availability and fields depend on Windows edition, storage driver, controller and enclosure. USB bridges and hardware RAID often hide underlying SMART/reliability data. Do not interpret `Healthy` as a complete media test.

Also review the **System** log for Disk, StorPort, stornvme, Ntfs and WHEA events around the symptom. Preserve the event ID, timestamp and device path; one event alone may describe a timeout anywhere in the path.

### Linux

Read-only discovery commands:

```bash
lsblk -o NAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINTS
findmnt
journalctl -k -b | grep -Ei 'ata|nvme|scsi|i/o error|reset|timeout|filesystem'
```

Kernel log access can require elevation. Device names can change between boots; identify a target using topology and model/capacity before issuing any later command. Avoid publishing raw outputs that include serials, WWNs, hostnames or real mount paths.

## Device health

Where the controller exposes it, `smartmontools` can read ATA/SCSI/NVMe health on Windows and Linux:

```bash
sudo smartctl --all /dev/sdX
sudo smartctl --xall /dev/nvme0
```

Replace the example device only after positive identification. Reading is normally non-destructive, but support through RAID and USB may require a controller-specific device type. Do not guess passthrough options against an array.

For NVMe on Linux, `nvme-cli` can provide the native log:

```bash
sudo nvme smart-log /dev/nvme0
sudo nvme error-log /dev/nvme0
```

Interpret attributes using the drive or platform vendor's documentation:

- an overall SMART pass is not a guarantee against failure;
- raw ATA attribute formats and thresholds are vendor-specific;
- NVMe `critical_warning`, `media_errors`, available spare, temperature and percentage used need context;
- interface CRC/link errors can implicate a cable, connector or signal path rather than the media;
- corrected events or normal wear indicators become useful when compared with a prior baseline.

A SMART self-test runs inside the drive and can create extra load. Confirm duration, workload impact and vendor guidance before starting one. Preserve the pre-test log and review the self-test result afterwards.

## Branch A: device not detected or intermittent

1. Compare firmware, controller and OS visibility to locate the failing boundary.
2. Power down and follow the vendor discharge/hot-swap procedure. Ordinary internal SATA/NVMe work should be de-energised; supported hot-swap bays require their own procedure.
3. Inspect and reseat the data and power path at both ends where accessible.
4. For SATA, test a compatible known-good cable and then a known-good port, changing one variable at a time.
5. For M.2, verify protocol, key, length, standoff position, heatsink installation and motherboard lane-sharing rules.
6. For externally attached media, test the approved port/cable and account for enclosure power and USB/SAS bridge behaviour.
7. Check whether a recent firmware change altered AHCI/RAID/VMD or PCIe settings.

Never move or initialise members of an unknown RAID set independently. On systems with multipath, hot-swap, hardware RAID or shared storage, use the platform procedure and confirm redundancy before touching a path.

## Branch B: health or media errors

- Capture health counters and OS/controller logs before reseating or updating anything.
- If reads are still reliable and policy permits, prioritise a backup or controlled image over a stress test.
- Correlate errors by time: device error, controller reset, power event and application timeout may be one chain.
- Where safe, compare whether interface errors stop after a cable/port change while media errors remain attached to the device.
- Replace a device when vendor criteria, array state or repeatable evidence justifies it. Do not wait for a generic SMART “FAILED” state if the system is already losing data.

For an array, degraded is not the same as protected. Confirm which member failed, the remaining redundancy and the rebuild plan before removal. A second wrong drive can make data unavailable.

## Branch C: filesystem or volume

First confirm the block device is stable. Filesystem repair on failing media can turn readable metadata into additional writes and obscure the original evidence.

Controlled scan examples:

**Windows (NTFS):**

```powershell
chkdsk X: /scan
```

Run CHKDSK from an administrator terminal. `/scan` is an online NTFS **change**: it writes diagnostic state and can perform supported online repair unless `/forceofflinefix` is used to queue detected defects for offline repair. Confirm backup, the exact volume and change authority before running it, especially when media may be failing. Other filesystems and older Windows versions differ; `/f`, `/r` and offline repair are more disruptive and can require downtime.

**Linux:**

```bash
findmnt /mount/point
sudo fsck -N /dev/example
```

`fsck -N` shows what would be run; it does not perform a check. Actual repair syntax is filesystem-specific. Never run a modifying `fsck` on a mounted filesystem, and do not run a generic repair command against an encrypted container, RAID member or volume-manager physical volume. Identify and unmount the correct filesystem through an approved recovery procedure first.

A full volume may mimic device failure. Check free space, inode use where relevant, snapshots, quotas and the process generating data before deleting anything.

## Branch D: slow storage

Measure before benchmarking:

- latency and queue depth during the complaint;
- active processes and I/O pattern;
- free capacity and thin-provisioning state;
- thermal throttling;
- negotiated link width/speed and controller mode;
- RAID rebuild, scrubbing, backup, antivirus or update activity;
- memory pressure that is causing paging.

Do not run an unbounded write benchmark on a production, thin-provisioned, deduplicated or endurance-limited device. Use a representative, size-bounded test file on approved scratch space and record caching conditions if performance testing is authorised.

## Corrective-action boundaries

Firmware updates, secure erase, reinitialisation, RAID rebuilds and filesystem repairs are state-changing operations. They require a verified backup/recovery route, exact vendor procedure, stable power and approval. Do not use destructive “bad block” write tests on data-bearing media.

Escalate when:

- important data is at risk or recovery is the priority;
- RAID topology or failed-member identity is uncertain;
- the device drops during reads or health data worsens rapidly;
- enclosure/controller passthrough hides evidence needed for diagnosis;
- proprietary tools, clean-room recovery, a hot-swap procedure or a maintenance window is required;
- replacement and restore authority is outside scope.

## Validate the result

- Device presence remains stable across an authorised cold start and restart.
- Firmware/controller/OS all report the expected device and logical volumes.
- No new link resets, I/O errors or critical health warnings appear during a representative read/write workload.
- Filesystem or application checks complete without new errors.
- Capacity, mount points/drive letters, permissions and encryption state are correct.
- The backup job and, where the fault affected data, an agreed restore/readback check succeed.
- The original symptom is reproduced as fixed, and the cause is recorded only to the level supported by evidence.

If the device disappears with wider system resets, include the [power fault methodology](../diagnostics/power-fault-methodology.md) in the investigation.
