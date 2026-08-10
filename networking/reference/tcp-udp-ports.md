# TCP and UDP ports

A port number identifies a transport endpoint on a host. The same number can be used by TCP and UDP for different behaviours. An assigned or common port does not prove that a service is installed, listening, permitted or safe to expose.

| Port / transport | Common use | Diagnostic note |
|---|---|---|
| 22/TCP | SSH | Confirm listener and authorised source; not every SSH service uses 22 |
| 53/UDP and TCP | DNS | Normal queries often use UDP; TCP is also required for some responses and operations |
| 67-68/UDP | DHCPv4 server/client | Initial traffic is local broadcast unless relayed |
| 80/TCP | HTTP | Redirects/proxies may lead elsewhere; TCP success is not an HTTP health check |
| 123/UDP | NTP | Time service policy and implementation vary |
| 161-162/UDP | SNMP queries/traps | Versions/security differ; avoid exposing legacy community credentials |
| 389/TCP and UDP | LDAP / CLDAP uses | Authentication and protection depend on operation; do not assume encryption |
| 443/TCP | HTTPS | Validate TLS name/certificate and application response after TCP |
| 443/UDP | HTTP/3 over QUIC | Not interchangeable with TCP 443; fallback may hide UDP filtering |
| 445/TCP | SMB | Commonly restricted across network boundaries |
| 514/UDP or TCP | Syslog transport conventions | TLS commonly uses a different configured transport/port; verify implementation |
| 636/TCP | LDAP over TLS (LDAPS) | Certificate validation remains required |
| 3389/TCP and UDP | RDP | TCP establishes core connectivity; modern RDP may also use UDP |

This is a troubleshooting shortlist, not a firewall policy or complete IANA registry. Applications can use dynamic, negotiated or custom ports.

## Listener, reachability and application health

Check each separately:

1. **Listener:** local OS shows a process bound to the expected address and port.
2. **Reachability:** a client completes the TCP handshake or receives the expected UDP reply.
3. **Protocol:** TLS/banner/request behaves as expected.
4. **Application:** a safe transaction completes through dependencies and authentication.

Windows:

```powershell
Get-NetTCPConnection -State Listen
Test-NetConnection host.example -Port 443
```

Linux:

```bash
ss -lntup
python3 scripts/python/port_check.py host.example 443
```

The script path assumes the command is run from the repository root.

Process information may require elevated access. A TCP scanner result of “open” reaches only step two, while UDP status is often ambiguous without a protocol-aware request.

## Ephemeral source ports

Clients normally use a temporary local source port selected by the OS. Return traffic must be permitted as part of the state or appropriate policy. Do not write a rule assuming the client also originates from the server's well-known port. NAT may further change the addresses/ports seen at different enforcement points.

Probe only systems you own or are authorised to test, use bounded connection attempts, and retain the source/destination/transport tuple in evidence.
