# High School Learning Hub · 高中学习中枢

[简体中文](README.md) · English

A reusable Agent Skill for textbook-led Chinese high-school study, especially the Shanghai curriculum. It supplies teaching rules, blank record templates and Python tools, rather than a standalone tutoring app. Instructional rules and the bundled curriculum are primarily Chinese.

The teaching flow is explanation → textbook example → inquiry → practice → grading → error analysis → remediation → summary. Records distinguish a single observation from repeated evidence; the skill must not invent textbook pages, student answers or mastery.

## Install the rules without downloading textbooks

For agents that discover user skills in `~/.agents/skills/`, use Git sparse checkout:

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/XiaoRui114514/high-school-learning-hub.git ~/.agents/skills/high-school-learning-hub
git -C ~/.agents/skills/high-school-learning-hub sparse-checkout set assets references scripts
```

Cone-mode sparse checkout includes root files such as `SKILL.md` and omits `textbooks/`. Other agents may use a different skills directory. Check their installation instructions; loading a skill does not authorize account access or make private history available across products.

Use your own authorized textbook copies in a private workspace. The full repository also contains publisher-owned PDF/Word materials, excluded from the MIT license and the default publication ZIP. The rules-only installation does not include those files; never claim to have checked a page that is unavailable. Do not redistribute publisher materials without the necessary rights.

## Start a workspace

Python 3.8+; initialization previews changes unless `--apply` is supplied:

```sh
python scripts/init_workspace.py /path/to/private-workspace
python scripts/init_workspace.py /path/to/private-workspace --apply
python scripts/check_workspace.py --root /path/to/private-workspace --mode workspace --json
```

Ask the agent, for example, to study a specific textbook section or review an essay. It should first locate the relevant index/pages and follow [SKILL.md](SKILL.md). Word is the first reading source; original PDF pages resolve pagination, diagrams and transcription uncertainty. Personal grades, answers and progress belong in the private workspace, not this repository.

## Validate and package

```sh
python -m unittest discover -s tests -v
python scripts/check_workspace.py --mode package --json
python scripts/package_skill.py --out /tmp/high-school-learning-hub.zip
```

The explicit [publication allowlist](publication-files.json) controls ZIP contents; the packager checks links and writes a reproducible hash manifest. Add only reusable final rules, scripts or blank templates. Do not add research logs, personal records, credentials or textbooks to the publication archive.

Rules, scripts and documentation use [MIT](LICENSE); textbook copyright remains with the respective publishers. The skill does not guarantee learning outcomes or replace textbook verification.
