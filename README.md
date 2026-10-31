# 高中学习中枢 · Agent Skill

把「高中学习中枢」学习工作区的运行规则打包成一个可复用的 Agent Skill。核心是五件事：

- **教材驱动**：以官方教材为唯一知识结构基准，按节推进，不整本扫描。
- **一次一个点**：每轮只讲一个知识点或一道题，讲完停下等确认。
- **记得有价值的信息**：原始记录、讲题提示卡、长期记忆、错题分层管理，有证据门槛。
- **英语写作专用流程**：审题 → 整体评价 → 逐句批改 → 错因 → 分层修改 → 记录进展，不伪造官方分数。
- **不伪造**：不虚构页码、板块、学习记录或掌握程度。

适合高中阶段（尤其上海教材体系）的日常学习：按教材开新课、讲题答疑、出题、批改、英语作文、复习、错题整理、学习记录维护。

## 安装

DeepSeek Harness / Codex 等使用 `~/.dsh/skills/` 的环境：

```powershell
git clone https://github.com/XiaoRui114514/high-school-learning-hub.git "$env:USERPROFILE\.dsh\skills\high-school-learning-hub"
```

macOS / Linux：

```bash
git clone https://github.com/XiaoRui114514/high-school-learning-hub.git ~/.dsh/skills/high-school-learning-hub
```

其他兼容 `SKILL.md` 的 Agent：把本仓库放进它的 skills 目录，目录名保持 `high-school-learning-hub`。若环境只读 `name` / `description` 两个 frontmatter 字段，可忽略 `whenToUse`。

> 仓库包含四科教材（PDF + Word），克隆约 305MB；首次下载会慢一些。

## 使用

安装后，当任务涉及以下内容时会自动匹配（也可以直接点名 `high-school-learning-hub`）：

- 「开始学习 数学 1.1」「按教材讲这一节」
- 「这道题教我一下」「教我咋推」
- 「帮我复习集合」「帮我改一下」
- 「批改这篇英语作文」「写作训练」
- 「整理错题」「更新学习记录」
- 「检查工作区」「维护高中学习中枢」

示例：

```text
开始学习 数学 1.1
```

Agent 应先读 `textbooks/01_数学/01_官方教材/INDEX.md`（有工作区时读工作区同名文件）定位，再只打开对应教材页，先说明本节的真实板块与页码，然后一次只推进一个知识点。

## 目录

```text
.
├─ SKILL.md                       # 主规则（Agent 加载入口）
├─ README.md                      # 本文件
├─ references/
│  ├─ teaching-flow.md            # 教材教学、讲题、批改、复习的展开流程
│  ├─ memory-rules.md             # 记忆分层、证据门槛、掌握判定与维护
│  ├─ workspace-map.md            # 目录结构、关键文件、命名与页码规则
│  └─ english-writing.md          # 英语作文批改、评分边界、错因与训练路线
├─ assets/templates/
│  ├─ 学习记录模板.md
│  └─ 错题模板.md
├─ textbooks/                     # 四科教材：PDF + Word + INDEX + 教材信息
│  ├─ 01_数学/01_官方教材/
│  ├─ 02_物理/01_官方教材/
│  ├─ 03_化学/01_官方教材/
│  └─ 04_英语/01_官方教材/
└─ scripts/
   ├─ check_workspace.py          # 工作区自检
   ├─ extract_textbook_page.py    # 按页码提取 PDF 文字 / 渲染页面
   └─ extract_word_text.py        # 提取 Word 文字 / 表格（目录、关键词、段落范围）
```

## 工作区要求

Skill 假设存在一个「高中学习中枢」工作区，根目录包含：

```text
AGENTS.md
README.md
00_学习控制中心/
01_数学/  02_物理/  03_化学/  04_英语/
05_跨学科学习记录/  06_公共错题与复习/  07_公共资料/  08_系统工具/
```

如果工作区里已有 `AGENTS.md` / `AGENT_INSTRUCTIONS.md` / `MEMORY_RULES.md`，以工作区原文件为准；本 Skill 是这些规则的**去个人化、可移植版本**。没有工作区时，也可以直接用自带的 `textbooks/` 阅读教材；但学习记录、进度、错题仍需要建立工作区后再写，不能凭空引用。

脚本依赖 Python 3.8+：

```powershell
py -3 -m pip install pypdf pypdfium2 pillow
```

## 教材阅读顺序：Word 优先，PDF 校对

仓库自带四科教材，`Word/` 是日常阅读首选，`PDF/` 是原版校对与页码依据：

- `Word/`：文字、定义、公式、关键词、例题/练习文字优先从 Word 读取。
- `PDF/`：Word 识别不到、缺字/乱码、表格/图片/公式不清或内容有误时，回 PDF 原页核对。
- 教材页码、图片、实验、例题/练习排版与最终校对以 PDF 为准；Word 的页码/排版不可当作教材页码引用。
- Word 与 PDF 冲突时，以 PDF 原版为准。

自带教材路径：`textbooks/0X_学科/01_官方教材/{PDF,Word}/`，每科另有 `INDEX.md` 与 `教材信息/`。

读 Word 时不要直接打开整份文件；用脚本按目录、关键词或段落取文字：

```powershell
py -3 scripts/extract_word_text.py "textbooks/01_数学/01_官方教材/Word/数学必修第一册_沪教版_上海教育出版社_2020年7月第1版.docx" --outline
py -3 scripts/extract_word_text.py <DOCX> --grep "集合" --context 1
py -3 scripts/extract_word_text.py <DOCX> --start 76 --end 95
```

## 边界

- 本仓库包含四科教材 PDF/Word 与规则/工具；**不包含**个人学习记录、账号信息或隐私数据。
- 教材版权归原出版社所有，仅限个人学习使用；请勿再分发或用于商业用途。
- 资源获取遵循「尽合理范围搜索 → 验证 → 成功则保存，失败则停止」，不绕过登录、付费或权限限制。

## 来源

规则提炼自「高中学习中枢」工作区的 `AGENTS.md`、`00_学习控制中心/AGENT_INSTRUCTIONS.md`、`MEMORY_RULES.md`、`README.md`、`01_官方教材/说明.md`、`04_英语/09_英语写作提升/README.md` 与各学科 `00_学科记忆/PROFILE.md`。教材文件由用户提供，整理日期：2026-10-25。

## 更新记录

- 2026-10-25 v1.2：教材 PDF/Word 随仓库分发；阅读顺序改为 Word 优先、PDF 校对。
- 2026-10-25 v1.1：增加 Word 版使用边界、教材上传与版本变更流程、英语写作专用流程与参考文件。
- 2026-10-25 v1.0：初版，提炼工作区规则并上传。

## License

规则、文档与脚本采用 MIT；`textbooks/` 中的教材版权归原出版社，不在 MIT 授权范围内。
