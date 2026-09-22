#!/usr/bin/env bash
set -euo pipefail

dropin=/etc/ssh/sshd_config.d/00-hardening-toolkit.conf
[[ ! -e "$dropin" ]] || rm -f -- "$dropin"
sshd -t
systemctl reload ssh
echo "SSH hardening drop-in removed"

