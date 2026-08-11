# Hardware Diagnostics Checklist

Use this checklist to control and close a hardware investigation. The diagnostic detail lives in [hardware fault isolation](../hardware/diagnostics/fault-isolation.md) and the linked specialist guides.

Each checked line needs an observable result or a note. Mark a branch `N/A` with the reason rather than checking work that was not performed.

```text
Diagnostic reference:
System reference (no public serial):
Date/time:
Reported symptom:
Observed symptom:
Impact:
Investigator:
Current service/data state:
```

## Safety and evidence gate

- [ ] Smoke, burning/ozone smell, liquid, battery swelling, damaged insulation and hazardous electrical symptoms are explicitly present or absent in the record.
- [ ] Equipment is isolated and escalated without further power-on when any hazardous condition is present.
- [ ] Important data and the current storage/RAID/encryption layout are protected before write tests or device movement.
- [ ] Before any load test that could reproduce a hard power loss, backup readback is verified, no required data exists only on the host, downtime is approved, and a disposable test image or isolated non-essential data disks are used where practical.
- [ ] A potential power-loss reproduction is limited to one bounded progression with temperatures and connectors observed; the first hard loss, connector heat, odour, discolouration or threshold breach ends testing immediately, with no later stage or repeat attempt.
- [ ] Warranty, downtime, replacement and production-impact authority are known.
- [ ] Firmware settings, diagnostic indicators and volatile logs are captured before reset or reseating.
- [ ] Unique identifiers, credentials, keys and personal/customer information are excluded from shared evidence.

Do not open a PSU/UPS, bypass protection, hot-plug ordinary internal components, repair a mounted filesystem, clear a TPM, or update firmware as an exploratory first step.

## Establish the fault

- [ ] The reported symptom is recorded separately from what was directly observed.
- [ ] A safe reproduction step, expected result and actual result are recorded.
- [ ] Frequency, timing, workload and cold/warm state are recorded.
- [ ] Recent hardware, firmware, driver, location, cleaning and power changes are recorded.
- [ ] The stage of failure is identified: no power, pre-POST, POST, boot, OS idle or workload.
- [ ] Scope is identified: one component/path, the whole system or multiple systems/upstream service.
- [ ] At least two plausible hypotheses are listed where the evidence does not yet isolate one cause.
- [ ] Exact timestamps, POST/beep/LED codes and OS/management log references are retained.

## Read-only baseline

- [ ] External power, display, input and removable-device paths are checked without opening the chassis.
- [ ] Firmware detection of CPU, memory, storage and required PCIe devices is recorded.
- [ ] CPU temperature trend and required fan/pump feedback are recorded.
- [ ] OS device state and relevant hardware-error events are recorded when the OS is reachable.
- [ ] The physical port/slot/cable mapping of affected hardware is recorded before movement.
- [ ] The current configuration can be restored from the notes or photographs taken.

## Controlled isolation

- [ ] A vendor-supported minimum or known-good baseline is defined.
- [ ] Each test entry states one intended change and the hypothesis it separates.
- [ ] Starting state, expected outcome, observed result and evidence are recorded for every change.
- [ ] Power is disconnected and the vendor discharge procedure followed before each ordinary internal change.
- [ ] Removed devices and cables are labelled so topology can be restored correctly.
- [ ] Known-good test parts are confirmed compatible and are not exposed to visibly damaged hardware.
- [ ] Modular PSU substitution uses only the replacement PSU's own approved cable set.
- [ ] The last known-good state is retested after a failure-producing change where practical.
- [ ] More than one successful cycle is observed before an intermittent fault is considered absent.

```text
Test ID | Starting state | Single change | Expected | Observed | Evidence | Next step
        |                |               |          |          |          |
```

## Specialist branch used

- [ ] No-power or hard power-loss evidence is assessed with [power fault methodology](../hardware/diagnostics/power-fault-methodology.md), or marked N/A.
- [ ] Power-present/no-POST evidence is assessed with the [no-POST workflow](../hardware/diagnostics/no-post-troubleshooting.md), or marked N/A.
- [ ] Memory capacity/training/error evidence is assessed with [RAM troubleshooting](../hardware/memory/ram-troubleshooting.md), or marked N/A.
- [ ] Missing/slow/erroring storage is assessed with [storage diagnostics](../hardware/storage/storage-diagnostics.md), or marked N/A.
- [ ] Temperature/throttling/shutdown evidence is assessed with [CPU and thermal troubleshooting](../hardware/thermals/cpu-thermal-troubleshooting.md), or marked N/A.
- [ ] Firmware, boot-security or controller settings are assessed with the [BIOS/UEFI checklist](../hardware/firmware/bios-uefi-configuration.md), or marked N/A.
- [ ] Vendor-specific codes, service instructions and limitations for the exact system/board revision are recorded.

## Corrective-action gate

- [ ] Evidence identifies the component/path/settings targeted by the proposed action.
- [ ] Backup, encryption recovery, rollback and downtime requirements are satisfied.
- [ ] The action is within authority and follows the exact vendor procedure.
- [ ] Stable power is available before any approved firmware operation.
- [ ] State-changing storage or filesystem work targets a positively identified device and has a tested recovery route.
- [ ] Replacement parts match electrical, firmware, form-factor and population requirements.
- [ ] Removed parts are labelled and handled under the applicable warranty/disposal process without exposing identifiers.

## Escalation gate

- [ ] Work stops when the next test is hazardous, destructive, outside authority or risks the only copy of data.
- [ ] Socket/board damage, liquid, mains/PSU internals, battery damage and unknown proprietary pinouts are escalated to the correct owner.
- [ ] Intermittent faults that require unsafe stress or unavailable known-good parts are escalated with the observation window recorded.
- [ ] Escalation includes current safe state, impact, configuration, evidence, tests in order, remaining hypotheses and requested next action.

## Recovery validation

- [ ] The original reproduction test passes, or the unresolved/non-reproduced status and observation window are recorded.
- [ ] Firmware and the OS consistently detect every intended component.
- [ ] Cold start, restart, controlled shutdown and relevant sleep/wake behaviour pass.
- [ ] A representative workload completes without the original symptom or new hardware error.
- [ ] Temperatures, fan/pump feedback, power state and device-health indicators remain within exact platform requirements.
- [ ] Storage layout, encryption, data access and required backup/readback checks pass after affected work.
- [ ] Temporary test parts/settings are removed and all cables, panels, filters and airflow paths are restored.
- [ ] New logs/counters are compared with the captured baseline and any remaining events are explained.
- [ ] Outcome is classified as confirmed root cause, isolated fault domain, symptom resolved/cause unconfirmed, not reproduced, or escalated unresolved.
- [ ] Root cause is claimed only when a controlled result supports it.

```text
Outcome classification:
Confirmed/remaining fault domain:
Corrective action or escalation:
Validation evidence:
Known limitations/follow-up:
Completed by/date:
```
