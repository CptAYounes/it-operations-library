# Diagnostic scripts

The tools in this section make routine evidence collection repeatable without turning a quick check into a large software project.

- [Bash tools](bash/README.md) — local Linux health, filesystem, systemd service and network checks
- [PowerShell tools](powershell/README.md) — Windows health, service and volume checks plus a cross-platform network check
- [Python tools](python/README.md) — host, TCP port, inventory and bounded text-log checks

## Safety model

Every script is read-only by default. Network tools still generate DNS, ICMP or TCP traffic, so use them only on hosts you own or are authorised to test. Output can include hostnames, addresses, paths and service names; review it before including it in a ticket or public document.

Exit codes are intended for simple automation:

- `0` — requested checks completed without a warning;
- `1` — a negative result or threshold warning needs interpretation;
- `2` — invalid input, unsupported platform or incomplete collection where the script handles that condition explicitly.

The individual language READMEs document exceptions and platform limits. A healthy result is a snapshot, not proof of future availability; an alert result is evidence to investigate, not a root-cause diagnosis.

## Testing

Bash and Python tools are exercised on Debian GNU/Linux 13. The cross-platform PowerShell network check is exercised there with PowerShell 7.6.4. See each language README for native-platform limits and permission requirements.

Start with the language README, which lists prerequisites, examples and limitations. Run a tool interactively before using its exit code in automation, and retain enough output to explain a warning or incomplete result rather than reducing every non-zero status to “down”.
