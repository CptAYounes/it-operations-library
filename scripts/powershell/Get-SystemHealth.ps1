#requires -Version 5.1
<#
.SYNOPSIS
Collects a concise, read-only Windows health summary.

.DESCRIPTION
Reports uptime, recent CPU load, available memory, fixed-volume capacity and
optionally selected service states. No configuration is changed.

.EXAMPLE
.\Get-SystemHealth.ps1 -DiskWarningPercent 15 -ServiceName W32Time,Dnscache

.NOTES
Exit 0: checks completed without a threshold warning.
Exit 1: at least one threshold or service warning.
Exit 2: unsupported platform, invalid environment or collection failure.
#>

[CmdletBinding()]
param(
    [ValidateRange(1, 100)]
    [int]$DiskWarningPercent = 10,

    [ValidateRange(1, 100)]
    [int]$MemoryWarningPercent = 10,

    [string[]]$ServiceName = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$isWindowsPlatform = $env:OS -eq 'Windows_NT'
if (-not $isWindowsPlatform) {
    [Console]::Error.WriteLine('Get-SystemHealth.ps1 requires Windows.')
    exit 2
}

try {
    $operatingSystem = Get-CimInstance -ClassName Win32_OperatingSystem
    $processors = @(Get-CimInstance -ClassName Win32_Processor)
    $volumes = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType = 3')

    $uptime = (Get-Date) - $operatingSystem.LastBootUpTime
    $cpuLoad = if ($processors.Count -gt 0) {
        [math]::Round(($processors | Measure-Object -Property LoadPercentage -Average).Average, 1)
    }
    else {
        $null
    }

    $totalMemoryKiB = [double]$operatingSystem.TotalVisibleMemorySize
    $freeMemoryKiB = [double]$operatingSystem.FreePhysicalMemory
    $freeMemoryPercent = if ($totalMemoryKiB -gt 0) {
        [math]::Round(($freeMemoryKiB / $totalMemoryKiB) * 100, 1)
    }
    else {
        $null
    }

    $warning = $false
    Write-Output "Computer: $env:COMPUTERNAME"
    Write-Output ('Uptime: {0}d {1:00}h {2:00}m' -f [int]$uptime.TotalDays, $uptime.Hours, $uptime.Minutes)
    Write-Output "CPU load: $cpuLoad%"
    Write-Output "Memory free: $freeMemoryPercent% (warning below $MemoryWarningPercent%)"

    if ($null -eq $freeMemoryPercent -or $freeMemoryPercent -lt $MemoryWarningPercent) {
        $warning = $true
    }

    foreach ($volume in $volumes | Sort-Object DeviceID) {
        if ([double]$volume.Size -le 0) {
            Write-Output "Volume $($volume.DeviceID) | capacity unavailable"
            $warning = $true
            continue
        }

        $freePercent = [math]::Round(([double]$volume.FreeSpace / [double]$volume.Size) * 100, 1)
        $freeGiB = [math]::Round([double]$volume.FreeSpace / 1GB, 1)
        Write-Output "Volume $($volume.DeviceID) | $freePercent% free ($freeGiB GiB; warning below $DiskWarningPercent%)"
        if ($freePercent -lt $DiskWarningPercent) {
            $warning = $true
        }
    }

    foreach ($name in $ServiceName) {
        try {
            $service = Get-Service -Name $name -ErrorAction Stop
            Write-Output "Service $($service.Name): $($service.Status)"
            if ($service.Status -ne 'Running') {
                $warning = $true
            }
        }
        catch {
            Write-Output "Service ${name}: unavailable ($($_.Exception.Message))"
            $warning = $true
        }
    }

    if ($warning) {
        Write-Output 'Status: warning'
        exit 1
    }

    Write-Output 'Status: healthy'
    exit 0
}
catch {
    [Console]::Error.WriteLine("Health collection failed: $($_.Exception.Message)")
    exit 2
}
