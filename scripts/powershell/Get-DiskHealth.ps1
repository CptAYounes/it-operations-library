#requires -Version 7.4
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
    $allVolumes = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType = 3')
    if ($allVolumes.Count -eq 0) {
        [Console]::Error.WriteLine('No fixed-volume records were returned.')
        exit 2
    }

    $volumes = $allVolumes
    $missing = @()
    if ($Drive.Count -gt 0) {
        $requested = @($Drive | ForEach-Object { $_.ToUpperInvariant() })
        $volumes = @($volumes | Where-Object { $_.DeviceID -in $requested })
        $missing = @($requested | Where-Object { $_ -notin $volumes.DeviceID })
        foreach ($item in $missing) {
            Write-Output "Volume ${item}: not found"
        }
    }

    if ($volumes.Count -eq 0) {
        exit 1
    }

    $warning = $false
    $collectionIncomplete = $false
    Write-Output "Free-space warning threshold: $FreeWarningPercent%"

    foreach ($volume in $volumes | Sort-Object DeviceID) {
        if ([string]::IsNullOrWhiteSpace([string]$volume.DeviceID) -or $null -eq $volume.Size -or $null -eq $volume.FreeSpace) {
            Write-Output "Volume $($volume.DeviceID) | capacity unavailable"
            $collectionIncomplete = $true
            continue
        }

        $sizeBytes = [double]$volume.Size
        $freeBytes = [double]$volume.FreeSpace
        if ([double]::IsNaN($sizeBytes) -or [double]::IsInfinity($sizeBytes) -or
            [double]::IsNaN($freeBytes) -or [double]::IsInfinity($freeBytes) -or
            $sizeBytes -le 0 -or $freeBytes -lt 0 -or $freeBytes -gt $sizeBytes) {
            Write-Output "Volume $($volume.DeviceID) | capacity unavailable"
            $collectionIncomplete = $true
            continue
        }

        $freePercent = [math]::Round(($freeBytes / $sizeBytes) * 100, 1)
        $freeGiB = [math]::Round($freeBytes / 1GB, 1)
        $sizeGiB = [math]::Round($sizeBytes / 1GB, 1)
        $state = if ($freePercent -lt $FreeWarningPercent) { 'warning' } else { 'healthy' }
        Write-Output "Volume: $($volume.DeviceID) | free: $freeGiB GiB of $sizeGiB GiB ($freePercent%) | status: $state"
        if ($state -eq 'warning') {
            $warning = $true
        }
    }

    if ($collectionIncomplete) {
        exit 2
    }
    if ($warning -or $missing.Count -gt 0) {
        exit 1
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("Disk capacity check failed: $($_.Exception.Message)")
    exit 2
}
