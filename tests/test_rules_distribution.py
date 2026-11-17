import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from publish_rules import stage_rules
from package_skill import publication_files


class RulesDistributionTests(unittest.TestCase):
    def test_staged_tree_is_exactly_the_publication_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            staged = Path(tmp) / 'rules'
            manifest = stage_rules(ROOT, staged)
            actual = {p.relative_to(staged).as_posix() for p in staged.rglob('*') if p.is_file()}
            expected = {n for n, _ in publication_files(ROOT)}
            self.assertEqual(actual, expected | {'PUBLICATION.json'})
            self.assertEqual(json.loads((staged / 'PUBLICATION.json').read_text()), manifest)
            self.assertTrue(all(hashlib.sha256((staged / n).read_bytes()).hexdigest() == digest for n, digest in manifest.items()))
            self.assertFalse(any(n.startswith(('textbooks/', 'private/', 'worklogs/', 'references/research/')) for n in actual))
            self.assertLess(sum(p.stat().st_size for p in staged.rglob('*') if p.is_file()), 300_000)
            with self.assertRaises(ValueError):
                stage_rules(ROOT, staged)

    def test_source_archives_omit_textbooks_but_retain_rules_and_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.gitattributes').write_bytes((ROOT / '.gitattributes').read_bytes())
            for name in ['SKILL.md', 'scripts/check.py', 'tests/example.py', 'textbooks/physics/example.pdf', 'private/example.md', 'references/research/example.md']:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('Synthetic archive fixture')
            for args in [['init', '-q'], ['add', '.'], ['-c', 'user.name=Archive test', '-c', 'user.email=archive-test@example.invalid', 'commit', '-q', '--no-gpg-sign', '-m', 'Archive fixture']]:
                subprocess.run(['git', *args], cwd=root, check=True, stdout=subprocess.DEVNULL)
            raw = subprocess.check_output(['git', 'archive', '--format=tar', 'HEAD'], cwd=root)
            with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
                names = archive.getnames()
            self.assertIn('SKILL.md', names)
            self.assertIn('tests/example.py', names)
            self.assertFalse(any(n.startswith(('textbooks', 'private', 'references/research')) for n in names))
            self.assertTrue((root / 'textbooks/physics/example.pdf').exists())
