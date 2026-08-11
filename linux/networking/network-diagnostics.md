# Linux network diagnostics

Work from the host outward. A successful DNS lookup does not prove the application port is reachable; a failed ping does not prove the host is down. Each check should isolate one layer and produce evidence for the next decision.

The main diagnostic path does not change local network configuration. It does include active probes such as DNS queries, ICMP, TCP connections, TLS handshakes and HTTP requests; these generate traffic and logs and can trigger rate limits or security monitoring. Use only an authorised, non-destructive endpoint and method. Command availability varies by installed packages and network manager.

## Capture the context

Record:

- affected host/interface and expected path;
- exact destination name, address, protocol and port;
- local-only, subnet, site, Internet or single-application impact;
- IPv4, IPv6 or both;
- start time, last known-good time and recent network/firewall changes;
- whether another client or destination behaves differently.

Avoid publishing real addresses, DNS suffixes, packet captures or service banners.

## 1. Interface and link

```bash
ip -brief link
ip -s link
ip -brief address
```

Look for the expected interface, `UP` state, carrier/lower-layer state, address family and increasing error/drop counters. A virtual bridge, container veth or tunnel may be legitimate; do not “clean up” unfamiliar interfaces during an incident.

If installed and appropriate:

```bash
ethtool interface-name
networkctl status interface-name
nmcli device show interface-name
```

`ethtool` can report negotiated speed/duplex and link detection for many physical NICs. Some data and driver operations require privilege. A link marked up proves only local carrier/administrative state, not switch VLAN, upstream routing or application reachability.

## 2. Address and subnet

```bash
ip address show dev interface-name
ip route show table main
ip -6 route show table main
```

Confirm:

- expected address and prefix length;
- no duplicate or unexpected address;
- correct source interface;
- connected route for the local subnet;
- expected default route and metric;
- whether IPv6 has a usable route rather than only a link-local address.

Ask the kernel how it would route a specific destination:

```bash
ip route get 203.0.113.10
ip -6 route get 2001:db8::10
```

The documentation addresses above are examples. Replace them with an authorised target. The result shows chosen interface, gateway and source address; it does not send a probe.

Multiple routing tables and policy rules can override the main table:

```bash
ip rule show
ip route show table all
```

Large output is normal on container or VPN hosts. Do not add/delete routes while still determining which network manager owns them.

## 3. Local stack and neighbour resolution

```bash
ping -c 4 -W 2 127.0.0.1
ping -c 4 -W 2 local-interface-address
ip neigh show
```

Then, where policy allows, test a known peer or the configured gateway. ICMP may be blocked or deprioritised, so packet loss is evidence about that probe—not definitive application status.

Neighbour states help with same-link faults:

- `REACHABLE`/`STALE` can be normal;
- `INCOMPLETE` or `FAILED` after traffic suggests unresolved ARP/NDP;
- the wrong link-layer address may indicate a duplicate address, stale state or network misconfiguration.

Do not flush the neighbour table as a first response; preserve evidence and check VLAN, subnet and duplicate-address possibilities.

## 4. Route through the network

```bash
tracepath destination.example
traceroute destination.example
```

Either command may be absent. Firewalls and routers can suppress or rate-limit the diagnostic packets, and the forward and return paths may differ. Asterisks do not by themselves identify the failed hop. Compare from a known-good source and use the application protocol before escalating a transit-network conclusion.

## 5. Name resolution

Use the system resolver path first because it reflects Name Service Switch configuration:

```bash
getent ahosts destination.example
getent hosts destination.example
```

Inspect resolver ownership:

```bash
cat /etc/nsswitch.conf
ls -l /etc/resolv.conf
cat /etc/resolv.conf
resolvectl status
```

`resolvectl` applies only when systemd-resolved is present. `/etc/resolv.conf` may be a generated symlink managed by systemd-resolved, NetworkManager, resolvconf, DHCP or a container runtime; editing it directly may be temporary or conflict with its owner.

If `dig` is installed, compare the configured resolver with an explicitly authorised server:

```bash
dig destination.example
dig @resolver-address destination.example
```

A direct query bypasses part of the host resolver path and may violate network policy if aimed at an external resolver. Compare record type, response code, answer, TTL and server used. Check A and AAAA separately when only one address family fails.

Distinguish:

- name does not exist (`NXDOMAIN`);
- resolver cannot answer (`SERVFAIL`/timeout);
- name resolves to an unexpected address;
- local NSS source such as `/etc/hosts` overrides DNS;
- DNS works, but transport/application fails.

## 6. Listening and transport ports

On the server:

```bash
ss -lntup
ss -lnt 'sport = :443'
```

Check address binding as well as port: `127.0.0.1:443` is not reachable remotely; `0.0.0.0:443` and `[::]:443` have address-family and socket-option implications. Process details may require privilege.

On the client, where `nc` is installed:

```bash
nc -vz -w 3 destination.example 443
```

Interpret common outcomes carefully:

- **succeeded** — a TCP connection completed; the application can still fail later;
- **connection refused** — the destination or an intermediary actively rejected it, often because no listener is present;
- **timed out** — packets or replies may be filtered/lost, the route may fail, or the endpoint may be overloaded;
- **name resolution error** — transport was not tested.

For UDP, a lack of response is especially ambiguous. Use an application-aware query.

## 7. Application and TLS

Test the protocol the user actually needs:

```bash
curl --verbose --connect-timeout 5 --max-time 15 https://destination.example/health
openssl s_client -connect destination.example:443 -servername destination.example </dev/null
```

Only query approved endpoints. Verbose output may expose headers, cookies, proxy details or tokens; redact before sharing. `openssl s_client` proves aspects of the TLS handshake and certificate presentation, not HTTP or application health.

Check:

- proxy environment and application-specific proxy settings;
- TLS name/SNI and certificate time validity;
- authentication versus network failure;
- server response code and a meaningful health response;
- load balancer path versus direct node path, if authorised.

## 8. Firewall and packet evidence

Inspect the active firewall stack before assuming one tool owns policy. Follow [firewall fundamentals](firewall-fundamentals.md). Also account for upstream ACLs, cloud security groups, hypervisor bridges, container rules and the remote host firewall.

Packet capture can answer whether a SYN left, a reply returned or DNS traffic used the expected server. It usually requires privilege and may collect credentials or personal data. Obtain authority, constrain interface/host/port/count, store output securely and stop after the necessary window. Do not publish raw captures without review.

## Network manager and state-change boundary

Identify ownership before changing an interface:

```bash
systemctl is-active NetworkManager
systemctl is-active systemd-networkd
systemctl status networking.service --no-pager
```

Cloud-init, ifupdown, netplan or orchestration may also generate configuration. Restarting a network manager or applying a new address remotely can remove the only access route and affect every interface it controls. Preserve console access, use the manager's validation/checkpoint feature where available, and schedule changes through the appropriate owner.

## Fast decision sequence

```text
Interface absent/down?
  -> hardware, driver, VM attachment or manager
Address/prefix wrong?
  -> DHCP/static configuration or duplicate
No route / wrong source?
  -> routing, policy rule, VPN or namespace
Local neighbour unresolved?
  -> subnet, VLAN, ARP/NDP or link path
Name fails but address works?
  -> NSS/DNS configuration or resolver path
TCP port fails but host path works?
  -> listener, bind address, firewall or service
TCP connects but request fails?
  -> TLS, authentication, proxy or application
```

## Validate and escalate

After an approved fix, repeat only the checks that prove each affected layer: link/address, route decision, resolver result, transport connection and functional application request. Confirm monitoring from the user's path and watch error/drop counters for recurrence.

Escalate with timestamps, source/destination/protocol/port, scope, route decision, resolver used, exact error, comparison host and recent changes when the fault crosses network ownership. Escalate immediately for suspected address conflict, route leak, unauthorised listener, packet evidence of an attack, or a change that would cut off the only management path.
