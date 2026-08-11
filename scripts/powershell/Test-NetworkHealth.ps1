#requires -Version 7.4
<#
.SYNOPSIS
Performs DNS resolution plus bounded ICMP and optional TCP checks.

.DESCRIPTION
Uses one overall timeout budget for DNS and all address attempts. Each attempt
is capped to a fair share of the remaining budget so a silent first address
cannot consume every later address's opportunity. ICMP failure does not
override a successful TCP result.

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

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

function Get-RemainingMillisecond {
    $remaining = ($TimeoutSeconds * 1000) - $stopwatch.ElapsedMilliseconds
    if ($remaining -le 0) {
        return 0
    }
    return [int][math]::Floor($remaining)
}

function Get-AddressAttemptMillisecond {
    param(
        [ValidateRange(1, [int]::MaxValue)]
        [int]$RemainingAddressCount
    )

    $remaining = Get-RemainingMillisecond
    if ($remaining -le 0) {
        return 0
    }
    return [int][math]::Max(1, [math]::Floor($remaining / $RemainingAddressCount))
}

try {
    $resolveTask = [System.Net.Dns]::GetHostAddressesAsync($Target)
    $remainingMilliseconds = Get-RemainingMillisecond
    if ($remainingMilliseconds -le 0 -or -not $resolveTask.Wait($remainingMilliseconds)) {
        Write-Output "Resolution: timed out after ${TimeoutSeconds}s"
        Write-Output 'Status: warning'
        exit 1
    }
    $addresses = @($resolveTask.GetAwaiter().GetResult())
    if ($addresses.Count -eq 0) {
        [Console]::Error.WriteLine("No address was returned for $Target.")
        exit 1
    }

    $addresses = @($addresses |
        Sort-Object { if ($_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork) { 0 } else { 1 } } |
        Select-Object -Unique)

    Write-Output "Target: $Target"
    foreach ($address in $addresses) {
        Write-Output "Resolved address: $($address.IPAddressToString)"
    }

    if ($PSBoundParameters.ContainsKey('Port')) {
        $successfulAddress = $null
        for ($index = 0; $index -lt $addresses.Count; $index++) {
            $address = $addresses[$index]
            $attemptMilliseconds = Get-AddressAttemptMillisecond -RemainingAddressCount ($addresses.Count - $index)
            if ($attemptMilliseconds -le 0) {
                Write-Output "TCP ${Port}: overall timeout exhausted"
                break
            }

            $client = [System.Net.Sockets.TcpClient]::new($address.AddressFamily)
            try {
                $connectTask = $client.ConnectAsync($address, $Port)
                if (-not $connectTask.Wait($attemptMilliseconds)) {
                    Write-Output "TCP $($address.IPAddressToString):${Port}: timed out"
                    continue
                }
                [void]$connectTask.GetAwaiter().GetResult()
                Write-Output "TCP $($address.IPAddressToString):${Port}: connection succeeded"
                $successfulAddress = $address
                break
            }
            catch {
                Write-Output "TCP $($address.IPAddressToString):${Port}: failed ($($_.Exception.GetBaseException().Message))"
            }
            finally {
                $client.Dispose()
            }
        }

        if ($null -eq $successfulAddress) {
            Write-Output "Status: warning (no resolved address accepted TCP ${Port} within ${TimeoutSeconds}s)"
            exit 1
        }

        if (-not $SkipPing) {
            $remainingMilliseconds = Get-RemainingMillisecond
            if ($remainingMilliseconds -le 0) {
                Write-Output 'ICMP: skipped (overall timeout exhausted after TCP success)'
            }
            else {
                $ping = [System.Net.NetworkInformation.Ping]::new()
                try {
                    $reply = $ping.Send($successfulAddress, $remainingMilliseconds)
                    if ($reply.Status -eq [System.Net.NetworkInformation.IPStatus]::Success) {
                        Write-Output "ICMP $($successfulAddress.IPAddressToString): reply in $($reply.RoundtripTime) ms"
                    }
                    else {
                        Write-Output "ICMP $($successfulAddress.IPAddressToString): $($reply.Status)"
                        Write-Output 'Note: ICMP failed, but the requested TCP service was reachable.'
                    }
                }
                catch {
                    Write-Output "ICMP $($successfulAddress.IPAddressToString): failed ($($_.Exception.GetBaseException().Message))"
                    Write-Output 'Note: ICMP failed, but the requested TCP service was reachable.'
                }
                finally {
                    $ping.Dispose()
                }
            }
        }

        Write-Output 'Status: reachable'
        exit 0
    }

    for ($index = 0; $index -lt $addresses.Count; $index++) {
        $address = $addresses[$index]
        $attemptMilliseconds = Get-AddressAttemptMillisecond -RemainingAddressCount ($addresses.Count - $index)
        if ($attemptMilliseconds -le 0) {
            Write-Output 'ICMP: overall timeout exhausted'
            break
        }

        $ping = [System.Net.NetworkInformation.Ping]::new()
        try {
            $reply = $ping.Send($address, $attemptMilliseconds)
            if ($reply.Status -eq [System.Net.NetworkInformation.IPStatus]::Success) {
                Write-Output "ICMP $($address.IPAddressToString): reply in $($reply.RoundtripTime) ms"
                Write-Output 'Status: reachable'
                exit 0
            }
            Write-Output "ICMP $($address.IPAddressToString): $($reply.Status)"
        }
        catch {
            Write-Output "ICMP $($address.IPAddressToString): failed ($($_.Exception.GetBaseException().Message))"
        }
        finally {
            $ping.Dispose()
        }
    }

    Write-Output "Status: warning (no resolved address answered ICMP within ${TimeoutSeconds}s; ICMP may be filtered)"
    exit 1
}
catch {
    [Console]::Error.WriteLine("Network check failed: $($_.Exception.GetBaseException().Message)")
    exit 1
}
