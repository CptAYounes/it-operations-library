# VLAN fundamentals

A VLAN separates Layer 2 broadcast domains on shared switching hardware. Communication between VLANs requires a Layer 3 interface/router and whatever security policy applies there.

## Access, tagged and native traffic

- An **access/untagged** endpoint port normally places untagged frames into one configured VLAN.
- A **trunk/tagged** link carries selected VLANs using IEEE 802.1Q tags.
- Some links define a **native/untagged VLAN**. Both ends must agree; relying on implicit defaults makes mismatches harder to see.
- A VLAN ID has local administrative meaning. It does not by itself provide encryption, authentication or an Internet-wide segment.

Virtual switches, hypervisors and operating systems can apply or remove tags too. Document which component owns tagging so two layers do not both tag unexpectedly.

## Symptoms of a mismatch

- link is up but no DHCP offer arrives;
- the host receives an address from the wrong scope;
- local peers/gateway cannot be resolved with ARP;
- one VLAN works across a trunk while another does not;
- untagged management traffic works only from one side;
- frames appear double-tagged or on an unexpected virtual interface.

These symptoms still need evidence; DHCP, gateway or firewall faults can look similar.

## Verification path

1. Confirm intended endpoint VLAN and IP prefix from approved design/inventory.
2. Check endpoint/virtual-switch tagging and physical switch port mode.
3. On every trunk in the path, verify the VLAN is created, permitted and in a forwarding state.
4. Check native/untagged VLAN agreement at both ends.
5. Confirm MAC learning in the intended VLAN.
6. Confirm the VLAN's Layer 3 gateway/interface is up with the expected address.
7. Test local neighbour resolution, then gateway/routing, then the required application.

Do not make a trunk “allow all” or change an access VLAN simply to see whether traffic appears. That can expose networks, bypass segmentation intent or remove management. Record current configuration and rollback before an authorised change.

## Design cautions

Keep management access and recovery paths explicit. Use the same VLAN number consistently where that simplifies operations, but do not assume the number proves end-to-end continuity. Avoid spanning a Layer 2 domain farther than required; larger fault and broadcast domains increase impact. Inter-VLAN filtering belongs at the routing/security boundary and should be tested in both intended-allow and intended-deny directions.

After correction, verify endpoint lease/address, local peer and gateway reachability, inter-VLAN policy, redundancy and monitoring—not only a green switch port.
