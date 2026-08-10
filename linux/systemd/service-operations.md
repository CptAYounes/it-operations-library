# systemd service operations

`systemctl status` answers only part of a service question. A reliable investigation also checks how the unit was loaded, what it depends on, why it stopped, and whether the application is actually usable.

Examples assume a systemd-based distribution. Debian commonly names OpenSSH's unit `ssh.service`; Fedora/RHEL commonly use `sshd.service`. Substitute the unit that exists on the host.

## Find the actual unit

```bash
systemctl list-unit-files --type=service
systemctl list-units --type=service --all
systemctl status example.service --no-pager --full
systemctl show example.service \
  -p Id -p LoadState -p ActiveState -p SubState -p UnitFileState \
  -p FragmentPath -p DropInPaths -p ExecMainPID -p Result
systemctl cat example.service
```

Do not infer these states as if they were synonyms:

- **loaded** — systemd found and parsed a unit definition;
- **active** — the unit currently satisfies its active-state rules;
- **enabled** — links/dependencies arrange for it to be pulled in at boot or by another target;
- **static** — it has no independent install section and is normally started through a dependency or explicit request;
- **failed** — its last operation failed and systemd retained that state;
- **masked** — starts are deliberately blocked by a link to `/dev/null`.

An exited oneshot unit may correctly remain `active (exited)`. A forking service can report active even when the child application is unhealthy. Read the unit's `Type=`, `RemainAfterExit=`, `PIDFile=` and health semantics.

## Build a failure timeline

Start with read-only evidence:

```bash
systemctl status example.service --no-pager --full
journalctl -u example.service -b --no-pager
journalctl -u example.service --since '30 minutes ago' --no-pager
systemctl show example.service -p Result -p ExecMainStatus -p NRestarts
systemctl list-dependencies example.service
systemctl list-dependencies --reverse example.service
```

Then check the application itself:

- Does the configured executable and account exist?
- Can the service account read its configuration, certificates and data paths?
- Is the expected port free and then listening?
- Are required mounts, sockets, network targets or secrets available?
- Did a package, certificate, permission or configuration change precede the failure?
- Is systemd rate-limiting repeated starts (`Start request repeated too quickly`)?
- Is the process being killed by the kernel, a timeout or resource limit?

A unit log may contain only the wrapper failure. Follow application logs and dependent-unit logs without assuming the last error line is root cause.

## Change state with an impact boundary

These commands change service state:

```bash
sudo systemctl start example.service
sudo systemctl stop example.service
sudo systemctl restart example.service
sudo systemctl reload example.service
sudo systemctl reload-or-restart example.service
```

- `restart` causes interruption even if the unit is healthy.
- `reload` asks the application to re-read configuration only if the unit implements it; it is not a universal zero-downtime restart.
- `reload-or-restart` may restart, so its name is the warning.
- Repeated start attempts can obscure the first failure and trigger rate limiting.
- Stopping a socket-activated service may not stop its socket unit; a new connection can start it again.

Before using them, confirm authority, current impact, active sessions/jobs, redundancy and rollback. Prefer the least disruptive operation that the application's documentation supports.

Enablement is separate:

```bash
systemctl is-enabled example.service
sudo systemctl enable example.service
sudo systemctl disable example.service
```

`enable --now` combines persistent enablement with an immediate start. Use the separate steps when review and evidence matter. Disabling a unit does not stop its current process, and another unit can still start it as a dependency. Masking is stronger and can break dependencies; do not use it as routine tidying.

## Validate configuration before restart

Use the application's own validation command where one exists. Examples include `sshd -t`, `nginx -t` or a daemon-specific dry run. Run it with the required privileges and configuration path; a command that validates a default file may not check the file the unit actually uses.

Inspect the exact launch command and environment references:

```bash
systemctl cat example.service
systemctl show example.service -p ExecStart -p EnvironmentFiles -p User -p Group
```

Environment displayed by systemd can contain sensitive values. Redact evidence and do not paste secret-bearing output into tickets or public notes.

## Make local overrides maintainable

Do not edit a vendor unit in `/usr/lib/systemd/system` or `/lib/systemd/system`; package upgrades can replace it. Create a drop-in:

```bash
sudo systemctl edit example.service
```

A typical override is stored below `/etc/systemd/system/example.service.d/`. After unit-file changes:

```bash
sudo systemctl daemon-reload
systemctl cat example.service
systemd-analyze verify example.service
```

`daemon-reload` makes the manager re-read unit definitions; it does not restart the service. `systemd-analyze verify` can report dependencies outside the single file and is not a substitute for an application configuration test.

Be careful when clearing list-type directives such as `ExecStart=`: overriding them often requires an empty assignment before the replacement. Confirm the merged result with `systemctl cat` and `systemctl show` rather than assuming the drop-in won.

## Dependencies, ordering and boot timing

`After=` controls ordering when both units are scheduled; it does not by itself pull another unit in. `Requires=` expresses a stronger requirement but still does not define all application readiness. `Wants=` is weaker. Network targets indicate stages of network management, not necessarily that an external endpoint or DNS name is reachable.

Read boot timing without changing it:

```bash
systemd-analyze time
systemd-analyze blame
systemd-analyze critical-chain example.service
```

`blame` measures activation time and can be misleading for background, device and dependency waits. Correlate it with the critical chain and logs.

## Timers

```bash
systemctl list-timers --all
systemctl status example.timer --no-pager
systemctl cat example.timer example.service
journalctl -u example.timer -u example.service --no-pager
```

The timer activation and the service result are separate evidence. Check `OnCalendar=`, monotonic timers, `Persistent=`, random delay, last/next activation and the triggered service. A “last triggered” time does not prove the job completed successfully.

## Recovery and validation

After an approved correction:

```bash
systemctl status example.service --no-pager --full
systemctl show example.service -p ActiveState -p SubState -p Result -p ExecMainPID
journalctl -u example.service --since '10 minutes ago' --no-pager
ss -lntup
```

Then exercise a safe application request from the expected client path. Confirm dependencies, authentication, data access and error rate. Observe long enough to catch a restart loop.

`sudo systemctl reset-failed example.service` clears the recorded failed state and start-rate counter; it does not fix the service. Use it only after preserving evidence and correcting the cause.

Escalate when a restart would breach availability, the unit handles storage/database recovery, credentials are implicated, dependency ownership is unclear, failures follow an unknown change, a security sandbox would need weakening, or the service repeatedly fails after one safe and validated correction. Hand over unit state, timestamps, relevant journal excerpt, changes, dependency status and functional impact—redacted of secrets.
