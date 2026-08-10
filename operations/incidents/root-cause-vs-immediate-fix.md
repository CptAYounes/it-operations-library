# Root cause and immediate fix

Restoring service and explaining why it failed are related but separate outcomes.

- **Immediate fix / mitigation:** reduces impact or restores function now.
- **Root cause:** the underlying condition that produced the failure, supported by evidence.
- **Contributing condition:** increased likelihood or impact without being sufficient alone.
- **Corrective action:** reduces recurrence or consequence of the established cause.

## Example distinction

A service is restarted and requests succeed again. That demonstrates an effective mitigation. It does not prove the cause was “service stopped”; that restates a symptom. Logs might later show the process exited after it could not write to a full filesystem, while failed log rotation caused the growth. Recovery, causal evidence and prevention occur at different layers.

## Keep confidence visible

Use labels such as:

- **confirmed:** evidence and mechanism establish the cause;
- **likely:** evidence strongly supports it but a key proof is unavailable;
- **unknown:** service recovered without a defensible causal conclusion.

Do not rewrite “likely” as confirmed in a final summary for neatness. Unknown is more useful than a false cause because it preserves the need for monitoring or follow-up.

## Work backwards with evidence

1. Build a timestamped sequence from monitoring, logs, changes and actions.
2. Identify the first abnormal state rather than the loudest downstream alert.
3. Explain the mechanism connecting proposed cause to fault and impact.
4. Look for evidence that would contradict it and compare healthy peers.
5. Confirm whether reversing/controlling the condition changed the expected result.
6. Separate why the component failed, why service impact occurred and why detection/recovery took the observed time.

Techniques such as repeated “why?” questions can help expose deeper controls, but stop where evidence stops. Avoid assigning personal blame to fill a technical gap; procedures, design, workload and organisational controls belong in the mechanism too.

## Operational closure

An incident can close after [service validation](../maintenance/service-validation.md) while root-cause work continues with an owner and due date. Record mitigation, cause confidence, corrective action and effectiveness check separately. A corrective action is complete only after implementation and evidence that it addresses the risk without creating another one.
