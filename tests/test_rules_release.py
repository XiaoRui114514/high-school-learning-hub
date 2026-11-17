import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from package_skill import publication_files
from release_rules import build_assets, validate_tag


class RulesReleaseTests(unittest.TestCase):
    def test_release_assets_match_allowlist_and_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive, checksum = build_assets(ROOT, Path(tmp))
            self.assertEqual(checksum.read_text().split()[0], hashlib.sha256(archive.read_bytes()).hexdigest())
            with zipfile.ZipFile(archive) as package:
                expected = {name for name, _ in publication_files(ROOT)}
                self.assertEqual(set(package.namelist()), expected | {'PUBLICATION.json'})
                manifest = json.loads(package.read('PUBLICATION.json'))
                self.assertTrue(all(hashlib.sha256(package.read(n)).hexdigest() == d for n, d in manifest.items()))

    def test_only_explicit_version_tags_are_accepted(self):
        for value in ['', None, '../main', 'v1.0', '--latest', 'rules-2026.11.17;echo bad', 'rules-2026.11.17\n']:
            with self.assertRaises(ValueError):
                validate_tag(value)
        self.assertEqual(validate_tag('rules-2026.11.17'), 'rules-2026.11.17')
        self.assertEqual(validate_tag('rules-2026.11.17.2'), 'rules-2026.11.17.2')
