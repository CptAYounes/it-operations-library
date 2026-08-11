# Host unreachable

Use when a known host cannot be reached from one or more sources. A failed ping is the symptom; it is not enough to declare the host down.

## Immediate checks

1. Confirm the target name/address, source system, time, expected service and exact error.
2. Check planned work, monitoring state and whether one user, one network or all observers are affected.
3. Try the required service as well as ICMP. Firewalls may discard ping while the application remains available.
4. Preserve alerts and recent-change information. Do not restart the host as a first diagnostic step.

## Narrow the fault domain

| Question | Windows | Linux | What it separates |
|---|---|---|---|
| Does the name resolve? | `Resolve-DnsName host.example` | `getent ahosts host.example` | Naming from reachability |
| Is a route selected? | `Test-NetConnection host.example -InformationLevel Detailed` | `ip route get 192.0.2.10` | Local routing from a remote fault |
| Is the service port reachable? | `Test-NetConnection host.example -Port 443` | `python3 scripts/python/port_check.py host.example 443` (repository root) | Host path from application/service |
| Where does the path stop? | `tracert -d 192.0.2.10` | `tracepath -n 192.0.2.10` (when installed) | A likely boundary, not proof of the failing device |

Use the real authorised source and target in the restricted operational record so another responder can reproduce the check. Redact or replace them with documentation addresses only when preparing a public example. See the [layered connectivity workflow](../networking/diagnostics/layered-connectivity-troubleshooting.md) for local link, address, gateway and neighbour checks.

Debian supplies `tracepath` in the optional `iputils-tracepath` package. If it is not already approved and installed, use an available site-standard path-tracing tool rather than installing software during incident triage. A silent intermediate hop is not proof that the device failed to forward application traffic.

If management access is unavailable but an approved console or out-of-band path exists, check:

- power and hardware alarm state;
- firmware/POST or operating-system console state;
- current address and interface state;
- boot time and recent critical logs.

Do not bypass access controls or expose a new management path.

## Safe corrective actions

Only act when the evidence identifies a reversible fault and the action is authorised. Examples include correcting a mistyped target, restoring a known disabled local interface, or reverting the documented change that introduced the failure. Record state before and after.

A reboot, switch-port change, route/firewall edit or power cycle can widen impact and erase evidence. Treat it as a controlled change, not a connectivity test.

## Escalate when

- several hosts, a shared gateway or a network segment is affected;
- console evidence indicates hardware, boot, storage or security failure;
- the route or filter is owned by another team;
- there is no safe management path or the next action could lock it out;
- customer impact, redundancy loss, data risk or required downtime exceeds authority;
- the host repeatedly fails after an apparently successful recovery.

## Validate and record

Test name resolution, required ports and the actual service from an affected source. Confirm monitoring recovers and remains stable for the agreed period. Record source, target, timestamps, scope, route/port evidence, recent changes, action, outcome and escalation in a [troubleshooting record](../templates/troubleshooting-record.md).
