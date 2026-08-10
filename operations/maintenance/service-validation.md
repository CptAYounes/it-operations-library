# Service validation

Validation answers whether the intended service works after a change, repair, failover or recovery. It should be written before disruptive work so success is not redefined around whatever state is reached.

## Establish the baseline

Record current health, representative transaction, relevant metric range, active alarms and known pre-existing faults. Identify the service owner or person authorised to accept the result.

## Use several levels

| Level | Example | Limitation |
|---|---|---|
| Component | Process is running; volume mounted | Component may not perform useful work |
| Local service | Health endpoint or local request succeeds | Can bypass network, proxy or identity path |
| Dependency | Database, DNS, certificate and queue checks | Individual checks may miss transaction flow |
| User path | Safe representative transaction from normal entry point | Needs controlled test data and authority |
| Operational | Monitoring, redundancy, backlog and scheduled work normal | Often requires an observation period |

Select checks relevant to the change. A firewall change needs intended allow and deny behaviour; a storage recovery needs consistency; a patch needs version plus service behaviour; a cluster change needs member/redundancy state.

## Define each check

For a reproducible validation, record:

- source and target;
- command/action and safe test data;
- expected result and acceptable range;
- timeout or observation period;
- evidence location;
- owner and what failure triggers.

Avoid using a privileged local check as the only proof for ordinary users. Do not run synthetic writes or transactions against live services unless designed and authorised for that purpose.

## Watch after the first success

Confirm error and latency trends, resource use, queue/backlog, replication, scheduled jobs and monitoring recovery. Check that temporary bypasses, maintenance modes, silences and elevated access are removed. A short check may miss memory growth, retries or delayed consistency; choose the period from the failure mode.

## Failed validation

Do not close because the implementation command succeeded. Pause, retain evidence and compare with the backout/incident trigger. Distinguish a new regression from a known pre-existing issue. If accepting a partial result, record authority, impact, workaround, monitoring and follow-up owner.

Attach concise results to the [change template](../../templates/change-record.md) or incident record. The final statement should say what path was proven, when, from where and what remains untested.
