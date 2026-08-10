# RAM Troubleshooting

Memory faults can appear as no-POST, application crashes, corrupted output, spontaneous restarts or machine-check/WHEA events. The same symptoms can also come from CPU, power, storage or driver faults. The aim is to build a repeatable module/slot/settings test matrix rather than replace the first DIMM named by an error.

## Protect the system first

Stop normal use if memory errors coincide with data corruption, filesystem faults or incorrect computational output. Continuing to write data through an unstable system can enlarge the damage.

Before opening the machine:

- record the installed module count, expected total capacity and current speed/timings;
- record whether XMP/EXPO, CPU overclocking or undervolting is active;
- note recent firmware, CPU, cooler or memory changes;
- capture exact POST codes and OS hardware-error events;
- arrange downtime for offline testing and back up important data while the system is stable enough to do so safely.

Power down, disconnect external power and follow the vendor discharge procedure before touching memory. Hot-plugging is limited to specialised platforms and procedures; ordinary DIMMs are not hot-pluggable.

## Confirm the symptom

### Firmware

Compare installed and detected capacity. If firmware sees less memory than expected, the OS cannot correct that. Check the board's population diagram and any channel status or training messages.

Return CPU and memory settings to supported defaults before fault isolation. XMP/EXPO is an overclocking profile and should not remain an uncontrolled variable. If defaults restore stability, the modules are not automatically defective; the profile, controller, board training or combined population may be marginal.

### Windows observations

- Task Manager and System Information can confirm usable capacity, but reserved memory and edition limits need separate interpretation.
- **Windows Memory Diagnostic** (`mdsched.exe`) schedules a restart and is disruptive; it is a useful screen, not proof that memory is healthy.
- In Event Viewer, review **System** events from WHEA-Logger and hardware-related bugcheck evidence. A WHEA record identifies a reported hardware path but does not always name the replaceable component.

### Linux observations

Read-only discovery commands:

```bash
free -h
sudo dmidecode --type memory
journalctl -k -b | grep -Ei 'edac|ecc|mce|machine check|memory error'
```

`dmidecode` reports SMBIOS data supplied by firmware and can contain blank, generic or incorrect fields. Kernel log access may require elevated privileges. No matching log output means no matching messages were recorded; it does not prove there were no memory errors.

On supported ECC platforms, EDAC/RAS tooling may expose corrected and uncorrected events. Use platform management logs as well, because OS visibility varies by controller and firmware.

## Build a module/slot matrix

Label modules by position with temporary non-damaging tags; do not publish serial numbers. Use the vendor's preferred slot for a single module.

1. Reseat one module and make sure the notch and both required latches are fully engaged.
2. Test each module **individually in the same slot**.
3. Keep one module that passes there as the control, then test that module in each required slot/channel.
4. Rebuild the documented population one module at a time.
5. Record whether each state reaches POST and whether the offline test reports errors.

| Test state | POST result | Test result | Temperature/settings | Interpretation |
|---|---|---|---|---|
| Module A, reference slot |  |  |  |  |
| Module B, reference slot |  |  |  |  |
| Control module, second slot |  |  |  |  |
| Full supported population |  |  |  |  |

Keep every other variable—firmware settings, GPU, PSU and test image—the same. A result gathered after several simultaneous changes is not a clean comparison.

## Run an offline memory test

Use a current bootable memory-test tool supported by the platform, such as the vendor's diagnostics, MemTest86 or Memtest86+. These tools are distinct projects with different platform support; follow the documentation for the chosen image.

- Verify the download using the publisher's checksum/signature where provided.
- Boot it in the intended firmware mode.
- Confirm the tool reports the expected total capacity and test CPU(s).
- Run all standard patterns for at least one complete pass as an initial screen; intermittent faults may need multiple passes or a longer authorised test.
- Photograph or record the test version, module/slot state, settings, pass count and exact failing addresses/tests.

Any repeatable error at supported default settings is significant. Conversely, one clean pass reduces suspicion but does not prove stability under every temperature and workload.

Do not run a destructive stress workload on a system that is carrying live services or unprotected data. Offline testing consumes downtime and can raise temperature; monitor cooling and stop on thermal or power instability.

## Interpret the pattern

| Pattern | Stronger hypothesis | Checks before replacement |
|---|---|---|
| One module fails repeatedly in slots where another passes | Module fault | Clean contacts visually; retest at defaults; confirm compatibility |
| Several modules fail only in one slot/channel | Board/channel path | CPU socket contacts, cooler pressure, board damage, population rules |
| Modules pass alone but fail together | Training, timings, controller load or mixed kit | Supported speed at that population, firmware notes, matched kit |
| Errors appear only with XMP/EXPO | Profile instability | Standard supported settings, CPU controller limit, relevant firmware fixes |
| Corrected ECC count rises on one location | Developing DIMM or channel-path fault | Management logs, vendor thresholds, module/slot swap under procedure |
| Errors move with the module after an A/B swap | Module implicated | Repeat to rule out seating and environmental changes |
| Errors stay with the slot after an A/B swap | Slot/channel path implicated | Board, socket, CPU memory controller and mount |
| Random errors coincide with resets or voltage/temperature changes | Power or thermal stability | [Power](../diagnostics/power-fault-methodology.md) and [thermal](../thermals/cpu-thermal-troubleshooting.md) checks |

A swap is most useful when the error either follows the module or stays with the slot. On ECC servers, follow the vendor's event-decoding and service procedure; physical labels, logical channels and firmware event locations may not map intuitively.

## Corrective actions and boundaries

Safe, evidence-led actions include:

- cleaning dust from the slot with the vendor-approved method while de-energised;
- reinstalling modules in the supported order;
- using standard supported frequency/timings;
- installing a relevant approved firmware update on an otherwise stable system;
- replacing a proven faulty module with a compatible type and population.

Do not mix registered and unbuffered memory, ECC and non-ECC types, or different DDR generations. Avoid abrasives, liquids and household vacuums around contacts. Do not disable ECC reporting to silence alerts.

Escalate when socket damage, a board/channel fault, repeated uncorrected ECC events, data corruption, warranty restrictions, inaccessible vendor logs or required production downtime exceeds your authority. Preserve event details and the matrix for the next support tier.

## Validate after the change

- Firmware and the OS report the full expected capacity and intended supported speed.
- The final population completes the agreed offline test with no errors.
- Several cold starts and restarts complete without extended or failed training.
- Hardware-error counters/logs show no new events during an authorised representative workload.
- Previously failing applications or workloads complete correctly.
- The removed component, slot and settings are recorded without exposing unique identifiers.

If errors stop but no controlled test identifies why, report the result as “not reproduced after reseat/settings reset” rather than a confirmed root cause. For a machine that cannot POST at all, return to the [no-POST workflow](../diagnostics/no-post-troubleshooting.md).
