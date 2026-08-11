# Establishing normal behaviour

A baseline is a description of expected behaviour under stated conditions. It is not one quiet afternoon captured forever.

## Decide what normal means

Tie the observation to a service or capacity question. Examples:

- request latency and error rate during normal and peak demand;
- CPU, queue and storage latency during a scheduled batch;
- daily filesystem growth and retention processing;
- memory footprint after startup and after sustained work;
- expected number and timing of backup or maintenance jobs.

Record architecture, software version, capacity, collection interval and workload. A baseline from a two-core test VM is not directly transferable to a larger host, and an average can hide short peaks that affect users.

## Collect representative periods

1. Verify monitoring timestamps and missing-data handling.
2. Include weekdays/weekends, shift boundaries and known batch or backup windows where relevant.
3. Mark deployments, incidents, maintenance and unusual demand rather than allowing them to silently shape normal.
4. Retain maximum and percentile behaviour alongside averages.
5. Compare service outcomes with resource signals; resource use alone does not define health.

Do not generate artificial load on a shared or production service without a controlled test plan and authority.

## Turn observation into a working range

Summarise:

| Context | Signal | Typical range | Expected peak / duration | Concern begins when |
|---|---|---|---|---|
| Synthetic weekday lab test, 09:00–17:00 | Request latency (p95, five-minute windows) | 70–110 ms | 150 ms for one window during the test batch | Above 180 ms for two windows, or any matching error-rate rise |

The row is a filled synthetic example, not a local baseline. Copy the columns into an operational record and populate them with measured interactive, scheduled-job and degraded-dependency periods. Use ranges and distributions rather than false precision. Where capacity grows, estimate rate and time to an operational limit, then verify the estimate regularly.

Record degraded-dependency periods separately as comparison evidence; do not allow impaired behaviour to become part of the healthy baseline merely because it recurs.

## Keep it current

Rebaseline after material workload, resource, software or monitoring changes. Keep the old period long enough to explain why the expected range moved. Slow degradation can become accepted as normal if a rolling model has no fixed service objectives or absolute safety thresholds, so review long trends separately.

A useful baseline shortens investigation: it tells the responder which signal is unusual, for how long and under which workload. It does not prove cause. Feed it into [threshold design](thresholds-baselines.md) and include the relevant comparison in alert context.
