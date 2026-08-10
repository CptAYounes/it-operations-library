#requires -Version 5.1
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
    [ValidateNotNullOrEmpty()]
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
    if ($serviceName -notmatch '^[A-Za-z0-9_.-]+$') {
        Write-Output "Service ${serviceName}: invalid name"
        $result = 2
        continue
    }

    try {
        $service = Get-Service -Name $serviceName -ErrorAction Stop
        $escapedName = $service.Name.Replace("'", "''")
        $serviceConfiguration = Get-CimInstance -ClassName Win32_Service -Filter "Name = '$escapedName'"
        $startMode = if ($null -ne $serviceConfiguration) { $serviceConfiguration.StartMode } else { 'unknown' }
        $state = if ($service.Status -eq 'Running') { 'healthy' } else { 'warning' }

        Write-Output "Service: $($service.Name) | display: $($service.DisplayName) | status: $($service.Status) | start: $startMode | result: $state"
        if ($service.Status -ne 'Running' -and $result -lt 1) {
            $result = 1
        }
    }
    catch {
        Write-Output "Service ${serviceName}: unavailable ($($_.Exception.Message))"
        if ($result -lt 1) {
            $result = 1
        }
    }
}

exit $result
