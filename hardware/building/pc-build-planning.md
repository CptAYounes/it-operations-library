# PC Build Planning

A build plan should answer two questions before packaging is opened: will the parts work together, and can the finished system meet its purpose without an avoidable power, cooling or expansion constraint?

Use the exact motherboard revision, CPU model and case/PSU documentation. A retailer's compatibility filter is useful for discovery, but it is not the final authority.

## Define the build

- [ ] State the intended workloads and the operating systems or hypervisor to be installed.
- [ ] Record the required CPU performance, memory capacity, storage capacity, network speed, display outputs and external I/O.
- [ ] Separate mandatory requirements from optional upgrades.
- [ ] Set the budget, physical size, noise and energy constraints.
- [ ] Identify any parts being reused and record their proven condition, interfaces and power requirements.
- [ ] Decide which future upgrades must remain possible: memory slots, PCIe slots, drive bays, cooling capacity and PSU headroom.

A gaming GPU, a large CPU cooler or many drives can each change the case, board and power choice. Define those constraints early rather than treating the enclosure and PSU as afterthoughts.

## Prove compatibility

### Processor, board and firmware

- [ ] Confirm the CPU appears on the support list for the **exact motherboard model and revision**.
- [ ] Record the minimum firmware version required for that CPU.
- [ ] If an update may be needed before the CPU can boot, confirm whether the board supports firmware update without a working CPU and what file/USB format the vendor requires.
- [ ] Confirm socket, chipset features, PCIe lane allocation and required display capability. Motherboard video connectors normally depend on a processor with integrated graphics.
- [ ] Confirm the board form factor fits the case and that the case has the correct standoff positions.

A matching socket is not enough. A board can have the right physical socket but lack firmware support or suitable power delivery for a particular processor.

### Memory

- [ ] Confirm the supported memory generation; DDR generations are not mechanically or electrically interchangeable.
- [ ] Confirm capacity limits, supported module count and whether the platform expects UDIMM, SO-DIMM or RDIMM.
- [ ] Check ECC support across the CPU, board, firmware and module type rather than relying on one component's specification.
- [ ] Prefer a matched kit for multi-channel operation and check the vendor's population rules for the target module count.
- [ ] Treat the qualified-vendor list as evidence that a configuration was tested, not as a guarantee that every unlisted module will fail or every listed overclock will be stable.

### Cooling and enclosure

- [ ] Confirm the cooler supports the socket and includes the correct mounting hardware.
- [ ] Compare cooler height and radiator dimensions with the case limits.
- [ ] Check for clearance conflicts with memory, motherboard heatsinks, the GPU and the top/front radiator position.
- [ ] Confirm the cooler is suitable for the processor's vendor-specified power and thermal requirements.
- [ ] Plan intake and exhaust paths and verify the case supplies, or can accept, the required fan sizes.
- [ ] For a liquid cooler, confirm radiator, tube and pump placement comply with the cooler and case instructions.

### Graphics and expansion

- [ ] Check GPU length, height, thickness and slot count against the case and adjacent expansion cards.
- [ ] Confirm the board provides the required physical slots and electrical lane width.
- [ ] Review lane-sharing rules. Populating an M.2 socket can disable or reduce another PCIe slot or SATA port on some boards.
- [ ] Confirm required display connectors and any specialised capture, storage or network card support.

### Storage

- [ ] Match each drive to a supported interface: SATA, PCIe/NVMe, SAS or another platform-specific connection.
- [ ] For M.2 devices, confirm key, length, protocol and the lanes supported by the chosen socket; an M.2 shape alone does not prove compatibility.
- [ ] Check the number of available ports, drive bays, cables, power connectors and motherboard standoffs/heatsinks.
- [ ] Record the intended boot, data, scratch and backup roles. Redundancy is not a backup.
- [ ] If RAID or hardware encryption is planned, confirm controller, OS, recovery and replacement-drive requirements before storing data.

### Power

- [ ] Estimate maximum system demand using component-vendor data or a reputable calculator, then allow sensible headroom for transient load, ageing and planned upgrades.
- [ ] Confirm the PSU provides the required motherboard, CPU, GPU, SATA and peripheral connectors without unsafe splitters.
- [ ] Confirm case compatibility, cable reach and PSU form factor.
- [ ] Check input-voltage and plug requirements for the intended location.
- [ ] Use only the modular cables supplied for, or explicitly approved for, the exact PSU model. PSU-side pinouts are not standardised.

A high wattage label does not establish quality or connector suitability. Protections, platform quality, warranty, acoustics and operation at the intended load also matter.

## Firmware and operating-system requirements

- [ ] Confirm the target OS supports the CPU architecture, storage controller, NIC, GPU and other essential devices.
- [ ] Obtain storage/network drivers in advance if the installer may not include them.
- [ ] Confirm UEFI, Secure Boot and TPM requirements for the target OS.
- [ ] Check whether virtualisation extensions, IOMMU, SR-IOV or other workload-specific firmware features are available.
- [ ] Identify the vendor support page and save the manuals, firmware notes and driver sources needed during the build.

## Build materials and recovery plan

- [ ] Prepare a clear, static-safe workspace with suitable lighting.
- [ ] Obtain the correct hand tools, thermal interface material if not pre-applied, cable ties and a labelled container for screws.
- [ ] Prepare the OS installer from an authoritative source and verify its published checksum where one is supplied.
- [ ] Decide how important data from reused storage will be backed up before the drive enters the new system.
- [ ] Record return windows and warranty routes without publishing serial numbers or proof-of-purchase details.

## Ready-to-build gate

Do not proceed until all mandatory requirements have a compatible part and a source of evidence. Record unresolved uncertainties explicitly; do not turn “probably compatible” into an assembly-time surprise.

The next steps are the [physical assembly checklist](physical-assembly.md), then [BIOS/UEFI configuration](../firmware/bios-uefi-configuration.md). The repository-level [new system build checklist](../../checklists/new-system-build.md) provides a concise end-to-end sign-off.
