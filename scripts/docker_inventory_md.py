#!/usr/bin/env python3
"""Convert `docker inspect` JSON from stdin into a Markdown exposure table."""

from __future__ import annotations

import json
import sys


def main() -> None:
    containers = json.load(sys.stdin)
    print("| Container | Image | Network | Restart | Privileged / caps | Ports | Mounts |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for container in containers:
        name = container["Name"].lstrip("/")
        image = container["Config"]["Image"]
        host = container["HostConfig"]
        caps = ",".join(host.get("CapAdd") or []) or "-"
        ports = []
        for container_port, bindings in (host.get("PortBindings") or {}).items():
            for binding in bindings or []:
                address = binding.get("HostIp") or "*"
                ports.append(f"{address}:{binding.get('HostPort', '')}→{container_port}")
        mounts = "; ".join(
            f"{mount['Source']}→{mount['Destination']} "
            f"{'rw' if mount['RW'] else 'ro'}"
            for mount in container.get("Mounts", [])
        )
        print(
            f"| {name} | {image} | {host['NetworkMode']} | "
            f"{host['RestartPolicy']['Name']} | {host['Privileged']} / {caps} | "
            f"{', '.join(ports) or '-'} | {mounts or '-'} |"
        )


if __name__ == "__main__":
    main()

