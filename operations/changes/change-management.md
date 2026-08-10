# Change management

Change management makes intended state, risk, authority, execution and validation visible. It should scale with the change; a concise low-risk record is better than a large form copied without thought.

## Define before scheduling

- What exact components and environments are in scope?
- What outcome and user/service value are expected?
- What is the current version/state and baseline health?
- Which dependencies, owners and simultaneous changes matter?
- What downtime, security, data and capacity risks exist?
- Who can approve, implement, validate and decide backout?

Classifications such as standard, normal and emergency are local process definitions. “Standard” should mean a pre-authorised, repeatable change with controlled scope and evidence—not permission to skip validation.

## Plan the whole state transition

Use the [change record](../../templates/change-record.md) to capture:

1. prerequisites, access, backup/recovery readiness and communications;
2. ordered implementation steps with expected result and stop condition;
3. service-level validation, not only command success;
4. backout trigger, decision owner, steps and the point where reversal becomes unsafe;
5. evidence and monitoring required before closure.

A backup is not a backout plan until restore scope, time and dependency consistency are understood.

## Assess risk honestly

Consider likelihood and consequence across availability, data, security, safety and recovery. Risk rises with unknown starting state, novelty, broad scope, weak testing, narrow window, irreversible migration, shared dependency and missing observability. Reduce risk by narrowing scope, testing, staged rollout, peer/vendor review, stronger recovery and a clearer stop point.

## Execute with control

At the window, recheck health, conflicts, approvals and go/no-go conditions. Record start and significant results. Make one planned state transition at a time. If output differs from expectation, pause at the documented boundary; do not silently redesign the change under time pressure.

Emergency handling may compress approval and documentation, but it does not remove ownership, evidence, risk and retrospective recording.

## Close or back out

Run the pre-written validation from the affected perspective, compare monitoring/baseline and observe long enough to detect immediate regression. If the backout trigger is met, make the decision while the recovery window remains usable. Validate a backout as carefully as the forward change.

Record actual outcome, versions/state, impact, deviations, evidence and remaining work. Confirm temporary access, monitoring silences, feature flags or workarounds are restored or explicitly owned. A command returning success is not change completion.
