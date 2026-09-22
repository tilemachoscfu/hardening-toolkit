#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

require_root
load_config "${1:-}"
require_value LAN_IF
require_value LAN_V4
for command in ufw iptables ip6tables systemd-run; do require_command "$command"; done

destination=$(backup_dir)
[[ -s "$destination/iptables.v4" && -s "$destination/iptables.v6" ]] || {
    echo "error: run backup-baseline.sh first" >&2
    exit 66
}

install -m 0755 "$SCRIPT_DIR/rollback-firewall.sh" /usr/local/sbin/hardening-rollback-firewall
BACKUP_ROOT=${BACKUP_ROOT:-/root/hardening-backups} arm_rollback hardening-firewall-rollback /usr/local/sbin/hardening-rollback-firewall

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow in on "$LAN_IF" from "$LAN_V4" comment 'trusted LAN'
if [[ -n ${VPN_IF:-} ]]; then ufw allow in on "$VPN_IF" comment 'trusted VPN'; fi
if [[ -n ${VPN_UDP_PORT:-} ]]; then ufw allow in on "$LAN_IF" proto udp to any port "$VPN_UDP_PORT" comment 'VPN direct path'; fi
ufw logging low
ufw --force enable

export LAN_IF LAN_V4 VPN_IF VPN_V4 VPN_V6
"$SCRIPT_DIR/firewall-rules.sh"
ufw status verbose
iptables -S DOCKER-USER
ip6tables -S DOCKER-USER

