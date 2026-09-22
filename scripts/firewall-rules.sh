#!/usr/bin/env bash
set -euo pipefail

: "${LAN_IF:?set LAN_IF}"
: "${LAN_V4:?set LAN_V4}"
VPN_IF=${VPN_IF:-}
VPN_V4=${VPN_V4:-}
VPN_V6=${VPN_V6:-}

iptables -N DOCKER-USER 2>/dev/null || true
iptables -F DOCKER-USER
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
[[ -z "$VPN_IF" ]] || iptables -A DOCKER-USER -i "$VPN_IF" -j ACCEPT
iptables -A DOCKER-USER -i "$LAN_IF" -s "$LAN_V4" -j ACCEPT
[[ -z "$VPN_V4" ]] || iptables -A DOCKER-USER -i "$LAN_IF" -s "$VPN_V4" -j ACCEPT
iptables -A DOCKER-USER -i "$LAN_IF" -m limit --limit 6/min --limit-burst 10 -j LOG --log-prefix "DOCKER-EXT-DROP "
iptables -A DOCKER-USER -i "$LAN_IF" -j DROP
iptables -A DOCKER-USER -j RETURN

ip6tables -N DOCKER-USER 2>/dev/null || true
ip6tables -F DOCKER-USER
ip6tables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
[[ -z "$VPN_IF" ]] || ip6tables -A DOCKER-USER -i "$VPN_IF" -j ACCEPT
ip6tables -A DOCKER-USER -i "$LAN_IF" -s fe80::/10 -j ACCEPT
[[ -z "$VPN_V6" ]] || ip6tables -A DOCKER-USER -i "$LAN_IF" -s "$VPN_V6" -j ACCEPT
ip6tables -A DOCKER-USER -i "$LAN_IF" -m limit --limit 6/min --limit-burst 10 -j LOG --log-prefix "DOCKER6-EXT-DROP "
ip6tables -A DOCKER-USER -i "$LAN_IF" -j DROP
ip6tables -A DOCKER-USER -j RETURN

