# 高中学习中枢 · Agent Skill

把「高中学习中枢」学习工作区的运行规则打包成一个可复用的 Agent Skill。核心是四件事：

- **教材驱动**：以官方教材为唯一知识结构基准，按节推进，不整本扫描。
- **一次一个点**：每轮只讲一个知识点或一道题，讲完停下等确认。
- **记得有价值的信息**：原始记录、讲题提示卡、长期记忆、错题分层管理，有证据门槛。
- **不伪造**：不虚构页码、板块、学习记录或掌握程度。

适合高中阶段（尤其上海教材体系）的日常学习：按教材开新课、讲题答疑、出题、批改、复习、错题整理、学习记录维护。

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

## 使用

安装后，当任务涉及以下内容时会自动匹配（也可以直接点名 `high-school-learning-hub`）：

- 「开始学习 数学 1.1」「按教材讲这一节」
- 「这道题教我一下」「教我咋推」
- 「帮我复习集合」「帮我改一下」
- 「整理错题」「更新学习记录」
- 「检查工作区」「维护高中学习中枢」

示例：

```text
开始学习 数学 1.1
```

Agent 应先读 `01_数学/01_官方教材/INDEX.md` 定位，再只打开对应教材页，先说明本节的真实板块与页码，然后一次只推进一个知识点。

## 目录

```text
.
├─ SKILL.md                       # 主规则（Agent 加载入口）
├─ README.md                      # 本文件
├─ references/
│  ├─ teaching-flow.md            # 教材教学、讲题、批改、复习的展开流程
│  ├─ memory-rules.md             # 记忆分层、证据门槛、掌握判定与维护
│  └─ workspace-map.md            # 目录结构、关键文件、命名与页码规则
├─ assets/templates/
│  ├─ 学习记录模板.md
│  └─ 错题模板.md
└─ scripts/
   ├─ check_workspace.py          # 工作区自检
   └─ extract_textbook_page.py    # 按页码提取教材文字 / 渲染页面
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

如果工作区里已有 `AGENTS.md` / `AGENT_INSTRUCTIONS.md` / `MEMORY_RULES.md`，以工作区原文件为准；本 Skill 是这些规则的**去个人化、可移植版本**。没有工作区时，也可以只把 `SKILL.md` 当作教学规则使用，但涉及页码、进度、错题时必须先建立工作区，不能凭空引用。

脚本依赖 Python 3.8+：

```powershell
py -3 -m pip install pypdf pypdfium2 pillow
```

## 边界

- 本仓库**不包含**任何个人学习记录、教材 PDF、账号信息或隐私数据。
- 教材版权归原出版社所有；本仓库只包含规则与工具，不分发教材。
- 资源获取遵循「尽合理范围搜索 → 验证 → 成功则保存，失败则停止」，不绕过登录、付费或权限限制。

## 来源

规则提炼自「高中学习中枢」工作区的 `AGENTS.md`、`00_学习控制中心/AGENT_INSTRUCTIONS.md`、`MEMORY_RULES.md`、`README.md` 与各学科 `00_学科记忆/PROFILE.md`。整理日期：2026-10-25。

## License

MIT
