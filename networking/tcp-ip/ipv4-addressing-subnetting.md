# IPv4 addressing and subnetting

An IPv4 interface needs an address and prefix length. The prefix identifies which leading bits describe the local network; the remaining bits identify an address within it.

## Read CIDR in an investigation

For `192.0.2.77/27`:

- subnet mask: `255.255.255.224`;
- network: `192.0.2.64`;
- broadcast: `192.0.2.95`;
- conventional host range: `192.0.2.65` through `192.0.2.94`;
- conventional usable host addresses: 30.

These values were calculated from the prefix, not guessed from the decimal address. `192.0.2.0/24` is reserved for documentation, so it is suitable for public examples and should not be configured as a real Internet destination.

Common masks:

| Prefix | Mask | Addresses | Conventional usable hosts* |
|---:|---|---:|---:|
| /24 | 255.255.255.0 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 |

\*Traditional subnet use reserves network and broadcast addresses. `/31` is a special case supported for point-to-point links, and `/32` identifies one host/route; do not apply the subtraction rule blindly.

## Local or routed?

The host applies its own prefix to decide whether a destination is on-link. If it believes the destination is local, it uses ARP. Otherwise it sends the packet to a selected gateway. Two hosts with compatible-looking addresses but different masks can make different decisions and fail asymmetrically.

During diagnosis, capture all of:

- address and prefix/mask;
- default gateway and relevant specific routes;
- DHCP versus static source;
- duplicate address indication;
- expected VLAN/network.

Windows:

```powershell
Get-NetIPConfiguration
Get-NetIPAddress -AddressFamily IPv4
Get-NetRoute -AddressFamily IPv4
```

Linux:

```bash
ip -4 address
ip -4 route
ip route get 192.0.2.20
```

## Address ranges and public documentation

RFC 1918 private ranges are `10.0.0.0/8`, `172.16.0.0/12` and `192.168.0.0/16`. They are not globally routed on the public Internet, but they are not secret and can overlap between connected organisations or VPNs. Avoid publishing a real private addressing plan simply because the addresses are private.

Use IANA documentation blocks such as `192.0.2.0/24`, `198.51.100.0/24` and `203.0.113.0/24` in examples. An automatically assigned `169.254.0.0/16` address often indicates no usable DHCP lease, though link-local addressing itself is valid for limited local communication.
