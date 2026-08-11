#requires -Version 7.4
<#
.SYNOPSIS
Reports the current state and configured start mode of Windows services.

.EXAMPLE
.\Get-ServiceHealth.ps1 -Name W32Time,Dnscache

.NOTES
This script does not start, stop or reconfigure services.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [AllowEmptyString()]
    [string[]]$Name
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    [Console]::Error.WriteLine('Get-ServiceHealth.ps1 requires Windows.')
    exit 2
}

$result = 0

foreach ($serviceName in $Name) {
    if ([string]::IsNullOrWhiteSpace($serviceName) -or $serviceName.IndexOfAny([char[]]'*?[]') -ge 0) {
        Write-Output "Service ${serviceName}: invalid literal name"
        $result = 2
        continue
    }

    try {
        $services = @(Get-Service -Name $serviceName -ErrorAction Stop)
        if ($services.Count -eq 0) {
            Write-Output "Service ${serviceName}: not found"
            if ($result -eq 0) {
                $result = 1
            }
            continue
        }
        if ($services.Count -ne 1) {
            throw "Expected one service record; received $($services.Count)."
        }
        $service = $services[0]
    }
    catch {
        if ([string]$_.FullyQualifiedErrorId -like 'NoServiceFoundForGivenName*') {
            Write-Output "Service ${serviceName}: not found"
            if ($result -eq 0) {
                $result = 1
            }
        }
        else {
            Write-Output "Service ${serviceName}: collection failed ($($_.Exception.Message))"
            $result = 2
        }
        continue
    }

    try {
        # WQL string literals use backslash escapes rather than SQL quote
        # doubling. Escape backslashes first so the escapes added for quotes
        # are not escaped a second time.
        $escapedName = $service.Name.Replace('\', '\\')
        $escapedName = $escapedName.Replace("'", "\'")
        $escapedName = $escapedName.Replace('"', '\"')
        $serviceConfigurations = @(Get-CimInstance -ClassName Win32_Service -Filter "Name = '$escapedName'")
        if ($serviceConfigurations.Count -ne 1 -or [string]::IsNullOrWhiteSpace([string]$serviceConfigurations[0].StartMode)) {
            throw "Expected one complete service-configuration record; received $($serviceConfigurations.Count)."
        }
        $startMode = $serviceConfigurations[0].StartMode
        $state = if ($service.Status -eq 'Running') { 'healthy' } else { 'warning' }

        Write-Output "Service: $($service.Name) | display: $($service.DisplayName) | status: $($service.Status) | start: $startMode | result: $state"
        if ($service.Status -ne 'Running' -and $result -lt 1) {
            $result = 1
        }
    }
    catch {
        Write-Output "Service $($service.Name): configuration unavailable ($($_.Exception.Message))"
        $result = 2
    }
}

exit $result
