# Linux performance investigation

High CPU, low “free” memory and a large load average are observations, not root causes. Establish the affected service and time window, then correlate CPU, runnable tasks, memory pressure, swapping and storage latency.

The commands below observe state but can themselves add load if run at short intervals or over large process sets. Capture a bounded sample and avoid leaving monitors running indefinitely.

## Define the problem before collecting metrics

Record:

- user-visible symptom and affected service;
- start time, duration and recurrence;
- expected baseline or known-good comparison;
- workload, scheduled jobs, deployments and backups at that time;
- VM/container limits and host contention if applicable;
- whether latency, throughput, errors or saturation changed.

“Host is slow” is too broad. “HTTPS p95 latency rose while requests remained constant” gives the measurements a question to answer.

## A two-minute first pass

```bash
uptime
free -h
vmstat 1 5
ps -eo pid,ppid,user,stat,comm,%cpu,%mem,rss --sort=-%cpu
ps -eo pid,ppid,user,stat,comm,%cpu,%mem,rss --sort=-rss
systemctl --failed --no-pager
journalctl -b -p warning --since '15 minutes ago' --no-pager
```

Capture CPU count for load and `%CPU` context:

```bash
nproc
lscpu
```

Do not copy full `lscpu`, process arguments or environment into public evidence without reviewing identifiers and secrets.

## Read `vmstat` as a relationship

For interval lines after the first summary line:

- `r` — runnable tasks; sustained values above available CPUs suggest CPU queueing;
- `b` — tasks blocked in uninterruptible sleep, often I/O-related;
- `si`/`so` — swap in/out activity during the interval;
- `bi`/`bo` — blocks received/sent; units depend on implementation;
- `us`/`sy` — user/kernel CPU time;
- `id` — idle;
- `wa` — CPU time waiting for I/O, useful but not a complete storage-latency measure;
- `st` — time taken by the hypervisor from a virtual CPU.

The first `vmstat` line commonly represents averages since boot, so do not mix it with the timed samples. A single one-second spike may be normal; sustained queueing correlated with user impact is stronger evidence.

## CPU and scheduler

```bash
ps -eo pid,ppid,user,stat,etimes,comm,%cpu,%mem --sort=-%cpu
pidstat -u -p ALL 1 5
systemd-cgtop
```

`pidstat` is supplied by `sysstat` and may not be installed. `systemd-cgtop` helps attribute resource use to services/containers but may need additional accounting enabled for complete data.

Points that prevent common misreadings:

- A process can report over 100% CPU when it uses more than one logical CPU, depending on the tool.
- Load average includes runnable and uninterruptible tasks; it is not CPU percentage.
- High system CPU (`sy`) can come from network, filesystem, driver or syscall load rather than application calculation.
- A process at 100% of one CPU may be the bottleneck on a many-core host even when total CPU looks mostly idle.
- CPU frequency, thermal throttling and virtual CPU steal can reduce delivered capacity.

If permitted and available, correlate temperature/frequency and kernel messages rather than immediately changing governors or limits.

## Memory and swap

```bash
free -h
vmstat 1 5
ps -eo pid,user,comm,rss,vsz,%mem --sort=-rss
journalctl -k -b | grep -i -E 'out of memory|oom-kill|killed process'
```

Linux uses otherwise idle memory for filesystem cache. In `free`, **available** is usually more useful than **free** for estimating headroom. Swap usage alone is not an incident; sustained `si`/`so`, reclaim pressure and latency are more meaningful.

Check Pressure Stall Information when the kernel exposes it:

```bash
grep . /proc/pressure/cpu /proc/pressure/memory /proc/pressure/io
```

PSI reports time tasks were stalled for resources. `some` means at least one task was stalled; `full` means all non-idle tasks in that scope were stalled. Use the `avg10`/`avg60`/`avg300` windows and totals with workload context rather than applying a universal threshold.

Memory diagnosis should distinguish:

- growing process RSS/leak;
- page cache from active file I/O;
- tmpfs/shared memory;
- container/cgroup memory limit;
- kernel slab usage;
- NUMA locality on larger systems;
- an OOM kill, which may target a victim other than the original pressure source.

Do not clear caches as a routine fix. It discards useful cache, changes the workload and can create a misleading temporary improvement without removing the cause.

## Storage I/O and latency

If `sysstat` is installed:

```bash
iostat -xz 1 5
pidstat -d -p ALL 1 5
```

Use throughput, request size, queueing and latency together. `%util` interpretation varies with device parallelism, RAID, virtual disks and modern NVMe; 100% is not a universal proof of maximum physical capability. Correlate device names back to filesystems and applications with `lsblk`/`findmnt`.

Also inspect:

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
df -hT
df -ih
journalctl -k --since '30 minutes ago' -p warning --no-pager
```

A full filesystem can make services slow or fail, but deleting logs without finding the writer makes recurrence likely. Device errors, resets or an unexpectedly read-only mount require the [disk and filesystem investigation](../storage/disk-filesystem-investigation.md).

## Network and external waits

A process can be mostly idle while waiting on DNS, a database, storage or an API. Check application latency/error logs and the relevant dependency path. Useful host observations include:

```bash
ss -s
ip -s link
ss -tan
```

Large socket listings can be expensive/noisy. Narrow by port or state when the service is known. Retransmissions and queue growth need protocol and workload context; follow [network diagnostics](../networking/network-diagnostics.md).

## Historical evidence

Live tools cannot prove what happened before the investigation began. If sysstat collection or monitoring was already enabled, query the retained interval with `sar`; do not assume it was enabled or complete. Application metrics, cgroup history, hypervisor metrics and monitoring are often better sources for a past spike.

Logs provide event context but not a full performance profile:

```bash
journalctl --since '2026-08-10 19:00:00' --until '2026-08-10 19:15:00' \
  -p warning -o short-iso-precise --no-pager
```

Use the real incident window and record time zone/clock skew.

## Safe action order

1. Preserve a bounded baseline and the impact measurement.
2. Identify the saturated or stalled resource, not merely the busiest process.
3. Map that resource to a service, workload and recent change.
4. Check resource limits and dependencies before changing the host globally.
5. Prefer workload control, configuration correction or planned capacity work over killing processes.
6. If a process must be stopped, confirm owner, data-integrity behaviour, redundancy and restart path. Use the service manager where applicable.
7. Change one variable and repeat the same measurements.

`kill -9` gives a process no opportunity to flush data or clean up. It is an emergency last resort under an approved recovery plan, not a normal response to high CPU.

## Validation and escalation

Recovery requires the original user/service measurement to return to an acceptable range, resource pressure to fall without new errors, queues to drain, required services to remain functional and monitoring to stay stable for a representative period.

Escalate for sustained saturation with customer/service impact, OOM kills, I/O errors, thermal/hardware warnings, unknown high-privilege processes, evidence of denial-of-service, database/storage recovery risk, or a change requiring capacity/architecture ownership. Hand over timestamps, workload, baseline, bounded samples, resource hypothesis, recent changes and what improved or did not—without process arguments or logs containing secrets.
