# -*- coding: utf-8 -*-
"""工作区自检：目录结构、必需文件、公共文件与模板、教材完整性、重复文件、空目录。

用法：在「高中学习中枢」工作区根目录运行
  py -3 scripts/check_workspace.py
（Windows 上 python 命令可能未加入 PATH 时用 py -3；本脚本来自 skill 的 scripts/ 目录。）
"""
import hashlib, os, sys

# 统一输出编码：管道 / 重定向读取时避免中文乱码（真实控制台输出不受影响）
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SUBJECTS = ["01_数学", "02_物理", "03_化学", "04_英语"]
ROOT_DIRS = ["00_学习控制中心", "05_跨学科学习记录", "06_公共错题与复习", "07_公共资料", "08_系统工具"]
SUB_DIRS = ["00_学科记忆", "01_官方教材", "01_官方教材/PDF", "01_官方教材/Word", "01_官方教材/教材信息",
            "02_课程标准", "03_教案与教学参考", "04_章节资料", "05_错题", "06_学习记录", "07_拓展资料", "08_讲题提示"]
CTRL_FILES = ["AGENT_INSTRUCTIONS.md", "MEMORY_RULES.md", "USER_PROFILE.md", "LEARNING_MEMORY.md",
              "CURRENT_STATUS.md", "LEARNING_HABITS.md", "LONG_TERM_GOALS.md", "GENERAL_WEAKNESSES.md",
              "GENERAL_STRENGTHS.md", "LEARNING_HISTORY.md", "WORKSPACE_STATUS.md", "resource_acquisition.log"]
MEM_FILES = ["PROFILE.md", "PROGRESS.md", "KNOWLEDGE_MAP.md", "WEAKNESSES.md", "STRENGTHS.md",
             "HABITS.md", "COMMON_MISTAKES.md", "REVIEW_PLAN.md"]
TB_FILES = ["01_官方教材/INDEX.md", "01_官方教材/说明.md", "01_官方教材/教材信息/教材信息.md",
            "01_官方教材/教材信息/当前版本.md", "01_官方教材/教材信息/版本变更记录.md"]
SUB_ROOT_FILES = ["目录说明.md"]
PUBLIC_FILES = ["05_跨学科学习记录/INDEX.md", "06_公共错题与复习/公共错题.md",
                "06_公共错题与复习/复习调度.md", "07_公共资料/资料登记表.md",
                "00_学习控制中心/模板/学习记录模板.md", "00_学习控制中心/模板/错题模板.md",
                "08_系统工具/工具说明.md", "08_系统工具/检查工作区.py", "08_系统工具/提取教材页.py",
                "08_系统工具/提取Word文字.py", "08_系统工具/运行自检.cmd"]

ok, problems, notes = [], [], []


def check(cond, good, bad):
    (ok if cond else problems).append(good if cond else bad)


def main():
    root = os.getcwd()
    print("工作区：%s\n" % root)
    check(os.path.isfile("README.md"), "根 README.md 存在", "缺少根 README.md")
    for d in ROOT_DIRS:
        check(os.path.isdir(d), "目录存在：%s" % d, "缺少目录：%s" % d)
    for s in SUBJECTS:
        check(os.path.isdir(s), "学科目录存在：%s" % s, "缺少学科目录：%s" % s)
        for f in SUB_ROOT_FILES:
            p = os.path.join(s, f)
            check(os.path.isfile(p), "学科说明存在：%s" % p, "缺少学科说明：%s" % p)
        for d in SUB_DIRS:
            p = os.path.join(s, d)
            check(os.path.isdir(p), "目录存在：%s" % p, "缺少目录：%s" % p)
        for f in MEM_FILES:
            p = os.path.join(s, "00_学科记忆", f)
            check(os.path.isfile(p), "记忆文件存在：%s" % p, "缺少记忆文件：%s" % p)
        prompt_card = os.path.join(s, "08_讲题提示", "提示卡.md")
        check(os.path.isfile(prompt_card), "讲题提示卡存在：%s" % prompt_card, "缺少讲题提示卡：%s" % prompt_card)
        for f in TB_FILES:
            p = os.path.join(s, f)
            check(os.path.isfile(p), "教材文件存在：%s" % p, "缺少教材文件：%s" % p)
        pdf_dir = os.path.join(s, "01_官方教材", "PDF")
        pdfs = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")] if os.path.isdir(pdf_dir) else []
        check(bool(pdfs), "教材 PDF：%s（%d 个）" % (s, len(pdfs)), "教材 PDF 缺失：%s" % s)
        word_dir = os.path.join(s, "01_官方教材", "Word")
        words = [f for f in os.listdir(word_dir) if f.lower().endswith(".docx")] if os.path.isdir(word_dir) else []
        check(bool(words), "教材 Word：%s（%d 个）" % (s, len(words)), "教材 Word 缺失：%s" % s)
        for f in words:
            p = os.path.join(word_dir, f)
            size = os.path.getsize(p)
            if size < 100 * 1024:
                problems.append("教材 Word 过小，可能损坏：%s（%d 字节）" % (p, size))
            else:
                ok.append("教材 Word 大小正常：%s（%.1f MB）" % (p, size / 1024 / 1024))
    for f in CTRL_FILES:
        p = os.path.join("00_学习控制中心", f)
        check(os.path.isfile(p), "控制中心文件存在：%s" % f, "缺少控制中心文件：%s" % f)
    for f in PUBLIC_FILES:
        check(os.path.isfile(f), "公共文件存在：%s" % f, "缺少公共文件：%s" % f)

    # PDF 完整性与重复
    hashes, sizes = {}, []
    try:
        import pypdf
        have_pypdf = True
    except ImportError:
        have_pypdf = False
        notes.append("未安装 pypdf，跳过 PDF 页数校验（py -3 -m pip install pypdf）")
    for s in SUBJECTS:
        pdf_dir = os.path.join(s, "01_官方教材", "PDF")
        if not os.path.isdir(pdf_dir):
            continue
        for f in sorted(os.listdir(pdf_dir)):
            if not f.lower().endswith(".pdf"):
                continue
            p = os.path.join(pdf_dir, f)
            size = os.path.getsize(p)
            sizes.append((p, size))
            h = hashlib.md5(open(p, "rb").read(1 << 20)).hexdigest()
            hashes.setdefault(h, []).append(p)
            if size < 100 * 1024:
                problems.append("教材文件过小，可能损坏：%s（%d 字节）" % (p, size))
            else:
                ok.append("教材大小正常：%s（%.1f MB）" % (p, size / 1024 / 1024))
            if have_pypdf:
                try:
                    n = len(pypdf.PdfReader(p).pages)
                    ok.append("PDF 可打开：%s（%d 页）" % (f, n))
                except Exception as e:
                    problems.append("PDF 打开失败：%s（%s）" % (p, e))
    for h, ps in hashes.items():
        if len(ps) > 1:
            problems.append("疑似重复文件（首块哈希相同）：%s" % "；".join(ps))

    # 空目录（排除已由说明文件解释的目录）
    for dp, dn, fn in os.walk("."):
        if os.path.basename(dp).startswith("."):
            continue
        if not dn and not fn:
            notes.append("空目录（如无内容可忽略）：%s" % dp)

    print("通过 %d 项" % len(ok))
    for x in ok:
        print("  [OK] %s" % x)
    print("\n问题 %d 项" % len(problems))
    for x in problems:
        print("  [!!] %s" % x)
    print("\n提示 %d 项" % len(notes))
    for x in notes:
        print("  [--] %s" % x)
    if os.environ.get("WORKSPACE_CHECK_WAIT") == "1":
        print("\n窗口将在 60 秒后自动关闭（按任意键立即关闭）。")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
