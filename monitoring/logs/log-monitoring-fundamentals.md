# Log monitoring fundamentals

Logs are event evidence, not a complete account of system truth. Applications may omit failures, repeat one event at several layers, use the wrong severity or stop logging when storage and dependencies fail.

## Build from a question

Collect a source because it helps detect or investigate something specific:

- service start, stop and crash;
- authentication or privilege change;
- hardware, kernel, filesystem or storage error;
- backup, patch or scheduled-job outcome;
- application error rate or dependency failure;
- security event required by policy.

For each source, document owner, format/version, timestamp and timezone, host/service identity, transport, retention, access controls and expected volume. Synchronised clocks and preserved original timestamps are essential for cross-system timelines.

## Prefer structured fields

Where the source supports it, extract fields such as event ID, severity, service, correlation/request ID and outcome rather than matching arbitrary words. Text matching still has a place, but `error` can appear in a harmless explanation while a serious event may use another phrase.

A practical rule should account for:

- event rate and duration rather than one line where appropriate;
- duplicate suppression without losing count;
- known maintenance and retry behaviour;
- source silence or ingestion delay;
- software version and message-format changes;
- a safe sample or link to access-controlled evidence.

### Synthetic end-to-end example

A lab worker process emits a structured event such as:

```text
timestamp=2026-08-10T12:00:00Z service=example-worker event=job_failed job=demo-42 severity=error
```

The parser retains timestamp, service, event, job and severity as separate fields. It evaluates the rule every minute. One alert opens when three or more distinct `job_failed` events occur within ten minutes; repeated copies with the same service, event and job are counted in the evidence but do not open duplicate alerts. The failure alert closes after a full ten-minute window with no new failure and a current collector heartbeat. Two missed one-minute collection intervals create a separate source-silence alert; it closes after two consecutive on-time heartbeats.

The alert should include the window, distinct-event count, affected service, last event time, collection state and a link to restricted evidence. Validate it with one approved synthetic event, then the threshold count, a duplicate and a paused lab collector. Confirm one alert opens, duplicate handling is visible, silence is detected and both recovery rules close at the stated boundaries.

## Protect the logs

Logs can contain usernames, addresses, paths, tokens, submitted data and customer information. Minimise collection, restrict access, encrypt in transit/at rest where required and set retention by policy. Do not solve parsing by copying raw production logs into a public repository or unapproved tool.

Redaction at display time is not enough if the unredacted event has already travelled to an inappropriate destination. Correct logging at the source where practical and test that secret fields are not emitted.

## Validate the pipeline

A useful lab or controlled test checks:

1. a known benign event is emitted with the expected timestamp and identity;
2. the collector receives it within the expected delay;
3. parsing produces correct fields and severity;
4. the rule fires once with useful context;
5. permissions expose it only to intended readers;
6. recovery/closure works and a silent source is detectable.

Review unmatched and parse-failure rates after upgrades. A green collector with every message in an `unknown` field is not healthy log monitoring.
