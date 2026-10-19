import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import tcp_scan


class ProbeTests(unittest.TestCase):
    def test_socket_configuration_results_and_cleanup(self):
        for status, expected in ((0, 443), (111, None)):
            with self.subTest(status=status), patch.object(tcp_scan.socket, 'socket') as factory:
                sock = factory.return_value.__enter__.return_value
                sock.connect_ex.return_value = status
                self.assertEqual(tcp_scan.probe('example.invalid', 443, 0.5), expected)
                factory.assert_called_once_with(tcp_scan.socket.AF_INET, tcp_scan.socket.SOCK_STREAM)
                sock.settimeout.assert_called_once_with(0.5)
                sock.connect_ex.assert_called_once_with(('example.invalid', 443))
                factory.return_value.__exit__.assert_called_once_with(None, None, None)

    def test_socket_is_closed_when_connection_raises(self):
        with patch.object(tcp_scan.socket, 'socket') as factory:
            sock = factory.return_value.__enter__.return_value
            error = OSError('synthetic connection failure')
            sock.connect_ex.side_effect = error
            with self.assertRaises(OSError) as raised:
                tcp_scan.probe('example.invalid', 443, 0.5)
            self.assertIs(raised.exception, error)
            factory.return_value.__exit__.assert_called_once()
            self.assertIs(factory.return_value.__exit__.call_args.args[1], error)


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
