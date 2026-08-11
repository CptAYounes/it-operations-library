# Operating system will not boot

First identify the stage that fails. Power, POST, firmware, bootloader, kernel and operating-system startup are different fault domains; using one recovery tool at the wrong stage can make the fault harder to recover.

## Triage by last known stage

- **No power or no POST:** follow the [no-POST workflow](../hardware/diagnostics/no-post-troubleshooting.md).
- **Firmware cannot see the boot device:** record firmware detection and cabling/slot state; do not initialise or format the device.
- **No boot entry / bootloader error:** confirm boot mode, device order and recent firmware/storage changes.
- **Kernel or Windows loader starts then fails:** photograph or transcribe the exact stop code/message and time.
- **Login never appears but the system responds remotely:** treat it as a display or service fault, not necessarily a boot failure.

## Safe evidence collection

1. Check maintenance, patch and change records before another restart.
2. Use the approved console. Record exact messages and the last successful stage.
3. Disconnect newly connected non-essential peripherals only if physical work is authorised and shutdown state is safe.
4. In firmware, verify the expected storage device and boot entry are visible. Record settings before changing anything.
5. If a recovery environment is available, inspect rather than repair first:
   - Windows: use WinRE **Troubleshoot > Advanced options** and Startup Repair logs. Record boot entries with `bcdedit`. To identify volumes, use the explicit DiskPart sequence below and record volume number, letter, label, filesystem, size and status before exiting:

     ```text
     diskpart
     list volume
     exit
     ```

     DiskPart is write-capable. In this diagnostic step, do not use `clean`, `format`, `delete`, `create`, `extend`, `shrink`, `assign` or any other state-changing command;
   - Linux: previous boot entries, recovery target, kernel command line, and an approved live/rescue environment.
6. Check storage health before repeated repair attempts when I/O errors or disappearing devices are present.

Filesystem repair (`chkdsk /f`, `fsck`), boot-record changes, registry edits and restoring a snapshot all modify state. Use them only with a backup/recovery decision, correct device identification and change authority. Never run `fsck` on a mounted read-write filesystem.

## Recovery choices

Prefer the least invasive supported option that matches evidence: revert one known configuration change, boot a previous known-good kernel, use Windows Startup Repair, or restore through the documented recovery procedure. Keep a record of every attempt; repeated automatic repair cycles can hide which action changed the state.

## Stop and escalate

Escalate for storage failure indications, encrypted volumes without the approved recovery material, possible compromise, unknown disk layout, repeated kernel/stop errors, data-loss risk, or any action beyond local authority. Escalate early if redundancy or a time-critical service is affected.

## Confirm recovery

A login screen is not enough. Confirm expected volumes, services, networking, logs, update/driver state and monitoring. Perform a controlled restart only if required by the recovery plan and safe for the service. Record the boot stage, evidence, action, recovered state and follow-up; link to the appropriate [Windows](../windows/README.md) or [Linux](../linux/README.md) boot guide.
