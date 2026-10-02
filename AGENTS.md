# rednote-to-obsidian

**Version:** 2.0.0 | **Port:** N/A (CLI) | **Stack:** Python 3.10+, httpx, xiaohongshu-cli, Codex Agent Skill

## What

A Codex Agent Skill that collects a user's own Rednote/Xiaohongshu notes and comments, then turns them into structured Markdown for personal learning and Obsidian archives.

## Quick Start

```bash
./setup.sh
./install-skill.sh --force
.venv/bin/python scripts/rednote_auth.py login
.venv/bin/python scripts/rednote_config.py init --vault /path/to/ObsidianVault
.venv/bin/python scripts/rednote_scraper.py status
```

## Commands

```bash
# Setup and validation
./setup.sh
.venv/bin/python scripts/rednote_config.py check
.venv/bin/python -m compileall -q scripts
.venv/bin/python -m unittest discover -s tests -v

# Search and collection (requires an explicit local CLI session)
.venv/bin/python scripts/rednote_scraper.py search "KEYWORDS" --limit 20
.venv/bin/python scripts/rednote_ingest.py "AUTHOR KEYWORDS" --author "AUTHOR"
.venv/bin/python scripts/rednote_collect_note.py --id NOTE_ID --xsec-token "XSEC_TOKEN" --slug short-name
```

The standard-library `unittest` suite covers authentication selection, response normalization, and Obsidian archive generation. No server or Docker runtime is required.

## Architecture

```text
SKILL.md                       Skill workflow and behavior
agents/openai.yaml             Skill UI metadata and default prompt
scripts/rednote_config.py      Local path configuration
scripts/rednote_auth.py        Explicit QR-saved or legacy-file authentication
scripts/rednote_scraper.py     xiaohongshu-cli client adapter and CLI
scripts/rednote_ingest.py      Search, rank, and collect workflow
scripts/rednote_collect_note.py  Note/comment/image collection
scripts/rednote_markdown.py    Traceable Markdown and Obsidian archive writer
references/                    Setup, safety, routing, and output guidance
```

`rednote_auth.py` reads only a QR-saved session or an explicitly supplied legacy export; it deliberately does not auto-scan browser profiles. The ingest command searches through the upstream client, ranks results, collects assets, and writes a source Markdown archive into the configured vault. Codex can then interpret the material into a richer learning note.

## Key Files

```text
SKILL.md                     Agent instructions and supported modes
requirements.txt            Python runtime dependencies
.env.example                Optional cookie-path environment example
references/setup.md         First-time configuration guide
references/safety.md        Privacy, copyright, and anti-abuse boundaries
references/output-templates.md  Markdown output structures
references/obsidian-routing.md  Suggested vault destinations
```

## Configuration

The preferred configuration is `~/.rednote-to-obsidian/config.json`, created by `rednote_config.py init`. The cookie path can alternatively come from the environment:

| Variable | Required | Description |
|----------|----------|-------------|
| `REDNOTE_COOKIE_FILE` | Conditional | Path to the user's local Cookie-Editor JSON export when no configured cookie path exists |

Never commit cookies, tokens, generated output, or user-specific configuration. Network commands require the user's own authorized Rednote session and may stop working when the platform changes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
