# No-POST Troubleshooting

Use this workflow when a machine receives power but does not complete its power-on self-test (POST). The boundary matters:

- **No power indication at all:** start with [power fault methodology](power-fault-methodology.md).
- **POST completes but no OS starts:** investigate boot configuration and storage rather than dismantling known-working hardware.
- **The system may have completed POST but there is no picture:** test the display path before treating it as a board failure.

## Before changing anything

Record the reported symptom and reproduce it once if doing so is safe. Note whether the fault followed transport, cleaning, a component change, a firmware change, a power event or a period of normal operation.

Stop immediately for smoke, burning smell, liquid, arcing, severe physical damage or a PSU protection trip. Disconnect supply power and escalate rather than repeatedly energising the system.

## Fast external checks

1. Confirm the monitor has power, is on the correct input and works with another source if one is available.
2. Connect the display cable to the active graphics device. Motherboard video outputs normally require a CPU with integrated graphics and firmware support.
3. Remove non-essential USB devices, hubs and removable media. A failed peripheral or damaged port can prevent early initialisation.
4. Check the AC path, PSU rear switch, external power leads and any chassis interlock without opening the PSU.
5. Allow time for memory training after a CPU, memory or firmware change. Some boards restart more than once; use the board manual to distinguish expected training from a loop.

If this restores a display, reconnect peripherals one at a time and validate repeated starts. A single successful POST is evidence, not yet a complete repair.

## Read the board's evidence

Before reseating parts, observe:

- standby and power LEDs;
- fan start, stop or cycling behaviour;
- speaker beep pattern;
- two-digit POST code;
- CPU/DRAM/VGA/BOOT diagnostic LEDs;
- whether the keyboard initialises or the system responds to the firmware setup key.

Look up codes in the manual for the exact board or system. Similar-looking codes are not standard across vendors, and a lit stage LED shows where progress stopped—not necessarily which component is defective.

## Isolation sequence

Power down, disconnect external power and use the vendor's discharge procedure before every internal change. Confirm standby LEDs are off. Do not insert or remove components while the board is energised.

### 1. Verify recent work and power connections

- Inspect the 24-pin motherboard connector, CPU EPS connector(s), GPU power and cooler connections.
- Confirm PCIe/GPU and EPS/CPU cables have not been interchanged and that modular cables belong to the exact PSU model.
- Look for a trapped lead, loose screw, incorrect standoff, partly seated card or damaged front USB header.
- If the fault began after assembly, compare every connection against the manuals instead of relying on memory.

Attempt one controlled POST after correcting an observed problem. Record the change and result.

### 2. Reduce to minimum POST hardware

Disconnect or remove non-essential devices until only the supported minimum remains:

- motherboard and CPU with correctly installed cooler;
- one memory module in the vendor-recommended single-module slot;
- PSU and required power leads;
- firmware speaker/diagnostic display if available;
- integrated graphics, or one GPU only when the CPU/platform has no usable integrated graphics;
- power button, or the documented board power control.

Storage is normally unnecessary to reach firmware. Removing it separates a POST fault from a boot-device fault. Photograph or label storage and expansion connections first when topology matters.

If the minimum system reaches POST, reconnect one device or cable at a time until the failure returns. Re-test the last good state before assigning cause.

### 3. Isolate memory

1. Restore standard memory settings if firmware is accessible; XMP/EXPO and manual tuning introduce a stability variable.
2. Reseat one module in the recommended slot.
3. Test each module individually in that same known-working slot.
4. If one module works, use it to test the other required slots.

This matrix can separate a module from a slot/channel problem, but it may also expose CPU socket contact, cooler pressure or memory-controller faults. Continue with the [RAM troubleshooting guide](../memory/ram-troubleshooting.md) before condemning the board.

### 4. Isolate the graphics path

- Reseat the GPU and its power connectors.
- Try a known-good cable, monitor and one supported output at a time.
- If the CPU and board support integrated graphics, remove the discrete card and test the motherboard output.
- Otherwise test a compatible known-good GPU only if its power demand and connectors are supported.

A successful test with another GPU narrows the fault to the original card or its power/cabling/configuration; it does not by itself prove which of those is responsible.

### 5. Reset firmware settings only when justified

A CMOS/firmware-settings reset can clear an invalid memory, PCIe or boot configuration. Before doing it:

- record accessible custom settings;
- consider full-disk encryption recovery implications;
- use the exact vendor procedure with external power disconnected;
- never improvise by shorting unidentified pins;
- expect date/time, fan, storage mode, Secure Boot and boot settings to need review.

Do not update firmware on an unstable system merely as an experiment. A failed update can create a second fault. Use the [BIOS/UEFI guide](../firmware/bios-uefi-configuration.md) and the vendor's recovery route if evidence points to corrupted or incompatible firmware.

### 6. Inspect the CPU/socket late in the process

Remove the cooler and CPU only after power, memory and graphics checks fail. Socket contacts and mounting hardware are easy to damage.

Check for:

- bent or contaminated contacts;
- CPU orientation;
- thermal material outside the intended contact area;
- wrong or uneven cooler hardware;
- excessive board flex;
- missing socket-area components or other physical damage.

Reinstall with the documented mounting pattern and fresh thermal material where the cooler vendor requires it. If contact damage is present, stop unless authorised and equipped for that repair.

### 7. Bench test only with a controlled setup

Testing the minimum hardware outside the case can expose a standoff or chassis short. Use a stable non-conductive surface and a documented method to start the board. Keep conductive tools away after power is applied.

Do not bench-test proprietary systems whose chassis, airflow, grounding or interlocks are required for safe operation.

## Interpreting outcomes

| Observation | What it supports | What remains possible |
|---|---|---|
| POST returns after one peripheral is removed | Peripheral, cable, port or resource interaction | An intermittent seating or power fault |
| One DIMM fails in a slot where another works | DIMM fault or incompatible settings | Marginal controller/firmware behaviour |
| No DIMM works in one channel | Slot/channel path | CPU socket contact, mount pressure, board or CPU |
| Integrated graphics works after GPU removal | Discrete graphics path | GPU, its power, slot or firmware setting |
| Board works outside the case | Chassis/standoff/front-panel interaction | A connection disturbed during removal |
| Compatible known-good PSU restores POST | Original PSU or its cabling | Load-specific or connector fault not yet separated |

These are diagnostic directions, not automatic part-replacement decisions.

## Escalate when

- socket contacts, board traces or connectors are damaged;
- a firmware recovery or replacement procedure requires equipment or authority not available;
- proprietary components or warranty seals make further disassembly inappropriate;
- the fault is intermittent and cannot be reproduced without unsafe stress or repeated hard power cycles;
- a compatible known-good substitution cannot be made safely;
- component replacement, downtime or data/encryption impact exceeds the work authorisation.

Provide the minimum configuration, exact diagnostic indications, each controlled change, known-good parts used and results. “Still no POST” without the test state is not enough for the next person to continue efficiently.

## Validate the repair

- Confirm all intended components are reinstalled and detected at expected settings.
- Complete several cold starts and warm restarts without a training loop or diagnostic warning.
- Recheck CPU temperature and fan/pump reporting in firmware.
- Restore only documented firmware settings and verify the boot device remains correct.
- Boot the OS, check device and hardware-error logs, then run a controlled workload appropriate to the suspected component.
- Record the evidence that identifies the cause. If the cause remains unproven, record the issue as unresolved or monitored rather than claiming a root cause.
