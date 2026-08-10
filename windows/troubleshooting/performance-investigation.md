# W10 — Windows performance investigation

“Slow” is a symptom, not a counter. Define which action is slow, when it changed and what normal looked like before tuning or terminating anything.

**Applies to:** Windows 11 and Windows Server 2022/2025. Task Manager, Resource Monitor and Performance Monitor are available on client and Server with Desktop Experience. Server Core uses PowerShell, `typeperf`, Performance Monitor remotely, Windows Performance Recorder or the owning platform. Counter sets vary by feature, hardware and display language.

## Write a measurable symptom

Prefer:

> Interactive sign-in takes 95 seconds after entering credentials; normal was about 15 seconds. The delay began after the 08:00 restart and affects all tested accounts.

Capture:

- start/end time and time zone;
- affected operation, user scope and input size;
- baseline or comparison host;
- recent update, deployment, reboot or workload;
- whether delay is CPU time, waiting, network latency or blocked I/O;
- power/thermal state on physical hardware.

Do not apply an “optimisation pack” before a baseline. It destroys the comparison.

## Fast triage

### GUI systems

Task Manager gives a first view of CPU, memory, disk, network, GPU, startup impact and per-process activity. Use **Performance > Open Resource Monitor** for disk files, wait chains, TCP endpoints and memory composition. Performance Monitor (`perfmon.msc`) is better for a timed counter set.

Sort by more than one column. A process may use little CPU while blocked on storage or network. Task Manager percentages are sampled snapshots and can miss a short spike.

### PowerShell snapshot

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object LastBootUpTime, FreePhysicalMemory, TotalVisibleMemorySize

Get-Process |
    Sort-Object CPU -Descending |
    Select-Object -First 15 Name, Id, CPU, WorkingSet64, PagedMemorySize64, HandleCount, StartTime

Get-Volume | Where-Object DriveLetter |
    Select-Object DriveLetter, HealthStatus, SizeRemaining, Size
```

These are **read-only**. `Process.CPU` is cumulative processor time since the process started, not current utilisation; compare samples or use performance counters. Some protected/system processes deny individual properties, so handle access errors rather than treating them as zero.

## Capture a short counter baseline

List locally available counter sets first:

```powershell
Get-Counter -ListSet * | Select-Object CounterSetName, Paths
```

Counter names are localised on non-English Windows, so English paths below may need the local names. Available instances also change over time.

**Read-only — one minute, five-second samples:**

```powershell
$counters = @(
    '\Processor(_Total)\% Processor Time'
    '\System\Processor Queue Length'
    '\Memory\Available MBytes'
    '\Memory\Committed Bytes'
    '\Paging File(_Total)\% Usage'
    '\PhysicalDisk(_Total)\Avg. Disk sec/Transfer'
    '\PhysicalDisk(_Total)\Current Disk Queue Length'
    '\Network Interface(*)\Bytes Total/sec'
)
Get-Counter -Counter $counters -SampleInterval 5 -MaxSamples 12
```

Run long enough to cover the symptom and save raw data where comparison matters. A single sample does not establish sustained pressure.

To create a reusable Data Collector Set, use Performance Monitor and define the counter set, interval, duration, destination capacity and owner. Collection can expose process names, paths and traffic patterns; protect the output.

## Interpret resources together

### CPU

Useful evidence includes sustained total utilisation, per-process/thread consumption, processor queue, clock/power state and interrupt/DPC load. High CPU can be legitimate throughput. Low total CPU can still hide a single-thread bottleneck on one logical processor.

Check whether the process work matches the reported action. If System/interrupt activity is high, investigate drivers/devices rather than blaming an arbitrary user process.

### Memory

Working set is memory currently resident for a process; commit represents promised virtual memory backed by RAM or page file. High “used memory” can include useful cache. More useful signs are low available memory, commit approaching its limit, hard-fault/paging activity and performance recovering when the workload ends.

Do not disable the page file as a generic tuning step. It changes commit capacity and crash-dump support. A continuously growing private-byte/commit pattern under a stable workload is stronger leak evidence than one large working set.

### Storage

Correlate latency, queue, throughput, free capacity, process I/O and storage events. 100% active time with little throughput can indicate small random I/O or retries; high throughput with acceptable application latency may be healthy work. Virtual and SAN storage can make guest physical-disk counters incomplete.

Use [W09 — Storage and filesystem diagnostics](../storage/storage-filesystem-diagnostics.md) if resets, health warnings or filesystem issues appear. Avoid benchmarks on suspect or shared storage.

### Network and external wait

Compare interface throughput/errors with connection state, DNS and application response. Low host CPU during a slow request can mean it is waiting on DNS, a remote service, lock or storage. Use [W08 — Network diagnostics](../networking/network-diagnostics.md) for path testing.

### GPU and thermal/power limits

Task Manager and vendor tools can expose engine use and dedicated/shared memory on supported drivers. For laptops/workstations, compare active power plan, AC/battery state, clocks and temperatures. Thermal throttling needs hardware/vendor telemetry; high temperature alone does not identify the heat source or cooling fault.

```text
powercfg /getactivescheme
powercfg /a
```

These commands are read-only. Changing power plans is a **change** and should match device role rather than an assumed “maximum performance” rule.

## Process and wait investigation

Resource Monitor's **Analyze Wait Chain** can show threads waiting on another process, but ending a process from that view is disruptive. For services, map PID without killing shared hosts:

```powershell
Get-CimInstance Win32_Service | Where-Object ProcessId -ne 0 |
    Select-Object Name, State, ProcessId, StartName
```

Capture repeated process samples:

```powershell
1..6 | ForEach-Object {
    Get-Process | Sort-Object CPU -Descending |
        Select-Object -First 10 @{n='Time';e={Get-Date}}, Name, Id, CPU, WorkingSet64, Handles
    Start-Sleep -Seconds 10
}
```

This creates no configuration change but the output can be large. Cumulative CPU must be compared between samples, and restarted PIDs/processes must not be treated as the same instance.

## Deep tracing boundary

Windows Performance Recorder (WPR) and Windows Performance Analyzer can capture CPU sampling, disk I/O, file I/O, networking and boot traces. Example profile names/options vary by installed WPR version; inspect locally first:

```text
wpr -profiles
wpr -status
```

Starting/stopping a trace is a **diagnostic change** with performance, disk-space and privacy impact. Use a focused profile and bounded duration, reproduce once, stop the trace cleanly, then review the ETL as sensitive evidence. Do not publish ETL files without inspection.

ProcDump, Process Monitor, RAMMap and WPA are Microsoft Sysinternals/ADK tools but are not built into every Windows installation. Document source/version and capture scope before using them.

## Correct only the evidenced constraint

Possible actions include fixing a runaway application's configuration, removing a failed dependency, rescheduling competing work, correcting storage capacity, repairing a driver, or scaling a legitimately saturated resource. Each needs an owner and post-change comparison.

Avoid:

- force-ending a process before logs/counters are captured;
- disabling antivirus, updates, indexing or page file as generic tuning;
- clearing caches repeatedly to create an artificial “fast” test;
- changing several services/power/registry settings together;
- treating an arbitrary percentage as a universal threshold.

## Validate and close

Repeat the same workload and measurement method. Record:

- median/range before and after, not just the best run;
- counter window and sample interval;
- resource that changed and evidence linking it to the symptom;
- application correctness and service stability;
- side effects on other workloads;
- rollback result if the change did not help.

A good closure is “the 95-second sign-in now completes in 17–20 seconds over five trials, and the profile-service event delay no longer repeats,” not “performance looks better.”
