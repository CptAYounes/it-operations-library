#requires -Version 7.4
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

foreach ($name in $ServiceName) {
    if ([string]::IsNullOrWhiteSpace($name) -or $name.IndexOfAny([char[]]'*?[]') -ge 0) {
        [Console]::Error.WriteLine('ServiceName values must be non-empty literal service names without wildcard characters.')
        exit 2
    }
}

$systemDrive = [string]$env:SystemDrive
if ($systemDrive -notmatch '^[A-Za-z]:$') {
    [Console]::Error.WriteLine('SystemDrive did not identify a Windows system volume.')
    exit 2
}

try {
    $operatingSystems = @(Get-CimInstance -ClassName Win32_OperatingSystem)
    $processors = @(Get-CimInstance -ClassName Win32_Processor)
    $volumes = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType = 3')

    if ($operatingSystems.Count -ne 1) {
        throw "Expected one operating-system record; received $($operatingSystems.Count)."
    }
    $operatingSystem = $operatingSystems[0]
    if ($null -eq $operatingSystem.LastBootUpTime) {
        throw 'The operating-system record did not include LastBootUpTime.'
    }
    if ($processors.Count -eq 0) {
        throw 'No processor records were returned.'
    }
    if ($volumes.Count -eq 0) {
        throw 'No fixed-volume records were returned.'
    }

    $uptime = (Get-Date) - $operatingSystem.LastBootUpTime
    if ($uptime.TotalSeconds -lt 0) {
        throw 'LastBootUpTime is later than the current time.'
    }
    $uptimeDays = [math]::Floor($uptime.TotalDays)

    $cpuValues = @($processors | ForEach-Object {
        if ($null -eq $_.LoadPercentage) {
            throw 'A processor record did not include LoadPercentage.'
        }
        $loadPercentage = [double]$_.LoadPercentage
        if ([double]::IsNaN($loadPercentage) -or [double]::IsInfinity($loadPercentage) -or
            $loadPercentage -lt 0 -or $loadPercentage -gt 100) {
            throw "A processor record returned invalid LoadPercentage: $loadPercentage."
        }
        $loadPercentage
    })
    $cpuLoad = [math]::Round(($cpuValues | Measure-Object -Average).Average, 1)

    if ($null -eq $operatingSystem.TotalVisibleMemorySize -or $null -eq $operatingSystem.FreePhysicalMemory) {
        throw 'The operating-system record did not include memory capacity.'
    }
    $totalMemoryKiB = [double]$operatingSystem.TotalVisibleMemorySize
    $freeMemoryKiB = [double]$operatingSystem.FreePhysicalMemory
    if ([double]::IsNaN($totalMemoryKiB) -or [double]::IsInfinity($totalMemoryKiB) -or
        [double]::IsNaN($freeMemoryKiB) -or [double]::IsInfinity($freeMemoryKiB) -or
        $totalMemoryKiB -le 0 -or $freeMemoryKiB -lt 0 -or $freeMemoryKiB -gt $totalMemoryKiB) {
        throw 'The operating-system record returned invalid memory capacity.'
    }
    $freeMemoryPercent = [math]::Round(($freeMemoryKiB / $totalMemoryKiB) * 100, 1)

    $warning = $false
    $collectionIncomplete = $false
    $systemVolumeSeen = $false
    $systemVolumeValid = $false
    Write-Output "Computer: $env:COMPUTERNAME"
    Write-Output ('Uptime: {0}d {1:00}h {2:00}m' -f $uptimeDays, $uptime.Hours, $uptime.Minutes)
    Write-Output "CPU load: $cpuLoad%"
    Write-Output "Memory free: $freeMemoryPercent% (warning below $MemoryWarningPercent%)"

    if ($null -eq $freeMemoryPercent -or $freeMemoryPercent -lt $MemoryWarningPercent) {
        $warning = $true
    }

    foreach ($volume in $volumes | Sort-Object DeviceID) {
        if ([string]$volume.DeviceID -ieq $systemDrive) {
            $systemVolumeSeen = $true
        }
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
        if ([string]$volume.DeviceID -ieq $systemDrive) {
            $systemVolumeValid = $true
        }
        Write-Output "Volume $($volume.DeviceID) | $freePercent% free ($freeGiB GiB; warning below $DiskWarningPercent%)"
        if ($freePercent -lt $DiskWarningPercent) {
            $warning = $true
        }
    }

    if (-not $systemVolumeSeen) {
        Write-Output "System volume $systemDrive | capacity unavailable (not returned as a fixed volume)"
        $collectionIncomplete = $true
    }
    elseif (-not $systemVolumeValid) {
        $collectionIncomplete = $true
    }

    foreach ($name in $ServiceName) {
        try {
            $services = @(Get-Service -Name $name -ErrorAction Stop)
            if ($services.Count -eq 0) {
                Write-Output "Service ${name}: not found"
                $warning = $true
                continue
            }
            if ($services.Count -ne 1) {
                Write-Output "Service ${name}: unavailable (expected one service record; received $($services.Count))"
                $collectionIncomplete = $true
                continue
            }
            $service = $services[0]
            Write-Output "Service $($service.Name): $($service.Status)"
            if ($service.Status -ne 'Running') {
                $warning = $true
            }
        }
        catch {
            if ([string]$_.FullyQualifiedErrorId -like 'NoServiceFoundForGivenName*') {
                Write-Output "Service ${name}: not found"
                $warning = $true
            }
            else {
                Write-Output "Service ${name}: collection failed ($($_.Exception.Message))"
                $collectionIncomplete = $true
            }
        }
    }

    if ($collectionIncomplete) {
        Write-Output 'Status: incomplete'
        exit 2
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
