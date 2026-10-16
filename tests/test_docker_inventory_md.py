"""Inventory reports must include source-less mounts, not crash mid-report."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/docker_inventory_md.py"


class InventoryTests(unittest.TestCase):
    def report(self, mounts, **fields):
        container = {
            "Name": "/example", "Config": {"Image": "example/app:1"},
            "HostConfig": {"NetworkMode": "bridge", "RestartPolicy": {"Name": "no"},
                           "Privileged": False, "CapAdd": None, "PortBindings": {}},
            "Mounts": mounts,
        }
        container.update(fields)
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

    def test_mount_pipes_and_line_breaks_do_not_create_rows_or_columns(self):
        report = self.report([{"Type": "bind", "Source": "/srv/a|b\r\nc\rd\ne",
                               "Destination": "/data", "RW": True}])
        self.assertEqual(len(report.splitlines()), 3)
        self.assertEqual(report.splitlines()[-1].count("|"), 8)
        self.assertIn("/srv/a&#124;b<br>c<br>d<br>e→/data rw", report)

    def test_html_and_existing_entities_are_literal_input(self):
        report = self.report([{"Type": "bind", "Source": "/srv/<b>&lt;text&gt;</b>",
                               "Destination": "/data", "RW": False}])
        self.assertNotIn("<b>", report)
        self.assertIn("&lt;b&gt;&amp;lt;text&amp;gt;&lt;/b&gt;", report)

    def test_other_container_fields_also_stay_in_their_cells(self):
        report = self.report([], Name="/name|with\nnewline", Config={"Image": "<example>"})
        self.assertEqual(len(report.splitlines()), 3)
        self.assertEqual(report.splitlines()[-1].count("|"), 8)
        self.assertIn("name&#124;with<br>newline", report)
        self.assertIn("&lt;example&gt;", report)


if __name__ == "__main__":
    unittest.main()
