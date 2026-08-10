# SSH or RDP unavailable

Use when a host is otherwise expected to be online but its remote administration service cannot be reached or authenticated. Protect the last working management path.

## Separate the failure stage

| Stage | Typical evidence | Fault area to investigate |
|---|---|---|
| Name resolution | Name fails or points elsewhere | DNS/client suffix |
| Route/host | No path from affected source | Link, address, route, host state |
| TCP connection | Port 22/3389 times out or is refused | Listener, firewall, service, NAT/policy |
| Protocol negotiation | Banner/TLS/session setup fails | Service configuration, crypto, resource pressure |
| Authentication | Prompt then rejection/lockout | Account, key, password policy, directory/time |
| Session | Login succeeds but shell/desktop fails | Profile, shell, licensing/session host, disk/resources |

From an authorised client:

```powershell
Test-NetConnection host.example -Port 3389
Test-NetConnection host.example -Port 22
```

```bash
nc -vz -w 3 host.example 22
ssh -vv -o ConnectTimeout=5 user@host.example
```

Verbose SSH output can expose names, paths and key metadata; store it only in the approved evidence location. Do not publish it unchanged.

## Host-side checks

Use an existing approved console or alternate management path—never create an exposed path for convenience.

- Linux: `systemctl status ssh`, `ss -ltnp`, recent SSH unit/authentication logs, disk space and account/key permissions. Distribution service names and log locations vary. See [SSH configuration and troubleshooting](../linux/configuration/ssh-configuration-troubleshooting.md).
- Windows: verify Remote Desktop is intended and authorised, TermService state, `Get-NetTCPConnection -LocalPort 3389 -State Listen`, relevant Event Viewer channels, firewall profile/rule scope and session/resource state.

Check time synchronisation and identity-provider reachability for domain/Kerberos or certificate-dependent access. Confirm whether a recent key, policy, firewall, update or network change matches the failure time.

## Avoid lockout

Do not restart networking, replace `sshd_config`, disable a firewall or close the current console/session until a validated fallback exists. Test SSH configuration with `sshd -t` before an authorised reload. For RDP, policy, Network Level Authentication and firewall changes can have security consequences; follow the approved change path.

## Escalate when

Escalate for suspected attack/lockout, several hosts affected, directory or bastion failure, unknown policy change, certificate/key recovery, licensing/session-host issues, or if the next action risks the final management route.

## Validate

Open a new session from the originally affected source while retaining the fallback path. Confirm authentication, expected privilege and a basic non-destructive command/desktop action. Check logs and monitoring for continued failures, then record stage, client/source scope, exact error, host listener/service evidence, change and validation.
