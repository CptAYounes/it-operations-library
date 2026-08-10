# BIOS/UEFI Configuration

Firmware settings sit below the operating system. A change to storage mode, boot mode, Secure Boot keys, memory tuning or TPM state can make a working installation unbootable or trigger an encryption recovery prompt. Review settings deliberately and change only those tied to a requirement.

Labels differ between vendors and firmware releases. The system or motherboard manual and the release notes for the installed version take precedence over this checklist.

## Capture the starting state

- [ ] Record the exact system/board model and board revision without publishing serial or asset identifiers.
- [ ] Record the current firmware version and date.
- [ ] Photograph or transcribe non-default settings needed for storage, boot, cooling, virtualisation and power recovery; check images for identifiers before publication.
- [ ] Confirm recovery material is available for encrypted operating-system volumes before changing boot security, TPM or firmware.
- [ ] Confirm the intended OS, boot device, storage-controller mode and any virtualisation requirement.
- [ ] Use stable utility power. Do not start a firmware update while power or the system itself is unreliable.

Loading “optimised defaults” changes many settings at once. It can be a valid recovery step, but it is not a harmless way to begin a routine review.

## Baseline hardware checks

Before tuning anything, confirm firmware reports:

- [ ] the expected CPU model and sensible idle temperature trend;
- [ ] the full installed memory capacity at a standard supported speed;
- [ ] every expected SATA and NVMe boot/storage device;
- [ ] CPU fan and, where applicable, pump speed;
- [ ] the intended GPU or other critical PCIe devices where the firmware exposes them;
- [ ] a plausible date and time that remain correct after power removal.

Missing capacity, a rapidly rising temperature or a device that appears only intermittently is a hardware problem to resolve before OS installation. Use [RAM troubleshooting](../memory/ram-troubleshooting.md), [storage diagnostics](../storage/storage-diagnostics.md) or the [thermal guide](../thermals/cpu-thermal-troubleshooting.md) as appropriate.

## Boot configuration

- [ ] Prefer native UEFI boot for a modern OS unless a documented legacy requirement exists.
- [ ] Confirm Compatibility Support Module (CSM)/legacy boot is disabled when the OS and devices support UEFI and Secure Boot.
- [ ] Put the intended installer or OS boot entry first without leaving untrusted removable media as a permanent higher-priority option.
- [ ] Distinguish a UEFI OS boot entry such as “Windows Boot Manager” from the physical disk. Selecting the disk directly can bypass the expected bootloader path.
- [ ] Confirm the storage-controller mode—such as AHCI, RAID/VMD or vendor-specific mode—matches the driver and installation design.
- [ ] Do not change controller mode on an installed OS until its boot-driver and recovery procedure have been prepared and downtime authorised.
- [ ] Remove temporary network/PXE boot precedence after deployment unless network boot is an operational requirement.

## CPU, memory and PCIe settings

- [ ] Leave CPU voltage, multiplier and platform power controls at supported defaults unless tuning is explicitly in scope.
- [ ] Establish a stable baseline at standard memory settings before enabling XMP/EXPO or manual timings.
- [ ] Treat XMP/EXPO as a memory overclocking profile: it can be useful, but the advertised module profile may exceed the CPU's official memory specification.
- [ ] After enabling a memory profile, confirm capacity, speed and stability with the method in [RAM troubleshooting](../memory/ram-troubleshooting.md).
- [ ] Enable CPU virtualisation extensions only where required; enable IOMMU/VT-d/AMD-Vi separately if device passthrough or isolation requires it.
- [ ] Set PCIe generation manually only to work around a confirmed compatibility or signal issue; “Auto” is normally the better baseline.
- [ ] Enable features such as Resizable BAR only when the CPU, board, GPU, firmware and OS/driver combination supports them.

Changing many performance controls together destroys the baseline. Apply one related group, validate it, and retain a route back to the last stable state.

## Platform security

- [ ] Confirm whether the OS requires a firmware TPM and which implementation is active.
- [ ] Verify Secure Boot mode and key state against the OS requirement rather than assuming “enabled” means active.
- [ ] Do not clear the TPM or replace Secure Boot keys as a troubleshooting experiment. Either action can affect protected data, credentials or boot trust.
- [ ] Record encryption recovery readiness before a TPM, Secure Boot, CSM, boot-order or firmware change.
- [ ] Disable unused boot sources or external interfaces only where this matches the system's operational and recovery requirements.
- [ ] Set firmware administrator passwords only under an approved credential-storage and recovery process. A lost firmware password can require vendor service or board replacement.

## Cooling, power and operational behaviour

- [ ] Map each reported fan to its physical header before changing curves.
- [ ] Select PWM or DC control to match the fan and header documentation.
- [ ] Keep a fail-safe response for CPU cooling; do not silence a fan warning until the sensor/pump arrangement has been verified.
- [ ] Check fan response at low and higher temperature points without permitting fan-stop settings to hide a failed fan.
- [ ] Set behaviour after AC loss—remain off, previous state or power on—to match the system's operational requirement.
- [ ] Configure Wake-on-LAN, scheduled power-on and USB wake only when needed, then test both the wake path and unintended-wake behaviour.
- [ ] Preserve vendor thermal and current protections. Do not disable them to keep an unstable workload running.

## Firmware updates

Update firmware for a supported CPU, a relevant defect/security fix, required device compatibility or an approved standard—not simply because a newer file exists.

Before an update:

- [ ] Match the file to the exact system/board model and hardware revision.
- [ ] Read every intervening release note and vendor prerequisite, including staged or bridge versions.
- [ ] Check whether the update resets settings, management-controller configuration or Secure Boot state.
- [ ] Back up important data and prepare OS encryption recovery.
- [ ] Return unstable CPU and memory tuning to supported defaults.
- [ ] Use the vendor-supported update mechanism and required filesystem/file naming.
- [ ] Do not use a firmware image from a visually similar board or interrupt an update that appears slow.

After the update, allow documented restarts and memory training to finish. If the process fails, use only the vendor recovery mechanism; repeated blind power cycles can make recovery harder.

## Post-change validation

- [ ] Save settings once, restart, re-enter firmware and confirm the intended values persisted.
- [ ] Confirm CPU, full memory and all expected storage devices are still detected.
- [ ] Confirm fan/pump readings and temperature are normal for the system and environment.
- [ ] Boot the intended OS without an unexpected recovery prompt.
- [ ] In the OS, verify time, network, storage, device status and encryption/protection state.
- [ ] Test the feature that justified the change: virtual-machine launch, Secure Boot status, wake event, memory stability or the required boot path.
- [ ] Complete a controlled shutdown, cold start and restart.
- [ ] Record changed settings, reason, firmware version and validation result.

Escalate rather than proceed when release notes are ambiguous for the exact revision, stable power cannot be assured, recovery material is missing, the device is under a vendor-managed update policy, or a failed update requires board-level programming. The [new system build checklist](../../checklists/new-system-build.md) uses these checks as its firmware sign-off.
