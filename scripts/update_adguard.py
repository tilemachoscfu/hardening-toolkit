#!/usr/bin/env python3
"""Apply a conservative encrypted-upstream profile to AdGuardHome.yaml."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def update_config(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    dns = data.setdefault("dns", {})
    dns["upstream_dns"] = ["tls://dns.quad9.net"]
    dns["bootstrap_dns"] = ["9.9.9.9", "149.112.112.112"]
    dns["fallback_dns"] = []
    dns["enable_dnssec"] = True
    dns["cache_enabled"] = True
    dns["cache_size"] = max(int(dns.get("cache_size", 0)), 33_554_432)
    dns["cache_optimistic"] = True

    filtering = data.setdefault("filtering", {})
    filtering["filtering_enabled"] = True
    filtering["protection_enabled"] = True
    filtering["filters_update_interval"] = 24

    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path, help="Path to AdGuardHome.yaml")
    args = parser.parse_args()
    update_config(args.config)


if __name__ == "__main__":
    main()

