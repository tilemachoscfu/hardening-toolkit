#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

require_root
load_config "${1:-}"
for command in sshd systemd-run; do require_command "$command"; done

destination=$(backup_dir)
[[ -f "$destination/sshd_config" ]] || { echo "error: run backup-baseline.sh first" >&2; exit 66; }

install -m 0755 "$SCRIPT_DIR/rollback-ssh.sh" /usr/local/sbin/hardening-rollback-ssh
BACKUP_ROOT=${BACKUP_ROOT:-/root/hardening-backups} arm_rollback hardening-ssh-rollback /usr/local/sbin/hardening-rollback-ssh
install -m 0644 "$PROJECT_DIR/config/ssh-hardening.conf" /etc/ssh/sshd_config.d/00-hardening-toolkit.conf
sshd -t
systemctl reload ssh
sshd -T | grep -E '^(passwordauthentication|kbdinteractiveauthentication|permitrootlogin|pubkeyauthentication|x11forwarding)'

