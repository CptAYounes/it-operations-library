# Maintenance windows

A maintenance window is an agreed period for controlled work and expected impact. It is not permission for unbounded changes, and reaching the end of the window does not make an impaired service acceptable.

## Set a realistic window

Account for:

- pre-change checks and stakeholder confirmation;
- implementation, staged rollout or redundancy sequencing;
- restart, resynchronisation and backlog drain;
- service-level validation and observation;
- a decision point with enough time to back out;
- communication and monitoring restoration.

Schedule around workload, backup, batch, patch and dependent-team activity. State timezone and daylight-saving assumptions explicitly.

## Readiness gate

Before the window:

- scope, owner and authority are confirmed;
- affected people and support teams know expected impact and update channel;
- dependencies and conflicting changes are checked;
- current service health is acceptable or the exception is recorded;
- implementation, validation and backout plans are accessible;
- backups/recovery prerequisites have been verified;
- console/fallback access and monitoring are working;
- required people, vendor/support routes and spare capacity are available.

Postpone rather than stack a risky change on an unexplained incident, missing recovery path or unavailable decision owner.

## During the window

Announce start through the agreed channel, capture baseline and reapply the go/no-go decision. Keep one timeline. Call out each major transition, unexpected result and scope change. Do not use spare window time for unrelated “quick” work.

Define checkpoints for continue, pause and backout. If investigation begins consuming the rollback reserve, escalate the decision rather than letting the window expire unnoticed.

## Finish the window

Complete [service validation](../maintenance/service-validation.md), including dependencies, redundancy, queued work and monitoring. Remove temporary bypasses and confirm automation/alerts are re-enabled. Communicate outcome, actual impact, remaining observation and next update.

If service is not recovered by the planned end, the state becomes an incident or extended change under local process; it is not quietly left for the next shift. Hand over with current evidence, ownership, risk and decision required.

Retain actual timestamps and lessons on duration. Repeated overruns indicate that estimates, prerequisites or backout points need improvement, not that every future window should simply be longer.
