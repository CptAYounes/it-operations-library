# ARP and local communication

IPv4 Address Resolution Protocol maps an on-link IP address to a link-layer address. A host normally resolves either the destination itself (same subnet) or its gateway (remote subnet); it does not ARP for a server several routers away.

## Read the neighbour state

Windows:

```powershell
Get-NetNeighbor -AddressFamily IPv4
arp -a
```

Linux:

```bash
ip -4 neigh show
ip neigh get 192.0.2.20 dev eth0
```

Typical Linux states such as `REACHABLE`, `STALE`, `DELAY`, `PROBE`, `FAILED` and `INCOMPLETE` describe neighbour-cache state, not application health. `STALE` is normal until traffic requires reachability confirmation. Interface names vary; use the actual interface.

## Failure patterns

- **Incomplete/failed entry:** no ARP reply; check VLAN/link, target state, prefix, filtering/port security and duplicate addressing.
- **Unexpected MAC change:** could be failover, a moved VM, proxy ARP, a gateway change or a duplicate/spoofing concern. Correlate with approved changes and switch evidence.
- **One-way communication:** masks may make hosts disagree about what is local, or policy/return path may differ.
- **Intermittent conflict:** duplicate IP ownership can produce changing neighbour entries and unstable sessions.
- **No entry:** the host may not have attempted traffic, may use another route/interface, or the cache expired.

Gratuitous ARP can announce or update an address-to-MAC mapping and is used by legitimate failover. It is evidence to correlate, not proof of an attack.

## Safe diagnostic sequence

1. Confirm the source address/prefix and selected route.
2. Trigger one authorised connection or ping to create neighbour activity.
3. Inspect the neighbour entry on the correct interface.
4. Compare with approved inventory, gateway redundancy state or switch MAC table when available.
5. Capture ARP at the affected segment only with permission; MACs and topology can be sensitive.

Clearing a neighbour cache removes evidence and affects current connectivity. Do it only after recording the entry and when a stale mapping is a supported hypothesis. Disabling security controls or configuring a static ARP entry is not a general fix.

IPv6 uses Neighbor Discovery over ICMPv6 rather than ARP. Blocking required ICMPv6 messages can break address resolution and path behaviour; apply the IPv6-specific procedure instead of assuming the IPv4 mechanism.
