# `journalctl` and log investigation

A good log query has a time window, boot, unit and severity appropriate to the symptom. Dumping the entire journal usually hides the useful sequence and increases the chance of collecting credentials or personal data.

## First establish the clock and boot

```bash
date --iso-8601=seconds
timedatectl status
who -b
journalctl --list-boots
```

If the clock stepped or the time zone is wrong, record that before comparing events from another system. Journal entries retain structured timestamps, but an application's own text message may use a different time zone.

## Start narrow, then widen

For a named service in the current boot:

```bash
systemctl status example.service --no-pager --full
journalctl -u example.service -b --no-pager
journalctl -u example.service \
  --since '2026-08-10 19:00:00' \
  --until '2026-08-10 19:15:00' \
  --no-pager
```

Relative times are convenient during live work:

```bash
journalctl -u example.service --since '30 minutes ago' --no-pager
journalctl -u example.service -n 100 --no-pager
journalctl -u example.service -f
```

`-f` follows new entries until interrupted; it is observational but can run indefinitely. Use an explicit time zone in the incident record when people or systems are in different zones.

Move outward only when the narrow query shows a dependency or host event:

```bash
journalctl -b -p warning --no-pager
journalctl -k -b --no-pager
journalctl -b -1 -p warning --no-pager
```

`-b -1` requires a retained previous boot. If it returns no entries, check `--list-boots` and journal persistence before concluding that the earlier boot was clean.

## Useful selectors

```bash
journalctl _PID=1234 --no-pager
journalctl _UID=1000 --since today --no-pager
journalctl _COMM=process-name --no-pager
journalctl _EXE=/usr/bin/process-name --no-pager
journalctl SYSLOG_IDENTIFIER=identifier --no-pager
journalctl /usr/bin/process-name --no-pager
```

Selectors on different fields are combined as AND; repeated values for the same field can express alternatives. Use the field names actually present in the event:

```bash
journalctl -u example.service -n 1 -o verbose
```

The verbose form reveals structured fields such as `_SYSTEMD_UNIT`, `_BOOT_ID`, `_PID`, `PRIORITY` and transport. It may also expose more sensitive context.

Priority names from most to least severe are `emerg`, `alert`, `crit`, `err`, `warning`, `notice`, `info` and `debug`. With `-p warning`, journalctl includes warning and all more severe priorities. Application authors do not always assign levels consistently; severity is a filter, not proof of impact.

## Output formats for different jobs

```bash
journalctl -u example.service -o short-iso-precise --no-pager
journalctl -u example.service -o cat --no-pager
journalctl -u example.service -o json-pretty -n 1 --no-pager
```

- `short-iso-precise` is useful for a timeline.
- `cat` removes metadata and is convenient for raw messages, but can discard the context needed to attribute them.
- JSON preserves fields for tooling but can contain control characters, large payloads and secrets.

Keep original timestamps and unit/host context when extracting evidence. Avoid rewrapping logs in a way that changes line boundaries.

## Access and retention limits

A normal user often sees their own user journal and selected system entries. Membership of groups such as `systemd-journal` or `adm` can grant wider access depending on the distribution. Do not interpret “no entries” until permission scope is known.

```bash
id
journalctl --disk-usage
journalctl --header
```

`journalctl --verify` checks journal-file consistency and can be I/O intensive on a large journal:

```bash
journalctl --verify
```

Journald storage can be volatile or persistent. `Storage=auto` typically uses persistent storage when `/var/log/journal` exists and volatile storage otherwise, but packaged defaults and local drop-ins matter. Inspect the effective configuration and filesystem before changing it. Retention settings such as `SystemMaxUse=` must fit the disk and evidence requirements.

Vacuum and rotation operations remove or retire history. Do not run `journalctl --vacuum-*` as an ad hoc fix for a full disk until important evidence is preserved and the log writer is understood.

## Journald is not every log

Also check, as applicable:

- application-owned files under `/var/log`;
- rotated/compressed logs;
- kernel audit records;
- container runtime and container logs;
- remote logging or observability platforms;
- firmware, hypervisor and storage-controller logs;
- application databases or admin consoles.

On Debian, classic files such as `/var/log/syslog` depend on a syslog daemon being installed and configured. Their absence is not itself a fault.

To discover an application's destinations, inspect its unit and configuration:

```bash
systemctl cat example.service
systemctl show example.service -p StandardOutput -p StandardError
```

## Investigation pattern

1. **State the observed symptom and impact.** “Unit inactive” and “application unavailable” are different observations.
2. **Anchor the window.** Note report time, system time, boot ID and any time skew.
3. **Query the closest source.** Start with the unit/application and a small window.
4. **Preserve the first error and preceding context.** The last message is often cleanup, not cause.
5. **Correlate dependencies.** Look for mount, DNS, certificate, memory, disk or network events at the same time.
6. **Test a hypothesis.** A log line is evidence; it is not automatically root cause.
7. **Expand only as needed.** Previous boot, kernel or host-wide warning queries should have a reason.
8. **Validate after correction.** Use a new time-bounded query plus a functional service test.

### Example: service exited

```bash
systemctl show example.service -p Result -p ExecMainStatus -p NRestarts
journalctl -u example.service --since '15 minutes ago' -o short-iso-precise --no-pager
journalctl -k --since '15 minutes ago' -p warning --no-pager
```

If the service log says only `Killed`, kernel messages may reveal an out-of-memory kill. If it says `permission denied`, check the full path, service identity, mount options and AppArmor/SELinux evidence before changing modes.

## Preserve evidence safely

For a bounded text export:

```bash
journalctl -u example.service \
  --since '2026-08-10 19:00:00' \
  --until '2026-08-10 19:15:00' \
  -o short-iso-precise --no-pager > service-window.log
```

Shell redirection creates or overwrites the destination file. Choose a protected location, set suitable permissions and confirm the time window before running it. Review before sharing: logs can contain usernames, internal addresses, query strings, tokens, certificate details and customer data. Keep an unmodified restricted copy when evidence integrity matters, and share only the necessary redacted extract.

## Escalation and closure

Escalate when logs indicate data corruption, repeated kernel/hardware faults, credential exposure, an active security event, cross-service impact or an unknown change outside your authority. Include host/service, boot and time window, observed impact, exact query scope, relevant sequence, recent changes and tests already performed.

Close the investigation only after the functional symptom is gone, a fresh time-bounded query shows no recurrence, dependent paths pass, monitoring is normal for an appropriate observation period, and any retention or visibility limitation is recorded.
