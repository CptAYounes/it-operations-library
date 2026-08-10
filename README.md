# IT Operations Library

A collection of practical notes, checklists, troubleshooting workflows and small tools for computer hardware, operating systems, networking and day-to-day IT operations.

The material is written as a working technical reference. It concentrates on checks that narrow a fault, evidence worth retaining, boundaries for disruptive work and the validation needed before calling a service recovered.

## Library sections

| Area | Contents |
|---|---|
| [Hardware](hardware/README.md) | Build planning, physical assembly, firmware, POST, memory, storage, thermal and power fault isolation |
| [Windows](windows/README.md) | Installation, configuration, devices, updates, events, services, networking, storage, performance and recovery |
| [Linux](linux/README.md) | Debian-oriented installation, permissions, packages, systemd, journals, boot, networking, storage, SSH and maintenance |
| [Networking](networking/README.md) | TCP/IP, IPv4, routing, DNS, DHCP, switching, VLANs, firewalls and layered diagnostics |
| [Monitoring](monitoring/README.md) | Host signals, baselines, log monitoring, alert meaning and response |
| [Operations](operations/README.md) | Incidents, escalation, handover, changes, patching, backup, recovery and service validation |
| [Troubleshooting method](troubleshooting/README.md) | A cross-domain method that keeps symptom, evidence, hypothesis and cause separate |
| [Runbooks](runbooks/README.md) | Concise response sequences for ten common operational conditions |
| [Checklists](checklists/README.md) | Build, installation, diagnostics, patching, backup and handover gates |
| [Templates](templates/README.md) | Reusable troubleshooting, incident, change, build and shift records |
| [Scripts](scripts/README.md) | Four Bash, four PowerShell and four Python diagnostic utilities |

## Where to start

- For an unfamiliar fault, use the relevant subject guide and the [troubleshooting record](templates/troubleshooting-record.md).
- For an active, familiar condition, start with the matching [runbook](runbooks/README.md) and follow its escalation boundary.
- Before planned work, use the appropriate [checklist](checklists/README.md) and retain the result in a [record template](templates/README.md).
- For repeatable evidence collection, review each [script's prerequisites and limitations](scripts/README.md) before running it.

## Safety and evidence

Read-only observation comes before repair. Commands that change services, firmware, storage, network policy or boot state are identified as changes and are not presented as universal fixes. Local safety, security, change and escalation rules take precedence, as does vendor documentation for model- or release-specific work.

Examples use documentation addresses and neutral or synthetic details. They do not represent customer incidents. Outputs can still reveal usernames, hostnames, addresses, device identifiers or paths, so they must be reviewed before publication.

The material is presented as technical reference and reproducible lab procedure, not as a claim about production incidents, customers or employers.

## Tool validation

Bash and Python utilities are exercised on Debian GNU/Linux 13. The cross-platform PowerShell network check is exercised with PowerShell 7.6, while Windows-only PowerShell tools are parser-checked here and explicitly not claimed as Windows execution-tested. The committed validation and smoke-test utilities check required artifacts, relative links, script behaviour and common secret signatures without adding runtime dependencies to the tools themselves.

From the repository root, run the dependency-free checks with:

```console
$ python3 tests/validate-repository.py
Repository validation passed: 115 required files, 102 Markdown files, no broken relative links or secret signatures.
$ python3 tests/smoke-tools.py
Tool smoke tests passed.
```

The checks require Python 3.10 syntax and are exercised here with Python 3.13. Smoke coverage also uses the local Bash, Linux utilities and PowerShell installation where available. A missing optional platform command is reported as `SKIP`; review every skip and run that branch on a suitable host before relying on the affected tool. Run both commands before proposing a change.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the technical and privacy expectations applied to corrections.
