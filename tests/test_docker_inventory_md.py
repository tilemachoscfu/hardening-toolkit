"""Inventory reports must include source-less mounts, not crash mid-report."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/docker_inventory_md.py"


class InventoryTests(unittest.TestCase):
    def report(self, mounts):
        container = {
            "Name": "/example", "Config": {"Image": "example/app:1"},
            "HostConfig": {"NetworkMode": "bridge", "RestartPolicy": {"Name": "no"},
                           "Privileged": False, "CapAdd": None, "PortBindings": {}},
            "Mounts": mounts,
        }
        result = subprocess.run([sys.executable, str(SCRIPT)],
                                input=json.dumps([container]), text=True,
                                capture_output=True, check=True)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_tmpfs_without_source(self):
        report = self.report([{"Type": "tmpfs", "Destination": "/tmp", "RW": True}])
        self.assertIn("tmpfs→/tmp rw", report)

    def test_mixed_mounts_keep_sources_and_access_modes(self):
        report = self.report([
            {"Type": "bind", "Source": "/srv/config", "Destination": "/config", "RW": False},
            {"Type": "volume", "Source": "/srv/volume", "Destination": "/data", "RW": True},
            {"Type": "tmpfs", "Source": "", "Destination": "/run", "RW": True},
        ])
        self.assertIn("/srv/config→/config ro; /srv/volume→/data rw; tmpfs→/run rw", report)

    def test_empty_mounts_remain_supported(self):
        self.assertIn("| - | - |", self.report([]))

    def test_unknown_sourceless_mount_label(self):
        self.assertIn("unknown→/cache ro", self.report([{"Destination": "/cache", "RW": False}]))


if __name__ == "__main__":
    unittest.main()
