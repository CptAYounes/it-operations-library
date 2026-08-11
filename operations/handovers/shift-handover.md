# Shift handover

A good handover preserves operational continuity when the person changes. It should let the next person understand current state, risk and next action without replaying the whole shift.

## Build the handover during the shift

Keep incident/change records current as work happens. At handover time, reconcile monitoring, tickets, planned work and any silences/overrides so no live condition exists only in personal notes.

Order content by urgency:

1. critical action or decision due soon;
2. active impact and degraded redundancy;
3. changes in progress or recovery under observation;
4. planned maintenance and deadlines;
5. lower-risk watch items and routine work.

## Each open item needs

- affected system/service and current impact;
- start time and present state, not only the original symptom;
- evidence and record links;
- checks/actions completed, including what failed;
- working hypothesis with confidence;
- next safe action, owner and due time;
- stop/escalation condition;
- change, incident or vendor reference;
- monitoring or communication still required.

“Investigating server issue” is not a handover. A synthetic example is: “API node remains removed from rotation after repeated storage timeouts; service is healthy on remaining nodes; storage evidence is linked; platform owner acknowledged and next update is 22:00 UTC.” This gives state and action without inventing cause.

## Transfer actively

Use the [handover template](../../templates/shift-handover.md) and [checklist](../../checklists/shift-handover.md). For critical items, walk through the record live where policy permits and ask the receiver to confirm:

- required access and evidence are available;
- ownership and next action are understood;
- escalation/contact routes are known;
- deadlines and timezones are unambiguous.

Sending a list does not transfer an unacknowledged critical responsibility. Record acceptance and update the item if its state changes during the discussion.

## Protect information

Use approved ticket/contact references. Do not paste passwords, personal numbers, customer data or sensitive infrastructure into a general handover. Keep verbal-only details to the minimum allowed by policy; decisions and technical state still need a durable authorised record.

## Quality check

The receiving person should be able to answer: What is broken or at risk? Who is affected? What has been tried? What happens next, by when, and when should I stop/escalate? If any answer depends on guessing or contacting the previous shift, repair the record before handover completes.
