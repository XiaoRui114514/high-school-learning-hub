"""Publish one explicitly requested, allowlisted rules-package prerelease."""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from package_skill import ROOT
from publish_rules import REPOSITORY, git

NOTES = """A versioned package of the reusable teaching rules, reference documents,
blank templates and Python tools.

- Includes a per-file SHA-256 manifest and archive checksum.
- Excludes textbooks, private study records and research logs. Supply your own authorized textbook copies.
- The generated `rules` branch supports lightweight Git installation and updates; contribute source changes to `main`.

This prerelease packages the current rules. Loading it requires a compatible agent;
Python tools require Python 3.8+. It does not authorize accounts, synchronize private
records across products or establish learning outcomes. The existing license scope is unchanged.
"""


def validate_tag(tag):
    if not re.fullmatch(r'rules-\d{4}\.\d{2}\.\d{2}(?:\.\d+)?', tag or ''):
        raise ValueError('Use a new rules-YYYY.MM.DD or rules-YYYY.MM.DD.N tag')
    return tag


def build_assets(root, destination):
    destination = Path(destination)
    archive = destination / 'high-school-learning-hub-rules.zip'
    subprocess.run([sys.executable, str(root / 'scripts/package_skill.py'),
                    '--root', str(root), '--out', str(archive)], check=True,
                   stdout=subprocess.DEVNULL)
    checksum = destination / 'SHA256SUMS'
    checksum.write_text(hashlib.sha256(archive.read_bytes()).hexdigest() +
                        '  ' + archive.name + '\n', encoding='utf-8')
    return archive, checksum


def main():
    try:
        tag = validate_tag(os.environ.get('RELEASE_TAG'))
        # This operation is only offered by an explicit dispatch on the source repository.
        if (os.environ.get('GITHUB_REPOSITORY') != REPOSITORY or
                os.environ.get('GITHUB_REF') != 'refs/heads/main' or
                os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch'):
            raise ValueError('Release publishing requires a dispatch on the source main branch')
        source = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
        if (source != git(ROOT, 'rev-parse', 'origin/main').decode().strip() or
                git(ROOT, 'status', '--porcelain', '--untracked-files=no').strip()):
            raise ValueError('Publish only a clean, checked main source commit')
        if git(ROOT, 'ls-remote', '--tags', 'origin', 'refs/tags/' + tag).strip():
            raise ValueError('Tag already exists; existing versions are never replaced')
        with tempfile.TemporaryDirectory() as tmp:
            archive, checksum = build_assets(ROOT, Path(tmp))
            notes = Path(tmp) / 'notes.md'
            notes.write_text(NOTES, encoding='utf-8')
            # gh refuses duplicate releases; never use --clobber or delete existing assets.
            subprocess.run(['gh', 'release', 'create', tag, str(archive), str(checksum),
                            '--repo', REPOSITORY, '--target', source, '--prerelease',
                            '--title', 'Rules package ' + tag[len('rules-'):],
                            '--notes-file', str(notes)], check=True)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        reason = str(error) if isinstance(error, ValueError) else type(error).__name__
        sys.exit(reason + ': rules release stopped; existing versions retained.')


if __name__ == '__main__':
    main()
