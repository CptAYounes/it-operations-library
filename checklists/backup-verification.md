# Backup verification checklist

A successful backup job shows that data was written somewhere. Verification asks whether the right data can be recovered within the required time and trust boundary.

## Scope and policy

- [ ] Identify the protected systems, datasets and recovery objectives.
- [ ] Confirm the backup schedule, retention and legal or policy requirements.
- [ ] Verify critical dependencies are included: configuration, keys held in an approved system, application metadata and recovery documentation.
- [ ] Identify exclusions and confirm they are intentional.
- [ ] Confirm at least one copy is isolated from the protected system's normal credentials or failure domain.

## Job and repository health

- [ ] Review the latest job status and investigate warnings as well as failures.
- [ ] Compare protected object counts and data volume with a known baseline.
- [ ] Check repository capacity, retention processing and replication/copy status.
- [ ] Confirm encryption is enabled where required and recovery keys are available through the approved process.
- [ ] Review immutability, offline or off-site copy status where policy requires it.
- [ ] Check time synchronisation so restore points can be interpreted correctly.

## Restore test

- [ ] Select a restore point and representative data without overwriting the source.
- [ ] Record who authorised the test and where restored data may be placed.
- [ ] Restore into an isolated or designated validation location.
- [ ] Verify filenames, ownership/permissions, timestamps and expected object count.
- [ ] Open or otherwise validate representative content; a completed copy alone is insufficient.
- [ ] For application or system backups, perform the documented consistency or boot/service test.
- [ ] Record recovery duration and compare it with the recovery-time objective.
- [ ] Confirm the restored point satisfies the recovery-point objective.

## Finish

- [ ] Remove test data securely according to policy.
- [ ] Record evidence, exceptions, restore point, duration and software versions.
- [ ] Escalate corrupt media, missing keys, untested dependencies or missed objectives.
- [ ] Assign remediation and schedule a repeat test after corrective work.
- [ ] Confirm monitoring will alert on the next failed, missed or overdue backup.

Never publish backup reports that reveal customer names, private paths, repository addresses, encryption details or recovery credentials.
