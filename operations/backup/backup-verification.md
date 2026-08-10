# Backup verification

Backup monitoring proves that a job reported an outcome. Recovery confidence comes from confirming scope, independent copies, integrity and representative restores.

## Verify protection design

For each service/dataset, know:

- owner and required data/configuration/dependencies;
- recovery point objective (RPO) and recovery time objective (RTO);
- schedule, retention and legal/policy constraints;
- encryption/key recovery and authorised restore access;
- failure domains and at least one suitably isolated/off-site/immutable copy where required;
- application-consistency method and quiescing/snapshot limitations.

A snapshot on the same platform may be operationally useful but does not protect against every platform, credential or deletion failure.

## Check each protection cycle

Review job result, start/end, object count, data volume, changed rate and warnings. Compare with a baseline: a suddenly tiny “successful” backup can mean the source was not mounted or an exclusion changed. Verify copy/replication, repository capacity, retention processing and monitoring for missed or overdue jobs.

Do not put backup credentials, encryption material or full repository paths into general evidence.

## Restore representative data

Follow the [backup verification checklist](../../checklists/backup-verification.md):

1. choose a recovery point and test scope that represents critical content;
2. restore to an isolated/designated location without overwriting the source;
3. verify metadata, ownership/permissions and content/application consistency;
4. measure time and compare RPO/RTO;
5. prove required keys, catalogues, installers and dependency configuration are accessible;
6. remove test data under policy and retain safe evidence.

A file listing is weaker than opening representative files. A VM that powers on is weaker than validating services, identity, network isolation and data consistency.

## Treat failures as protection incidents

Escalate missing keys, unreadable media, repository corruption, repeated missed jobs, scope gaps or objectives that cannot be met. Avoid deleting old recovery points or reseeding a repository until retention, capacity and last-known-good copy are understood.

After remediation, run a new backup and restore test; clearing the job alert alone is not enough. Assign owners and dates for exceptions. The separate [recovery verification guide](../recovery/recovery-verification.md) covers whole-service recovery and dependencies.
