# CPU and Thermal Troubleshooting

A temperature number is useful only with its sensor, workload, ambient conditions and the processor's documented limits. A short boost to a high temperature may be normal for one platform; sustained throttling at light load is not. Diagnose the cooling path and workload before assuming the CPU has failed.

## Stop conditions

Shut down and remove external power if there is smoke, a burning smell, coolant leakage, a stopped pump with rising temperature, or repeated thermal shutdown. Do not keep rebooting to collect another reading.

Move or tilt liquid-cooled equipment only as its manufacturer permits. Keep liquid away from energised parts; a leak requires de-energisation and an appropriate inspection, not a quick wipe while powered.

## Define the symptom

Record which condition is actually present:

- firmware temperature rises quickly after power-on;
- fans run at maximum at idle;
- performance drops during a sustained task;
- OS or firmware logs report thermal throttling;
- the system shuts down or restarts under load;
- a monitoring alert reports a threshold crossing;
- only one utility shows an implausible value.

Also record ambient temperature, CPU model, cooler type, fan/pump readings, workload and recent changes. A cooler remount, BIOS update, new fan curve, dust cleaning or case move is often more relevant than the peak number alone.

## Check the reading before acting on it

1. Compare firmware hardware monitoring with one reputable OS utility that understands the platform.
2. Identify whether the value is package, core, socket, control temperature or another vendor-defined sensor.
3. Check the CPU vendor's specification for the exact model. Do not apply one generic “safe temperature” to all processors.
4. Watch the trend from idle into a known workload. Sudden sensor steps can be normal; continued rise with no cooling response is not.
5. Look for throttle flags, clock reduction and package power as well as temperature.

There is no dependable built-in Windows command that exposes CPU temperature across all hardware. Use the system/CPU vendor's supported monitoring utility or a well-established hardware monitor and verify sensor names.

On Linux, `lm-sensors` can expose supported sensors:

```bash
sensors
lscpu
journalctl -k -b | grep -Ei 'thermal|throttl|mce|machine check'
```

`sensors` requires the `lm-sensors` package and a supported kernel driver. Missing or oddly scaled data may be a support issue rather than a cooling fault. Kernel log access may require elevation.

## Separate workload from cooling

Check CPU utilisation before opening the system. A background update, malware scan, runaway process or virtual-machine workload can correctly make the cooling system respond.

- If utilisation is high, identify the process and decide whether the workload is expected.
- If utilisation is low but package power and temperature remain high, verify the measurement and CPU power settings.
- If temperature is high and clock speed falls under a steady workload, thermal or power-limit throttling is likely; identify the reported limit reason where tooling provides it.
- If the machine instantly loses power, include [power fault methodology](../diagnostics/power-fault-methodology.md). A restart under load is not proof of overheating.

Do not terminate an unknown process on a managed system just to lower the graph. Establish ownership and impact first.

## Inspect the cooling path

Power down, disconnect external power and use the vendor discharge procedure before internal work.

### Air cooling

- Confirm the heatsink does not rock and every fastener is engaged in the documented sequence.
- Check for a forgotten cold-plate film, missing/incorrect mounting spacer or uneven pressure.
- Inspect fins, filters and intakes for dust blockage.
- Spin fans only gently while de-energised; check for obstruction, damaged blades or bearing noise.
- Trace the CPU fan to the correct header and confirm PWM/DC mode matches the fan.
- Check that intake and exhaust fans form a coherent path rather than recirculating hot air.

### Liquid cooling

- Confirm pump power, tachometer and control connections match the cooler manual.
- Listen for abnormal grinding or persistent cavitation, while recognising that a brief bubble sound after movement can occur.
- Check tube routing, kinks, radiator blockage and fan direction.
- Inspect every fitting and nearby component for moisture or residue while de-energised.
- Use the vendor's required pump speed and radiator orientation. Do not assume every pump belongs on a generic motherboard “fan” curve.

A reported zero RPM can mean a failed pump/fan, an unmonitored fixed-speed device, the wrong header or a sensor below its detection range. Trace the physical connection before deciding.

## Remount only when evidence warrants it

A cooler remount is justified after disturbed mounting, uneven contact, wrong hardware or a persistent thermal pattern that other checks do not explain.

1. Confirm replacement thermal material and the exact mounting instructions are available.
2. Remove power and let the assembly cool.
3. Release fasteners gradually in the vendor's pattern; avoid pulling a socketed CPU from its socket with a stuck heatsink.
4. Clean only the intended mating surfaces using material and solvent approved by the cooler/CPU vendor.
5. Inspect the socket area and mounting hardware.
6. Apply the specified amount/pattern of thermal interface material and tighten evenly to the documented limit.
7. Reconnect the fan/pump before applying power.

More paste is not automatically better, and thermal interface material cannot compensate for a loose or incompatible mount.

## Controlled load test

Test only after idle temperature and cooling feedback are stable. Back up important data and get authority before stressing a managed host.

- Start with a short, representative workload rather than the most aggressive stress test available.
- Record ambient, idle baseline, workload name/settings, package power, clock, temperature, fan/pump speed and throttle flags.
- Increase duration gradually while watching for a stable plateau.
- Stop on vendor-limit breach, thermal shutdown, rapid uncontrolled rise, new hardware errors, coolant concern or abnormal electrical smell/noise.
- Allow a cool-down period and confirm the system returns towards baseline.

Synthetic CPU and combined CPU/GPU loads exercise different power and airflow conditions. A pass in one does not prove the other.

## What the pattern suggests

| Observation | Likely area to test next |
|---|---|
| Rapid rise in firmware with near-zero fan/pump feedback | Mount, fan/pump power or failed cooler |
| Normal idle, throttle only in sustained expected load | Cooler capacity, fan curve, airflow, ambient or CPU power settings |
| Temperature improves greatly with side panel removed | Case intake/exhaust restriction or recirculation |
| High temperature follows a cooler remount | Mounting hardware, contact, film or thermal material |
| Reset occurs under combined CPU/GPU load but not CPU-only | PSU capacity/path or case-wide heat, not CPU alone |
| One utility differs substantially from firmware/vendor tool | Sensor mapping or software interpretation |
| Clock is low while temperature is well below thermal limit | Power/current limit, OS policy or workload behaviour |

Use the pattern to choose a test, not to declare a component failed.

## Escalation and recovery validation

Escalate for liquid leakage, socket/board damage, an inaccessible proprietary cooling assembly, repeated thermal shutdown, cooler replacement outside authority, or a system whose safe workload cannot be reproduced within an approved window.

After corrective work:

- firmware shows the cooler's required fan/pump feedback;
- the OS reports expected CPU capacity and no new machine-check/thermal events;
- idle and controlled-load temperature trends are plausible for the exact platform and environment;
- the CPU sustains expected clocks without the original thermal throttle or shutdown;
- fan response increases and decreases with load without oscillation or obstruction;
- cold start, restart and the original workload all complete;
- the changed part/setting, before-and-after evidence and remaining limitation are recorded.

A lower temperature after opening the case is a diagnostic result, not a finished repair. Restore panels, filters and the intended fan control before final validation.
