# HARDENING TOOLKIT

Rollback-first Linux and Docker hardening utilities for small self-hosted systems.

The toolkit turns a working host configuration into a reviewable workflow: capture a baseline, apply one bounded change, verify the effective state, and keep a timed recovery path available. It covers UFW, Docker's `DOCKER-USER` chain, OpenSSH, AdGuard Home and basic exposure auditing.

> [!WARNING]
> These scripts change firewall and remote-access policy. Test from a local console, keep an authenticated SSH session open, and verify key-based login before disabling password authentication. Review every value before running on a real host.

## Modules

| Area | Entry point | Purpose |
| --- | --- | --- |
| Baseline | `scripts/backup-baseline.sh` | Save firewall, SSH and optional AdGuard state |
| Host firewall | `scripts/apply-firewall.sh` | Apply a deny-by-default UFW policy with timed rollback |
| Docker firewall | `scripts/firewall-rules.sh` | Restrict published container ports through `DOCKER-USER` |
| SSH | `scripts/apply-ssh.sh` | Install and validate a conservative OpenSSH drop-in |
| AdGuard Home | `scripts/apply-adguard.sh` | Update DNS policy with backup, validation and health check |
| Inventory | `scripts/docker_inventory_md.py` | Render an inspectable Docker exposure table |
| Verification | `scripts/tcp_scan.py` | Check TCP exposure on systems you own or administer |

## Requirements

- Debian or Ubuntu host with `systemd`
- root access
- `ufw`, `iptables`, `ip6tables`, `nftables`, `openssh-server`
- Docker and Tailscale only if their matching rules are enabled
- Python 3 and PyYAML for the AdGuard module

## Quick start

```sh
git clone https://github.com/tilemachoscfu/hardening-toolkit.git
cd hardening-toolkit
cp config/hardening.env.example config/hardening.env
$EDITOR config/hardening.env
sudo scripts/backup-baseline.sh config/hardening.env
```

Then apply one module at a time:

```sh
sudo scripts/apply-firewall.sh config/hardening.env
sudo scripts/apply-ssh.sh config/hardening.env
sudo scripts/apply-adguard.sh config/hardening.env
```

Each apply script validates its prerequisites and arms a three-minute `systemd-run` rollback before changing access policy. After confirming connectivity and effective settings, cancel the matching timer shown by the script.

## Configuration

`config/hardening.env.example` is intentionally non-runnable. Copy it to the gitignored `config/hardening.env` and replace every `CHANGE_ME` value. The toolkit refuses unresolved placeholders.

The systemd unit reads `/etc/default/homelab-hardening`. Install a reviewed copy of the same environment file there before enabling it:

```sh
sudo install -m 0600 config/hardening.env /etc/default/homelab-hardening
sudo install -m 0755 scripts/firewall-rules.sh /usr/local/sbin/homelab-firewall-rules
sudo install -m 0644 systemd/homelab-docker-firewall.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now homelab-docker-firewall.service
```

## Verification

```sh
sudo ufw status verbose
sudo iptables -S DOCKER-USER
sudo ip6tables -S DOCKER-USER
sudo sshd -t
sudo sshd -T | grep -E '^(passwordauthentication|kbdinteractiveauthentication|permitrootlogin|pubkeyauthentication|x11forwarding)'
docker inspect $(docker ps -q) | python3 scripts/docker_inventory_md.py
python3 scripts/tcp_scan.py 192.0.2.10 --ports 22,80,443
```

Only scan systems you own or have explicit permission to test.

## Design notes

- Live addresses, usernames, compose paths and secrets are deliberately excluded.
- The firewall policy trusts one explicit LAN CIDR plus an optional VPN interface.
- Docker filtering happens in `DOCKER-USER`, before Docker's own accept rules.
- Backups are stored outside the repository with mode `0700`.
- Rollback is a normal stage of every remote-access change, not an afterthought.

See [SECURITY.md](SECURITY.md) before adapting the toolkit for an internet-facing host.

