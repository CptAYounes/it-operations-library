# High CPU

A CPU alert says that demand was high during a window. It does not say whether the work was useful, whether users were affected, or which component caused it.

## Confirm the signal

- Check duration, host scope, core count and the monitoring aggregation used.
- Compare with the same workload's baseline and recent deployments, jobs or traffic.
- Confirm impact: response time, queue depth, timeout/error rate and load average or run queue.
- Check whether virtual CPU steal, power/thermal throttling or a constrained container changes the interpretation.

Windows starting points:

```powershell
Get-Counter -ListSet *
Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 5
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, Id, CPU, WorkingSet64
```

Performance-counter set and path names are localised. Use the first command to discover the installed names and substitute the local processor path when the English path is absent.

Linux starting points:

```bash
uptime
ps -eo pid,ppid,user,stat,pcpu,pmem,etime,comm --sort=-pcpu | head -n 15
vmstat 1 5
```

`CPU` in `Get-Process` is accumulated processor time, not current percentage. A `D` state on Linux points to uninterruptible wait, often I/O, even when load average is high. Continue with the [Windows performance guide](../windows/troubleshooting/performance-investigation.md) or [Linux performance guide](../linux/troubleshooting/performance-investigation.md) for a deeper investigation.

## Narrow the cause

1. Identify whether one process, many processes, kernel/interrupt work or another virtual guest accounts for demand.
2. Relate the process to a service, job, request rate and recent change.
3. Check memory pressure and storage/network latency; retries or blocked dependencies can drive CPU symptoms.
4. Capture the time window, process identity and useful application metrics before changing state.

## Safe response

Prefer reducing or rescheduling a known workload through its supported control. A process kill or service restart can lose transactions and usually discards the best diagnostic state. Do it only under the service's incident/change procedure and after checking redundancy and restart behaviour. Do not change affinity, priority, CPU limits or firmware power settings speculatively.

## Escalate when

Escalate for sustained user impact, an unknown privileged process, suspected compromise, thermal/power alarms, a shared platform constraint, repeated saturation, or when profiling/termination exceeds authority.

## Validate

Confirm the user-facing symptom, queue/error rate and CPU trend recover together. Ensure work was not silently dropped and the process does not immediately return to saturation. Record the monitoring window, baseline, top consumers, correlated event/change, action and residual capacity concern.
