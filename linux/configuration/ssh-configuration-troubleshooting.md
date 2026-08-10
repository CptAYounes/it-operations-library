# SSH configuration and troubleshooting

SSH has three separate fault domains: the network path to a listening server, the SSH handshake/host identity, and user authentication/authorisation. Diagnose them in that order. A firewall change will not repair a rejected key, and regenerating host keys will not repair a closed port.

> **Lockout warning:** keep a tested console or out-of-band route and the current administrative session open while changing SSH, authentication, network or firewall settings. Validate syntax, reload rather than restart when supported, and prove a second session before closing the first.

Examples favour Debian 13, where the OpenSSH server package is `openssh-server` and the systemd unit is normally `ssh.service`. Other distributions often use `sshd.service`.

## Read the current state

On the server:

```bash
systemctl status ssh.service --no-pager --full
ss -lnt 'sport = :22'
dpkg-query -W openssh-server
sudo /usr/sbin/sshd -t
sudo /usr/sbin/sshd -T
```

The package query and service name are Debian-specific. `sshd -t` checks configuration syntax and key sanity; `sshd -T` prints effective configuration. Reading host private keys and some effective settings can require root. Neither command proves the network path or user login.

On the client:

```bash
ssh -V
ssh -G alias-or-host
ssh -vvv user@host
```

`ssh -G` expands effective client configuration without connecting. Verbose output can reveal usernames, hostnames, addresses, key paths and authentication methods. Capture only the needed lines and redact them before sharing.

## Client configuration and selection

OpenSSH client settings can come from command-line options, `~/.ssh/config` and system configuration. The first obtained value for many options is used, so put host-specific entries before broad wildcard entries and inspect with `ssh -G`.

A minimal per-host example:

```sshconfig
Host lab-web
    HostName server.example
    User operator
    IdentityFile ~/.ssh/id_ed25519_lab
    IdentitiesOnly yes
```

Set private client configuration and key permissions so they are not writable/readable by unintended users:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config ~/.ssh/id_ed25519_lab
chmod 644 ~/.ssh/id_ed25519_lab.pub
```

These commands change modes; verify paths and existing policy first. A public key may be shared for its intended purpose, but private keys must never be pasted into documentation, tickets or chat.

Generate a new user key only when key ownership, passphrase and recovery/rotation requirements are known:

```bash
ssh-keygen -t ed25519 -a 64 -f ~/.ssh/id_ed25519_lab
```

Use an algorithm compatible with the required clients and security policy. A hardware-backed or centrally managed key may be preferable. `ssh-copy-id` modifies the remote account's authorised keys; inspect the destination account and key before using it.

## Server configuration on Debian

Debian's `/etc/ssh/sshd_config` normally includes files from `/etc/ssh/sshd_config.d/`. OpenSSH does not follow a generic “last file wins” rule for every scalar setting: the first value obtained is often retained. Inspect the packaged `Include` position, lexical drop-in order, `Match` blocks and final `sshd -T` output instead of assuming an override worked.

Before editing:

```bash
sudo sh -c 'umask 077; /usr/sbin/sshd -T > /root/sshd-effective.before'
sudo /usr/sbin/sshd -t
```

The first command creates a root-only before-state file and therefore changes storage. Use another approved protected path if `/root` is unsuitable; do not copy the file into public evidence.

Common controls that require a policy decision include:

```sshconfig
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
AllowGroups ssh-users
```

Do not apply this as a block. `AllowGroups` can exclude every user; `PasswordAuthentication no` can remove the last usable route; root-login policy can affect recovery/automation. Authentication can also be governed by PAM, `KbdInteractiveAuthentication`, certificate authorities and `AuthenticationMethods`.

For a small local change, use a governed drop-in name and then validate both syntax and effective settings:

```bash
sudo /usr/sbin/sshd -t
sudo /usr/sbin/sshd -T | less
sudo systemctl reload ssh.service
```

A reload avoids dropping established sessions in normal OpenSSH operation, but new sessions use the new policy. Test one immediately from an expected client and keep the original session available.

For settings inside `Match`, test a representative connection context:

```bash
sudo /usr/sbin/sshd -T -C user=operator,host=server.example,addr=192.0.2.25
```

The address is from a documentation range. Replace all values with the intended account, server name and client source. A successful test for one context does not validate every group or address path.

## Authorised keys and path permissions

On the server, for the default per-user key model:

```bash
namei -l /home/operator/.ssh/authorized_keys
stat /home/operator /home/operator/.ssh /home/operator/.ssh/authorized_keys
```

Typical secure modes are a user-owned home not writable by group/other, `.ssh` at `0700`, and `authorized_keys` at `0600`, but central key commands, ACLs, network homes and local policy can differ. Check `AuthorizedKeysFile` and `StrictModes` in effective configuration.

Each line in `authorized_keys` may include restrictions such as `from=`, `command=`, `no-port-forwarding` and `no-pty`. These are valuable least-privilege controls but can cause an apparently valid key to be rejected or limited. Compare the client's offered public-key fingerprint—not the private key—with the installed entry:

```bash
ssh-keygen -lf ~/.ssh/id_ed25519_lab.pub
```

## Troubleshoot in layers

### 1. Name and route

```bash
getent ahosts server.example
ip route get 192.0.2.10
```

Confirm the client resolves the intended address and chooses the expected source/route. See [network diagnostics](../networking/network-diagnostics.md) for IPv6, DNS and path isolation.

### 2. TCP connection

```bash
nc -vz -w 3 server.example 22
```

If `nc` is not installed, the SSH client's own timeout/refusal is still useful. `Connection refused` suggests an active reject or no listener; timeout suggests loss/filtering/route issues but is not proof of which firewall. On the server, confirm bind address and port with `ss` and inspect the active firewall.

### 3. Host identity and negotiation

The first connection must verify the host-key fingerprint through a trusted independent channel. A changed key can follow a legitimate rebuild, but it can also indicate redirection or interception. Do not simply suppress `StrictHostKeyChecking`.

After independently confirming a legitimate change, remove only the stale host entry:

```bash
ssh-keygen -F server.example
ssh-keygen -R server.example
```

`-R` changes `known_hosts`; check aliases, addresses and hashed entries first. Reconnect and verify the new fingerprint.

Negotiation errors such as “no matching host key type” or “no matching key exchange” should be fixed by updating obsolete software or applying the narrowest time-bounded compatibility exception. Do not globally re-enable weak algorithms.

### 4. Authentication/authorisation

Compare the client debug sequence with server logs in the same time window:

```bash
journalctl -u ssh.service --since '10 minutes ago' --no-pager
```

Check:

- correct account and whether it is locked/expired;
- key fingerprint and whether the client actually offered it;
- `AllowUsers`/`AllowGroups`/`Deny*` and `Match` results;
- home, `.ssh` and `authorized_keys` ownership/modes/ACLs;
- PAM, MFA or directory-service availability;
- shell and account access policy;
- AppArmor/SELinux denials where applicable;
- source-address restrictions and clock validity for certificates.

Never request a user's password or private key as troubleshooting evidence.

## Firewall and port changes

Changing `Port` does not replace authentication controls and only reduces background noise. Before moving or adding a port:

1. confirm the service will listen on it;
2. allow the intended source through host and upstream firewalls;
3. account for SELinux port labelling on enforcing distributions;
4. validate configuration;
5. reload SSH;
6. prove a second session on the new path;
7. only then remove the old path under an approved rollback plan.

Follow [firewall fundamentals](../networking/firewall-fundamentals.md). Never apply an input default-drop policy before the management allow rule and return-traffic rules are verified.

## Recovery validation

A recovered SSH service must pass more than `systemctl active`:

- a new connection from the expected source resolves the right host;
- host-key fingerprint matches the trusted record;
- intended user/key/MFA succeeds and an unauthorised method remains denied;
- command/shell and required forwarding restrictions behave as designed;
- logs identify the successful path without repeated errors;
- firewall exposure and listening addresses are no wider than planned;
- console/recovery access remains available.

Escalate for unverified host-key changes, suspected key disclosure, brute-force/security events, directory-service/PAM failures, policy ambiguity, no console fallback, or any change likely to remove the only administrative path. Hand over timestamps, client source, destination/port, exact stage/error, effective non-secret settings, key fingerprints and relevant redacted logs.
