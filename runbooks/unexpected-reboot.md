# Unexpected reboot

An uptime reset can result from planned maintenance, a clean restart, kernel/stop failure, watchdog, power loss, hypervisor action or hardware protection. Establish the reboot time and shutdown evidence before assigning a cause.

## Immediate response

1. Confirm current service state, redundancy and user impact.
2. Record current uptime and monitoring gap/recovery time.
3. Check the change calendar, update tooling, automation and platform owner for an intended restart.
4. Preserve logs and console/platform events around the estimated time. Do not trigger another reboot to see whether it repeats.
5. If there is a safety, burning smell, unstable power, overheating or repeated reset concern, follow physical safety procedure and escalate.

## Evidence by platform

Windows:

```powershell
(Get-CimInstance Win32_OperatingSystem).LastBootUpTime
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddHours(-4)} |
    Where-Object Id -in 41, 1074, 6005, 6006, 6008 |
    Select-Object TimeCreated, Id, ProviderName, Message
```

Event 1074 can record an initiated restart; 6006 a clean event-log stop; 6008 an unexpected previous shutdown; Kernel-Power 41 says Windows did not complete a clean shutdown, not why power was lost.

Linux:

```bash
uptime -s
last -x reboot shutdown | head
journalctl --list-boots
journalctl -b -1 -e
journalctl -k -b -1
```

Previous-boot journal availability depends on persistent journal configuration. Look for orderly shutdown, panic/OOM, watchdog, thermal, machine-check and storage I/O evidence. Also inspect the hypervisor/cloud/platform event log where applicable; a guest cannot always see the initiating cause.

## Correlate, do not guess

- Match OS time with monitoring, power, hardware-management and platform records.
- Check update/reboot coordinators and scheduled jobs.
- Review temperature, voltage, ECC/machine-check and storage alarms.
- Determine whether the clock changed after boot before relying on sequence.
- Treat missing logs as an evidence gap, not proof of sudden power loss.

## Safe action

If the system is healthy, preserve evidence and monitor while the cause is investigated. Do not update firmware, disable watchdogs, replace hardware or stress-test an unstable service without a planned diagnostic window. A known failed change should use its backout/recovery plan.

## Escalate and close

Escalate immediately for repeated reboots, hardware/power alarms, data or filesystem integrity concern, cluster failover, suspected compromise, kernel/bugcheck dump analysis or platform actions outside ownership.

Validate application transactions, storage/filesystems, dependent services, redundancy and monitoring—not just host availability. Record reboot window, clean/unclean evidence, correlated events, cause confidence (confirmed/likely/unknown), service validation and follow-up action.
