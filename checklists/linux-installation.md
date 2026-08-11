# Linux installation sign-off

Use this as a reusable installation sign-off. For partition planning, Debian installer decisions, recovery boundaries and command examples, follow the detailed [Linux installation checklist](../linux/installation/linux-installation-checklist.md).

> Formatting or repartitioning a disk destroys data. Stop if the target disk or backup status is uncertain.

## Plan

- [ ] Purpose, owner, distribution, release and architecture recorded.
- [ ] Hardware/VM requirements and required firmware confirmed.
- [ ] Required data backed up to separate storage and a restore/read test passed.
- [ ] Official installer image obtained and its authenticated checksum matched.
- [ ] Firmware mode, Secure Boot position and storage-controller mode recorded.
- [ ] Target disk matched by model, capacity and stable identifier.
- [ ] Partition, filesystem, swap, encryption and bootloader plan reviewed.
- [ ] Encryption recovery material stored securely; no key is present in this record.
- [ ] Hostname, network method, time zone and initial administrator model agreed.

## Install

- [ ] Every proposed delete, format and mount operation rechecked before writing changes.
- [ ] Expected EFI system partition and bootloader destination selected.
- [ ] Only required package/software tasks selected.
- [ ] Official or approved signed repositories configured.
- [ ] Installation completed without unexplained disk, firmware or package errors.
- [ ] Installation media removed before the first normal boot.

## Validate

- [ ] Correct OS release, architecture and kernel booted from the installed disk.
- [ ] Expected filesystems, encryption, swap and free space confirmed.
- [ ] No required mount is missing or unexpectedly read-only.
- [ ] Local login and approved privilege escalation work.
- [ ] Time synchronisation, interface address, default route and DNS pass.
- [ ] Required services work functionally; failed units were investigated.
- [ ] Listening ports and firewall exposure match the build purpose.
- [ ] Updates were reviewed/applied under the correct change boundary.
- [ ] Reboot completed successfully after final changes.
- [ ] Backup, console/recovery and escalation routes tested or explicitly handed over.
- [ ] Build evidence is complete and contains no credentials, keys or unique identifiers intended to remain private.

**Result:** [ ] Pass  [ ] Pass with recorded exceptions  [ ] Fail/escalate

**Exceptions, evidence or next action:**
