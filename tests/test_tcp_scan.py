import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import tcp_scan


class TimeoutTests(unittest.TestCase):
    def test_invalid_timeouts_are_rejected_before_network_access(self):
        for value in ('0', '-1', 'nan', 'inf', '-inf', 'invalid'):
            with self.subTest(value=value), patch.object(sys, 'argv', ['scan', 'example.invalid', '--timeout=' + value]), patch.object(tcp_scan, 'probe') as probe, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    tcp_scan.main()
                self.assertEqual(result.exception.code, 2)
                probe.assert_not_called()

    def test_positive_timeout_reaches_probe(self):
        with patch.object(sys, 'argv', ['scan', 'example.invalid', '--ports=443', '--timeout=0.5']), patch.object(tcp_scan, 'probe', return_value=443) as probe, contextlib.redirect_stdout(io.StringIO()) as output:
            tcp_scan.main()
            probe.assert_called_once_with('example.invalid', 443, 0.5)
            self.assertIn('443', output.getvalue())


class PortTests(unittest.TestCase):
    def test_invalid_ports_never_start_network_probes(self):
        for value in ('', '0', '-1', '65536', '22,0', '22,', 'http', '22.5'):
            with self.subTest(value=value), patch.object(sys, 'argv', [
                'scan', 'example.invalid', '--ports=' + value
            ]), patch.object(tcp_scan, 'probe') as probe, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    tcp_scan.main()
                self.assertEqual(result.exception.code, 2)
                probe.assert_not_called()

    def test_boundary_ports_are_valid_and_duplicates_are_probed_once(self):
        with patch.object(sys, 'argv', ['scan', 'example.invalid', '--ports=65535,1,1']), \
                patch.object(tcp_scan, 'probe', return_value=None) as probe, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            tcp_scan.main()
        self.assertEqual(probe.call_count, 2)
        self.assertEqual({call.args[1] for call in probe.call_args_list}, {1, 65535})
        self.assertIn('none', output.getvalue())
