# Users, groups and permissions

Linux access problems are easiest to solve by separating identity, group membership, mode bits, ACLs and the privilege mechanism. Do not start with `chmod -R 777`: it discards useful boundaries, may expose secrets, and rarely identifies why access was denied.

## Read the effective identity first

```bash
whoami
id
id account-name
getent passwd account-name
getent group group-name
namei -l /path/to/object
stat /path/to/object
```

`getent` uses the configured Name Service Switch sources, so it can see directory-backed identities that are not literal lines in `/etc/passwd`. `namei -l` is useful because access to a file also depends on execute/search permission on every parent directory.

For a running process, distinguish the user who launched it from its effective and saved IDs:

```bash
ps -o pid,user,group,euser,egroup,comm -p PID
```

Replace `PID` with an observed process ID. Containers, systemd sandboxing, SELinux/AppArmor and network filesystems can impose controls beyond normal Unix permissions.

## How the permission check works

A typical mode string such as `-rw-r-----` contains:

- object type (`-` for regular file, `d` for directory);
- owner permissions (`rw-`);
- owning-group permissions (`r--`);
- other-user permissions (`---`).

The kernel selects one of those classes based on the caller's identity. It does not combine “other” permissions with a matched owner's missing permission.

| Permission | Regular file | Directory |
|---|---|---|
| read (`r`) | read contents | list names, subject to other permissions |
| write (`w`) | modify contents | create/remove/rename entries, normally with `x` too |
| execute (`x`) | execute a valid program/script | search/traverse the directory |

Directory write permission can allow deletion of a file even when the file itself is read-only, because deletion changes the directory entry. The sticky bit on a shared directory restricts who can remove entries.

Numeric modes are sums per class: read 4, write 2 and execute 1. `640` therefore means owner read/write, group read and no access for others. Symbolic changes are often clearer during review:

```bash
chmod u=rw,g=r,o= file
chmod g+x directory
```

Both commands change state. Use `stat` before and after and apply them only to the intended object.

## Ownership, groups and account state

Read-only inventory:

```bash
getent passwd
getent group
getent group sudo
lastlog
```

Some distributions use `wheel` rather than Debian's `sudo` group. Group membership alone does not prove a user has a particular command entitlement; inspect the effective `sudoers` policy with authorised tools.

Common administrative operations:

```bash
sudo adduser newaccount                         # Debian/Ubuntu helper
sudo useradd --create-home --shell /bin/bash newaccount  # lower-level portable-style tool
sudo groupadd appops
sudo usermod --append --groups appops newaccount
sudo passwd --lock newaccount
sudo chown appuser:appgroup /srv/application
```

These are examples, not a sequence to run. Important boundaries:

- `usermod -G appops user` without `--append` replaces supplementary groups and can remove administrative or service access.
- Group changes usually take effect at the next login. Existing processes retain their credentials.
- Locking a password does not necessarily stop SSH keys, tokens, scheduled jobs or running sessions.
- Deleting an account does not explain what should happen to its files, services, jobs or numeric UID.
- Recursive ownership changes can cross mount points or alter application-managed files. Preview the exact tree and filesystem boundaries first.
- Do not repurpose an existing UID/GID until orphaned ownership and remote identity sources have been checked.

After a new login session, validate:

```bash
id newaccount
getent group appops
sudo -l -U newaccount
```

`sudo -l -U` requires suitable privilege. Use `sudo -l` as the account during a controlled validation where possible.

## Default permissions and `umask`

`umask` removes permissions from the application's requested creation mode; it does not change existing objects.

```bash
umask
umask -S
```

A common `0022` mask generally produces `0644` files and `0755` directories when applications request `0666` and `0777`. A collaborative group may instead need a controlled `0002` model plus setgid directories. Applications can request stricter modes, so the result is not determined by `umask` alone.

Set a persistent mask only in the configuration layer that actually starts the process: login profile, PAM, systemd unit or application configuration. A shell profile does not govern an unrelated service.

## Special mode bits

Inspect them with `stat` or `find` before changing anything:

```bash
stat -c '%A %a %U:%G %n' /path/to/object
find /srv/application -xdev -type f -perm /6000 -print
find /srv/application -xdev -type d -perm /1000 -print
```

- **setuid on an executable** runs it with the file owner's effective identity. It creates a security boundary and should be rare and package-managed where possible.
- **setgid on an executable** uses the file's group identity.
- **setgid on a directory** makes new entries inherit the directory's group, useful for controlled shared trees.
- **sticky on a directory** allows shared creation while normally limiting deletion/rename to the file owner, directory owner or root; `/tmp` is the familiar example.

Do not recursively copy special bits from an unrelated tree.

## ACLs when three classes are not enough

If `getfacl` is installed:

```bash
getfacl -p /srv/application/item
```

An ACL is signalled by `+` in output such as `-rw-r-----+`. The ACL mask limits the effective permissions of named users, named groups and the owning group. This explains cases where a named entry appears to grant access but its `#effective:` value is narrower.

State-changing examples:

```bash
sudo setfacl --modify user:analyst:r-- /srv/application/report
sudo setfacl --modify default:group:appops:rwx /srv/application/shared
```

Default ACLs affect future children, not existing ones. Record and validate ACLs before backup/migration because some copy and archive workflows need explicit options to preserve them.

## A safe access-denied workflow

1. **Reproduce narrowly.** Record the account, exact object and operation. Avoid testing by granting broader rights.
2. **Trace the path.** Use `namei -l`, `stat` and `getfacl` to find the first restrictive component.
3. **Check the process identity.** A daemon may use a different account than an interactive test.
4. **Check object and mount context.** A read-only mount, NFS root squashing or container user mapping can look like a mode-bit problem.
5. **Check mandatory controls and logs.** AppArmor/SELinux policy can deny an operation even when Unix permissions allow it.
6. **Form the smallest change.** Prefer a service group or targeted ACL over world-writable access.
7. **Preserve a rollback record.** Capture original owner, group, mode and ACL.
8. **Retest as the real service identity.** A root test proves little about a least-privileged process.

One controlled test method, when authorised, is:

```bash
sudo -u service-account -- test -r /path/to/object
sudo -u service-account -- test -w /path/to/object
```

The lack of output means the `test` expression succeeded; check the exit status immediately if scripting. It does not prove the application can parse or safely use the object.

## `sudoers` is a separate policy

Always edit through `visudo`, preferably as a small file in `/etc/sudoers.d/` with an ownership and mode acceptable to `sudo`:

```bash
sudo visudo -f /etc/sudoers.d/appops
sudo visudo -c
```

Grant commands as narrowly as the operational task allows. Wildcards, editors, shells and programs that can load arbitrary files often provide more authority than their command name suggests. Test a new rule in a second session before closing the known-good administrative session.

## Escalate when

Stop and obtain the system or security owner when the proposed fix changes privileged access, affects a large or unfamiliar tree, touches a mounted application dataset, conflicts with directory-service identity, exposes secret material, or appears to be an AppArmor/SELinux denial. Record the observed identity, path traversal, current modes/ACLs, mount type, relevant log event and the smallest failed operation—not passwords, private keys or shadow-file content.
