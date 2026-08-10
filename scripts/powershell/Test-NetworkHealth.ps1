#requires -Version 7.0
<#
.SYNOPSIS
Performs DNS resolution plus bounded ICMP and optional TCP checks.

.EXAMPLE
.\Test-NetworkHealth.ps1 -Target example.org -Port 443 -TimeoutSeconds 3

.NOTES
The script sends no application payload. A TCP success validates only the
connection handshake, not TLS or application health.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Target,

    [ValidateRange(1, 65535)]
    [int]$Port,

    [ValidateRange(1, 30)]
    [int]$TimeoutSeconds = 3,

    [switch]$SkipPing
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($SkipPing -and -not $PSBoundParameters.ContainsKey('Port')) {
    [Console]::Error.WriteLine('Use a port when -SkipPing is specified; otherwise no reachability check remains.')
    exit 2
}

try {
    $addresses = @([System.Net.Dns]::GetHostAddresses($Target))
    if ($addresses.Count -eq 0) {
        [Console]::Error.WriteLine("No address was returned for $Target.")
        exit 1
    }

    $address = $addresses |
        Sort-Object { if ($_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork) { 0 } else { 1 } } |
        Select-Object -First 1

    Write-Output "Target: $Target"
    Write-Output "Resolved address: $($address.IPAddressToString)"

    $pingSucceeded = $false
    if (-not $SkipPing) {
        $ping = [System.Net.NetworkInformation.Ping]::new()
        try {
            $reply = $ping.Send($address, $TimeoutSeconds * 1000)
            $pingSucceeded = $reply.Status -eq [System.Net.NetworkInformation.IPStatus]::Success
            if ($pingSucceeded) {
                Write-Output "ICMP: reply in $($reply.RoundtripTime) ms"
            }
            else {
                Write-Output "ICMP: $($reply.Status)"
            }
        }
        finally {
            $ping.Dispose()
        }
    }

    if ($PSBoundParameters.ContainsKey('Port')) {
        $client = [System.Net.Sockets.TcpClient]::new($address.AddressFamily)
        try {
            $connectTask = $client.ConnectAsync($address, $Port)
            if (-not $connectTask.Wait($TimeoutSeconds * 1000)) {
                Write-Output "TCP ${Port}: timed out after ${TimeoutSeconds}s"
                Write-Output 'Status: warning'
                exit 1
            }
            [void]$connectTask.GetAwaiter().GetResult()
            Write-Output "TCP ${Port}: connection succeeded"
            if (-not $pingSucceeded -and -not $SkipPing) {
                Write-Output 'Note: ICMP failed, but the requested TCP service was reachable.'
            }
            Write-Output 'Status: reachable'
            exit 0
        }
        catch {
            Write-Output "TCP ${Port}: failed ($($_.Exception.GetBaseException().Message))"
            Write-Output 'Status: warning'
            exit 1
        }
        finally {
            $client.Dispose()
        }
    }

    if ($pingSucceeded) {
        Write-Output 'Status: reachable'
        exit 0
    }

    Write-Output 'Status: warning (ICMP may be filtered)'
    exit 1
}
catch {
    [Console]::Error.WriteLine("Network check failed: $($_.Exception.GetBaseException().Message)")
    exit 1
}
