# Switching fundamentals

An Ethernet switch forwards frames within a Layer 2 broadcast domain. It learns source MAC addresses on ingress ports and uses that table to forward known unicast traffic. Unknown unicast and broadcast traffic is flooded within the VLAN, subject to policy.

## What the forwarding table tells you

A MAC table links a learned address to a port and VLAN for an ageing period. Interpret it with time and topology:

- no entry may mean no recent traffic, wrong VLAN, down link or learning disabled;
- an address moving rapidly between ports can indicate a loop, duplicated identity, legitimate mobility/failover or a badly connected device;
- the same MAC in different VLANs can be valid;
- a table entry confirms learned frames, not end-to-end IP or application health.

Commands differ by switch vendor. Use read-only `show`/display commands from the approved management path and redact serials, management addresses and full MACs before public evidence.

## Port evidence

Check both ends where possible:

- administrative and operational state;
- access VLAN or permitted/tagged VLANs;
- speed, duplex and auto-negotiation;
- error, discard and pause counters as a rate;
- link transitions and time of last change;
- spanning-tree state;
- port-security, authentication or storm-control events;
- transceiver/cable diagnostics within vendor limits.

A rising CRC/FCS error count can point to the physical link, transceiver, cable or interference. A static non-zero counter from months ago is weaker evidence. Duplex mismatch can produce poor throughput and errors even while link remains up; modern Ethernet normally uses auto-negotiation at both ends.

## Loops and spanning tree

Redundant Layer 2 paths can loop broadcasts and unknown unicast indefinitely. Spanning Tree Protocol blocks selected paths to maintain a loop-free topology and reconverges after change. Do not disable spanning tree, clear tables repeatedly or move redundant links as a quick fix: a loop can affect an entire broadcast domain.

Topology change, MAC flapping, high broadcast rate and widespread intermittent access are reasons to escalate to the network owner with timestamps and affected VLAN/ports.

## Diagnostic order

1. Confirm the endpoint's physical/interface state.
2. Confirm switch port state and expected VLAN.
3. Compare fresh counter changes during a controlled test.
4. Verify MAC learning in the correct VLAN and expected direction.
5. Check spanning-tree and security-policy events.
6. Move or replace a cable/transceiver only through an authorised test that preserves redundancy and records original placement.
7. Validate link, address/ARP, required service and monitoring after recovery.

Continue with [VLAN fundamentals](../vlans/vlan-fundamentals.md) when the link is up but the endpoint appears in the wrong broadcast domain.
