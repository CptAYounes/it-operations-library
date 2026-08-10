# Diagnostic scripts

The tools in this section make routine evidence collection repeatable without turning a quick check into a large software project.

- [Bash tools](bash/README.md) — local Linux health, filesystem, systemd service and network checks
- [PowerShell tools](powershell/README.md) — Windows health, service and volume checks plus a cross-platform network check
- [Python tools](python/README.md) — host, TCP port, inventory and bounded text-log checks

## Safety model

Every script is read-only by default. Network tools still generate DNS, ICMP or TCP traffic, so use them only on hosts you own or are authorised to test. Output can include hostnames, addresses, paths and service names; review it before adding an example to a ticket or public document.

Exit codes are intended for simple automation:

- `0` — requested checks completed without a warning;
- `1` — a negative result or threshold warning needs interpretation;
- `2` — invalid input, unsupported platform or incomplete collection.

The individual language READMEs document exceptions and platform limits. A healthy result is a snapshot, not proof of future availability; an alert result is evidence to investigate, not a root-cause diagnosis.

## Testing

Bash and Python tools are exercised on Debian GNU/Linux 13. The cross-platform PowerShell network check is exercised with PowerShell 7.6.4 on the same host. Windows-only PowerShell scripts receive parser checks here but are explicitly not described as Windows-tested.
