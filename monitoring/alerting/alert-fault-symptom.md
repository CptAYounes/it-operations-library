# Alert, fault and symptom

These terms describe different things and should not be used interchangeably.

- **Alert:** a rule reported that observed data met a condition, or required data was absent.
- **Symptom:** an externally visible or reported effect, such as timeouts or slow login.
- **Fault:** a system or component state that cannot provide its intended function.
- **Cause:** the event or condition that produced the fault; it may remain unknown after service is restored.

## One event, several interpretations

A `95% disk used` alert might indicate:

- expected growth with no current service impact;
- imminent write failure on a small remaining capacity;
- a runaway log caused by an application fault;
- stale monitoring after a volume was extended;
- capacity consumed by deleted files still held open.

The alert provides a starting metric. Local capacity, growth rate, write errors, ownership and recent changes establish what it means.

Similarly, a `service stopped` alert may be the direct fault, an intentional maintenance state, or a downstream symptom of failed storage, identity, DNS or configuration. Restarting it can mitigate the symptom without identifying the cause.

## Response language

Prefer records that preserve confidence:

> Monitoring reported root filesystem use at 96% for 10 minutes. Local `df` confirmed 4.1 GiB free; application logs were growing at approximately 900 MiB per hour after a configuration change.

Avoid:

> Disk caused the outage.

unless the evidence actually establishes that causal link.

## Correlation without overreach

Events close in time deserve comparison but are not automatically related. Ask:

1. Does the proposed cause precede the symptom?
2. Is there a mechanism connecting them?
3. Does evidence appear on affected systems and not healthy peers?
4. Did reversing or controlling the condition recover the service?
5. Is there a competing explanation?

Monitoring tools may group alerts by topology or time. That reduces noise; it does not replace technical confirmation.

## Operational result

An alert can close after the monitored condition recovers while an incident remains open for validation or follow-up. Conversely, a service can be restored before the root cause is known. Record immediate fix, service validation and cause confidence separately, following [root cause versus immediate fix](../../operations/incidents/root-cause-vs-immediate-fix.md).
