# DNS troubleshooting

Start with the question the client actually asked: exact name, record type, configured resolver and time. “DNS is broken” can mean no route to a resolver, an authoritative-data error, search-suffix behaviour, a stale cache or an application that never queried DNS.

## Compare client path and direct query

Windows:

```powershell
Get-DnsClientServerAddress
Resolve-DnsName host.example -Type A
Resolve-DnsName host.example -Type A -Server 192.0.2.53
```

Linux:

```bash
cat /etc/resolv.conf
getent ahosts host.example
resolvectl status                 # where systemd-resolved is in use
resolvectl query host.example
dig A host.example @192.0.2.53    # when the dnsutils/bind-tools package is installed
```

The normal application path matters: `getent` uses the system name-service configuration, while `dig` directly tests DNS and can bypass `/etc/hosts`, mDNS or another NSS source. Substitute an authorised resolver for the documentation address.

## Interpret the response

| Result | Meaning to investigate |
|---|---|
| `NOERROR` with answer | Check value, type, TTL and whether it matches the required view |
| `NOERROR` with no requested data | Name may exist without that record type |
| `NXDOMAIN` | Resolver says the name does not exist; negative caching may retain it |
| `SERVFAIL` | Resolver could not complete the answer; delegation, DNSSEC or upstream failure are possibilities |
| Timeout | Reachability, filtering, resolver load or packet-size/TCP fallback may be involved |
| Different answers | Caching, load distribution, split horizon or inconsistent authority needs context |

## Work from local to authoritative

1. Check spelling, trailing dot and search suffix. Compare the fully qualified name.
2. Identify cache layers: application, operating system/stub and recursive resolver.
3. Confirm UDP and TCP port 53 reachability to the intended resolver.
4. Query the same name/type through another approved resolver to separate client and recursive paths.
5. Follow delegation with `dig +trace` only when public/authorised data and policy make it appropriate; split/private zones will not trace through public roots.
6. Query authoritative servers and compare serial/answers when zone ownership is involved.
7. Review recent record, zone, DNSSEC, DHCP registration and resolver changes.

## Avoid destructive shortcuts

Capture the failing answer and TTL before flushing caches. Do not edit hosts files or change clients to an arbitrary public resolver as a permanent workaround; either can bypass intended security, split DNS and service discovery. A lower TTL affects future cache duration but does not instantly remove already cached data.

## Validate

Repeat through the client's normal resolver path, then complete the intended application connection. Check all record types the application uses, including IPv6 where applicable, and account for propagation/cache time. The [DNS failure runbook](../../runbooks/dns-resolution-failure.md) provides the shorter response sequence.
