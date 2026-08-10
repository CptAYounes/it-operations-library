# Troubleshooting method

Good fault finding reduces uncertainty without creating a second problem. The basic cycle is short:

1. **Define the symptom.** Record what was reported, what can be reproduced, when it began, scope and user/service impact.
2. **Establish the expected state.** A stopped service or high metric may be normal for this system at this time.
3. **Check recent change.** Deployments, patches, physical work, configuration, workload and upstream dependencies often explain timing, but correlation still needs evidence.
4. **Split the fault domain.** Choose a check that separates two plausible areas: name from address, host from service, hardware from operating system, capacity from performance.
5. **Record evidence.** Keep commands, timestamps and significant output in an approved location before restarting or clearing state.
6. **Test one hypothesis.** Predict the result that would support or weaken it. Avoid changing several variables together.
7. **Apply the least risky authorised correction.** Use a known recovery or backout path; stop when data, security, downtime or ownership exceeds authority.
8. **Validate from the affected perspective.** A process can be running while the service remains unusable.
9. **Monitor and document.** Record whether the cause was confirmed, suspected or not established, along with follow-up work.

## Observation is not cause

Keep these statements distinct:

- **Symptom:** the client receives a timeout.
- **Observation:** TCP connection attempts reach the timeout and no listener is visible on the host.
- **Hypothesis:** the application failed before binding its port.
- **Cause:** only confirmed after evidence identifies why it failed.
- **Mitigation:** restarting a service may restore access without establishing the cause.

This distinction prevents a plausible first explanation from becoming an unsupported incident record.

## Useful working material

- [Troubleshooting record](../templates/troubleshooting-record.md)
- [Operational runbooks](../runbooks/README.md)
- [Hardware fault isolation](../hardware/diagnostics/fault-isolation.md)
- [Layered network troubleshooting](../networking/diagnostics/layered-connectivity-troubleshooting.md)
- [Technical escalation](../operations/escalation/technical-escalation.md)

## Stop conditions

Escalate rather than experiment when there is data-loss or security risk, shared/customer impact, physical danger, uncertain ownership, no rollback, missing privileged access, a potentially destructive command, or danger of losing the final management path. Record the current state and the next unanswered question so the receiving person can continue rather than repeat the investigation.
