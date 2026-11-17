"""Build a reproducible, explicitly allowlisted skill archive (no private records)."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DENIED = ('references/research', 'private', 'worklogs', '.git', 'textbooks')


def publication_files(root):
    root = Path(root).resolve()
    names = json.loads((root / 'publication-files.json').read_text(encoding='utf-8'))
    if not isinstance(names, list) or not names or len(names) != len(set(names)):
        raise ValueError('发布白名单必须是非空、无重复的文件列表')
    files = []
    for name in names:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name or any(name == d or name.startswith(d + '/') for d in DENIED):
            raise ValueError('不允许公开的路径：' + name)
        target = root / name
        if any(part.is_symlink() for part in [target, *target.parents]) or not target.is_file() or root not in target.resolve().parents:
            raise ValueError('文件缺失、越界或为符号链接：' + name)
        if target.suffix == '.md':
            text = target.read_text(encoding='utf-8')
            for dest in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if re.match(r'[a-zA-Z]+:', dest) or dest.startswith('#'):
                    continue
                linked = target.parent / dest.split('#', 1)[0]
                if not linked.is_file() or root not in linked.resolve().parents:
                    raise ValueError('公开文档链接缺失或越界：' + dest)
                rel = linked.relative_to(root).as_posix()
                if rel not in names:
                    raise ValueError('公开链接指向未发布文件：' + rel)
        files.append((name, target))
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--out', type=Path, help='不指定时只检查并显示最终文件清单')
    a = ap.parse_args()
    try:
        files = publication_files(a.root)
        manifest = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files}
        if a.out:
            if a.out.resolve() in [path.resolve() for _, path in files]:
                raise ValueError('输出不能覆盖发布输入')
            a.out.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED) as archive:
                for name, path in files:
                    info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, path.read_bytes())
                archive.writestr(zipfile.ZipInfo('PUBLICATION.json', (2026, 1, 1, 0, 0, 0)), json.dumps(manifest, ensure_ascii=False, indent=2))
        print(json.dumps({'ok': True, 'files': manifest}, ensure_ascii=False, indent=2))
    except (ValueError, OSError, TypeError) as error:
        ap.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
