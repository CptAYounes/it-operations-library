# Service not running

Use when a required process or service is stopped, failed, repeatedly restarting or not accepting work. Process state alone does not establish application health.

## Observe before restarting

1. Confirm the correct service, host, expected state and user impact.
2. Check for planned maintenance, deployment, dependency or configuration changes.
3. Record status and recent failure detail:

    ```powershell
    Get-Service -Name W32Time
    Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddMinutes(-30)} -MaxEvents 100
    ```

    ```bash
    systemctl status --no-pager example.service
    systemctl show example.service -p LoadState -p ActiveState -p SubState -p Result
    journalctl -u example.service --since '-30 minutes' --no-pager
    ```

4. Check resource conditions: free space and inodes, memory pressure, file/port availability and required network/DNS paths.
5. Identify dependencies and startup ordering. A stopped application can be downstream evidence of a failed database, mount, certificate, account or configuration.
6. Validate configuration with the application's read-only test command where one exists. Do not assume a successful syntax test proves dependencies are available.

The [Windows service guide](../windows/services/service-troubleshooting.md) and [systemd guide](../linux/systemd/service-operations.md) provide deeper platform detail.

## Corrective action

A restart may restore service, but it also destroys process state and can create a loop. Restart only when:

- authority and expected impact are clear;
- essential evidence has been captured;
- dependencies and resource constraints have been checked;
- the service's documented stop/start behaviour is understood;
- repeated automatic restart is not already worsening the fault.

If a known recent change caused the failure, use its approved backout path rather than making several speculative edits.

## Escalate when

Stop and escalate if the service handles stateful transactions, restart could corrupt or duplicate work, a shared dependency is impaired, credentials/certificates are involved, logs suggest compromise, the configuration owner is unknown, or the service fails again after one authorised recovery attempt.

## Validate recovery

Confirm all of the following that apply:

- process/service remains in its expected state;
- required listener is bound to the intended address and port;
- a local health check succeeds;
- a dependent or user-path transaction succeeds;
- queues/backlogs begin draining safely;
- logs and monitoring show no new failure cycle.

Record symptom, exact evidence window, dependencies checked, action, user-path result and any residual risk.
