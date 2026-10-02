# Setup

## First-Time User Flow

Goal: configure once, then allow one-sentence Rednote learning requests.

1. Prefer the Codex in-app browser. Open Xiaohongshu visibly and let the user use the site's QR login only if required.
2. Never inspect or export the browser's cookies or storage.
3. Ask for the Obsidian vault path and save it.

For CLI-only environments, run the explicit terminal QR-code login:

```bash
.venv/bin/python scripts/rednote_auth.py login
.venv/bin/python scripts/rednote_config.py init --vault /path/to/ObsidianVault
```

4. Check config and saved session:

```bash
.venv/bin/python scripts/rednote_config.py check
.venv/bin/python scripts/rednote_auth.py check
```

5. Check login:

```bash
.venv/bin/python scripts/rednote_scraper.py status
```

## Required Dependencies

The scripts require:

- Python 3.10+
- `httpx`
- `xiaohongshu-cli` (imported as `xhs_cli`) with `xhs_cli.signing`

If the local system Python lacks dependencies, use an existing Python environment that has them or help the user install dependencies in a virtual environment. Do not hardcode one user's local Python path in the public skill.

## Config File

The skill stores local settings here:

```text
~/.rednote-to-obsidian/config.json
```

Expected shape:

```json
{
  "obsidian_vault": "/path/to/ObsidianVault",
  "output_dir": "outputs/rednote-notes"
}
```

The CLI QR session is stored separately by `xiaohongshu-cli` with restricted permissions. Never commit or share it. A Cookie-Editor export remains an optional legacy compatibility path via `--cookies`. Browser-mode sessions remain inside the in-app browser and are never copied into the CLI.

## Daily Use Examples

One note:

```bash
.venv/bin/python scripts/rednote_ingest.py "夏小懒瓜 字节国际电商 数分 二三面" --author "夏小懒瓜"
```

Manual search:

```bash
.venv/bin/python scripts/rednote_scraper.py search "字节国际电商 数分 二三面" --limit 20
```

Manual read:

```bash
.venv/bin/python scripts/rednote_scraper.py read NOTE_ID "XSEC_TOKEN" --raw
```

Manual comments:

```bash
.venv/bin/python scripts/rednote_scraper.py comments NOTE_ID "XSEC_TOKEN"
```
