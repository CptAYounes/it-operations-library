# Python diagnostic tools

These utilities use only the Python standard library and do not change system configuration. They were exercised with Python 3.13 on Debian GNU/Linux 13. Windows-specific host and memory paths were syntax-checked but not executed on Windows; unsupported systems return an explicit incomplete result rather than guessing at incompatible commands.

Run a tool with `python3 scripts/python/tool_name.py --help`. Exit `0` means the requested check completed successfully, `1` represents a negative check or input resource that could not be examined, and `2` is used for command-line or missing-tool errors where applicable.

The user needs permission to run the platform `ping`, open the requested network connection, inspect the selected filesystem path and read any log supplied to `log_summary.py`. Network checks generate traffic and logs. Do not use broader privilege merely to bypass an unexplained denial.

The terminal blocks below show example invocations with illustrative output. Hostnames, addresses, timings, capacities and log counts are synthetic.

## `host_check.py`

Resolves one host and sends one bounded ICMP echo request. Resolution and the complete `ping` child process each use the selected timeout. The tool requires the operating system's `ping` command.

```console
$ python3 scripts/python/host_check.py --timeout 1 127.0.0.1
Host: 127.0.0.1
Resolved address: 127.0.0.1
ICMP: reply received
Status: reachable
```

Use `--ipv6` for an IPv6 result. No reply is not proof that a host is unavailable: firewalls commonly filter ICMP, so follow with a service-specific check when appropriate.

## `port_check.py`

Attempts a TCP connection but sends no application data. One overall timeout covers resolution and all distinct resolved addresses, without allowing one unresponsive address to consume the entire check.

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

The tool counts severity words in text; it does not understand a log schema. A harmless sentence containing `error` can therefore increase the count. By default it reads at most 100,000 lines and 10 MiB from the start and excludes a partial final line at the byte boundary. Logs may contain credentials or personal data even though message bodies are not printed—do not copy raw logs into the repository.
