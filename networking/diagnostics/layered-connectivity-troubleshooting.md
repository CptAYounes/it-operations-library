# Layered connectivity troubleshooting

Use this when an application cannot communicate between a known source and destination. Record the exact source, destination name/address, protocol/port, timestamp, error and expected path before testing.

## 1. Physical or virtual link

- Is the correct interface administratively and operationally up?
- Did link state or error counters change at the failure time?
- For a VM/container, is the virtual NIC attached to the intended network?
- Is physical work safe and authorised?

```powershell
Get-NetAdapter
Get-NetAdapterStatistics
```

```bash
ip -brief link
ip -s link
```

## 2. Address and subnet

Confirm address, prefix/mask, source (DHCP/static), gateway and expected VLAN. A wrong mask can make one host ARP for a destination that the other tries to route.

```powershell
Get-NetIPConfiguration
Get-NetIPAddress
```

```bash
ip address
ip route
```

## 3. Local neighbour and gateway

For an on-link target or gateway, inspect ARP/ND state. Test the gateway as a path point without assuming a failed ping proves it is down.

```powershell
Get-NetNeighbor
```

```bash
ip neigh
ip route get 198.51.100.20
```

## 4. Route and path

Check the route actually selected from the affected source. Then trace with numeric output where possible; non-responding hops may simply filter probes.

```powershell
Test-NetConnection 198.51.100.20 -InformationLevel Detailed
tracert -d 198.51.100.20
```

```bash
ip route get 198.51.100.20
tracepath -n 198.51.100.20
```

## 5. Name resolution

Compare the fully qualified name with the known expected address. Query through the normal client path first. Continue with [DNS troubleshooting](../dns/dns-troubleshooting.md) if name and address tests differ.

## 6. Transport

Test only the required service port. A ping result is not a TCP/UDP result.

```powershell
Test-NetConnection host.example -Port 443
```

```bash
python3 ../../scripts/python/port_check.py host.example 443 --timeout 3
ss -lntup                           # on the server, when accessible
```

Timeout, refusal and completed TCP handshake lead to different next checks. UDP usually needs a protocol-specific response.

## 7. Application and dependencies

Complete a safe protocol/application request. Check TLS name/certificate, proxy, authentication and dependencies. A listening process may still be unable to serve work.

## 8. Direction, policy and scope

Compare an affected source with a known-good one, and forward with return direction. Identify endpoint, network, virtual/cloud and proxy controls. Do not disable firewalls, add broad routes, reset the stack or move VLANs as exploratory tests.

## Decide and validate

Change one identified cause within authority, with current state and rollback recorded. Escalate shared impact, security/policy, network-device ownership, loss of management path, unknown topology or disruptive work. After recovery, repeat the original application action, confirm required routes/ports in both directions, check errors and monitoring, and record the layer where evidence changed.
