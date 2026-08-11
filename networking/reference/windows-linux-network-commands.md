# Windows and Linux network commands

The two platforms expose similar questions through different tools. Run only the command needed for the question; broad captures and full configuration output can contain sensitive names, addresses and topology.

| Question | Windows PowerShell / built-in | Linux (iproute2 and common tools) |
|---|---|---|
| Interface state | `Get-NetAdapter` | `ip -brief link` |
| Addresses and gateway | `Get-NetIPConfiguration` | `ip address`; `ip route` |
| Address details | `Get-NetIPAddress` | `ip -details address` |
| Selected route | `Test-NetConnection target -InformationLevel Detailed` | `ip route get 192.0.2.20` |
| Routing table | `Get-NetRoute` | `ip route`; `ip rule` |
| Neighbour/ARP cache | `Get-NetNeighbor`; `arp -a` | `ip neigh` |
| DNS client settings | `Get-DnsClientServerAddress` | `resolvectl status` or resolver-manager configuration |
| DNS query | `Resolve-DnsName host.example` | `getent ahosts host.example`; `resolvectl query`; `dig` when installed |
| ICMP test | `Test-Connection host.example -Count 2` | `ping -c 2 host.example` |
| Path trace | `tracert -d 192.0.2.20` | `tracepath -n 192.0.2.20` or `traceroute` when installed |
| TCP port test | `Test-NetConnection host.example -Port 443` | `python3 scripts/python/port_check.py host.example 443` from the repository root |
| Listening TCP sockets | `Get-NetTCPConnection -State Listen` | `ss -ltnp` |
| Listening UDP sockets | `Get-NetUDPEndpoint` | `ss -lunp` |
| Connection/socket state | `Get-NetTCPConnection` | `ss -tanp` |
| Interface counters | `Get-NetAdapterStatistics` | `ip -s link` |
| Firewall overview | `Get-NetFirewallProfile`; `Get-NetFirewallRule` | owning manager, or privileged `nft list ruleset` |
| DHCP details | `ipconfig /all` | `nmcli device show`, `networkctl status`, or client logs |

## Notes that prevent false comparisons

- Linux resolver state depends on NetworkManager, systemd-resolved, systemd-networkd or another manager; `/etc/resolv.conf` may be a generated symlink.
- `Test-NetConnection` combines several checks. Read the detailed fields instead of treating its summary as a root cause.
- `ss -p` and some Windows process/owner details may require elevated access.
- `tracert`, `tracepath` and `traceroute` use different probes/options. A silent intermediate hop does not prove it failed to forward application traffic.
- `nc` implementations and timeout flags differ. The repository's Python [port checker](../../scripts/python/port_check.py) provides a consistent bounded TCP check where Python is available.
- A direct `dig` result can differ from an application's lookup because `getent`/Windows name resolution may consult hosts files, suffix rules or other name services.

For a sequence rather than a lookup table, use the [layered connectivity workflow](../diagnostics/layered-connectivity-troubleshooting.md).
