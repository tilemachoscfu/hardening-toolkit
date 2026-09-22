#!/usr/bin/env bash
set -euo pipefail

load_config() {
    local config=${1:-}
    if [[ -z "$config" || ! -r "$config" ]]; then
        echo "usage: $0 /path/to/hardening.env" >&2
        exit 64
    fi
    # shellcheck disable=SC1090
    source "$config"
}

require_root() {
    if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
        echo "error: run as root" >&2
        exit 77
    fi
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "error: required command not found: $1" >&2
        exit 69
    }
}

require_value() {
    local name=$1 value=${!1:-}
    if [[ -z "$value" || "$value" == *CHANGE_ME* ]]; then
        echo "error: set $name in the environment file" >&2
        exit 78
    fi
}

backup_dir() {
    printf '%s/%s\n' "${BACKUP_ROOT:-/root/hardening-backups}" "$(hostname -s)"
}

arm_rollback() {
    local unit=$1 command=$2
    local delay=${ROLLBACK_SECONDS:-180}
    systemctl stop "${unit}.timer" "${unit}.service" 2>/dev/null || true
    systemctl reset-failed "${unit}.timer" "${unit}.service" 2>/dev/null || true
    systemd-run --unit="$unit" --on-active="${delay}s" \
        --setenv="BACKUP_ROOT=${BACKUP_ROOT:-/root/hardening-backups}" "$command" >/dev/null
    printf 'rollback armed: systemctl status %s.timer\n' "$unit"
    printf 'cancel after verification: systemctl stop %s.timer\n' "$unit"
}
