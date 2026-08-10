# Patch management

Patching is a lifecycle: know what exists, decide what matters, test and deploy with recovery, then prove the intended state. Installing packages is only the middle.

## Inventory and intake

Maintain enough inventory to map vendor advisories to product, version, role, owner and exposure. Include operating system, firmware/drivers and important applications; an unowned device cannot be patched reliably.

For each update, establish:

- vendor-supported source, digest/signature where supplied and release notes;
- affected versions and whether the vulnerable/defective component is enabled or reachable;
- severity, exploitation or reliability evidence and local impact;
- prerequisites, supersedence, dependencies and known issues;
- restart/downtime and rollback/recovery behaviour.

A severity score helps triage but does not replace local exposure and business impact. Conversely, low-severity fixes can be operationally important when they address an active reliability fault.

## Decide and prepare

Choose deploy, mitigate, defer with accepted risk, or mark not applicable—with evidence and an owner. Group only compatible changes; a large bundle makes a regression difficult to isolate.

Test representative hardware, roles, integrations and restart behaviour. No lab can reproduce every production state, so use staged rings/canaries, monitoring and stop criteria. Verify backup/recovery, free space, power, console access and the [patching checklist](../../checklists/patching.md).

## Deploy under change control

- record baseline health and installed versions;
- check active incidents and conflicting work;
- use the approved tool and maintenance sequence;
- watch installation output, restart, cluster/redundancy and capacity;
- pause when actual state differs from the plan;
- do not force power loss or repeated installer execution without vendor evidence.

An emergency patch may move faster and use a smaller first ring, but it still needs ownership, evidence, validation and a recovery decision.

## Validate

Confirm the target version and update history, then test boot/service state, devices/drivers, network and an actual service transaction. Check logs, monitoring, performance and redundant members. A package manager's success code does not prove the application loaded the new component; some processes need restart or reboot.

## Compliance and learning

Record success, failure, exception, next retry and evidence. Reconcile installed state back to inventory rather than relying only on deployment-tool status. Track overdue systems, failed installations and unsupported software separately. After failures, improve compatibility data, rings, timing or recovery instead of simply widening exclusions.
