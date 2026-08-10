# Physical Assembly

This checklist covers a conventional field-serviceable desktop. Small-form-factor systems, workstations, servers and vendor-integrated liquid cooling can require a different order and specialised service instructions.

## Safety and preparation

- [ ] Back up any data that must survive on reused drives.
- [ ] Shut down equipment, switch off and disconnect external power, then follow the case or system vendor's discharge procedure.
- [ ] Work on a stable, uncluttered, non-conductive surface with good lighting.
- [ ] Control electrostatic discharge with an appropriate grounded method and handle boards by their edges.
- [ ] Remove jewellery or loose items that could bridge contacts or catch in fans.
- [ ] Compare received parts with the build plan and inspect them for bent contacts, cracked boards, damaged sockets, leaking components or contaminated connectors.
- [ ] Read the motherboard CPU, memory, M.2 and front-panel sections before fitting parts.

Stop if there is physical damage, a foreign object in a socket, unclear liquid-cooler condition, or any sign of burning. Do not apply power merely to see whether damaged hardware still works.

## Prepare the board

Fitting the CPU, memory and primary M.2 device with the board outside the case usually gives better visibility. Support the board on its box or another vendor-approved non-conductive surface—not on the outside of an anti-static bag, whose surface may be conductive.

- [ ] Open the socket mechanism without touching socket contacts.
- [ ] Align the CPU using the vendor's triangle/notches and lower it without sliding or force.
- [ ] Close the retention mechanism as documented. Retention force can be normal; misalignment is not.
- [ ] Fit the cooler backplate and mounting hardware for the exact socket.
- [ ] Remove any protective film from the cooler cold plate.
- [ ] Use the pre-applied thermal interface material, or apply the cooler/vendor-specified amount—not both.
- [ ] Tighten the cooler gradually in the documented pattern so pressure remains even.
- [ ] Connect the cooler fan to the designated CPU fan header. Connect a pump only to the header and control mode specified by its manufacturer.
- [ ] Populate the recommended memory slots for the module count, align each notch and confirm both required latches are fully engaged.
- [ ] Install M.2 devices using the correct standoff position and fastener; remove any heatsink film and refit the thermal pad/heatsink as documented.

Never power a processor without its cooling assembly installed. Do not use a powered screwdriver around a board unless its torque is controlled for that task.

## Prepare the case

- [ ] Remove both side panels and the front/top panels needed for access without forcing hidden clips.
- [ ] Confirm motherboard standoffs exist only at mounting-hole positions for the selected form factor.
- [ ] Fit a separate I/O shield before the motherboard if the board does not have an integrated one; check that no spring tab enters a port.
- [ ] Install the PSU in the intended airflow orientation with its switch off and input cable disconnected.
- [ ] Fit case fans/radiators in the planned direction and confirm screws cannot contact a radiator channel.
- [ ] Route the CPU power cable before board installation if case access will become restricted.

An extra standoff under the board can short exposed contacts. This is a pre-power inspection item, not a detail to infer after a failure.

## Install and connect

- [ ] Lower the board onto the standoffs without scraping its underside or trapping cables.
- [ ] Start all motherboard screws by hand, then tighten until secure without distorting the board.
- [ ] Connect the 24-pin motherboard and required 4/8-pin CPU power connectors; a PCIe/GPU plug is not a substitute for an EPS/CPU plug.
- [ ] Connect front-panel power/reset/LED leads using the board pinout, not wire colour assumptions.
- [ ] Connect front USB and audio headers with correct keying and no bent pins.
- [ ] Mount 2.5/3.5-inch drives securely, then attach data and power without side-loading the connectors.
- [ ] Install the GPU or other cards in the intended slots, confirm the retention latch, secure the brackets and attach every required power connector.
- [ ] Keep cables clear of fans, heatsinks and panel edges; preserve the planned airflow path.
- [ ] Check that no unused screw or cut cable tie remains loose in the enclosure.

Do not force a keyed connector. If it does not seat with normal pressure, re-check connector family and orientation. For high-current GPU cabling, follow the GPU and PSU instructions on separate cable runs, adapter use, insertion depth and bend radius.

## Pre-power inspection

- [ ] CPU cooler is mechanically secure; its fan/pump connections match the manual.
- [ ] Memory and expansion cards are level and fully latched.
- [ ] Mainboard, CPU and GPU power plugs are fully inserted with no visible gap at the latch.
- [ ] The voltage selector, if a legacy PSU has one, matches the local supply. Do not change an automatic-ranging PSU.
- [ ] No standoff, screw, cable or I/O-shield tab can short or obstruct a component.
- [ ] The monitor is connected to the intended graphics device and set to the correct input.
- [ ] A keyboard is connected; non-essential USB devices and data drives may remain disconnected for first POST.
- [ ] Side panels can remain off for observation only if doing so is safe and does not defeat a required airflow duct or chassis interlock.

## First power and firmware detection

1. Connect the protected AC supply, switch on the PSU if applicable, and press the case power button once.
2. Observe fan movement, indicator LEDs, beep/debug codes and the display. Do not repeatedly cycle power while firmware may be training memory; the board manual should indicate expected behaviour.
3. Enter firmware setup and confirm CPU, installed memory and expected storage devices are detected.
4. Check the CPU temperature trend and fan/pump readings. Power down if temperature rises rapidly, a required pump/fan reads zero, there is unusual noise, or any smell/smoke appears.
5. If the system does not reach POST, disconnect power and use the [no-POST workflow](../diagnostics/no-post-troubleshooting.md). Avoid changing several connections at once.

## Close and validate

- [ ] Apply only the reviewed settings in the [BIOS/UEFI configuration checklist](../firmware/bios-uefi-configuration.md).
- [ ] Confirm the system completes a cold start and a firmware-controlled restart.
- [ ] Refit panels and filters, then verify that no cable contacts a fan and all external ports remain accessible.
- [ ] Confirm every installed component is detected in firmware and, after OS installation, by the operating system.
- [ ] Observe temperature, fan behaviour and system stability at idle, then under a controlled representative load.
- [ ] Record part models, firmware version, memory/storage detection and validation results; keep serial numbers out of public records.

The concise [new system build checklist](../../checklists/new-system-build.md) can be used as the final build record gate.
