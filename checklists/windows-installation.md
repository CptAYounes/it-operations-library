# C02 — Windows installation release gate

Use this checklist to confirm that a Windows installation is ready to hand over. It does not replace the detailed [W01 installation procedure](../windows/installation/windows-installation-checklist.md).

**Scope:** supported Windows 11 editions and Windows Server 2022/2025. Record the exact product, edition, build and **Server Core/Desktop Experience** choice. GUI steps and available security/recovery features differ by release, edition and installed role.

## Before installation

- [ ] Intended product, edition, language, architecture and licence route are recorded.
- [ ] Hardware/VM compatibility, UEFI mode, Secure Boot and TPM requirements are confirmed for this target.
- [ ] Required data, certificates, configuration and encryption recovery keys are backed up away from the target disk.
- [ ] A sample backup item has been restored/read successfully.
- [ ] Official installation media source and SHA-256 hash (when an authoritative expected hash is available) are recorded.
- [ ] Target disk is identified by model and capacity; non-target disks are disconnected where practical.
- [ ] Required storage/NIC drivers and a rollback/recovery route are available.

## Installation

- [ ] Installer was booted in the intended UEFI mode.
- [ ] Correct edition and Server Core/Desktop Experience option were selected.
- [ ] Destructive partition actions were limited to the independently confirmed target disk.
- [ ] Setup completed without an unexplained copy, restart, storage or stop-code error.
- [ ] First-run account, region, keyboard and privacy choices match the intended use and policy.
- [ ] No password, product key or recovery key was placed in notes or answer files.

## Validation and handover

- [ ] System boots from the internal target with installation media removed.
- [ ] Product, edition, build, architecture and activation state are expected.
- [ ] Computer identity, time zone and time source are correct.
- [ ] No required device is missing or has an unexplained problem state.
- [ ] Windows updates are applied for the chosen policy; no unexplained failure or pending restart remains.
- [ ] Network address, gateway, DNS and required application connection pass functional tests.
- [ ] Expected firewall, security provider, Secure Boot, TPM and BitLocker/Device encryption states are recorded.
- [ ] Required sign-in, restart, service and application checks succeed.
- [ ] Backup/recovery ownership and BitLocker key escrow location are recorded without exposing secrets.
- [ ] Build record contains media/driver sources, checks, exceptions and rollback information, with identifiers redacted before publication.

**Gate:** do not sign off if the edition is wrong, a restart is pending, a storage/controller warning is unexplained, required devices or network functions fail, or recovery depends on an unverified copy stored only on the new installation.
