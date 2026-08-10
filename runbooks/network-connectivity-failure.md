# Network connectivity failure

This runbook is for a connection that fails between a known source and destination. Work upward from the local link and keep DNS, transport and application results separate.

## Capture the tuple

Before testing, record:

- source host/network and destination name/address;
- protocol and port or application action;
- start time, exact error and scope;
- whether the path previously worked and what changed;
- expected route, security boundary and service owner.

## Layered checks

1. **Physical/link:** cable, radio/virtual NIC, switch/host link state. Do not reseat shared or redundant links without authority.
2. **Interface:** administrative and operational state, error counters, negotiated speed where relevant.
3. **Addressing:** expected address, prefix, DHCP/static source and duplicate-address signs.
4. **Local subnet:** neighbour resolution and another known peer; a failed ARP/ND exchange is local evidence.
5. **Gateway and route:** selected next hop and policy route from the affected source.
6. **DNS:** expected record and resolver response; compare with the destination address.
7. **Path:** bounded trace from both sides when possible. A silent hop may simply filter probes.
8. **Transport:** attempt the required TCP/UDP service, not a random familiar port.
9. **Application:** validate protocol handshake and a safe user-path request.

Useful starting commands are collected in the [layer-by-layer workflow](../networking/diagnostics/layered-connectivity-troubleshooting.md) and [Windows/Linux command comparison](../networking/reference/windows-linux-network-commands.md).

## Interpret combinations

- Link down plus no address points local before it points to DNS or firewall.
- Ping works but TCP fails narrows toward listener, transport filtering or policy.
- TCP connects but the application fails moves attention to TLS, authentication, dependency or application state.
- One source fails while peers work suggests source configuration, path policy or local filtering.
- A whole subnet failing suggests a shared link, gateway, route, DHCP or policy boundary.

## Corrective action

Make one evidence-backed, reversible change at the identified owner boundary. Record current interface, route and filter state before editing. Do not reset network stacks, disable firewalls, move switch ports or add routes as general tests; each can remove management access or broaden exposure.

## Escalate and validate

Escalate for shared impact, redundancy loss, physical/network-device ownership, security policy, unknown route/filter changes, asymmetric paths, or any action outside authority. After recovery, repeat the original application action from the affected source, then confirm transport, monitoring, errors/drops and redundant paths where applicable. Record the failing layer, before/after evidence, change and residual risk.
