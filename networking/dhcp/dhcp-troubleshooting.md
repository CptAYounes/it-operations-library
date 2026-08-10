# DHCP troubleshooting

DHCP supplies more than an address. A lease can also carry prefix/mask, gateway, DNS servers, search domain, routes and other vendor/site options. Verify the option that is wrong rather than treating every configuration issue as “no DHCP”.

## DHCPv4 exchange

A new client typically moves through Discover, Offer, Request and Acknowledge (DORA). Broadcast is used before normal IPv4 configuration; a DHCP relay forwards requests between a client subnet and a remote server. Renewal later commonly uses unicast before falling back to broader rebinding.

## Start at the client

Windows:

```powershell
Get-NetIPConfiguration
Get-NetIPInterface -AddressFamily IPv4
ipconfig /all
```

Linux (tool depends on network manager):

```bash
ip -4 address
ip -4 route
resolvectl status
nmcli device show                 # NetworkManager
networkctl status                 # systemd-networkd
journalctl -u NetworkManager --since '-30 minutes'
```

Record interface identity, lease source, address/prefix, gateway, DNS, lease times and any `169.254.0.0/16` link-local address. Confirm the client is on the intended physical/virtual link and VLAN before focusing on the server.

## Narrow the exchange

1. Check link and interface administrative state.
2. Determine whether one client, one VLAN/site or all scopes are affected.
3. Check for an existing valid lease versus a new allocation failure.
4. Confirm the scope has available addresses and the correct options.
5. Verify relay/helper destination and path from that VLAN.
6. Review server/relay logs for request, policy, conflict, reservation or exhaustion evidence.
7. If packet capture is authorised, capture only the affected test exchange at the correct boundary and protect client identifiers in the output.

A client can receive an address but fail because the gateway, DNS or class-specific option is wrong. Conversely, a server may never see the request because of VLAN, port-security, relay or local client issues.

## Safe recovery

Releasing a working lease can remove remote access. Do not use `ipconfig /release`, delete lease databases, restart DHCP services or alter scopes as generic tests. Prefer an authorised renewal on a locally accessible test client after evidence collection. Correct one identified scope/relay/client setting through change control and retain its previous state.

## Validate

Use a controlled client to obtain a lease, then verify address uniqueness, prefix, gateway, resolver and required routed/application access. Check server allocation and renewal, not only initial assignment. Monitor for scope pressure and duplicate/conflict events. Escalate shared-scope impact, exhaustion, suspected rogue DHCP, relay/network-device changes or ownership beyond authority.
