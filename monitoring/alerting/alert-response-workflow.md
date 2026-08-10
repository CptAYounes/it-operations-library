# Alert response workflow

The first job is to decide whether the signal is real, what is affected and who should own the response. A fast speculative change can remove evidence or turn a local warning into an outage.

## 1. Read the alert as data

Capture metric/event, value, threshold, duration, source, affected object, first/last occurrence and missing-data state. Check whether the alert is current, duplicated or suppressed by planned work.

## 2. Establish impact and scope

- Is the user/service path failing or degraded?
- Is one process, host, rack/network, dependency or whole service affected?
- Is redundancy reduced even if users are not yet affected?
- Is there security, safety or data-integrity risk?
- Does priority need to change as scope becomes clearer?

## 3. Confirm from an independent source

Compare monitoring with a local read-only command, second monitor, service transaction or platform console. Use the linked runbook. If local evidence disagrees, investigate collection time, stale data, aggregation and object identity before changing the host.

## 4. Correlate carefully

Review recent changes, related alerts, logs and dependency health around the same time. Separate a shared cause from many downstream symptoms. Preserve uncertainty: a correlation guides the next check but does not establish root cause.

## 5. Act or escalate

Take a documented, reversible mitigation only within authority and after useful evidence is retained. Escalate when impact, ownership, access, data/security risk, downtime or the next disruptive action exceeds the responder's boundary. Provide the receiving owner:

- impact and timeline;
- confirmed observations and source;
- checks/actions with results;
- recent change and dependency context;
- current hypothesis and alternatives;
- next safe action or decision required.

Use the [technical escalation guide](../../operations/escalation/technical-escalation.md) and an appropriate [runbook](../../runbooks/README.md).

## 6. Validate recovery

Confirm the original service/user symptom, local component state and monitoring condition all recover. Watch through the rule's recovery window and check for queued or dropped work. A manually closed alert without service validation is not recovery.

## 7. Record and improve

Update the incident or troubleshooting record with cause confidence, mitigation and follow-up. If the alert was unactionable, duplicated or missing context, assign a monitoring improvement rather than simply silencing it. If it detected the problem late, identify the user-facing or leading signal that was absent.
