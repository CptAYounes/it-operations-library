# W03 — Driver and device validation

A clean Device Manager is useful, but the real objective is that every required device is identified, uses an appropriate signed driver and works in its intended mode.

**Applies to:** Windows 11 and Windows Server 2022/2025. Device Manager is available on client and Server with Desktop Experience. Server Core is checked through PowerShell, `pnputil`, remote management or the hardware vendor's supported tooling. Device availability also depends on edition, role and installed features.

## Start with observation

Record the hardware/VM model, Windows build, firmware version, recently installed driver or firmware package, and the actual symptom. A yellow warning icon is evidence of a problem device; it is not proof that the driver alone is the root cause.

**Read-only — problem devices:**

```powershell
Get-PnpDevice -PresentOnly |
    Where-Object Status -ne 'OK' |
    Sort-Object Class, FriendlyName |
    Format-Table Status, Class, FriendlyName, InstanceId -AutoSize
```

**Read-only — built-in command-line alternatives:**

```text
pnputil /enum-devices /problem
pnputil /enum-devices /disconnected
pnputil /enum-drivers
```

`/enum-devices /problem` is supported on current Windows 11/Server builds but older releases have fewer `pnputil` switches. `pnputil /enum-drivers` lists third-party packages in the driver store; it does not mean those packages are all active.

In Device Manager (`devmgmt.msc`), use **View > Show hidden devices** only when investigating previous/disconnected instances. A grey device can be historical and does not automatically need removal.

## Separate the failure types

| Observation | First question |
|---|---|
| Device absent everywhere | Is it enabled/detected in firmware or exposed by the hypervisor? |
| Unknown device | What hardware ID identifies it? |
| Code 10/43 or similar | What exact status and event does the device report? |
| Driver installed but function fails | Does the device pass a real functional test? |
| Device appears only after rescan/reboot | Is there a power, connection, firmware or enumeration issue? |
| Duplicate/ghost entries | Is one active and the rest historical, or is enumeration repeating? |

For an unknown device, open **Properties > Details > Hardware Ids**. Search the system/OEM catalogue using the vendor and device identifiers, not a generic driver-download site. Hardware IDs can be identifying data; redact unique instance/serial portions from published evidence.

## Choose a defensible driver source

Use this order as a decision aid, not an absolute rule:

1. Windows Update for supported, signed packages distributed for the build.
2. The system OEM for chipset, platform, laptop power and device integration packages.
3. The component vendor where the OEM directs it or where a current standalone component has its own supported package.
4. The hypervisor's guest tools for virtual devices.

Avoid “driver updater” bundles. A newer date is not enough reason to replace a stable OEM package, especially for firmware-coupled laptop and server devices.

Before installing, record package version, source, release notes, supported hardware IDs/builds and rollback route. Check whether the package also updates firmware; that raises the risk and power requirements.

## Inspect the active driver

Device Manager's **Driver** tab shows provider, date, version and digital signer. PowerShell can correlate signed-driver records:

```powershell
Get-CimInstance Win32_PnPSignedDriver |
    Select-Object DeviceName, DeviceClass, DriverProviderName, DriverVersion, DriverDate, InfName, IsSigned |
    Sort-Object DeviceClass, DeviceName
```

WMI/CIM inventory may omit or normalise some fields. Confirm a suspect device in Device Manager or with `pnputil` rather than relying on one inventory source.

To inspect a specific package without installing it:

```text
pnputil /enum-drivers /files
```

The `/files` option is not present on every older Windows build. Use `pnputil /?` to confirm local syntax.

## Install one change at a time

Use the vendor installer when its release notes require services, control software or firmware coordination. For a plain INF package, current `pnputil` supports:

```text
pnputil /add-driver C:\Drivers\Example\driver.inf /install
```

This is a **change** and normally requires elevation. `/install` updates matching devices only when Windows ranks the package as appropriate; it does not force a lower-ranked package over the active driver. Add `/subdirs` only when the directory contents have been reviewed.

After each material driver change:

1. note the active version;
2. restart if requested;
3. rescan or re-query problem devices;
4. run a device-specific functional test;
5. review System log events at the installation/restart time.

Do not update chipset, storage, NIC, GPU and firmware packages in one unrecorded batch when troubleshooting. That makes rollback and attribution unreliable.

## Device-specific functional checks

- **Storage/controller:** all intended disks appear with the correct approximate capacity; no recurring disk/controller reset events; a normal read/write workload completes. Use [W09](../storage/storage-filesystem-diagnostics.md) for deeper checks.
- **Network:** expected link speed, addressing, DNS and a required TCP connection work. Use [W08](../networking/network-diagnostics.md).
- **Display/GPU:** expected resolution, refresh rate and multi-monitor layout work without repeated driver reset events.
- **Audio:** the intended playback/recording endpoint is present and passes a test; default-device selection is not a driver diagnosis.
- **USB/Bluetooth:** connect a known-good device at the intended port/range; check power-saving and firmware only after basic enumeration.
- **Virtual devices:** guest agent/tools version matches the supported hypervisor release; ballooning, time, NIC and storage drivers appear as intended.

## Rollback and removal boundaries

Device Manager may offer **Roll Back Driver** when Windows retained the previous package. If not, reinstall the recorded known-good package. Rollback is a **change** and may interrupt the device.

`pnputil /delete-driver oemNN.inf /uninstall` removes a third-party package and uninstalls it from devices. Adding `/force` or deleting storage/network packages remotely can make the host unbootable or unreachable. Do not use package deletion as routine cleanup; verify the exact published name, dependencies, recovery access and replacement first.

For boot-critical storage or display failures, use [boot troubleshooting](../troubleshooting/boot-troubleshooting.md) and [recovery options](../troubleshooting/recovery-options.md). WinRE/offline driver injection or removal is a separate recovery action and must target the offline image, not `X:\Windows` in WinRE.

## Validation record

Finish with:

- [ ] no required device is missing;
- [ ] no unexplained present-device status is non-OK;
- [ ] active driver provider/version/source are recorded for material devices;
- [ ] packages are signed or an approved exception is documented;
- [ ] each changed device passes a functional test;
- [ ] restart produces no repeating new hardware/controller error;
- [ ] rollback source is retained where failure would remove access or boot capability.

Do not publish complete PnP instance IDs, serial-bearing hardware IDs or diagnostic bundles without reviewing them for identifiers.
