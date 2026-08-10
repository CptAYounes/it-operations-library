# Bash diagnostic tools

These scripts collect a small amount of Linux diagnostic evidence without changing configuration. They were exercised on Debian GNU/Linux 13 with Bash 5.2. A warning result is a reason to investigate, not proof of a fault.

The terminal blocks below show example invocations with illustrative output. Hostnames, capacities and percentages are synthetic.

Examples assume the current directory is `scripts/bash`. Make a script executable with `chmod +x script-name.sh`, or invoke it explicitly with Bash. None requires root for its normal checks.

## `system-health.sh`

Summarises uptime, load, available memory, root-filesystem use, failed systemd services and administratively enabled non-loopback interfaces.

```console
$ ./system-health.sh --disk-warning 85 --memory-warning 90
Host: lab-node
Uptime: 3d 04h 12m
Load average (1/5/15m): 0.12 0.18 0.20
Memory used: 42% (warning at 90%)
Disk / used: 36% (warning at 85%)
Failed systemd services: 0
Non-loopback interfaces administratively up: 1
Status: healthy
```

Exit `0` means all available checks are below their thresholds, `1` means a warning was found, and `2` means input was invalid or at least one check could not be completed. It reads Linux `/proc`, GNU `df`, `ip` and systemd state; containers and non-systemd distributions may produce an incomplete result.

## `disk-check.sh`

Checks the filesystem containing each supplied path. The default is `/` at a 90% warning threshold.

```console
$ ./disk-check.sh --warning 80 / /var
Threshold: 80%
Path: / | used: 36% | available: 11223344 KiB | total: 20971520 KiB | status: healthy
Path: /var | used: 41% | available: 6182912 KiB | total: 10485760 KiB | status: healthy
```

Exit `0` means every path is below the threshold, `1` reports at least one threshold warning, and `2` identifies invalid input or an unreadable path. Values come from GNU `df -Pk`, which forces 1024-byte units even when `DF_BLOCK_SIZE`, `BLOCK_SIZE` or `POSIXLY_CORRECT` is set. Reserved filesystem blocks can still make these values differ from application-level free-space views.

## `service-check.sh`

Reports `LoadState`, `ActiveState` and `SubState` for one or more systemd services.

```console
$ ./service-check.sh ssh.service cron.service
Service: ssh.service | load: loaded | active: active | sub: running | status: healthy
Service: cron.service | load: loaded | active: active | sub: running | status: healthy
```

An inactive, failed or missing unit returns `1`; invalid input or an unavailable systemd interface returns `2`. An inactive oneshot service may be working as designed, so interpret the result in light of the unit type.

## `network-check.sh`

Shows administratively enabled links, IPv4 resolution, the selected route and a bounded ICMP test. Supply a host or address; if omitted, the first IPv4 default gateway is used so the script does not contact an arbitrary public service.

```console
$ ./network-check.sh --timeout 2 127.0.0.1
Target: 127.0.0.1
Interfaces administratively up:
  lo UNKNOWN
Resolved IPv4: 127.0.0.1
Route: local 127.0.0.1 dev lo src 127.0.0.1 uid 1000
ICMP: reply received
Status: healthy
```

Exit `1` indicates resolution, routing or ICMP warning; `2` indicates invalid input, an incomplete local query or a missing prerequisite. GNU `timeout` applies the selected limit to resolution and route queries, followed by at most a one-second termination grace; ICMP uses the selected wait directly. A failed ping does not prove the host is down because ICMP may be filtered. The command intentionally does not alter routes, interfaces or resolver settings.
