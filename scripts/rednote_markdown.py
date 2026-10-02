#!/usr/bin/env python3
"""Create a useful source archive in an Obsidian vault."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rednote_collect_note import safe_slug


def _yaml_text(value: Any) -> str:
    return json.dumps(str(value or ""), ensure_ascii=False)


def _comment_text(item: dict[str, Any]) -> str:
    user = item.get("user_info") or {}
    author = user.get("nickname") or "匿名"
    content = str(item.get("content") or "").strip()
    likes = item.get("like_count") or 0
    return f"- **{author}** ({likes} likes): {content}"


def render_markdown(data: dict[str, Any], image_names: list[str]) -> str:
    note_id = str(data.get("id") or "")
    title = str(data.get("title") or note_id or "Rednote note")
    author = str(data.get("author") or "")
    desc = str(data.get("desc") or "").strip()
    tags = [str(tag.get("name") or tag.get("title") or "") for tag in data.get("tags") or [] if isinstance(tag, dict)]
    comments = [item for item in data.get("comments") or [] if isinstance(item, dict) and item.get("content")]
    source = f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else ""

    lines = [
        "---",
        f"title: {_yaml_text(title)}",
        f"author: {_yaml_text(author)}",
        f"source: {_yaml_text(source)}",
        f"rednote_id: {_yaml_text(note_id)}",
        f"archived_at: {_yaml_text(datetime.now().astimezone().isoformat(timespec='seconds'))}",
        "tags:",
        "  - rednote",
        "  - source-archive",
    ]
    lines.extend(f"  - {_yaml_text(tag)}" for tag in tags if tag)
    lines.extend(["---", "", f"# {title}", "", f"- 作者 / Author: {author or '未知'}", f"- 原文 / Source: {source}", "", "## 正文 / Note", "", desc or "(原文无文字内容)"])
    if image_names:
        lines.extend(["", "## 图片 / Images", ""])
        lines.extend(f"![[{name}]]" for name in image_names)
    if comments:
        lines.extend(["", "## 评论摘要 / Comments", ""])
        lines.extend(_comment_text(item) for item in comments[:50])
    lines.extend(["", "> 这是可追溯的原始素材归档。可继续使用 Codex 对图片文字、评论与正文做学习型提炼。", ""])
    return "\n".join(lines)


def _available_target(base: Path) -> Path:
    if not base.exists():
        return base
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return base.with_name(f"{base.name}-{stamp}")


def archive_note(note_dir: Path, vault: Path, *, folder: str = "Rednote") -> Path:
    if not vault.is_dir():
        raise FileNotFoundError(f"Obsidian vault does not exist: {vault}")
    data = json.loads((note_dir / "note.json").read_text(encoding="utf-8"))
    slug = safe_slug(str(data.get("title") or data.get("id") or note_dir.name))
    target_dir = _available_target(vault / folder / slug)
    target_dir.mkdir(parents=True, exist_ok=False)
    image_names: list[str] = []
    for source in sorted(note_dir.glob("image-*")):
        target = target_dir / source.name
        shutil.copy2(source, target)
        image_names.append(target.name)
    markdown = target_dir / f"{slug}.md"
    markdown.write_text(render_markdown(data, image_names), encoding="utf-8")
    return markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive a collected Rednote folder into Obsidian.")
    parser.add_argument("note_dir", type=Path)
    parser.add_argument("--vault", required=True, type=Path)
    parser.add_argument("--folder", default="Rednote")
    args = parser.parse_args()
    print(json.dumps({"obsidian_markdown": str(archive_note(args.note_dir, args.vault.expanduser(), folder=args.folder))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
