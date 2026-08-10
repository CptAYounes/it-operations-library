# What to monitor on a host

Start with the service the host supports. A machine can have comfortable CPU and memory while its application returns errors; it can also run near a resource limit by design without user impact.

## Signal groups

| Area | Useful signals | Question answered |
|---|---|---|
| Reachability | agent heartbeat, expected management path, ICMP where useful | Is the host observable from the right place? |
| Operating-system state | uptime, boot events, clock offset, failed units/services | Did state change or a required component stop? |
| CPU | utilisation by mode, run queue/load, throttling, steal time | Is runnable work waiting or constrained? |
| Memory | available memory, paging/swap rate, OOM/allocation failures | Is the host under memory pressure? |
| Storage capacity | free bytes, free percentage, inodes/file count, growth rate | Can the system keep writing, and when will it run out? |
| Storage performance | latency, queue depth, throughput, I/O errors | Is storage delaying or failing work? |
| Network | link state, errors/discards, throughput, TCP failures | Is the interface/path carrying work cleanly? |
| Hardware/platform | temperature, fan/power state, ECC and disk/controller alarms | Is the underlying platform reporting degradation? |
| Logs | service failure, authentication/security, kernel and hardware patterns | What state transitions or failures need context? |
| Workload/service | request success, latency, queue depth, listener/health check | Can the host perform its intended function? |

Metric names and availability differ between physical hosts, virtual machines, containers and operating systems. For example, CPU steal is relevant to a virtual guest, while fan state may only exist through hardware management.

## Choose signals deliberately

For each item, define:

- source and collection interval;
- unit and aggregation (average, maximum, rate or count);
- normal range by workload period;
- warning and critical meaning;
- missing-data behaviour;
- owner and response link;
- retention needed for comparison or investigation.

Prefer a small set that detects user impact, imminent exhaustion and component failure over every available counter. Duplicate alerts from host, service and platform should be correlated or routed so one fault does not create several competing incidents.

## Common interpretation traps

- High memory **used** may be healthy filesystem cache; available memory and paging show pressure better.
- High load on Linux can include tasks blocked in uninterruptible I/O, not only CPU demand.
- Disk free percentage alone misses a small volume with little time remaining or inode exhaustion.
- One packet error counter may be cumulative since boot; monitor its rate and direction.
- Process running is weaker than a safe application transaction.
- No data can mean an agent, network or platform failure; it should not silently look healthy.

## Validation

Test collection failure and at least one safe threshold path in a lab or maintenance window. Confirm the alert contains host/service identity, metric, value, duration and a runbook link. After configuration changes, compare the monitor with local evidence and verify both firing and recovery behaviour.
