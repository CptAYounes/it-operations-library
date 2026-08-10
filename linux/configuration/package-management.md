# Package management

A package operation can replace libraries, restart services, install a new kernel or remove dependencies. Treat “update the server” as a change with a known package set, impact and recovery route—not as one undifferentiated command.

This guide uses Debian 13's APT and dpkg tools first, then notes equivalents for other distribution families.

## Separate the layers

- **Repository metadata** describes available packages and versions.
- **APT** resolves dependencies and retrieves Debian packages.
- **dpkg** installs and records individual `.deb` packages; it does not resolve repository dependencies by itself.
- **Package configuration** can run maintainer scripts and restart services.
- **A distribution release upgrade** changes the OS baseline and needs the release-specific upgrade procedure, not only normal package commands.

## Read before changing anything

```bash
cat /etc/os-release
apt-cache policy
apt-cache policy package-name
apt list --installed
dpkg-query -W -f='${binary:Package}\t${Version}\n'
apt list --upgradable
apt-mark showhold
dpkg --audit
```

`apt list` may label its interface unstable for scripting. It is convenient interactively; use stable interfaces such as `apt-get` and `dpkg-query` in automation.

Useful ownership and content queries:

```bash
dpkg-query -S /usr/bin/command-name
dpkg-query -L package-name
apt-cache show package-name
apt-cache depends package-name
apt-cache rdepends package-name
```

`apt-cache rdepends` is a repository-level hint, not proof that removing the package is safe on this host. Services, manually installed software and local scripts may depend on files without package metadata declaring it.

## Check repository trust and release scope

Debian 13 commonly stores deb822 entries in `/etc/apt/sources.list.d/*.sources`; older one-line entries may also exist in `/etc/apt/sources.list` or `.list` files.

Review:

- suite/codename (`trixie`, an approved stable alias, or another intended suite);
- repository URI and mirror ownership;
- enabled components such as `main`, `contrib`, `non-free-firmware` and `non-free`;
- `Signed-By` keyring references for third-party sources;
- duplicate, obsolete or mixed-release entries;
- proxy configuration and TLS interception requirements.

Do not solve a signature failure with `trusted=yes`, `--allow-unauthenticated` or disabled TLS verification. Check the clock, release-key package, repository URL, proxy and signing-key instructions from the repository owner. `apt-key` is deprecated; third-party keys should be scoped with `Signed-By` rather than added to a global trusted keyring.

## Preview a Debian update

Refreshes and simulations do different things:

```bash
sudo apt update
apt list --upgradable
apt-get --simulate upgrade
apt-get --simulate dist-upgrade
```

`apt update` changes the local metadata cache but does not install upgrades. The simulations calculate against that cached metadata and do not prove the packages will still be available when the real change runs.

Review the proposed transaction for:

- package removals or replacements;
- newly installed dependencies;
- held-back or held packages;
- kernel, bootloader, libc, SSH, network, database or storage changes;
- service restarts and active sessions;
- free space in `/`, `/var`, `/boot` and the EFI system partition;
- a usable console and tested backup/rollback route.

List likely reboot indicators after package work on Debian when the relevant mechanisms are present:

```bash
test -e /var/run/reboot-required && printf '%s\n' 'reboot required'
cat /var/run/reboot-required.pkgs 2>/dev/null
```

The absence of these files is not a universal guarantee that no restart is needed. Check service and kernel release notes.

## Install, upgrade and remove deliberately

Interactive Debian examples:

```bash
sudo apt install package-name
sudo apt upgrade
sudo apt remove package-name
```

Key distinctions:

- `remove` normally retains package-owned configuration marked as conffiles; `purge` removes those too.
- `autoremove` removes packages APT regards as automatically installed and no longer required. Always review its list.
- `upgrade` is conservative about removals; `full-upgrade` may remove packages to complete dependency changes.
- Installing a local `.deb` with `apt install ./package.deb` allows APT to resolve declared dependencies; direct `dpkg -i` may leave dependencies unconfigured.
- Reinstalling a package does not necessarily replace a locally modified conffile or repair application data.

Potentially wider-impact commands should be previewed and approved:

```bash
apt-get --simulate autoremove
apt-get --simulate remove package-name
```

Do not run `purge`, `autoremove` or a release upgrade merely as a generic cleanup step.

## Holds, pins and version selection

```bash
apt-mark showhold
apt-cache policy package-name
```

A hold can preserve compatibility temporarily, but it also creates patch debt. Record owner, reason and review date. APT preferences/pinning can select versions across repositories; mixed suites can create an upgrade path that is difficult to reverse. Use pins only with a documented repository design and test the candidate version using `apt-cache policy`.

Version-specific installation is state-changing and may require dependency downgrades:

```bash
sudo apt install package-name=version
```

Never force a downgrade without checking data formats and maintainer-script support. Package version rollback does not roll application schemas or configuration back automatically.

## If an operation is interrupted

Capture the exact error before trying several repair commands:

```bash
dpkg --audit
sudo dpkg --configure --pending
sudo apt-get --fix-broken install
```

The last two commands change state and can run scripts or remove/install packages. Read their proposed actions and preserve package-manager logs first:

```bash
less /var/log/apt/history.log
less /var/log/apt/term.log
```

For dpkg lock errors, identify the owner rather than deleting lock files:

```bash
ps -ef | grep -E '[a]pt|[d]pkg'
systemctl status apt-daily.service apt-daily-upgrade.service --no-pager
```

Another legitimate package process may be active. Removing lock files while it runs can corrupt package state.

## Distribution-specific equivalents

Confirm `/etc/os-release` before choosing a tool.

| Task | Debian 13 / Ubuntu | Fedora / RHEL family | Arch Linux |
|---|---|---|---|
| Query installed package | `dpkg-query -W name` | `rpm -q name` | `pacman -Q name` |
| Query available updates | `apt list --upgradable` | `dnf check-upgrade` | Use the supported full-upgrade workflow; avoid stale partial-upgrade assumptions |
| Install | `sudo apt install name` | `sudo dnf install name` | `sudo pacman -S name` |
| Normal full update | `sudo apt upgrade` after review | `sudo dnf upgrade` | `sudo pacman -Syu` |
| Remove | `sudo apt remove name` | `sudo dnf remove name` | `sudo pacman -R name` |
| History | APT/dpkg logs | `dnf history` | `/var/log/pacman.log` |

Repository formats, modular streams, weak dependencies, kernel retention and release upgrades differ. Use that release's documentation rather than translating APT flags literally.

## Validate the change

After package work:

```bash
dpkg --audit
systemctl --failed --no-pager
journalctl --since '15 minutes ago' -p warning --no-pager
ss -lntup
```

Also:

1. confirm installed versions with `dpkg-query` or the distribution's package query;
2. run application-level health checks, not only a service-state check;
3. confirm listening addresses, certificates and dependencies where relevant;
4. reboot only when authorised, after checking users/jobs and console recovery;
5. after reboot, verify the running kernel, mounts, network and required services;
6. record package names/versions, source, timing, warnings, restart/reboot and result.

Escalate when the transaction proposes unexplained removals, repository signatures fail, package ownership conflicts with manual files, database/schema compatibility is unknown, the boot path is being changed without recovery access, or dependency repair would make the service impact wider than authorised.
