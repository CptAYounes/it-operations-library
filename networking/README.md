# Networking

These notes approach networking as a path to test rather than a list of protocols to memorise.

For a live fault, begin at the affected endpoint: link and interface state, address and prefix, selected route, name resolution, transport connection and finally the application request. Compare the return direction as well as the forward path. This sequence prevents a DNS symptom, filtered probe or silent intermediate hop from being treated as proof that “the network” is down.

- [TCP/IP practical reference](tcp-ip/practical-reference.md)
- [IPv4 addressing and subnetting](tcp-ip/ipv4-addressing-subnetting.md)
- [Default gateways and routing](routing/default-gateway-routing.md)
- [DNS troubleshooting](dns/dns-troubleshooting.md)
- [DHCP troubleshooting](dhcp/dhcp-troubleshooting.md)
- [ARP and local communication](tcp-ip/arp-local-communication.md)
- [Switching fundamentals](switching/switching-fundamentals.md)
- [VLAN fundamentals](vlans/vlan-fundamentals.md)
- [Firewall troubleshooting](firewalls/firewall-troubleshooting.md)
- [TCP and UDP ports](reference/tcp-udp-ports.md)
- [Layered connectivity troubleshooting](diagnostics/layered-connectivity-troubleshooting.md)
- [Windows and Linux network commands](reference/windows-linux-network-commands.md)

The command examples use documentation-only addresses. Test only systems you own or are authorised to assess, and review captures or output before sharing them. Network-device changes, firewall edits and packet capture can expose traffic or remove access, so follow the appropriate authority and evidence controls.
