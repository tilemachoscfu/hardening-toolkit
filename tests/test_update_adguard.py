from pathlib import Path
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from update_adguard import update_config


class ConfigPreservationTests(unittest.TestCase):
    def test_preserves_unrelated_settings_and_is_idempotent(self):
        original = {
            'dns': {'cache_size': 67108864, 'port': 5353},
            'filtering': {'rewrites': [{'domain': 'example.invalid', 'answer': '127.0.0.1'}]},
            'custom': {'label': 'Δοκιμή', 'enabled': False},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.yaml'
            path.write_text(yaml.safe_dump(original), encoding='utf-8')
            update_config(path)
            first = path.read_bytes()
            result = yaml.safe_load(first)
            self.assertEqual(result['custom'], original['custom'])
            self.assertEqual(result['dns']['port'], 5353)
            self.assertEqual(result['dns']['cache_size'], 67108864)
            self.assertEqual(result['filtering']['rewrites'], original['filtering']['rewrites'])
            update_config(path)
            self.assertEqual(path.read_bytes(), first)

    def test_invalid_yaml_or_cache_size_does_not_overwrite_source(self):
        for content in ('dns: [unterminated', 'dns:\n  cache_size: invalid\n'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'config.yaml'
                path.write_text(content)
                before = path.read_bytes()
                with self.assertRaises((yaml.YAMLError, ValueError)):
                    update_config(path)
                self.assertEqual(path.read_bytes(), before)
