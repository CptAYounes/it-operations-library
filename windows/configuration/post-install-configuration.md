# W02 — Windows post-install configuration

A fresh desktop is not yet a supportable system. This procedure establishes identity, updates, security, time, networking and recovery without assuming that every Windows edition exposes the same controls.

**Applies to:** supported Windows 11 releases and Windows Server 2022/2025. GUI paths refer to Windows 11 or Server with Desktop Experience. On Server Core, use PowerShell and `sconfig`. Domain join, BitLocker, Remote Desktop hosting and policy controls vary by edition and installed features.

## Before changing the baseline

Record the intended owner/purpose, computer name, edition/build, activation method, network source, join state and required management method. Confirm that installation data is backed up and that the current administrator route is known.

**Read-only — compact baseline:**

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, CsName, CsDomain
Get-TimeZone
Get-NetIPConfiguration
Get-NetConnectionProfile
Get-BitLockerVolume
```

`Get-BitLockerVolume` is available only where BitLocker management components are present. Its absence is not proof that a volume is unencrypted; check **Settings > Privacy & security > Device encryption** on devices that offer Device encryption.

## 1. Set identity deliberately

Use a naming standard that does not expose a person's full name or a sensitive location. Check for duplicate names before a domain join.

**Change — requires a restart:**

```powershell
Rename-Computer -NewName 'WS-EXAMPLE-01' -Restart
```

For GUI-based client configuration, use **Settings > System > About > Rename this PC**. On Server Desktop Experience use Server Manager/Settings as appropriate; on Server Core use `sconfig` or `Rename-Computer`.

After restart, confirm `hostname` and the management platform both show the intended identity.

## 2. Correct locale, time and synchronisation

Wrong time causes misleading logs, certificate failures and domain authentication problems.

**Read-only:**

```powershell
Get-Culture
Get-WinSystemLocale
Get-TimeZone
w32tm /query /status
w32tm /query /source
```

**Change — example only:**

```powershell
Set-TimeZone -Id 'GMT Standard Time'
```

Domain members normally follow the domain time hierarchy; do not point them independently at an internet source without an approved time design. Validate the displayed time, time zone, source and recent successful synchronisation.

## 3. Validate devices before adding software

Follow [W03 — Driver and device validation](driver-device-validation.md). Resolve unknown storage, chipset, display and network devices using Windows Update, the system OEM or the component vendor. Avoid bulk third-party driver tools.

A restart after a driver package is part of the driver change, not an optional housekeeping step.

## 4. Patch, restart and prove the result

Run Windows Update through **Settings > Windows Update** on Windows 11. On Server with Desktop Experience, use the supported Windows Update/management route; on Server Core, `sconfig` provides an interactive route. Organisation-managed hosts may use WSUS, Windows Update for Business, Configuration Manager or another approved system instead.

Continue until there is no unexplained failure or pending restart, then apply [W04 — Update and patch validation](../maintenance/update-patch-validation.md). Do not install optional preview updates just to empty the screen.

## 5. Confirm activation and edition

Use **Settings > System > Activation** on Windows 11. On Server, use the licensing route supplied for that environment.

**Read-only:**

```text
slmgr.vbs /dlv
```

The dialog can reveal partial key and activation-service details. Do not publish screenshots or full output without redaction. An unexpected edition must be corrected through supported licensing/deployment methods, not an untrusted key source.

## 6. Establish account boundaries

- Keep at least one recoverable administrative route, but use a standard account for routine interactive work where practical.
- Do not enable or rename accounts as a substitute for a documented access policy.
- On domain/Entra-managed systems, follow the intended join and local-administrator design.
- Confirm recovery methods without recording passwords, PINs or security answers in the build record.
- Disable an unused temporary setup account only after another administrator has been tested.

Windows 11 Home cannot join an Active Directory domain. Pro, Enterprise and Education client editions expose broader join/management options. Server roles and domain-controller promotion require a separate design and procedure; they are not post-install defaults.

**Read-only — local account state:**

```powershell
Get-LocalUser | Select-Object Name, Enabled, LastLogon
Get-LocalGroupMember -Group 'Administrators'
```

Names of built-in groups are localised on non-English installations. `Get-LocalUser` is unavailable in 32-bit PowerShell on a 64-bit system and on a domain controller.

## 7. Check Windows security controls

Open **Windows Security** on Windows 11 and Server editions where the application is installed. Confirm that expected security providers are active rather than demanding that every host show the same Microsoft Defender screen.

**Read-only — Defender where present:**

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureLastUpdated, QuickScanAge
```

If a supported third-party security product owns antivirus state, investigate through that product and Windows Security Center; do not turn providers on and off merely to satisfy one cmdlet.

Check firewall profiles without disabling them:

```powershell
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
```

Secure Boot, TPM and BitLocker/Device encryption requirements depend on the platform and policy. Record the observed state and the reason for any exception.

## 8. Configure network from an approved source

Prefer DHCP unless a documented addressing plan requires a static configuration. Before assigning a static address, confirm address, prefix length, gateway, DNS servers and exclusion/reservation ownership. A duplicate address can disconnect two systems.

**Read-only:**

```powershell
Get-NetAdapter
Get-NetIPConfiguration
Get-DnsClientServerAddress -AddressFamily IPv4,IPv6
Get-NetRoute -DestinationPrefix '0.0.0.0/0','::/0'
```

Changing IP, DNS, VLAN or connection profile can immediately break the current session. Make remote changes only with out-of-band access or an approved rollback. Validate with the layer-by-layer checks in [W08 — Network diagnostics](../networking/network-diagnostics.md).

## 9. Enable only required remote management

Do not enable Remote Desktop, WinRM, OpenSSH Server or broad firewall exceptions “for later.” For each required service, define:

- who may connect and from which networks;
- authentication and group membership;
- firewall scope;
- certificate/NLA requirements where applicable;
- logging and recovery access;
- how to disable it if validation fails.

Windows Home can initiate Remote Desktop connections but does not provide the built-in Remote Desktop host. Server Core is commonly managed remotely but still needs a deliberate, policy-aligned setup.

After enabling a management path, test it from an authorised source and test the local/out-of-band fallback before relying on it.

## 10. Set power, storage and application defaults

Power policy should match the device role. Sleep may be suitable for a laptop and unsuitable for a remotely managed server; disabling every low-power state is not a universal performance fix.

**Read-only:**

```text
powercfg /getactivescheme
powercfg /a
```

Check free space and filesystem:

```powershell
Get-Volume | Sort-Object DriveLetter | Select-Object DriveLetter, FileSystem, HealthStatus, SizeRemaining, Size
```

Install only approved applications from a trusted source. Record package version and source when it affects support. Remove temporary installers and review startup applications instead of applying generic “debloat” scripts that may remove supported components.

## 11. Confirm recovery and maintenance ownership

- Check Windows Recovery Environment with `reagentc /info` on client/Desktop Experience systems where applicable.
- Confirm where BitLocker recovery keys are escrowed.
- Define the backup target, schedule, exclusions, encryption and owner.
- Perform a test restore appropriate to the data.
- Record the update channel and maintenance responsibility.
- Review [W12 — Recovery options](../troubleshooting/recovery-options.md) before assuming a restore point or Reset option will exist.

Enabling WinRE (`reagentc /enable`), encryption or scheduled backup is a **change** and should be handled only after storage layout, key ownership and policy are understood.

## Completion evidence

The baseline is complete when:

- [ ] product, edition, build, architecture and activation are expected;
- [ ] computer name and join state are correct;
- [ ] time zone and time source are correct;
- [ ] no device problem is unexplained;
- [ ] updates are current for the chosen policy and no restart is pending;
- [ ] expected security providers, firewall profiles and encryption state are known;
- [ ] network and required management paths pass a functional test;
- [ ] unnecessary remote services were not enabled;
- [ ] backup/recovery ownership is recorded and at least one restore check is complete;
- [ ] a restart, sign-in and core application/service check succeed.

Keep the evidence concise. Redact account names, addresses, serial numbers, activation data and recovery keys before publication.
