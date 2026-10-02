# rednote-to-obsidian

[English](#english) · [中文](#中文)

把你自己的 Rednote/小红书笔记、评论和图片素材整理成适合复习与归档的 Obsidian Markdown 文档。它既是一组 Python 命令行工具，也是一个可由 Codex 调用的 Agent Skill。

> 本项目面向个人知识管理、学习、研究与合规归档，不用于绕过访问控制、批量搬运内容或冒充原创作者。

## 中文

### 功能

- 通过明确的扫码登录保存本地会话，无需反复导出 Cookie
- 收集正文、互动信息、评论与图片到本地目录
- 按作者和关键词对搜索结果进行排序，辅助选择目标笔记
- 在 Codex 中优先复用内置浏览器的登录状态，不读取或导出浏览器 Cookie
- 指导 Codex 提炼图片文字、评论洞察和可复习的知识结构
- 自动生成可追溯 Markdown 并连同图片归档到 Obsidian

本仓库不会自动生成最终学习笔记；Python 脚本负责采集，`SKILL.md` 描述 Codex 如何检查素材、总结并归档。

### 前置条件

- Python 3.10+
- 一个你有权使用的 Rednote/小红书账号及当前有效的网页登录状态
- Obsidian（仅在需要归档到 Vault 时使用）
- Codex（仅在作为 Agent Skill 使用时需要）

依赖中的 PyPI 包名是 `xiaohongshu-cli`，代码导入名是 `xhs_cli`。本项目使用其 `xhs_cli.signing` 模块；不要安装另一个名为 `xhs-cli` 的发行包，因为其当前版本不提供该模块。

### 安装

```bash
git clone https://github.com/evv0207-dev/rednote-to-obsidian.git
cd rednote-to-obsidian
./setup.sh
./install-skill.sh --force
```

`install-skill.sh` 会安装/替换 Skill，并在 Skill 目录内创建独立的 `.venv`，所以 Codex 不依赖你的全局 Python 环境。

`setup.sh` 会创建 `.venv` 并从 `requirements.txt` 安装依赖。也可以手动执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### 配置

Codex Skill 模式优先直接打开内置浏览器；如未登录，在可见的小红书页面上扫官方二维码。Codex 不会读取、导出或复制浏览器 Cookie。

仅在没有可用浏览器或需要命令行自动化时，运行独立的扫码登录：

```bash
.venv/bin/python scripts/rednote_auth.py login
```

配置 Obsidian Vault 路径：

```bash
.venv/bin/python scripts/rednote_config.py init \
  --vault /path/to/ObsidianVault
```

扫码会话由 `xiaohongshu-cli` 保存到用户目录下的独立配置文件，权限为 `0600`；不会写入 Git 仓库。项目不会在未经额外明确请求时自动扫描浏览器 Cookie。旧 Cookie-Editor JSON 仍可以通过 `--cookies` 兼容使用。

检查配置与登录状态：

```bash
.venv/bin/python scripts/rednote_config.py check
.venv/bin/python scripts/rednote_auth.py check
.venv/bin/python scripts/rednote_scraper.py status
```

### 使用

搜索：

```bash
.venv/bin/python scripts/rednote_scraper.py search "作者 关键词" --limit 20
```

自动搜索、排序并采集一篇笔记：

```bash
.venv/bin/python scripts/rednote_ingest.py "作者 独特标题词" --author "作者"
```

已经知道搜索结果中的 `NOTE_ID` 和 `XSEC_TOKEN` 时：

```bash
.venv/bin/python scripts/rednote_collect_note.py \
  --id NOTE_ID \
  --xsec-token "XSEC_TOKEN" \
  --slug short-name
```

默认原始输出位于 `outputs/rednote-notes/`，包含 `note.json` 与下载的图片。如果已配置 Vault，`rednote_ingest.py` 还会在 `Vault/Rednote/`中自动生成 Markdown，并把图片复制到同一笔记目录。同名笔记不会被静默覆盖。

### 在 Codex 中使用

一键安装或替换本机 Codex Skill：

```bash
./install-skill.sh --force
```

然后可以这样请求：

```text
Use $rednote-to-obsidian to learn this Rednote note and archive it in my Obsidian vault.
```

Codex 会读取 `SKILL.md`，按需搜索、采集、检查图片和评论，并生成结构化学习文档。面向开发者的命令与架构见 [AGENTS.md](AGENTS.md)。

### Cookie 安全

- 只使用你自己的登录状态，绝不要提供账号密码。
- Cookie 等同于敏感会话凭据；不要发到 Issue、聊天记录、截图或提交中。
- Cookie 文件应保存在仓库之外，并限制本机文件权限。
- 本项目只保存 Cookie 文件路径，但采集命令会把 Cookie 发送到 Rednote/小红书所属的 Web 端点（非官方公开 API）以完成已登录请求。
- 如果怀疑 Cookie 泄露，请立即退出相关会话、重新登录，并删除旧导出文件。
- 提交前检查 `git status`；仓库的 `.gitignore` 已忽略常见 Cookie 文件名，但不能替代人工检查。

### 合规与限制

你必须遵守平台条款、版权、隐私规则及所在地法律，只采集你有权访问和处理的内容。不要用本项目绕过付费墙、访问控制、账号限制或反滥用机制，也不要大规模重发布他人内容。请合理控制请求频率；接口、签名规则和登录状态可能随平台更新而失效。本项目与小红书/Rednote 无隶属或认可关系。

## English

`rednote-to-obsidian` collects notes, comments, and images that you are authorized to access through your own Rednote/Xiaohongshu session, then guides Codex in turning the material into structured Markdown for personal learning and Obsidian archives.

### Features

- Search and read notes with your own authenticated web session
- Collect note metadata, comments, and images locally
- Rank search results by author and distinctive keywords
- Guide Codex to extract image text and high-value comment insights
- Route transformed study notes into an Obsidian vault

The Python scripts collect source material; the Agent Skill instructions in `SKILL.md` define the review, synthesis, and archival workflow.

### Requirements and installation

You need Python 3.10+ and a Xiaohongshu account you are authorized to use. Codex mode can reuse the visible in-app browser session without exporting cookies. CLI-only mode uses an explicit QR login. Obsidian is needed only when you want vault archiving.

```bash
git clone https://github.com/evv0207-dev/rednote-to-obsidian.git
cd rednote-to-obsidian
./setup.sh
```

The required PyPI distribution is `xiaohongshu-cli`, while Python imports it as `xhs_cli`. Do not substitute the separate `xhs-cli` distribution: its current release does not provide the `xhs_cli.signing` module used here.

### Configure and run

Log in explicitly by QR code, then configure your vault:

```bash
.venv/bin/python scripts/rednote_auth.py login
.venv/bin/python scripts/rednote_config.py init \
  --vault /path/to/ObsidianVault
.venv/bin/python scripts/rednote_config.py check
.venv/bin/python scripts/rednote_scraper.py status
```

Search or collect one result:

```bash
.venv/bin/python scripts/rednote_scraper.py search "AUTHOR KEYWORDS" --limit 20
.venv/bin/python scripts/rednote_ingest.py "AUTHOR KEYWORDS" --author "AUTHOR"
```

In Codex mode, the skill prefers the visible in-app browser and keeps its session inside that browser; it never reads or exports browser cookies. For CLI-only use, an explicit QR session is stored separately by `xiaohongshu-cli` with restricted permissions and is never committed to this repository. This project intentionally does not auto-scan browser profiles. A legacy Cookie-Editor export can still be supplied explicitly with `--cookies`. Configuration is stored at `~/.rednote-to-obsidian/config.json`.

When a vault is configured, `rednote_ingest.py` writes a traceable Markdown source archive and copies downloaded images into `Vault/Rednote/`. Existing notes are not silently overwritten.

### Privacy, security, and responsible use

Saved sessions are sensitive credentials. The default flow uses an explicit QR login and does not silently scan browser profiles. Never commit the saved session, paste it into an issue, or share it. Authenticated commands necessarily send the session to Rednote/Xiaohongshu-owned web endpoints, which are not an official public API. Re-login if the session expires and revoke it if it may have leaked.

Use this project only for personal knowledge management, research, learning, and lawful archival of material you are authorized to access. Do not bypass access controls, automate abuse, impersonate creators, or republish other people's work at scale. Respect platform terms, copyright, privacy, request limits, and applicable law. Rednote APIs and signing behavior may change without notice. This project is not affiliated with or endorsed by Xiaohongshu/Rednote.

## Contributing

Issues and pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing, and never include cookies or collected user content in bug reports.

## License

[MIT](LICENSE) © 2026 Contributors
