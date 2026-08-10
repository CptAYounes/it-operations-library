# W08 — Windows network diagnostics

Work from the local adapter outward. This prevents a DNS symptom, blocked TCP port and missing default route from all being labelled “the network is down.”

**Applies to:** Windows 11 and Windows Server 2022/2025. GUI paths use Windows 11 or Server with Desktop Experience; PowerShell and built-in command-line checks also suit Server Core. Wireless, VPN, Hyper-V, teaming and advanced firewall features vary by edition/role/driver.

## Define the failure

Record:

- affected host/interface and whether local or remote;
- exact destination by name, address, protocol and port;
- first/last occurrence and recent change;
- whether other hosts or destinations work;
- expected DHCP/static, VLAN, VPN/proxy and DNS design;
- error text and application test.

Preserve the current configuration before renewing, resetting or assigning addresses.

```powershell
Get-NetAdapter | Sort-Object ifIndex |
    Select-Object ifIndex, Name, InterfaceDescription, Status, LinkSpeed, MacAddress
Get-NetIPConfiguration -Detailed
Get-DnsClientServerAddress
Get-NetRoute | Sort-Object InterfaceIndex, DestinationPrefix, RouteMetric
```

These are **read-only**. MAC addresses, DNS suffixes and IPs may be sensitive in public evidence.

## 1. Adapter and link

```powershell
Get-NetAdapter -Physical
Get-NetAdapterStatistics
```

Check expected adapter, status, link speed and increasing errors/discards. A negotiated speed below expectation can be cable, switch port, transceiver, power policy or driver configuration; it is not proof of one cause.

For Wi-Fi client details:

```text
netsh wlan show interfaces
netsh wlan show drivers
```

Server Core normally has no Wi-Fi role/use case unless deliberately installed and supported.

If the adapter is missing or non-OK, move to [driver/device validation](../configuration/driver-device-validation.md) before resetting the stack.

## 2. Addressing

```text
ipconfig /all
```

Confirm address family, prefix, gateway, DHCP server, DNS servers, lease and suffix. An IPv4 address in `169.254.0.0/16` is APIPA/link-local and commonly indicates no usable DHCP lease, but does not by itself prove the DHCP server is down; VLAN, link, relay, firewall and client state are alternatives.

Check duplicate/conflict messages and compare with the approved addressing plan. Do not assign a “spare-looking” static address.

## 3. Local stack and neighbour

```text
ping 127.0.0.1
ping ::1
ping <own-IP>
arp -a
```

PowerShell alternatives:

```powershell
Get-NetNeighbor
Test-Connection -ComputerName '127.0.0.1' -Count 2
```

`-ComputerName` works in Windows PowerShell 5.1 and is an alias for `-TargetName` in current PowerShell 7 releases.

Ping uses ICMP, which may be filtered. A failed ping is a data point, not proof that a host or application is down. An ARP/neighbor entry only proves local resolution occurred recently; stale/incomplete states need timing and packet-path context.

## 4. Gateway and route

```powershell
Get-NetRoute -AddressFamily IPv4 |
    Sort-Object DestinationPrefix, RouteMetric |
    Format-Table ifIndex, DestinationPrefix, NextHop, RouteMetric, State -AutoSize
```

Test the configured gateway, then a known reachable address beyond it. On multi-homed, VPN or Hyper-V hosts, inspect interface and route metrics rather than assuming the default route chosen is the intended one.

```text
tracert -d <destination-IP>
pathping -n <destination-IP>
```

`tracert` shows TTL-expiry responses, not every forwarding device; missing hops may simply suppress ICMP. `pathping` takes several minutes and apparent loss at one transit hop is only significant if loss continues to later hops.

## 5. DNS

First test reachability by address, then resolution by name.

```powershell
Resolve-DnsName 'example.net'
Resolve-DnsName 'example.net' -Server '<expected-DNS-server>'
```

Also compare:

```text
nslookup example.net
```

`Resolve-DnsName` uses Windows DNS client behaviour and offers structured records; `nslookup` is useful for direct server queries but does not reproduce every application/client-cache behaviour. Check the requested record type, suffix search, split DNS/VPN context and whether IPv4/IPv6 answers are reachable.

Read the cache without changing it:

```powershell
Get-DnsClientCache
```

`Clear-DnsClientCache` or `ipconfig /flushdns` is a **change** to local cache and can remove evidence. Use it only after recording the suspect entry and expect the next query to return to DNS.

## 6. TCP/UDP and application path

Test the actual destination and port:

```powershell
Test-NetConnection -ComputerName 'example.net' -Port 443 -InformationLevel Detailed
```

A successful TCP test proves that a connection to that address/port completed at that moment. It does not prove TLS, authentication or application response. Follow with the application's supported health/transaction test.

Inspect local listeners/connections:

```powershell
Get-NetTCPConnection | Sort-Object State, LocalPort
Get-NetUDPEndpoint | Sort-Object LocalPort
```

Or from Command Prompt:

```text
netstat -abno
```

`netstat -b` normally requires elevation and may be slow. PID ownership can change between capture and lookup.

## 7. Firewall and profile

```powershell
Get-NetConnectionProfile
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
Get-NetFirewallRule -PolicyStore ActiveStore -Enabled True |
    Select-Object DisplayName, Direction, Action, Profile
```

A Public profile applied to a trusted internal connection can change allowed inbound traffic, but changing it without confirming network identity/security is not a safe shortcut.

Do not disable Windows Firewall to “test.” Instead, inspect the active profile, effective rules, application/port and firewall logs. Add a narrowly scoped temporary rule only with approval, source/destination/port constraints, an expiry/rollback and a test proving whether it mattered.

## 8. DHCP and controlled changes

On a DHCP client, after preserving `ipconfig /all` and confirming disruption is acceptable:

```text
ipconfig /release <adapter-name>
ipconfig /renew <adapter-name>
```

These are **changes** and can break a remote session. Adapter-name syntax and multi-interface behaviour require care; run locally/out-of-band. Repeated renewals do not repair a wrong VLAN, exhausted scope or blocked relay.

For a static client, review effective state with `Get-NetIPConfiguration` and the approved plan. `New-NetIPAddress`, `Set-DnsClientServerAddress`, disabling an adapter and `Restart-NetAdapter` are disruptive configuration changes; do not include guessed values in a generic repair sequence.

## Reset boundary

These are not first-line diagnostics:

```text
netsh winsock reset
netsh int ip reset
```

They are **changes**, can remove custom provider/stack configuration, commonly require restart and may affect security/VPN software. Windows 11 **Settings > Network & internet > Advanced network settings > Network reset** is broader and can remove/reinstall adapters and reset related settings. Record VPN, static addressing, virtual switches and recovery access before considering any reset.

## Virtual and complex hosts

For Hyper-V, containers, VPN, teaming or virtual appliances, map physical NIC, virtual switch, virtual adapter, VLAN and routes. Do not disable a physical NIC that carries management or all vSwitch traffic. Packet capture (`pktmon`, `netsh trace`, Wireshark) can provide evidence but may collect credentials or personal data; define filter, duration, storage and access first.

## Escalation and recovery proof

Escalate when the fault lies beyond the host, address/VLAN ownership is uncertain, packet capture contains sensitive data, a remote change risks lockout, firewall/policy has another owner, or repeated resets only provide temporary relief.

Validate at the failed layer and above it:

- expected adapter/link and address remain stable;
- intended route and DNS server answer correctly;
- required TCP/UDP/application test succeeds;
- another representative destination still works;
- remote management remains available;
- events/counters show no repeated disconnect/error;
- temporary rules or captures are removed/closed;
- change and evidence are recorded.
