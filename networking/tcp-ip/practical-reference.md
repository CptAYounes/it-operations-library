# TCP/IP practical reference

For fault finding, describe a connection as a path and a tuple:

```text
source address : source port -> destination address : destination port / protocol
```

Add the interface/VLAN, route, time and application action. “The network is down” is too broad to test.

## What each layer contributes

| Area | Practical concern | Evidence |
|---|---|---|
| Link | Interface state, frame errors, VLAN, MTU | NIC/switch state and counters |
| Internet | Source/destination IP, subnet, gateway, route, fragmentation | Address and routing tables, trace |
| Transport | TCP handshake/state or UDP request/reply, port and filtering | Socket table, bounded connection test, capture if authorised |
| Application | DNS, TLS, authentication, protocol response, dependency | Client error, application logs, safe transaction |

Encapsulation means the application payload is carried by transport, then IP, then the local link. Each router replaces the link-layer frame for the next network while forwarding the IP packet (subject to fields such as TTL/hop limit and policy). This is why a destination MAC address identifies the local next hop, not a remote server across routers.

## TCP observations

TCP establishes state before carrying application data. A typical opening is SYN, SYN-ACK, ACK. Diagnostic combinations:

- **timeout:** packets or replies may be filtered, misrouted or lost; it does not identify where;
- **connection refused / RST:** the destination path often worked, but no listener or a policy actively rejected the port;
- **connected, then application timeout:** transport succeeded; investigate TLS, protocol, dependency or server work;
- **many retransmissions:** loss, congestion, MTU/path or endpoint pressure needs correlation;
- **many `TIME_WAIT` sockets:** may be normal connection turnover; assess rate and port/resource impact.

Windows `Get-NetTCPConnection` and Linux `ss -tanp` show local socket state. Process details may require elevated access.

## UDP observations

UDP has no connection handshake or delivery acknowledgement. A client can send successfully even when the service or path is unavailable. Validate a protocol response (for example, a DNS answer) rather than relying on an “open” UDP socket test. ICMP unreachable messages can help, but filters often suppress them.

## MTU and fragmentation

A smaller MTU somewhere on the path can allow short probes while larger application transfers stall, particularly when Path MTU Discovery signals are blocked. Compare packet size, affected protocols and both directions before changing interface MTU. An arbitrary reduction hides the path issue and can reduce efficiency.

## A useful test order

1. local interface/link;
2. source address and subnet;
3. route/next hop;
4. name resolution if a name is used;
5. required transport port;
6. application handshake/transaction;
7. reverse path and policy when results are asymmetric.

Continue with the [layered workflow](../diagnostics/layered-connectivity-troubleshooting.md) and use the [port reference](../reference/tcp-udp-ports.md) only to identify expected traffic, not to infer exposure.
