# Hardware Fault Isolation

Fault isolation is the method behind the component-specific guides. It turns a broad report such as “the PC keeps crashing” into a smaller, testable boundary without replacing parts at random.

The core loop is simple:

```text
observe -> establish a baseline -> choose one hypothesis
       -> change one controlled variable -> reproduce -> compare
       -> narrow or reject the hypothesis -> validate the final state
```

The discipline matters more than the number of tools used.

## 1. Turn the report into an observable symptom

Capture both what was reported and what can be reproduced.

| Question | Useful evidence |
|---|---|
| What exactly happens? | Freeze, reset, power loss, POST code, corrupted output, missing device |
| At which stage? | Before POST, firmware, OS boot, idle, a named workload, shutdown |
| How often? | Every start, after a duration, intermittent, one occurrence |
| What changed? | Transport, cleaning, update, new component, power event, workload |
| What is the scope? | One port/device, one OS, all workloads, nearby systems too |
| What returns it to service? | Wait, cold boot, cable reseat, lower load, no known action |
| What must be protected? | Data, encryption keys, warranty, service availability, known-good parts |

Keep observations separate from interpretations:

> Observed: system loses power within two minutes of a combined CPU/GPU load; no graceful shutdown event is recorded.
>
> Hypothesis: load-related PSU, connector, GPU or thermal protection fault.

“PSU failure” is not an observation.

## 2. Set the safety and authority boundary

Before testing, decide what cannot be risked:

- preserve important data and current configuration;
- record storage/RAID topology before moving devices;
- secure encryption recovery before firmware/TPM changes;
- disconnect power before ordinary internal work;
- do not open a PSU or defeat an interlock;
- do not stress unstable hardware carrying the only copy of data;
- identify downtime, warranty and replacement authority.

When evidence points to burning, liquid, mains power, damaged lithium batteries, data recovery or board-level repair, isolation has reached an escalation boundary—not an invitation to improvise.

## 3. Establish a baseline

A baseline is the simplest safe state in which the symptom and evidence are understood. Record:

- exact installed component models and firmware/driver versions relevant to the fault;
- firmware detection and settings;
- OS device state and hardware events;
- temperatures, fan/pump feedback and power state;
- physical location/port/slot mapping;
- a precise reproduction step and expected result.

Capture logs before resets, reseats and firmware defaults erase context. Avoid publishing serial numbers, MAC addresses, private hostnames or raw logs containing personal data.

If the problem cannot be reproduced, improve observation rather than making more changes: check event timestamps, monitoring history, environmental conditions and the user's sequence. An intermittent fault needs a trigger model.

## 4. Locate the failing boundary

Divide the system at an observable interface:

```text
AC source -> PSU -> board power -> POST -> boot device -> OS -> application
                         |          |          |
                    CPU/RAM     graphics    storage path
                         |
                  cooling/firmware
```

Examples:

- No standby indication keeps the first boundary around external/standby power.
- A DRAM diagnostic LED moves the boundary to memory initialisation, while leaving CPU/socket/firmware possible.
- Firmware consistently detects a drive but the OS does not narrows the fault above the physical link.
- A second monitor displays the firmware screen narrows a “dead PC” report to the original display path.

Start with [power faults](power-fault-methodology.md) for a dead system or [no-POST troubleshooting](no-post-troubleshooting.md) where power exists but firmware does not complete.

## 5. Choose a discriminating test

A good test produces different expected outcomes for competing hypotheses.

| Technique | Example | Strong result | Main limitation |
|---|---|---|---|
| Remove | Disconnect non-essential USB devices | POST returns consistently | Reseating or reduced load may be the real change |
| Relocate | Known-working DIMM moved between slots | Error stays with one slot | CPU/socket/controller also forms the channel path |
| Swap | Modules A and B exchange slots | Error follows A | Both modules must be compatible and state unchanged |
| Substitute | Compatible known-good PSU installed | Load reset disappears | PSU and all substituted cables form one test path |
| Cross-test | Suspect GPU tested in a suitable second system | Fault follows card | Can put the second system at risk; compatibility matters |
| Reduce | Minimum hardware reaches POST | Added device/path causes failure | Lower power draw may mask a PSU fault |
| Revert | Memory profile returned to defaults | Errors stop | Shows settings sensitivity, not necessarily bad memory |
| Observe under load | Temperature and clocks captured | Throttle aligns with limit flag | Stress can be disruptive and synthetic |

Never cross-test a part with visible electrical damage or storage containing unprotected data. Treat a known-good component as valuable test equipment.

## 6. Change one variable and preserve controls

For each step record:

```text
Test ID:
Starting state:
Hypothesis:
Single change:
Expected result if hypothesis is true:
Observed result:
Evidence:
Interpretation:
Next safe step:
```

A “single change” can still have hidden variables. Reseating a GPU changes contact, mechanical pressure and perhaps cabling. Moving a system changes airflow and power source. Name those limitations.

Use a positive and negative control where practical:

- show the fault in the suspect state;
- show it absent in the known-good state;
- restore the suspect state and show it returns.

That A/B/A pattern is much stronger than one successful boot after several parts were reseated.

## 7. Use minimum configurations carefully

A minimum configuration reduces interactions and speeds POST isolation. It should be the **vendor-supported** minimum, not an arbitrary collection of parts.

Label connections before removal, especially storage, fan and front-panel headers. Keep the CPU cooler, required fan feedback and platform interlocks. Reintroduce one component or branch at a time.

If the full system fails but the minimum passes, consider two classes of cause:

1. the added component/path is faulty or incompatible;
2. the full configuration changes total power, heat, lane sharing, memory-controller load or firmware behaviour.

The second class is why “it works with the GPU removed” does not yet prove a failed GPU.

## 8. Handle intermittent faults

Intermittent faults need controlled repetition, not uncontrolled part swapping.

Build a table of occurrence against:

- cold versus warm start;
- time under load;
- CPU-only, GPU-only and combined load;
- temperature and ambient condition;
- cable/port/slot position;
- sleep/wake or power-source transition;
- full versus minimum configuration;
- firmware/driver/settings state.

Increase test stress or duration only within component limits and an authorised window. If reproducing the event risks data or hardware, stop and escalate with the captured pattern.

Environmental clues matter: dust, airflow restriction, vibration, an overloaded shared power path and intermittent external cabling can all follow the machine when the internal part is innocent.

## 9. Select the specialist branch

- [No POST](no-post-troubleshooting.md) — early firmware initialisation
- [RAM troubleshooting](../memory/ram-troubleshooting.md) — capacity, training, memory errors or ECC events
- [Storage diagnostics](../storage/storage-diagnostics.md) — missing devices, I/O errors, health or filesystems
- [CPU and thermal troubleshooting](../thermals/cpu-thermal-troubleshooting.md) — temperature, throttling or thermal shutdown
- [Power fault methodology](power-fault-methodology.md) — no power, hard loss or load-related reset
- [BIOS/UEFI configuration](../firmware/bios-uefi-configuration.md) — boot/security/controller/settings or approved firmware work

Use the branch only when evidence places the fault there; several branches may remain active for a cross-domain symptom.

## 10. Decide what has actually been proven

Use restrained outcome labels:

- **Confirmed root cause:** a controlled test repeatedly ties the fault to one cause and the repair removes it.
- **Fault domain isolated:** evidence narrows it to a path, such as board/CPU memory channel, but not one replaceable part.
- **Symptom resolved, cause unconfirmed:** service is stable after a change such as reseating, but the causal mechanism was not separated.
- **Not reproduced:** the defined test did not trigger the reported fault during the stated observation window.
- **Escalated unresolved:** safe/authorised local tests are exhausted and evidence is handed over.

This language prevents a plausible hypothesis becoming fictional certainty.

## Escalation package

Escalate when the next discriminating test is unsafe, destructive, outside authority, needs unavailable known-good hardware, threatens data/service, or requires vendor/board-level work.

Provide:

- reported and observed symptoms;
- impact and current safe state;
- recent changes;
- exact configuration and minimum state;
- diagnostic codes/log times;
- tests in order, including negative results;
- which variables were controlled and which were not;
- current fault domain and remaining hypotheses;
- requested next action or resource.

## Final validation

A replacement is not the end of the method. Confirm:

1. the original reproduction test now passes;
2. a control test still behaves as expected;
3. firmware and the OS detect all intended hardware;
4. hardware-error logs/counters remain clear or within the platform's accepted baseline;
5. cold start, restart, shutdown and the relevant sleep/wake path work;
6. representative workload, temperature and performance are stable;
7. temporary parts/settings are removed and all cables/panels/airflow are restored;
8. data, encryption, backup and service checks affected by the work pass;
9. the outcome label matches the strength of evidence.

The [hardware diagnostics checklist](../../checklists/hardware-diagnostics.md) is the shorter sign-off companion to this workflow.
