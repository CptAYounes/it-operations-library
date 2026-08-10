# Incident handling

An incident is unplanned service degradation or interruption that needs coordinated response. The immediate objective is safe service restoration; preserving evidence and managing risk remain part of that objective.

## 1. Confirm and open

- Record detection source, first known time, affected service and exact symptom.
- Confirm the signal from a second or local source where time allows.
- Establish impact, scope, current redundancy and security/data/safety concerns.
- Assign an owner/coordinator and create the authorised [incident record](../../templates/incident-record.md).
- Set an initial priority from evidence, then reassess as scope changes.

Do not wait for root cause before opening a record or escalating material impact.

## 2. Stabilise the response

Define who coordinates, investigates, communicates and approves disruptive action. One person can fill several roles in a small response, but decisions should remain explicit. Set an update interval and one shared timeline so parallel work does not create conflicting changes.

Capture before alteration:

- alerts, logs and metrics around the start time;
- recent deployments, patches, maintenance and infrastructure changes;
- host/service state and dependency health;
- actions already attempted and their results.

Use approved evidence systems. Do not copy confidential logs or credentials into general chat or public notes.

## 3. Investigate by fault domain

Form a testable hypothesis and choose a check that separates plausible areas. Use the relevant [runbook](../../runbooks/README.md). Treat a recent change as strong timing evidence, not automatic proof. Keep symptom, observation, hypothesis and confirmed cause distinct.

When several components alert together, find the common dependency or boundary before restarting each component independently.

## 4. Mitigate and recover

Prefer a documented, reversible mitigation with a clear owner and expected result. Before action, state:

- risk and user impact;
- authority/change reference;
- evidence already retained;
- rollback or stop condition;
- validation to run immediately afterwards.

Contain security events through the security incident process; ordinary troubleshooting can destroy forensic evidence or widen exposure.

## 5. Validate and communicate

Recovery requires more than a green process. Test the affected user/service transaction, dependencies, backlog/consistency, redundancy and monitoring. Observe through a meaningful period. Communicate facts, impact, action, current state, remaining risk and next update—avoid an unsupported cause statement.

## 6. Close and follow up

Close only when service state is accepted, monitoring is stable, open risk has an owner and stakeholders are updated. Record whether cause is confirmed, likely or unknown. Assign corrective, monitoring, documentation or review work with owners and dates. A separate problem/root-cause review may continue after incident closure.
