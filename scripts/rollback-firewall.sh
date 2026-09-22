#!/usr/bin/env bash
set -euo pipefail

BACKUP_ROOT=${BACKUP_ROOT:-/root/hardening-backups}
backup="$BACKUP_ROOT/$(hostname -s)"

ufw --force disable 2>/dev/null || true
[[ ! -s "$backup/iptables.v4" ]] || iptables-restore < "$backup/iptables.v4"
[[ ! -s "$backup/iptables.v6" ]] || ip6tables-restore < "$backup/iptables.v6"
echo "firewall baseline restored from $backup"

