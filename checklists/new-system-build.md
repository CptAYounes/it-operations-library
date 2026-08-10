# New System Build Checklist

Use this as the build sign-off, not as a substitute for the component manuals. Detailed decisions and techniques are in [PC build planning](../hardware/building/pc-build-planning.md), [physical assembly](../hardware/building/physical-assembly.md) and [BIOS/UEFI configuration](../hardware/firmware/bios-uefi-configuration.md).

Mark an item only when its outcome can be observed or recorded. Mark a non-applicable item `N/A` with a reason.

```text
Build reference:
Purpose:
Builder:
Date:
Board/system model and revision:
Firmware version before/after:
Exceptions or N/A reasons:
```

Do not record public serial numbers, product keys, account credentials or unredacted proof-of-purchase details.

## Plan and compatibility

- [ ] Intended workload, OS, required capacity, physical limits and budget are recorded.
- [ ] CPU support is confirmed for the exact motherboard/system revision and planned firmware version.
- [ ] Memory type, capacity, module count and population order match the platform support information.
- [ ] Cooler socket support, capacity and case/RAM/VRM clearance are confirmed.
- [ ] Board and PSU form factors match the case and the case has the required standoff positions.
- [ ] GPU and expansion-card dimensions, slot lanes, power connectors and display outputs are compatible.
- [ ] Each storage device matches a supported port/socket, protocol and physical size.
- [ ] M.2/PCIe/SATA lane-sharing effects are checked for the final device population.
- [ ] PSU capacity and all required motherboard, CPU, GPU and storage connectors are documented.
- [ ] Every modular power cable is supplied or explicitly approved for the exact PSU model.
- [ ] Required UEFI, TPM, Secure Boot, virtualisation, storage-controller and driver support is confirmed for the target OS.
- [ ] Upgrade headroom and any accepted compatibility limitations are recorded.

## Data, tools and safety

- [ ] Important data on every reused drive has a verified backup or an approved recovery plan.
- [ ] Encryption recovery material is available before firmware, TPM or storage changes.
- [ ] Vendor manuals, current support notes and required firmware/drivers are available offline.
- [ ] Installation media came from an authoritative source and matches the publisher's checksum where one is provided.
- [ ] Workspace is stable, well lit, uncluttered and suitable for ESD-controlled work.
- [ ] External power is disconnected before assembly and a labelled container is available for fasteners.
- [ ] Received/reused parts pass a visual inspection with no socket, connector, PCB, cable, coolant or battery damage.

Stop the build for physical/electrical damage, liquid, an unclear proprietary power pinout, missing recovery material or an unresolved mandatory compatibility check.

## Mechanical assembly

- [ ] CPU orientation is correct and the socket closed without contact damage or force.
- [ ] Correct cooler backplate, spacers and fasteners are installed in the documented pattern.
- [ ] Cold-plate protective film is removed and the specified thermal interface material is applied once.
- [ ] CPU fan and any pump are connected to the documented headers and power source.
- [ ] DIMMs occupy the documented slots and all required latches are fully engaged.
- [ ] M.2 devices use the correct standoff/fastener and their heatsink films/pads are correctly fitted.
- [ ] Case standoffs exist only beneath motherboard mounting holes.
- [ ] A separate I/O shield is fitted correctly, with no tab entering a port, if applicable.
- [ ] Motherboard and expansion-card fasteners are secure without visible board distortion.
- [ ] The 24-pin motherboard and required EPS/CPU power connectors are fully latched.
- [ ] GPU and other cards are fully seated, bracket-secured and supplied by the required power connectors.
- [ ] Storage devices are secured and their data/power connectors are not side-loaded.
- [ ] Front-panel, USB, audio and fan leads match the board pinout and connector keying.
- [ ] Fans/radiators follow the planned intake/exhaust direction and all fan blades are unobstructed.
- [ ] Cable routing respects high-current connector bend guidance and does not block airflow.

## Pre-power inspection

- [ ] No loose fastener, extra standoff, conductive debris or trapped cable remains inside the chassis.
- [ ] CPU cooler does not move under light inspection and required fan/pump connectors are present.
- [ ] Memory, cards and power connectors show no visible gap at their retention points.
- [ ] PSU input setting, removable cord and protected supply are suitable for the location.
- [ ] Monitor is attached to the intended active graphics output and the correct input is selected.
- [ ] Non-essential USB devices and non-boot data storage are disconnected for first POST or their inclusion is justified.

## First POST and firmware

- [ ] First-power fan, LED, beep/debug-code and display observations are recorded.
- [ ] Expected memory training is allowed to complete without repeated manual power cycling.
- [ ] Firmware completes POST without unresolved diagnostic warnings.
- [ ] Firmware reports the expected CPU model and total memory at supported baseline settings.
- [ ] Firmware reports every intended storage device and required PCIe device.
- [ ] CPU temperature trend is stable and required fan/pump speed is non-zero or otherwise correctly monitored.
- [ ] Date/time, native UEFI boot mode, boot order and storage-controller mode match the build plan.
- [ ] Secure Boot and TPM state match the OS plan without unapproved key or TPM clearing.
- [ ] CPU/memory voltage and performance controls remain at supported defaults for baseline validation.
- [ ] Virtualisation/IOMMU, fan control and AC-recovery settings match recorded requirements.
- [ ] Any firmware update used the exact model/revision image, vendor method, stable power and documented result.

Use the [no-POST workflow](../hardware/diagnostics/no-post-troubleshooting.md) if firmware does not complete; do not continue to OS installation on intermittent hardware detection or a rising CPU temperature.

## OS hand-off and final validation

- [ ] OS installer boots in the intended UEFI mode and targets the positively identified destination drive.
- [ ] All expected CPU threads, memory capacity, storage, GPU, NIC and other required devices appear in the installed OS.
- [ ] Device manager/logs contain no unexplained missing device or new hardware-error event.
- [ ] OS boot, controlled shutdown and restart complete without firmware or encryption recovery errors.
- [ ] At least one cold start completes with consistent component detection.
- [ ] Idle temperature, fan/pump response and system noise are checked with the case closed.
- [ ] A controlled representative workload completes with stable temperature, clocks, power and no hardware errors.
- [ ] Required network, display, audio, USB and storage ports are functionally checked.
- [ ] Backup or recovery setup required by the build plan is enabled and an agreed verification/readback succeeds.
- [ ] Panels, filters, slot covers and external cabling are fitted and airflow remains unobstructed.
- [ ] Component models, final firmware settings, validation evidence and known limitations are recorded.
- [ ] Temporary test parts, boot media and diagnostic settings have been removed or documented for retention.

```text
Validation result: PASS / PASS WITH RECORDED EXCEPTIONS / FAIL
Outstanding issue and owner:
Evidence location:
Completed by/date:
```

A build passes only when mandatory checks and the original purpose are met. A machine that merely reaches the desktop is not yet a validated build.
