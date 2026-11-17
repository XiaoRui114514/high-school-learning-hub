"""Publish the existing allowlist to an append-only, textbook-free rules branch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from package_skill import publication_files

ROOT = Path(__file__).resolve().parents[1]
BRANCH = 'rules'
REPOSITORY = 'XiaoRui114514/high-school-learning-hub'


def stage_rules(root, destination):
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Distribution destination must be empty')
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, source in publication_files(root):
        content = source.read_bytes()
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        manifest[name] = hashlib.sha256(content).hexdigest()
    (destination / 'PUBLICATION.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


def git(root, *args, data=None, env=None, check=True):
    return subprocess.run(['git', *args], cwd=root, input=data, capture_output=True,
                          env=env, check=check).stdout


def publish(root, staged, manifest):
    remote = git(root, 'remote', 'get-url', 'origin').decode().strip()
    if remote.endswith('.git'):
        remote = remote[:-4]
    if remote not in ['https://github.com/' + REPOSITORY, 'git@github.com:' + REPOSITORY]:
        raise ValueError('Publication is restricted to the configured source repository')
    if git(root, 'status', '--porcelain', '--untracked-files=no').strip():
        raise ValueError('Commit tracked source changes before publishing')
    source = git(root, 'rev-parse', 'HEAD').decode().strip()
    if source != git(root, 'rev-parse', 'origin/main').decode().strip():
        raise ValueError('Publish only the checked main source commit')
    refs = git(root, 'ls-remote', '--heads', 'origin', 'refs/heads/' + BRANCH).decode().split()
    previous = refs[0] if refs else None
    if previous:
        git(root, 'fetch', '--no-tags', '--depth=1', 'origin', 'refs/heads/' + BRANCH)
        message = git(root, 'show', '-s', '--format=%B', previous).decode()
        if 'Rules-Source: ' not in message:
            raise ValueError('Existing rules branch is not managed by this publisher')
        old = json.loads(git(root, 'show', previous + ':PUBLICATION.json'))
        names = set(git(root, 'ls-tree', '-rz', '--name-only', previous).decode().strip('\0').split('\0'))
        if names != set(old) | {'PUBLICATION.json'}:
            raise ValueError('Existing rules branch has unexpected files; keep it unchanged')
        for name, digest in old.items():
            if hashlib.sha256(git(root, 'show', previous + ':' + name)).hexdigest() != digest:
                raise ValueError('Existing distribution differs from its manifest')
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'),
                   GIT_AUTHOR_NAME='github-actions[bot]', GIT_COMMITTER_NAME='github-actions[bot]',
                   GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',
                   GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
        git(root, 'read-tree', '--empty', env=env)
        for name in sorted([*manifest, 'PUBLICATION.json']):
            blob = git(root, 'hash-object', '-w', '--stdin', data=(Path(staged) / name).read_bytes()).decode().strip()
            git(root, 'update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + name, env=env)
        tree = git(root, 'write-tree', env=env).decode().strip()
        if previous and tree == git(root, 'rev-parse', previous + '^{tree}').decode().strip():
            return {'changed': False, 'commit': previous, 'source': source}
        args = ['commit-tree', tree] + (['-p', previous] if previous else [])
        commit = git(root, *args, data=('Update reusable skill package\n\nRules-Source: ' + source + '\n').encode(), env=env).decode().strip()
        # Fast-forward only: concurrent or unmanaged changes are never overwritten.
        git(root, 'push', 'origin', commit + ':refs/heads/' + BRANCH)
        return {'changed': True, 'commit': commit, 'source': source}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--publish', action='store_true')
    args = ap.parse_args()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            destination = args.out or Path(tmp) / 'rules'
            manifest = stage_rules(args.root, destination)
            result = publish(args.root, destination, manifest) if args.publish else {'published': False}
            print(json.dumps({'branch': BRANCH, 'files': len(manifest) + 1, **result}, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        # Do not print Git subprocess stderr, which may include access details.
        reason = str(error) if isinstance(error, ValueError) else type(error).__name__
        ap.exit(1, reason + ': rules publication stopped; source and existing branch retained.\n')


if __name__ == '__main__':
    main()
