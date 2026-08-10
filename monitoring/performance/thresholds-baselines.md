# Thresholds and baselines

A threshold converts a measured condition into a decision to notify or act. It should represent risk or abnormal behaviour, not a round number chosen because a graph offers it.

## Static thresholds

Fixed limits are useful where a boundary is meaningful:

- filesystem space needed for safe writes or maintenance;
- certificate or backup age;
- temperature or voltage ranges supplied by a vendor;
- zero tolerance for a required service being absent;
- error counts that should never occur.

Include duration. CPU above 90% for one sample and for 20 minutes are different events. Add hysteresis or a separate recovery point so a value near the boundary does not repeatedly open and close an alert.

## Baseline-aware thresholds

Workload signals often vary by hour, day, batch cycle or business event. A baseline records that variation so monitoring can ask whether current behaviour is unusual for a comparable period.

Useful approaches include:

- percentile bands for the same period;
- deviation from a rolling median rather than a spike-sensitive average;
- rate-of-change or time-to-exhaustion for capacity;
- ratios, such as errors per request, instead of raw counts;
- peer comparison only when hosts genuinely carry comparable work.

Dynamic alerts can hide a slow deterioration if the baseline continuously adapts. Keep absolute safety limits and review long-term trends alongside them.

## Define an alert completely

| Element | Example question |
|---|---|
| Signal | Is this the right measure of the risk? |
| Scope | Per process, host, volume, service or fleet? |
| Aggregation | Maximum, average, percentile, rate or count? |
| Window | How long must the condition persist? |
| Severity | What impact or time-to-risk separates warning and critical? |
| Recovery | When is the condition stable enough to clear? |
| Missing data | Alert, hold last state, or mark unknown? |
| Ownership | Who can investigate and who can authorise change? |
| Context | Baseline, recent change and runbook included? |

## Tune with outcomes

Track alerts that were actionable, duplicates, false positives, false negatives found another way, and time spent before useful evidence appeared. Adjust one condition at a time and retain the reason. Silencing a noisy alert without correcting its definition or assigning a review date removes detection rather than improving it.

A threshold should be rechecked after capacity, workload, collection interval or architecture changes. Use [normal behaviour](normal-behaviour.md) to gather the evidence and [alert versus symptom](../alerting/alert-fault-symptom.md) to avoid encoding a weak diagnosis into the rule.
