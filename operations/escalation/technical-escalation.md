# Technical escalation

Escalation transfers or adds ownership when risk, impact, access, knowledge or authority reaches a boundary. It is not failure; continuing beyond that boundary without a safe plan is the operational failure.

## Continue locally when

- impact and fault domain remain within the responder's remit;
- checks are read-only or explicitly authorised;
- each next step has a clear question and expected result;
- evidence is improving the diagnosis;
- recovery/backout and management access remain safe;
- local response time still fits the incident priority.

## Stop and escalate when

- data loss, security, safety or physical/electrical risk is possible;
- customer/shared impact or reduced redundancy exceeds authority;
- a restart, failover, firewall/route, storage repair or hardware change needs approval;
- access is missing or the next action could remove the final management path;
- ownership crosses to network, platform, application, vendor or facilities support;
- the state is unknown after conflicting or undocumented changes;
- the same recovery attempt has failed or the fault is recurring;
- evidence suggests compromise or protected investigation requirements;
- time spent no longer matches impact and urgency.

## Send an evidence package, not a ticket number

A useful handoff answers:

1. **Impact:** affected service/users, scope, start time, priority and trend.
2. **Current state:** what works, what fails, redundancy/workaround and immediate risk.
3. **Evidence:** exact errors, timestamps, commands/outputs and approved evidence location.
4. **Work completed:** checks and changes in order, including failed attempts.
5. **Assessment:** current hypothesis, confidence, alternatives and recent changes.
6. **Request:** decision, access, specialist action or owner needed next.
7. **Constraints:** maintenance/change status, stop conditions and time boundary.

Keep raw confidential data in its controlled location and link to it. Redact screenshots/outputs appropriately.

## Preserve responsibility through acknowledgement

Use the approved queue/contact and match urgency. For a critical item, do not assume that sending a message transfers ownership. Obtain acknowledgement, state who coordinates meanwhile and escalate through the next level if response time is missed. Update the shared record when state changes during handoff.

## After escalation

Remain available for context and local actions unless formally released. Avoid parallel speculative changes while the receiving owner investigates. When service recovers, confirm the original user path and capture who owns remaining root-cause, replacement, monitoring or documentation work.

The [troubleshooting record](../../templates/troubleshooting-record.md) and [shift-handover template](../../templates/shift-handover.md) provide reusable formats.
