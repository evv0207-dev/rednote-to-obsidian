---
name: rednote-to-obsidian
description: Rednote/Xiaohongshu note ingestion and Obsidian knowledge-base workflow. Use when the user wants Codex to search, collect, learn, summarize, transcribe images, extract comments, or archive a Rednote/XHS/Xiaohongshu note, creator, topic, interview experience, course-like post, or saved content into Obsidian/Markdown. Also use when the user asks to configure a reusable one-command Rednote-to-Obsidian setup.
---

# Rednote To Obsidian

Turn Rednote/Xiaohongshu notes into structured Markdown study documents and Obsidian knowledge-base entries. Prefer personal learning, research, and archival use; do not help users impersonate, mass-republish, or monetize others' content.

## Modes

Use one of three modes:

1. **Setup**: user is new or says "configure/install/setup this skill".
2. **Ingest one note**: user gives a title, author, URL, screenshot, or query and wants one note learned/summarized/archived.
3. **Batch learning**: user gives a creator or topic and wants many notes categorized into a deep-learning document.

Read relevant references only when needed:

- Setup details: `references/setup.md`
- Safety and sharing boundaries: `references/safety.md`
- Output templates: `references/output-templates.md`
- Obsidian routing: `references/obsidian-routing.md`

## Preferred Collection Path

When the Codex in-app browser is available, prefer it over cookie-based CLI collection:

1. Open `https://www.xiaohongshu.com/` in the in-app browser and make it visible.
2. If the page asks for login, let the user scan the site's own QR code. Never ask for a password or inspect browser cookie/session storage.
3. Search through the visible site UI or a focused search URL.
4. Open the selected note and read the visible title, author, body, tags, images, and comments.
5. Build the learning Markdown and write it to the configured vault. Preserve the source URL.

Use the Python CLI path only when browser collection is unavailable or the user explicitly wants automation. The browser path and CLI path must produce the same learning-document structure.

## Setup Mode

First-time Codex users should use the in-app browser and the site's visible QR login when needed, then configure an Obsidian vault. Do not ask for the user's password. Do not inspect or export browser cookies. For CLI-only use, the explicit terminal QR flow stores a separate local session. Never invoke automatic browser-cookie scanning without a separate explicit user request.

For CLI-only use, run login and configuration with the repository virtual environment:

```bash
.venv/bin/python scripts/rednote_auth.py login
.venv/bin/python scripts/rednote_config.py init --vault /path/to/ObsidianVault
```

Then verify:

```bash
.venv/bin/python scripts/rednote_config.py check
.venv/bin/python scripts/rednote_scraper.py status
```

If Python dependencies are missing, help the user create an environment with `httpx` and the `xiaohongshu-cli` distribution (imported as `xhs_cli`), or use their existing environment that already provides them. Network calls to Rednote may require explicit user approval in sandboxed Codex sessions.

## Ingest One Note

When the user gives a title/query, search with short distinctive terms, not only the full title. Prefer:

1. author + unique title words
2. unique title words
3. screenshot-visible terms
4. synonyms or narrower terms

Use:

```bash
.venv/bin/python scripts/rednote_ingest.py "AUTHOR KEYWORDS" --author "AUTHOR"
```

If automatic ranking picks the wrong result, run manual search:

```bash
.venv/bin/python scripts/rednote_scraper.py search "KEYWORDS" --limit 20
```

Then collect the selected note:

```bash
.venv/bin/python scripts/rednote_collect_note.py --id NOTE_ID --xsec-token "XSEC_TOKEN" --slug short-name
```

The ingest command creates a traceable source Markdown file in the configured vault and stores its images beside it. It also keeps `note.json` and downloaded images in the raw collection folder. Inspect those surfaces, transcribe important image text, and improve the source archive into a learning document.

## Required Processing

Always process all available surfaces:

- title, author, body text, tags, interaction counts
- downloaded images
- comments and author replies
- video subtitles if available from collected metadata or user-provided transcript

For images, do not merely link them. If an image contains text, transcribe or summarize its content into the Markdown so the document is useful without opening images.

For comments, do not paste every comment. Extract:

- author clarifications
- high-value user questions
- repeated confusion points
- resource or context clues
- meaningful disagreements or limitations

## Writing Rules

Write the final artifact as a learning document, not a scraped dump.

For interview experiences, organize as:

- source information
- complete note/image content recovery
- interview question list
- what each question tests
- recommended answer
- likely follow-up questions
- reusable frameworks
- 10-minute review version

For creator/topic learning, organize as:

- one-sentence thesis
- knowledge map
- beginner concepts
- intermediate frameworks
- advanced cases/SOPs
- examples
- FAQ from comments
- original note index

For generic notes, choose the closest template from `references/output-templates.md`.

## Obsidian Archiving

If the user has configured an Obsidian vault, write the Markdown into the best matching folder. Use `references/obsidian-routing.md` for routing.

If no vault is configured, write into the workspace and tell the user the path. Ask for the vault path only if archiving is required.

Do not silently overwrite existing notes. If a same-name note exists, append a date or source suffix unless the user explicitly asks to update it.

## User Experience Goal

After setup, the user should be able to say one sentence like:

```text
Use rednote-to-obsidian to learn 夏小懒瓜的字节国际电商数分二三面 and save it to my data-analysis interview folder.
```

Then execute the full pipeline: search, select, collect, inspect, transcribe, synthesize, and archive.
