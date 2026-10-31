import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from init_workspace import initialize
from package_skill import publication_files

class WorkspaceToolsTests(unittest.TestCase):
    def test_preview_and_repeat_apply_preserve_user_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'study'
            self.assertTrue(initialize(root))
            self.assertFalse(root.exists())
            initialize(root, True)
            record = root/'01_数学/00_学科记忆/PROGRESS.md'
            record.write_text('existing progress', encoding='utf-8')
            self.assertEqual(initialize(root, True), [])
            self.assertEqual(record.read_text(), 'existing progress')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/check_workspace.py'), '--root', str(root), '--mode', 'workspace', '--json'],capture_output=True,text=True)
            report = json.loads(result.stdout)
            self.assertIn('problems', report)
            self.assertTrue(all('教材 PDF 缺失' in p or '教材 Word 缺失' in p for p in report['problems']))
    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'study'; root.mkdir()
            (root/'01_数学').symlink_to(Path(tmp),target_is_directory=True)
            with self.assertRaises(ValueError): initialize(root, True)
    def test_package_excludes_unlisted_and_rejects_private_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'SKILL.md').write_text('safe')
            (root/'private').mkdir(); (root/'private/secret.md').write_text('private')
            (root/'publication-files.json').write_text('["SKILL.md"]')
            self.assertEqual([n for n,_ in publication_files(root)], ['SKILL.md'])
            (root/'publication-files.json').write_text('["private/secret.md"]')
            with self.assertRaises(ValueError): publication_files(root)
    def test_package_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('one.zip','two.zip'):
                subprocess.run([sys.executable,str(ROOT/'scripts/package_skill.py'),'--out',str(Path(tmp)/name)],check=True,stdout=subprocess.DEVNULL)
            self.assertEqual((Path(tmp)/'one.zip').read_bytes(), (Path(tmp)/'two.zip').read_bytes())
            with zipfile.ZipFile(Path(tmp)/'one.zip') as archive:
                self.assertFalse(any(n.startswith(('textbooks/','references/research/','private/')) for n in archive.namelist()))
