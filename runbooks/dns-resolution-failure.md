# DNS resolution failure

Use when a name does not resolve, resolves to an unexpected answer or works through one resolver/client but not another. Do not replace names with hard-coded addresses as a permanent workaround.

## Establish the exact query

Record the full name, record type, client, configured resolver, time, expected answer and error. Check spelling, search-suffix expansion and whether the name is public, private or split-horizon.

```powershell
Get-DnsClientServerAddress
Resolve-DnsName host.example -Type A
Resolve-DnsName host.example -Type A -Server 192.0.2.53
```

```bash
cat /etc/resolv.conf
getent ahosts host.example
resolvectl query host.example       # systemd-resolved systems
# or, when installed: dig A host.example @192.0.2.53
```

Query the normal client path first (`getent`, `Resolve-DnsName` without `-Server`), then a known resolver directly. This separates local resolver/search behaviour from upstream zone data. Documentation addresses above must be replaced with the authorised resolver during real work.

## Diagnostic sequence

1. Test the service by a known address only as a diagnostic comparison. Success separates naming from broader reachability but does not make the address a supported endpoint.
2. Confirm the client can route to the configured resolver on UDP and TCP port 53. Large, DNSSEC and zone-transfer responses may use TCP.
3. Compare the same record and type through another approved resolver.
4. Check response status: `NXDOMAIN`, `SERVFAIL`, timeout and an empty/no-data answer mean different things.
5. Check authoritative delegation, record value, TTL and recent zone or DHCP changes through the [DNS troubleshooting guide](../networking/dns/dns-troubleshooting.md).
6. Consider negative caching and stale local/application caches. Capture the original answer before flushing anything.

## Safe corrective actions

Correct an identified client typo/configuration or revert a known bad DNS change through the approved path. Cache flushing is a diagnostic/action only after evidence is retained; it can hide a propagation or authoritative-data fault. Do not edit hosts files, point clients at arbitrary public resolvers or lower TTLs without ownership and change authority.

## Escalate when

Escalate for failed delegation/DNSSEC, inconsistent authoritative servers, many clients or zones affected, suspected poisoning/security change, resolver service failure, or when zone/resolver ownership lies elsewhere.

## Validate and record

Repeat the original query through the normal client path and confirm the intended application connection, not just a single lookup. Check both required address families/record types and monitoring. Record resolver, query type, response code/answer/TTL, scope, recent change, action and propagation or cache follow-up.
