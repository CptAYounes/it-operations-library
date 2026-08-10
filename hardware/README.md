# Hardware

This section covers the work around a system rather than a particular brand of component: planning a compatible build, assembling it safely, configuring firmware, and reducing a hardware symptom to a defensible fault domain.

The guides favour observations that do not change state. Power removal, component removal, firmware resets, stress tests and replacement come later, with explicit stop conditions. A motherboard or system service manual remains the authority for connector locations, supported components, diagnostic codes and disassembly.

## Guides

| ID | Guide | Use it when |
|---|---|---|
| H01 | [PC build planning](building/pc-build-planning.md) | Selecting parts and proving compatibility before assembly |
| H02 | [Physical assembly](building/physical-assembly.md) | Building or rebuilding a system and checking it before first power |
| H03 | [No-POST troubleshooting](diagnostics/no-post-troubleshooting.md) | Fans or indicators may operate, but firmware does not complete POST |
| H04 | [BIOS/UEFI configuration](firmware/bios-uefi-configuration.md) | Reviewing firmware settings, boot requirements or an approved update |
| H05 | [RAM troubleshooting](memory/ram-troubleshooting.md) | Investigating memory errors, instability, training failures or missing capacity |
| H06 | [Storage diagnostics](storage/storage-diagnostics.md) | Separating detection, device-health, filesystem and performance faults |
| H07 | [CPU and thermal troubleshooting](thermals/cpu-thermal-troubleshooting.md) | Investigating throttling, excessive temperature or thermal shutdown |
| H08 | [Power fault methodology](diagnostics/power-fault-methodology.md) | Investigating no-power, unexpected power loss or load-related resets |
| H09 | [Hardware fault isolation](diagnostics/fault-isolation.md) | Structuring an investigation when the failed component is not yet known |

The shorter [new system build checklist](../checklists/new-system-build.md) and [hardware diagnostics checklist](../checklists/hardware-diagnostics.md) are release gates. They point back to these guides instead of repeating the diagnostic detail.

## Choosing the right starting point

- **No lights, fans or standby indication:** start with [power fault methodology](diagnostics/power-fault-methodology.md).
- **Power is present but there is no firmware screen or successful POST indication:** use the [no-POST workflow](diagnostics/no-post-troubleshooting.md).
- **Firmware completes, but no operating system starts:** confirm boot-device detection in [storage diagnostics](storage/storage-diagnostics.md) and boot settings in [BIOS/UEFI configuration](firmware/bios-uefi-configuration.md). An OS boot guide is the next step once hardware detection is stable.
- **The system runs but fails intermittently:** use [fault isolation](diagnostics/fault-isolation.md), then follow the memory, storage, thermal or power branch supported by the evidence.

## Working rules

1. **Describe what is observed.** “Unexpected restart under graphics load” is evidence; “bad PSU” is only a hypothesis until isolated.
2. **Preserve data and configuration first.** Record firmware settings, encryption recovery requirements and storage layout before resetting or moving anything.
3. **De-energise before internal work.** Shut down, disconnect external power and follow vendor discharge instructions. A PSU enclosure is not a serviceable area.
4. **Change one controlled variable at a time.** Otherwise a successful boot does not show which change mattered.
5. **Treat known-good parts as test instruments.** Compatibility must be established, and the test must not put the known-good component or stored data at risk.
6. **Validate beyond the original symptom.** Confirm component detection, repeated starts where appropriate, OS health and the expected workload before closing the fault.

`POST` means the firmware power-on self-test. `BIOS/UEFI` is used where advice applies to firmware generally; exact labels and available controls vary by vendor, board revision and firmware release.
