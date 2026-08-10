# Python diagnostic tools

These utilities use only the Python standard library and are read-only by default. They were exercised with Python 3.13 on Debian GNU/Linux 13. The Windows-specific branch in `host_check.py` and Windows memory collection in `system_inventory.py` have been syntax-checked but not executed on Windows.

Run a tool with `python3 scripts/python/tool_name.py --help`. Exit `0` means the requested check completed successfully, `1` represents a negative check or input resource that could not be examined, and `2` is used for command-line or missing-tool errors where applicable.

The terminal blocks below show example invocations with illustrative output. Hostnames, addresses, timings, capacities and log counts are synthetic.

## `host_check.py`

Resolves one host and sends one bounded ICMP echo request. The selected timeout applies separately to resolution and the ICMP wait. The tool requires the operating system's `ping` command.

```console
$ python3 scripts/python/host_check.py --timeout 1 127.0.0.1
Host: 127.0.0.1
Resolved address: 127.0.0.1
ICMP: reply received
Status: reachable
```

Use `--ipv6` for an IPv6 result. No reply is not proof that a host is unavailable: firewalls commonly filter ICMP, so follow with a service-specific check when appropriate.

## `port_check.py`

Attempts a TCP connection but sends no application data. The selected timeout applies to resolution and separately to each attempted address.

```console
$ python3 scripts/python/port_check.py --timeout 2 example.org 443
Host: example.org
Port: 443/tcp
Address: 192.0.2.10
Result: reachable
Connection time: 28.4 ms
```

The displayed address and timing vary by resolver, route and load. A successful connect confirms only that the TCP handshake completed; it does not validate TLS, authentication or application health. Obtain permission before probing systems you do not manage.

## `system_inventory.py`

Reports OS, architecture, logical CPU count, physical memory and disk capacity. It deliberately omits serial numbers, MAC addresses and interface addresses.

```console
$ python3 scripts/python/system_inventory.py
Hostname: lab-node
Operating system: Linux 6.12.0
Architecture: x86_64
Logical CPUs: 4
Physical memory: 8.0 GiB
Disk path: /
Disk total: 40.0 GiB
Disk free: 22.7 GiB
```

Use `--json` for structured output or `--disk-path PATH` for another mounted filesystem. Memory reporting is implemented for Linux and Windows; other systems show it as unavailable. Hostnames and filesystem paths can still be sensitive, so review output before sharing it.

## `log_summary.py`

Counts common severity words and recognises ISO-like or traditional syslog timestamps in a plain-text file. It does not print message bodies.

```console
$ python3 scripts/python/log_summary.py --max-lines 50000 --max-bytes 10485760 application.log
File: application.log
Bytes read: 148220
Lines read: 1842
Input truncated: no
First recognised timestamp: 2026-08-10T08:00:01Z
Last recognised timestamp: 2026-08-10T08:42:17Z
CRITICAL: 0
ERROR: 3
WARNING: 11
INFO: 419
DEBUG: 0
TRACE: 0
```

Labels are counted by text, not by a schema-aware parser; a message containing the word `error` can therefore add to the count even if the source uses a different severity field. The defaults sample at most 100,000 lines and 10 MiB from the start of the file. A partial line at the byte boundary is excluded. Logs may contain credentials or personal data even though this tool suppresses message bodies—do not copy raw logs into the repository.
