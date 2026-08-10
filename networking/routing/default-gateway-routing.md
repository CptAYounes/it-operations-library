# Default gateways and routing

A default gateway is the next hop used when no more-specific route matches. It is not automatically used for destinations the host considers on-link.

## Route selection in practice

A routing table contains destination prefixes, next hops or on-link interfaces, and metrics. Selection generally starts with the longest matching prefix: a route to `192.0.2.64/27` is more specific than `192.0.2.0/24`, which is more specific than `0.0.0.0/0`. Metrics help choose between otherwise comparable routes, while policy routing can also use source, mark or table.

Inspect the route the operating system would select rather than reading only the default:

```powershell
Get-NetRoute -AddressFamily IPv4 | Sort-Object DestinationPrefix, RouteMetric
Test-NetConnection 198.51.100.20 -DiagnoseRouting -InformationLevel Detailed
```

```bash
ip -4 route
ip route get 198.51.100.20
ip rule show
```

Support for `-DiagnoseRouting` depends on the Windows version. `ip route get` reports a kernel route decision; it does not prove the next hop or destination will reply.

## Checks that narrow a gateway problem

1. Confirm interface state, address and prefix.
2. Determine whether the target is on-link or routed according to that prefix.
3. Verify a relevant route exists and uses the intended interface/source.
4. For a next hop on Ethernet, check neighbour resolution.
5. Test the gateway only as one path point. A gateway that answers ping may still lack the onward route; a gateway that filters ping may still forward correctly.
6. Trace towards the destination without treating the last responding hop as the failed device.
7. If the forward path works but the application does not, consider return routing, stateful policy and source NAT.

## Frequent fault patterns

- wrong prefix makes a remote destination appear local;
- missing/incorrect gateway allows local subnet access only;
- VPN or virtualisation installs a more-specific route;
- duplicate default routes select an unintended interface;
- return traffic follows another firewall or lacks a route;
- a route exists in a different network namespace/VRF than the process;
- stale instructions add a persistent route that outlives the original need.

## Change boundary

Adding a route can divert traffic or remove remote management. Record the current table, source/interface decision and rollback command before an authorised change. Do not “fix” one destination with a broad route when the ownership, prefix or return path is unknown. Validate the original service, route choice, reverse direction and monitoring after correction.
