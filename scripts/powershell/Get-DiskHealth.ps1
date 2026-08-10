#requires -Version 5.1
<#
.SYNOPSIS
Checks free capacity on fixed Windows volumes.

.EXAMPLE
.\Get-DiskHealth.ps1 -FreeWarningPercent 15
.\Get-DiskHealth.ps1 -Drive C: -FreeWarningPercent 10

.NOTES
This is a capacity check, not a physical-disk or SMART diagnostic.
#>

[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z]:$')]
    [string[]]$Drive = @(),

    [ValidateRange(1, 100)]
    [int]$FreeWarningPercent = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    [Console]::Error.WriteLine('Get-DiskHealth.ps1 requires Windows.')
    exit 2
}

try {
    $volumes = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType = 3')
    if ($Drive.Count -gt 0) {
        $requested = @($Drive | ForEach-Object { $_.ToUpperInvariant() })
        $volumes = @($volumes | Where-Object { $_.DeviceID -in $requested })
        $missing = @($requested | Where-Object { $_ -notin $volumes.DeviceID })
        foreach ($item in $missing) {
            Write-Output "Volume ${item}: not found"
        }
    }

    if ($volumes.Count -eq 0) {
        [Console]::Error.WriteLine('No matching fixed volumes were found.')
        exit 2
    }

    $warning = $false
    Write-Output "Free-space warning threshold: $FreeWarningPercent%"

    foreach ($volume in $volumes | Sort-Object DeviceID) {
        if ([double]$volume.Size -le 0) {
            Write-Output "Volume $($volume.DeviceID) | capacity unavailable"
            $warning = $true
            continue
        }

        $freePercent = [math]::Round(([double]$volume.FreeSpace / [double]$volume.Size) * 100, 1)
        $freeGiB = [math]::Round([double]$volume.FreeSpace / 1GB, 1)
        $sizeGiB = [math]::Round([double]$volume.Size / 1GB, 1)
        $state = if ($freePercent -lt $FreeWarningPercent) { 'warning' } else { 'healthy' }
        Write-Output "Volume: $($volume.DeviceID) | free: $freeGiB GiB of $sizeGiB GiB ($freePercent%) | status: $state"
        if ($state -eq 'warning') {
            $warning = $true
        }
    }

    if ($warning -or ($Drive.Count -gt 0 -and $missing.Count -gt 0)) {
        exit 1
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("Disk capacity check failed: $($_.Exception.Message)")
    exit 2
}
