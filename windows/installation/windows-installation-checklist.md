# W01 — Install Windows safely

Use this procedure for a clean installation of a supported Windows 11 edition or Windows Server 2022/2025. It is deliberately longer than the [release-gate checklist](../../checklists/windows-installation.md): the checklist confirms completion, while this document explains how to get there.

A clean installation replaces the operating system on the selected target. Partition deletion and `diskpart clean` are **destructive**. Do not rely on disk number alone when several similar devices are attached.

## 1. Define the target

Record these before downloading media:

- intended Windows product, edition, language and architecture;
- device model and firmware version;
- installation type: physical host or virtual machine;
- boot mode: UEFI for a current installation;
- target storage device by model and capacity;
- activation method and ownership of the licence;
- network, domain/Entra join and local administrator requirements;
- applications, data and recovery-time expectations.

Windows edition is not a cosmetic choice. Windows 11 Home cannot join an Active Directory domain; Pro/Enterprise management features differ; Windows Server Standard and Datacenter licensing and virtualisation rights differ. Installation media may contain several editions, so confirm the selection instead of accepting a default.

## 2. Pass the pre-install gates

### Data and recovery

- [ ] Back up every required user file, application configuration, certificate and encryption key to storage that will not be erased.
- [ ] Restore a sample from the backup, or otherwise verify that it is readable.
- [ ] Record the existing BitLocker recovery key where encryption is enabled. Do not store the key in this repository or in the same unverified disk being replaced.
- [ ] Export or record any vendor-specific storage, network or licence information needed after installation.
- [ ] Disconnect non-target removable and data disks where practical. This reduces both selection mistakes and the chance that boot files are placed on another disk.

### Compatibility

For Windows 11, check the current Microsoft hardware requirements, including a compatible 64-bit processor, UEFI firmware capable of Secure Boot and TPM 2.0. Do not disable requirement checks to make an unsupported device appear supported; the servicing and security consequences are different from a normal installation.

For Windows Server, check the server catalogue/OEM support, storage controller and NIC drivers, firmware compatibility, edition, Desktop Experience versus Server Core, and application support. Server Core is an installation choice, not a GUI setting that can be toggled later.

For a virtual machine, define vCPU, memory, virtual firmware, virtual TPM/Secure Boot requirements, storage controller and NIC model before starting. Take care not to confuse a hypervisor snapshot with an independent backup.

## 3. Obtain and verify installation media

Download the ISO or create client media from an official Microsoft source. Retain the download page and release/build identification in the build record. Avoid third-party images and pre-modified ISOs.

**Read-only — PowerShell:** compare the ISO hash with a value published by the source, when Microsoft provides one for that download channel.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\InstallMedia\Windows.iso'
```

A successful hash calculation only identifies the file; it proves integrity only when compared with a separately trusted expected value.

Create the USB using a method that supports the image size and UEFI boot. Eject it cleanly, reconnect it, and confirm that its files can be read. Label reusable media with the product and approximate release so an old image is not selected by accident.

Prepare these separately if the platform needs them:

- a signed storage-controller driver that Windows Setup can load;
- the supported NIC driver, especially for Server Core or hardware not covered by the image;
- an answer file only after checking that it contains no embedded credentials or product key.

## 4. Capture the firmware baseline

Before changing firmware, record the existing boot mode, boot order, Secure Boot, TPM, storage-controller mode and virtualisation settings. Photographs must exclude serial numbers and other identifiers before publication.

Prefer:

- UEFI rather than legacy/CSM for current Windows;
- Secure Boot enabled when supported by the chosen Windows release and hardware;
- TPM enabled for Windows 11;
- the OEM-supported storage mode.

Changing an existing controller between RAID/VMD and AHCI can make an installed OS unbootable. Do not change it merely because one mode looks simpler. Update firmware only through the vendor's procedure and with stable power; it is a separate risky change, not a routine installation step.

## 5. Boot the correct installer

1. Insert the media and use the firmware's one-time boot menu.
2. Select the entry explicitly marked **UEFI** if both UEFI and legacy entries appear.
3. Confirm language, regional and keyboard choices. A wrong keyboard layout can turn a known recovery password into an apparent authentication failure.
4. Select **Install now**, the intended product/edition, and the correct licensing path.
5. Choose **Custom: Install Windows only** for a clean installation.

GUI wording changes between Windows client and Server releases. Windows Server Setup also asks for Server Core versus Desktop Experience where the image offers both. Stop if the required edition or install type is not listed; do not install a nearby option and hope to convert it later.

## 6. Identify storage without guessing

Windows Setup may show a device by capacity only. Correlate capacity, bus/controller and the disks intentionally left connected. If no target appears, load the signed storage-controller driver obtained for this exact model. Treat an unexpected empty list as a driver or controller question, not an invitation to alter firmware at random.

If retaining existing data or a dual-boot arrangement, use a separately reviewed partition plan. The clean-install path below assumes the selected target may be erased.

### Normal clean-install path

1. Highlight each existing partition **on the confirmed target only**.
2. Delete those partitions until that target shows unallocated space.
3. Select its unallocated space and allow Windows Setup to create the required GPT/UEFI partitions.

Partition deletion is **destructive** and normally irreversible without specialist recovery.

### `diskpart` exception

Use `diskpart` only when Setup cannot prepare a confirmed target and the data-loss decision has already been approved. From Setup, `Shift+F10` opens a command prompt on many builds.

```text
diskpart
list disk
select disk <confirmed-number>
detail disk
clean
convert gpt
exit
```

- `list disk` and `detail disk` are **read-only**.
- `select disk` changes only the current selection.
- `clean` is **destructive**: it removes partitioning metadata from the selected disk.
- `convert gpt` changes partition style and assumes the disk is empty.

Stop after `detail disk` if model, size or connection do not match the build record. Never paste a guessed disk number into an unattended sequence.

## 7. Let Setup complete

Installation copies files and restarts several times. Remove the USB when the first boot would otherwise return to Setup, or restore the internal disk to the top of the boot order.

Treat these as faults worth recording rather than repeatedly restarting:

- file-copy or decompression errors — verify media hash, recreate media, check RAM/storage;
- target disappears after restart — check controller driver and firmware mode;
- unexpected reboot or bugcheck — record the code and stage, then check hardware and media;
- boot loops back to the installer — correct boot order before reinstalling.

## 8. Complete first-run setup

OOBE screens and network/account requirements change between Windows 11 releases, editions and organisation-managed images. Follow the supported prompts for that build; do not use undocumented bypass commands to defeat an account or network requirement.

During first-run setup:

- verify region and keyboard layout;
- use the intended organisation, Microsoft or local-account path permitted by the edition and policy;
- create or identify an administrator without publishing its name;
- do not reuse a personal password in build notes or answer files;
- review privacy and diagnostic-data choices against the intended use;
- give the device its planned name through the supported settings or later post-install procedure.

Windows Server Desktop Experience presents server-specific administrator and deployment screens rather than client OOBE. Server Core normally continues through command-line configuration; use `sconfig` where available.

## 9. Establish a minimal trusted baseline

Before loading general applications:

1. Install the supported chipset/storage/NIC packages from Windows Update, the system OEM or component vendor as appropriate.
2. Run the [driver and device validation](../configuration/driver-device-validation.md).
3. Apply updates and complete the [update validation](../maintenance/update-patch-validation.md).
4. Continue with [post-install configuration](../configuration/post-install-configuration.md).

Do not install a third-party “driver updater” to make Device Manager look clean. Unknown packages increase rather than reduce uncertainty.

## 10. Validate the installation

Run from an elevated PowerShell session where a command requires it.

**Read-only — identity and build:**

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture, CsName
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture, LastBootUpTime
```

On some current builds, marketing names returned by older management interfaces are imprecise; use the build number and Settings/`winver` together rather than trusting one label.

**Read-only — firmware/security (cmdlet availability depends on firmware, edition and installed features):**

```powershell
Confirm-SecureBootUEFI
Get-Tpm
```

`Confirm-SecureBootUEFI` fails on legacy BIOS or unsupported firmware; that failure is evidence to interpret, not proof that Secure Boot is simply off. `Get-Tpm` is relevant where the TrustedPlatformModule module is present.

**Read-only — disks and volumes:**

```powershell
Get-Disk
Get-Volume | Sort-Object DriveLetter
```

Also confirm:

- [ ] Windows boots from the internal target with installation media removed.
- [ ] The selected product and edition are correct and activation reports the expected state.
- [ ] Device Manager has no unexplained problem device.
- [ ] Network addressing, gateway and DNS match the intended network.
- [ ] Time, time zone and time synchronisation are correct.
- [ ] Windows Update has no unexplained failure or pending restart.
- [ ] Event logs contain no repeating critical boot, storage or hardware error introduced by the build.
- [ ] A normal restart and sign-in succeed.
- [ ] Recovery information and backup ownership are recorded without secrets.

Activation failure should be resolved through the legitimate licence or organisation activation service. Do not publish product keys or use untrusted activation tools.

## 11. Record and hand off

A useful installation record includes date, hardware/VM description, firmware mode, target disk model and capacity, Windows product/edition/build, media source and hash, driver sources, update state, checks performed, exceptions and the location of recovery material. Redact serial numbers, device IDs, usernames, licence keys and public/private network details not intended for release.

Do not call the installation complete while a restart is pending, a storage/controller warning is unexplained, or the only recovery copy sits on the installed disk.
