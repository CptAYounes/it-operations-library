# Power Fault Methodology

Power faults deserve a stricter safety boundary than most component diagnostics. The scope stops at external supply checks and replaceable low-voltage system parts. It does **not** include internal PSU, UPS, PDU or mains repair.

## Non-negotiable safety boundaries

- Do not open a PSU or UPS. Internal capacitors can retain hazardous energy after disconnection.
- Do not bypass earth, a fuse, a chassis interlock or a PSU protection circuit.
- Do not probe mains connectors or an energised internal system unless this is part of an approved procedure performed by a competent person with correctly rated equipment.
- Do not improvise a “paperclip test.” It can show that some rails start without load, but cannot prove regulation, protection, transient response or safe operation.
- Never reuse modular PSU cables merely because their connectors fit. PSU-side pinouts vary between models and can destroy components.
- Stop for smoke, arcing, burning/ozone smell, liquid, a hot or discoloured connector, damaged insulation, repeated breaker/RCD operation or an electric shock/tingle report. Isolate power and escalate.

## Classify the event

Write the observed state, not “power issue”:

| Symptom | Useful first boundary |
|---|---|
| No standby light, fan or response | AC path, external switch, standby supply, front-panel control |
| Standby indication but no start | Power button/header, board start logic, protection state |
| Starts then turns off before POST | Short/protection, CPU power, cooling, board/CPU |
| Restarts only under load | PSU capacity/transient path, GPU cabling, thermals, board/driver |
| Loses power at the same time as nearby equipment | Outlet/PDU/UPS/upstream supply |
| Powers off cleanly at a scheduled time | OS/management/policy rather than raw power loss |
| Fails after sleep/wake only | Firmware, device wake, OS power state or PSU standby behaviour |

Record timing, workload, whether the OS logged a controlled shutdown, other affected equipment, recent hardware changes and any UPS/PDU event. An OS “unexpected shutdown” event confirms the previous shutdown was not clean; it does not identify the PSU.

## External checks first

These avoid disturbing a system whose fault may be upstream.

1. Check whether the display or other equipment has power; do not confuse “no video” with “no power.”
2. Inspect the removable power cord, plug and inlet for damage while disconnected.
3. Confirm the PSU rear switch and any approved rack/PDU outlet state.
4. Test the wall outlet or managed outlet only by the site's approved method. A known-good low-risk appliance can establish basic availability, but it does not test earth quality or voltage under load.
5. Review UPS/PDU status and event logs if authorised: overload, on-battery, low battery, transfer, outlet command and upstream loss.
6. Remove unapproved extension leads or adapters from the hypothesis path; do not reconfigure shared power without authority.

A circuit breaker or RCD that trips again is not a reset loop to troubleshoot. Leave it isolated and refer it to the responsible electrical/facilities owner.

## Discharge and inspect the low-voltage path

Shut down if possible, disconnect external power and follow the system vendor's discharge procedure. Confirm standby indication has extinguished before internal work.

- Inspect for a loose screw, conductive debris, liquid, damaged port or incorrect motherboard standoff.
- Reseat the motherboard 24-pin, CPU EPS, GPU and drive power connectors.
- Verify connector families. EPS/CPU and PCIe/GPU plugs can look similar but are not interchangeable.
- Check high-current connectors for complete latch engagement, damaged terminals, discolouration and vendor-required bend clearance.
- Confirm every modular cable is approved for the installed PSU model.
- Inspect the case power-switch lead against the motherboard pinout.
- Disconnect a visibly damaged peripheral or cable; do not energise it for confirmation.

Do not insert, remove or reseat ordinary internal power connectors with input power attached.

## Reduce the load and isolate branches

Use the [no-POST minimum configuration](no-post-troubleshooting.md) when the machine cannot reach firmware. Otherwise, reduce one load/path at a time while retaining the minimum needed to reproduce the fault.

Do not deliberately reproduce a hard power loss until the service owner has approved the downtime, the current backup has passed a readback or test restore, and no required data exists only on the host. First rule out every stop condition in this guide, especially hot or damaged connectors. Use a disposable test image or disconnect non-essential data disks where practical, after recording topology and confirming the boot/storage effect.

Authorise only one bounded workload progression. It may advance from CPU-only to GPU-only and then combined load while every monitored value and connector remains within the pre-agreed limits; advancing stages does not start a new attempt. Stop immediately at any hard loss, connector heat, odour, discolouration or threshold breach. Preserve evidence and move to substitution or escalation—never continue to the next stage or repeat the progression after a stop event.

Possible controlled tests include:

1. Remove non-essential USB and externally powered devices.
2. Disconnect non-boot drives and optional expansion cards after recording topology.
3. If the CPU/platform provides usable integrated graphics, remove the discrete GPU and test the lower-power graphics path.
4. Where the preceding gate is satisfied, use the single bounded workload progression defined above to see which demand first triggers a stop condition.
5. If the progression completes without a stop event, restore the last known-good configuration and validate it without repeating the fault-inducing workload.

A system that starts with the GPU removed may have a GPU fault, GPU cable/connector fault, inadequate PSU, damaged slot or simply lower total demand. Continue isolation before replacing a part.

## Capacity and connection review

Revisit the actual component configuration rather than the original parts list:

- PSU continuous rating and supported input range;
- CPU and GPU vendor power recommendations;
- required number/type of dedicated connectors;
- transient-load guidance and PSU protection behaviour;
- ageing, later-installed drives/cards and simultaneous USB charging loads;
- whether adapters or split leads are explicitly supported;
- UPS output rating and load, including inrush/transfer behaviour where relevant.

A wattage calculation is a planning check, not a health test. A degraded or poorly connected PSU can fail below its label rating, while a protective shutdown can be the PSU responding correctly to a downstream short.

## Known-good substitution

The strongest field test is often a compatible, sufficient-capacity known-good PSU. Before substitution:

- confirm form factor, output capacity and every required connector;
- remove **all** modular cables from the suspect PSU and use only the cables belonging to the test PSU;
- preserve proprietary vendor harnesses only when the PSU/system documentation explicitly supports them;
- verify the test PSU will not overload any connector or adapter;
- connect the minimum system first, then restore loads one at a time;
- do not expose the known-good unit to a board with visible short or burn damage.

If the fault disappears, keep the known-good PSU and its own cables fitted. After the safety and data-protection gates above pass, validate with a representative version of the former workload. Do not reconnect the suspect PSU or cable merely to reproduce a hard loss. The result implicates the original PSU/cabling path but does not distinguish the PSU from a cable unless an approved specialist method does so safely.

## Test equipment and limitations

A simple ATX PSU tester can flag absent or grossly incorrect unloaded/lightly loaded rails; it does not validate ripple, transient response, protections or behaviour at system load. A multimeter provides better point measurements only when the operator has an authorised back-probing procedure, insulated probes and the competence to avoid shorts. Oscilloscope and mains-side work belong with appropriately equipped technicians.

Do not publish measured values without the test point, load state, instrument and expected vendor tolerance. “Voltages looked fine” is not reproducible evidence.

## Related faults

- **Turns on but no POST:** [No-POST troubleshooting](no-post-troubleshooting.md)
- **Shuts down at high temperature:** [CPU and thermal troubleshooting](../thermals/cpu-thermal-troubleshooting.md)
- **Storage resets/timeouts:** [Storage diagnostics](../storage/storage-diagnostics.md), while checking shared power/cabling
- **Memory errors under load:** [RAM troubleshooting](../memory/ram-troubleshooting.md), while retaining power as a competing hypothesis

## Escalate when

- hazardous electrical signs or upstream protection operation is present;
- PSU, UPS, PDU, outlet or building electrical repair is required;
- proprietary pinouts cannot be verified;
- a short or board burn is visible;
- shared-service power, redundant feeds or remote power controls would be changed;
- the fault needs energised measurements outside competence/authority;
- no compatible known-good supply is available;
- replacement or downtime requires another owner.

Escalation evidence should include the exact power state, external path checked, minimum hardware, PSU and cable compatibility, event timing, load that triggers the failure and every substitution result.

## Validate recovery

- Complete several cold starts, warm restarts, shutdowns and—if relevant—sleep/wake cycles.
- Only after the suspect power path has been replaced or corrected, run a representative workload long enough to cover the previous failure window while monitoring temperature and hardware events. Do not reinstall a suspect PSU or cable to recreate the fault.
- Confirm all original components have been restored and are detected.
- Inspect repaired/replaced connectors after the test for heat, smell or discolouration with power removed.
- Check OS and UPS/PDU logs for new unexpected-power events.
- Confirm redundant/managed power state and alarms are normal where applicable.
- Record whether the root cause was confirmed. If the event cannot be reproduced, state the observation period and unresolved hypotheses rather than declaring the PSU fixed it.
