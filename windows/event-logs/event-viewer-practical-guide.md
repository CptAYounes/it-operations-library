# W06 — Event Viewer: a practical guide

Windows event logs are most useful when a question and a time window come first. Opening **Administrative Events** and reacting to every red icon usually produces noise: many errors are transient, handled or unrelated to the reported symptom.

**Applies to:** Windows 11 and Windows Server 2022/2025. Event Viewer (`eventvwr.msc`) is available on client and Server with Desktop Experience. Use PowerShell, `wevtutil` or remote Event Viewer for Server Core. Log/channel availability depends on roles, features and audit policy.

## Frame the search

Write down:

- observed symptom and affected component;
- first and last known occurrence;
- host time zone and whether its clock is trustworthy;
- recent change/restart/sign-in/service name;
- account or correlation identifier, redacted when shared.

Start with a narrow window around the symptom. Expand only if the sequence points earlier.

## Know the main logs

| Log | Typical use |
|---|---|
| System | kernel, boot, service control, drivers, storage, network stack |
| Application | application and application-runtime events |
| Security | audited security activity; access and audit policy required |
| Setup | installation, role and servicing activity |
| Forwarded Events | events collected from other systems when forwarding is configured |
| Applications and Services Logs | provider-specific operational, analytic or debug channels |

An Event ID is unique only within its provider/log context. Record **time, log, provider, ID, level, machine and message**. “Event 1000” alone is not a diagnosis.

## Use Event Viewer without losing context

1. Open `eventvwr.msc`.
2. Select the relevant log rather than **Custom Views > Administrative Events** by default.
3. Choose **Filter Current Log**.
4. Set the shortest useful logged-time range, levels and provider.
5. Open an event and read both **General** and **Details**; the XML view preserves named data fields.
6. Use **Find** for a known service, executable, device or error value.
7. Save a custom view only if the question will recur.

Do not clear a log to make new events easier to see. Filtering preserves history and sequence.

## PowerShell queries

`Get-WinEvent` is the current general tool. `Get-EventLog` is older, supports only classic logs, and should not be the default for new procedures.

**Read-only — recent System warnings/errors:**

```powershell
$start = (Get-Date).AddHours(-2)
Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = $start
    Level     = 1,2,3
} -ErrorAction Stop |
    Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message
```

Levels 1, 2 and 3 correspond to Critical, Error and Warning. A provider can log useful diagnostics at Information, so severity-only filtering may miss the event that begins the sequence.

**Read-only — one provider and time window:**

```powershell
$start = Get-Date '2026-08-10T10:00:00'
$end   = Get-Date '2026-08-10T10:30:00'
Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Service Control Manager'
    StartTime    = $start
    EndTime      = $end
} | Select-Object TimeCreated, Id, Message
```

Use a real incident time and confirm whether it includes a time-zone offset. `FilterHashtable` filters at the event API and is usually more efficient than retrieving an entire log and piping everything through `Where-Object`.

**Read-only — list logs/providers:**

```powershell
Get-WinEvent -ListLog * | Where-Object RecordCount -gt 0 |
    Sort-Object LogName |
    Select-Object LogName, RecordCount, IsEnabled, LogMode, MaximumSizeInBytes

Get-WinEvent -ListProvider * | Select-Object Name, LogLinks
```

Some channels require elevation or are inaccessible by policy. Access denied is an evidence/authority issue, not proof that the log is empty.

## `wevtutil` for local and Server Core work

**Read-only:**

```text
wevtutil el
wevtutil gli System
wevtutil qe System /q:"*[System[(Level=1 or Level=2 or Level=3)]]" /c:20 /rd:true /f:text
```

- `el` enumerates logs.
- `gli` shows log information.
- `qe` queries; `/c:20` limits records, `/rd:true` reads newest first, and `/f:text` formats output.

XML query syntax is strict. If quoting becomes complicated, save a tested query or use `Get-WinEvent -FilterHashtable` rather than building an opaque one-liner.

## Build a timeline, not a pile

A useful sequence might be:

1. update/driver installation;
2. restart or service stop;
3. dependency or device error;
4. application timeout;
5. monitoring alert.

The alert or last error is often downstream. Compare providers and logs over the same time window, but keep observation separate from interpretation:

| Time | Observation | Interpretation/hypothesis |
|---|---|---|
| 10:03 | Provider A logged device reset | Device path may have stalled |
| 10:04 | Service B timed out | Could be downstream of reset |
| 10:05 | Application C unavailable | Impact confirmed, cause not yet proved |

Repeated identical errors are not necessarily multiple independent causes. Check the first occurrence, preceding events and recovery event.

## Export evidence safely

Exporting preserves metadata better than copying only the General message.

**Creates a file but does not clear the source log:**

```text
wevtutil epl System C:\Evidence\System.evtx /ow:true
```

`/ow:true` overwrites an existing destination, so choose the path carefully. In Event Viewer, **Save All Events As** provides the equivalent GUI route. Include display information when prompted if the recipient may not have the event provider resources.

For a small textual extract:

```powershell
Get-WinEvent -FilterHashtable @{ LogName='System'; StartTime=(Get-Date).AddHours(-1) } |
    Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message |
    Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath 'C:\Evidence\system-window.csv'
```

An `.evtx` or message can contain usernames, paths, hostnames, IP addresses, application data and security events. Store it as operational evidence, restrict access and redact/sanitise any public extract. Do not edit the original evidence file; make a separately labelled redacted copy.

## Log configuration boundaries

`wevtutil sl`, changing retention/maximum size, enabling analytic/debug channels and altering audit policy are **changes**. High-volume channels can consume disk and performance. Define the collection period, capacity and rollback before enabling them.

Clearing a log (`wevtutil cl`) is destructive to diagnostic history and may violate retention/security policy. It is not a troubleshooting step.

## Common mistakes

- Searching all history without a symptom window.
- Calling Warning/Error the root cause based on level alone.
- Looking up an ID without matching provider, build and message.
- Ignoring system clock drift.
- Copying a translated General message while omitting XML fields/error values.
- Exporting Security/Application logs publicly without a privacy review.
- Assuming no event means no fault; the channel may be disabled, overwritten or unaudited.

## Close the investigation

Record the query/window used, the smallest evidence set that supports the timeline, the hypothesis tested, action taken and the recovery event/functional result. Preserve contradictory events too. A good event investigation explains why an entry is relevant, not merely that it exists.
