# Contributing

Thanks for helping improve rednote-to-obsidian. Contributions should preserve its focus on personal knowledge management, explicit user authorization, and local credential safety.

## Development setup

```bash
git clone https://github.com/evv0207-dev/rednote-to-obsidian.git
cd rednote-to-obsidian
./setup.sh
.venv/bin/python -m compileall -q scripts
```

There is currently no automated test suite or configured linter. Before opening a pull request, compile all scripts and check the help output for any CLI you changed. Network calls require your own valid Rednote session; never use another person's credentials or include live response data in fixtures.

## Workflow

1. Search existing issues before opening a new one.
2. Create a focused branch from `main`.
3. Keep changes small and avoid unrelated formatting or generated files.
4. Update documentation when commands, configuration, or behavior change.
5. Open a pull request describing the motivation, behavior change, and checks performed.

Use clear Python, type hints where practical, `pathlib` for filesystem work, and actionable error messages. Maintain Python 3.10 compatibility. Do not silently overwrite user notes or weaken the safety guidance.

## Reporting issues safely

Include the operating system, Python version, command shape, and a redacted error message. Never include Cookie values, `xsec_token` values, account identifiers, private vault paths, raw collected notes, or screenshots containing personal information. Replace them with obvious placeholders.

For a suspected credential leak or security issue, revoke the affected session first. Avoid filing a public issue containing exploit details or secrets; use GitHub's private vulnerability reporting feature if enabled for the repository.

## Using Codex

Codex reads [AGENTS.md](AGENTS.md) for repository commands and architecture, and [SKILL.md](SKILL.md) for product behavior. Ask Codex to preserve the privacy and compliance boundaries in `references/safety.md`, and review generated diffs before committing.

By contributing, you agree that your contribution is licensed under the repository's [MIT License](LICENSE).
