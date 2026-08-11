# Firewall troubleshooting

A firewall decision can occur on the endpoint, a network device, a virtual/cloud policy layer or an application proxy. First define the exact traffic: source, destination, protocol, port, direction, interface/zone, time and expected policy.

## Distinguish the failure stage

- DNS failure occurs before an address-based firewall test.
- No route or neighbour resolution can prevent traffic reaching a filter.
- TCP timeout is consistent with silent filtering but also with loss, return-route or host failure.
- TCP refusal/reset often means the path reached a host/policy that actively rejected it.
- TCP connect followed by protocol failure shifts attention to TLS, proxy, authentication or application behaviour.
- Stateful devices need the return flow to match existing state; asymmetric routing can break that even when forward rules look correct.

## Read-only host checks

Windows:

```powershell
Get-NetConnectionProfile
Get-NetFirewallProfile -PolicyStore ActiveStore
Get-NetFirewallRule -PolicyStore ActiveStore -Enabled True |
    Select-Object DisplayName, Direction, Action, Profile
Get-NetTCPConnection -State Listen
```

`ActiveStore` shows the effective policy after local and Group Policy inputs are merged. Rules have separate port, address, application, service and interface filters; the rule summary is not the whole effective match. For one known rule, inspect its associated filters rather than inferring scope from its display name:

```powershell
$rule = Get-NetFirewallRule -PolicyStore ActiveStore -DisplayName 'Example HTTPS rule'
$rule | Select-Object DisplayName, Enabled, Direction, Action, Profile
$rule | Get-NetFirewallPortFilter |
    Select-Object Protocol, LocalPort, RemotePort
$rule | Get-NetFirewallAddressFilter |
    Select-Object LocalAddress, RemoteAddress
$rule | Get-NetFirewallApplicationFilter |
    Select-Object Program, Package
$rule | Get-NetFirewallServiceFilter |
    Select-Object Service
$rule | Get-NetFirewallInterfaceTypeFilter |
    Select-Object InterfaceType
```

Compare protocol, local port and source/destination addresses with the recorded traffic tuple. Substitute an existing approved rule name; these commands inspect it and do not create a rule.

Linux:

```bash
ss -lntup
sudo nft list ruleset
```

Ruleset access normally requires privilege and can reveal topology/policy. Some systems use a manager such as firewalld or UFW; inspect the owning layer rather than editing generated `nftables` rules directly.

## Work through policy

1. Confirm the service is listening on the intended address/port.
2. Test from the affected source and a known-good source if authorised.
3. Identify every enforcement point and the packet identity it sees before/after NAT.
4. Check rule order, zone/profile/interface, address family, direction and object membership.
5. Look for deny/drop logs at the exact time, accounting for sampling/rate limits.
6. Verify return routing and state/session tables through the device owner.
7. Compare the desired communication with the approved policy, not merely with an existing rule name.

## Change safely

Do not disable the firewall or create a broad `any/any` rule as a test. That weakens control and still may not identify the original mismatch. Use a narrow, time-bounded, logged rule only with authority, expected source/destination/service and rollback. Protect the final management path.

Validate both intended access and a representative denied path, application behaviour, logs and monitoring after correction. Escalate when policy ownership, security implications, shared/asymmetric paths, NAT or privileged changes exceed authority.
