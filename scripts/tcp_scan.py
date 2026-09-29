#!/usr/bin/env python3
"""Small, bounded TCP exposure check for authorized systems."""

from __future__ import annotations

import argparse
import concurrent.futures
import math
import socket


def parse_ports(value: str) -> list[int]:
    ports = sorted({int(item) for item in value.split(",")})
    if not ports or ports[0] < 1 or ports[-1] > 65535:
        raise argparse.ArgumentTypeError("ports must be between 1 and 65535")
    return ports


def parse_timeout(value: str) -> float:
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive finite number")
    return timeout


def probe(host: str, port: int, timeout: float) -> int | None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return port if sock.connect_ex((host, port)) == 0 else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check selected TCP ports on a system you are authorized to test."
    )
    parser.add_argument("host")
    parser.add_argument("--ports", type=parse_ports, default=parse_ports("22,80,443"))
    parser.add_argument("--timeout", type=parse_timeout, default=0.25)
    args = parser.parse_args()

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(64, len(args.ports))) as pool:
        results = pool.map(lambda port: probe(args.host, port, args.timeout), args.ports)
    open_ports = [port for port in results if port is not None]
    print("OPEN_TCP", args.host, ",".join(map(str, open_ports)) or "none")


if __name__ == "__main__":
    main()
