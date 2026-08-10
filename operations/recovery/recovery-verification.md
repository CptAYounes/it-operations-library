# Recovery verification

Recovery is the ability to restore an intended service state after loss or corruption. Verification must cover data, configuration, dependencies, identity, networking and user-visible behaviour—not merely whether a backup can be copied.

## Define the recovery claim

State:

- failure scenario and scope (file, host, site, account, application or dependency);
- recovery point and acceptable data loss (RPO);
- required recovery time (RTO);
- authority to declare recovery and return to service;
- dependencies, boot order and external services;
- integrity/consistency checks and user transaction;
- fallback if the recovery attempt fails.

Without a scenario, “DR tested” is too vague to defend.

## Prepare an isolated test

Use approved non-production or isolated resources so restored identities, scheduled jobs, agents and network services cannot conflict with live systems. Protect restored sensitive data to the same standard as the source. Confirm access to backup catalogues, keys, installation media, licences/configuration and vendor documentation without exposing them in the test record.

## Exercise the sequence

1. Start the clock and record selected recovery point.
2. Restore in the documented dependency order.
3. Record manual decisions, missing prerequisites and deviations.
4. Verify storage/filesystem and application consistency before enabling work.
5. Apply current security/configuration requirements that are not contained in the recovery point.
6. Connect dependencies using test/isolated endpoints.
7. Run a representative transaction and reconcile expected data.
8. Measure achieved RPO/RTO and observe logs/monitoring.

For failover tests, also prove how ownership/fencing prevents two active writers and how failback or continued operation will work.

## Decide the result honestly

- **Pass:** objectives and checks were met within the stated scenario.
- **Pass with exception:** service recovered, but an owned gap remains and does not invalidate the core scenario.
- **Fail:** recovery could not meet data, time, integrity or service requirements.

A recovery that required an undocumented key from one person's laptop is not reproducible even if it eventually worked.

## Finish safely

Remove or retain recovered data under policy, revoke temporary access, restore monitoring/test controls and ensure no recovered agent continues contacting live services. Update the procedure, dependency inventory and time estimates from actual evidence. Schedule a repeat after fixing failed steps rather than accepting a paper change.

Use [service validation](../maintenance/service-validation.md) for the final check and [backup verification](../backup/backup-verification.md) for routine restore confidence.
