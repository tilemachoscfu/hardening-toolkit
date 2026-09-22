#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

require_root
load_config "${1:-}"
require_value ADGUARD_CONFIG
require_value DNS_HEALTHCHECK_SERVER
for command in docker dig python3; do require_command "$command"; done

container=${ADGUARD_CONTAINER:-adguard-home}
health_name=${DNS_HEALTHCHECK_NAME:-dns.quad9.net}
backup="$(backup_dir)/AdGuardHome.yaml"
[[ -s "$backup" ]] || { echo "error: run backup-baseline.sh first" >&2; exit 66; }

restore() {
    cp -a "$backup" "$ADGUARD_CONFIG"
    docker start "$container" >/dev/null 2>&1 || true
}
trap restore ERR

docker stop --time 20 "$container" >/dev/null
python3 "$SCRIPT_DIR/update_adguard.py" "$ADGUARD_CONFIG"
python3 -c 'import sys, yaml; yaml.safe_load(open(sys.argv[1], encoding="utf-8"))' "$ADGUARD_CONFIG"
docker start "$container" >/dev/null

for _ in $(seq 1 30); do
    if dig +time=2 +tries=1 "@$DNS_HEALTHCHECK_SERVER" "$health_name" A >/dev/null 2>&1; then
        trap - ERR
        echo "AdGuard policy applied and DNS health check passed"
        exit 0
    fi
    sleep 1
done

echo "error: DNS health check failed; restoring baseline" >&2
false

