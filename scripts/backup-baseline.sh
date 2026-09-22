#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

require_root
load_config "${1:-}"
for command in iptables-save ip6tables-save nft; do require_command "$command"; done

destination=$(backup_dir)
install -d -m 0700 "$destination"
iptables-save > "$destination/iptables.v4"
ip6tables-save > "$destination/iptables.v6"
nft list ruleset > "$destination/nftables.ruleset"

[[ ! -d /etc/ufw ]] || cp -a /etc/ufw "$destination/ufw"
[[ ! -f /etc/ssh/sshd_config ]] || cp -a /etc/ssh/sshd_config "$destination/sshd_config"
[[ ! -d /etc/ssh/sshd_config.d ]] || cp -a /etc/ssh/sshd_config.d "$destination/sshd_config.d"

if [[ -n ${ADGUARD_CONFIG:-} && "$ADGUARD_CONFIG" != *CHANGE_ME* && -f "$ADGUARD_CONFIG" ]]; then
    cp -a "$ADGUARD_CONFIG" "$destination/AdGuardHome.yaml"
fi

printf 'baseline saved: %s\n' "$destination"
find "$destination" -maxdepth 2 -type f -printf '%p %s bytes\n' | sort

