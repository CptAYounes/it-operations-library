# High memory

High allocation is not automatically memory pressure. Modern operating systems use spare memory for cache; investigate paging, reclaim, failures and service impact rather than treating a percentage alone as the cause.

## Establish pressure and impact

- Confirm alert duration, total memory, baseline and whether the metric means used, committed or available memory.
- Check application latency, allocation failures, restarts and out-of-memory events.
- Look for paging/swap activity and sustained reclaim, not merely configured swap use.
- Correlate with workload, deployment, process count, virtual-machine/container limits and recent uptime.

Windows:

```powershell
Get-Counter -ListSet *
Get-Counter '\Memory\Available MBytes','\Memory\Pages/sec' -SampleInterval 2 -MaxSamples 5
Get-Process | Sort-Object WorkingSet64 -Descending |
    Select-Object -First 10 Name, Id, WorkingSet64, PrivateMemorySize64, CPU
```

Performance-counter set and path names are localised. Use the first command to discover the installed names and substitute local memory-counter paths when the English paths are absent. The [Windows performance guide](../windows/troubleshooting/performance-investigation.md) covers counter interpretation in more detail.

Linux:

```bash
free -h
vmstat 1 5
ps -eo pid,ppid,user,stat,rss,vsz,pmem,etime,comm --sort=-rss | head -n 15
journalctl -k --since '-2 hours' | grep -i -E 'out of memory|oom|killed process'
```

The final command reads kernel messages and searches for OOM evidence; access depends on local policy. `VIRT`/VSZ is address space, not physical memory in use. Cache and shared pages make simple process totals differ from host totals.

For deeper Linux sampling and interpretation, use the [Linux performance guide](../linux/troubleshooting/performance-investigation.md).

## Work the evidence

1. Identify the process, service, container or guest with a changing footprint.
2. Compare current and earlier samples; one snapshot cannot establish a leak.
3. Check whether a cache is bounded and reclaimable, or a queue/backlog is retaining work.
4. Review service logs, limits and the change/workload timeline.
5. Preserve OOM and process evidence before restarting anything.

## Corrective action and escalation

Use the application's supported cache, queue or workload control when the cause is known. Restarting may be an authorised mitigation but does not prove a leak or prevent recurrence. Killing a process can lose state; increasing swap or changing memory limits can shift failure into severe latency. Treat either as a planned change.

Escalate on OOM kills, possible data loss, rapid uncontrolled growth, a privileged/unknown consumer, cluster-wide pressure, suspected compromise, or when dump/profiling/restart authority is unavailable.

## Validate

Confirm available memory and paging recover, the application path succeeds, queues are consistent and no new OOM event appears. Continue trending long enough to catch regrowth. Record metric definitions, samples, top consumers, impact, change correlation, mitigation and follow-up ownership.
