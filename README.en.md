# High School Learning Hub · 高中学习中枢

[简体中文](README.md) · English

A reusable Agent Skill for textbook-led Chinese high-school study, especially the Shanghai curriculum. It supplies teaching rules, blank record templates and Python tools, rather than a standalone tutoring app. Instructional rules and the bundled curriculum are primarily Chinese.

The teaching flow is explanation → textbook example → inquiry → practice → grading → error analysis → remediation → summary. Records distinguish a single observation from repeated evidence; the skill must not invent textbook pages, student answers or mastery.

## Install the rules without downloading textbooks

For agents that discover user skills in `~/.agents/skills/`, install the generated, textbook-free `rules` branch:

```sh
git clone --depth 1 --single-branch --branch rules https://github.com/XiaoRui114514/high-school-learning-hub.git ~/.agents/skills/high-school-learning-hub
```

The [rules branch](https://github.com/XiaoRui114514/high-school-learning-hub/tree/rules) contains only the publication allowlist plus a SHA-256 manifest. Update it with `git -C ~/.agents/skills/high-school-learning-hub pull --ff-only`. Keep personal records in a separate private workspace; do not edit the generated branch. Contribute reusable changes to `main`. Other agents may use a different installation directory.

For a versioned ZIP, use the [rules package releases](https://github.com/XiaoRui114514/high-school-learning-hub/releases), verify `SHA256SUMS`, and extract into your agent's supported skills directory. Loading a skill does not authorize accounts or share private history between products.

An ordinary clone of `main` still includes textbooks. GitHub source ZIP/tar archives now omit `textbooks/`; the generated rules branch and explicit release ZIP are the bounded installation paths. Do not use an unrestricted recursive installer on the main repository root.

Use your own authorized textbook copies in a private workspace. The full repository also contains publisher-owned PDF/Word materials, excluded from the MIT license and the rules distribution, source archives and explicit publication ZIP. The rules-only installation does not include those files; never claim to have checked a page that is unavailable. Do not redistribute publisher materials without the necessary rights.

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
