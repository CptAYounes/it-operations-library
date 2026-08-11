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

Examples use documentation addresses and neutral or synthetic details; they are not records of real customer or production work. Outputs can still reveal usernames, hostnames, addresses, device identifiers or paths, so they must be reviewed before publication.

## Quality checks

Automated checks cover the planned structure, links, Markdown, scripts and obvious unsafe artifacts. They support technical review rather than replacing it; platform-specific claims, example destinations and publication safety still need a person to inspect them.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the validation commands and the technical and privacy expectations applied to corrections.
