"""Preview missing workspace files; --apply creates only missing, blank files."""
import argparse
from pathlib import Path
import check_workspace as schema

ROOT = Path(__file__).resolve().parents[1]


def initialize(root, apply=False):
    root = Path(root).absolute()
    if root == ROOT or ROOT in root.parents:
        raise ValueError('个人工作区不能建在技能包内')
    files = {'README.md': '# 高中学习中枢\n\n个人学习工作区；未填项目均待确认。\n',
             'AGENTS.md': '# 工作区规则\n\n遵循已安装的 high-school-learning-hub 技能；只记录有证据的学习事实。\n'}
    for name in schema.CTRL_FILES:
        files['00_学习控制中心/' + name] = '' if name.endswith('.log') else '# ' + name[:-3] + '\n\n待填写；暂无学习证据。\n'
    for subject in schema.SUBJECTS:
        for name in schema.MEM_FILES:
            files[subject + '/00_学科记忆/' + name] = '# ' + name[:-3] + '\n\n待填写；不代表已学习或已掌握。\n'
        for name in schema.TB_FILES + ['目录说明.md', '08_讲题提示/提示卡.md']:
            files[subject + '/' + name] = '# 待填写\n\n教材版本、页码与学习事实须核验后填写。\n'
    for name in ['README.md', '上海高中英语写作要求与评分依据.md', '训练路线.md', '我的写作笔记.md', '作文练习记录.md']:
        files['04_英语/09_英语写作提升/' + name] = '# 英语写作\n\n遵循已安装技能 references/english-writing.md。暂无个人学习记录；未配置可核验的官方完整评分细则时，只给训练性评价。\n'
    for name in schema.PUBLIC_FILES:
        files.setdefault(name, '# 待填写\n' if name.endswith('.md') else '')
    tools = {'检查工作区.py': 'check_workspace.py', '提取教材页.py': 'extract_textbook_page.py', '提取Word文字.py': 'extract_word_text.py'}
    for dest, src in tools.items():
        files['08_系统工具/' + dest] = (ROOT/'scripts'/src).read_text(encoding='utf-8')
    files['08_系统工具/运行自检.cmd'] = '@echo off\nchcp 65001 >nul\ncd /d "%~dp0.."\npy -3 "08_系统工具/检查工作区.py" --mode workspace\n'
    for name in ['学习记录模板.md', '错题模板.md']:
        files['00_学习控制中心/模板/' + name] = (ROOT/'assets/templates'/name).read_text(encoding='utf-8')
    for directory in schema.ROOT_DIRS + [s+'/'+d for s in schema.SUBJECTS for d in schema.SUB_DIRS]:
        target = root/directory
        if any(p.is_symlink() for p in [target, *target.parents]):
            raise ValueError('工作区路径含符号链接：' + str(target))
        if apply:
            target.mkdir(parents=True, exist_ok=True)
    missing = []
    for name, content in files.items():
        path = root/name
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError('工作区路径含符号链接：' + name)
        if path.exists():
            continue
        missing.append(name)
        if apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x', encoding='utf-8') as stream:
                stream.write(content)
    return missing


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root', type=Path)
    ap.add_argument('--apply', action='store_true', help='默认仅预览；此参数只创建缺失项')
    a = ap.parse_args()
    try:
        for path in initialize(a.root, a.apply):
            print(('创建：' if a.apply else '将创建：') + path)
    except (OSError, ValueError) as error:
        ap.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
