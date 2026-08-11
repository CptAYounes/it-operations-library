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
| Different answers | Caching, load distribution, split view or inconsistent authority needs context |

## Work from local to authoritative

1. Check spelling, trailing dot and search suffix. Compare the fully qualified name.
2. Identify cache layers: application, operating system/stub and recursive resolver.
3. Confirm UDP and TCP port 53 reachability to the intended resolver.
4. Query the same name/type through another approved resolver to separate client and recursive paths.
5. Follow delegation with `dig +trace` only when public/authorised data and policy make it appropriate; split/private zones will not trace through public roots.
6. Query authoritative servers and compare serial/answers when zone ownership is involved.
7. Review recent record, zone, DNSSEC, DHCP registration and resolver changes.

## Delegation, transport and DNSSEC

A recursive resolver follows delegation on the client's behalf; an authoritative server answers for a zone it serves. When public DNS ownership is in scope, compare the parent delegation, the authoritative name-server set and the answer from each authority. `dig +trace host.example` can expose where public delegation stops, but it does not reproduce a private/split view or the client's recursive cache.

Use an approved resolver or authoritative server when checking transport and DNSSEC details:

```bash
dig A host.example @192.0.2.53 +tcp
dig A host.example @192.0.2.53 +dnssec
dig NS child.example @192.0.2.53
dig DS child.example @192.0.2.53
dig DNSKEY child.example @198.51.100.53 +dnssec
delv @192.0.2.53 host.child.example A
```

A UDP answer does not prove large responses can fall back to TCP. `dig +dnssec` sets the DNSSEC OK (DO) bit so the server may return DNSSEC records; it does not validate the chain locally. The `ad` flag can report validation by a trusted recursive resolver, subject to that resolver's policy and trust anchors. Where BIND's `delv` is installed, use it for a validating lookup. Compare the parent NS/DS set with each authoritative server's NS/DNSKEY/RRSIG data and the recursive resolver's result/logs. `SERVFAIL` from a validating resolver can mean validation, time, delegation or upstream trouble; do not disable DNSSEC as a test.

## Split views

Private, VPN and public clients may be intended to receive different answers. Record the client's source/network and resolver, then compare only with another client in the same intended view. Sending a private name to an arbitrary public resolver can leak it and does not test the managed path.

## Avoid destructive shortcuts

Capture the failing answer and TTL before flushing caches. Do not edit hosts files or change clients to an arbitrary public resolver as a permanent workaround; either can bypass intended security, split DNS and service discovery. A lower TTL affects future cache duration but does not instantly remove already cached data.

## Validate

Repeat through the client's normal resolver path, then complete the intended application connection. Check all record types the application uses, including IPv6 where applicable, and account for propagation/cache time. The [DNS failure runbook](../../runbooks/dns-resolution-failure.md) provides the shorter response sequence.
