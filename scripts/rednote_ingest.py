#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from rednote_collect_note import collect, safe_slug
from rednote_config import load_config
from rednote_auth import load_cookies
from rednote_markdown import archive_note
from rednote_scraper import RednoteClient, summarize_search


def score_result(item: dict[str, Any], query: str, author: str | None) -> int:
    title = str(item.get("title") or "")
    item_author = str(item.get("author") or "")
    compact_query = re.sub(r"\s+", "", query.lower())
    compact_title = re.sub(r"\s+", "", title.lower())
    score = 0
    if author and author in item_author:
        score += 80
    for token in re.split(r"\s+", query.strip()):
        if token and token.lower() in title.lower():
            score += 12
        if token and token.lower() in item_author.lower():
            score += 8
    if compact_query and compact_query in compact_title:
        score += 60
    try:
        score += min(int(item.get("liked_count") or 0), 1000) // 100
    except ValueError:
        pass
    return score


def choose_result(items: list[dict[str, Any]], query: str, author: str | None) -> dict[str, Any]:
    if not items:
        raise SystemExit(f"No Rednote results for query: {query}")
    ranked = sorted(items, key=lambda item: score_result(item, query, author), reverse=True)
    best = ranked[0]
    if not best.get("id") or not best.get("xsec_token"):
        raise SystemExit("Best result is missing id or xsec_token; try another query.")
    return best


def run(args: argparse.Namespace) -> int:
    config = load_config()
    cookie_path = Path(args.cookies).expanduser() if args.cookies else None
    output_dir = Path(args.output_dir or config.get("output_dir", "outputs/rednote-notes")).expanduser()
    cookies = load_cookies(cookie_path)

    with RednoteClient(cookies) as client:
        search = summarize_search(client.search(args.query, page_size=args.limit))
    best = choose_result(search["items"], args.query, args.author)
    slug = args.slug or safe_slug(best.get("title") or args.query)
    out = collect(best["id"], best["xsec_token"], slug=slug, output_dir=output_dir, cookies_file=cookie_path)
    archive = None
    vault_value = args.vault or config.get("obsidian_vault")
    if vault_value and not args.no_archive:
        archive = archive_note(out, Path(vault_value).expanduser(), folder=args.vault_folder)
    print(
        json.dumps(
            {
                "query": args.query,
                "selected": best,
                "output": str(out),
                "note_json": str(out / "note.json"),
                "obsidian_markdown": str(archive) if archive else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search and collect one Rednote note for Obsidian study processing.")
    parser.add_argument("query", help="Search query, usually author + distinctive title keywords.")
    parser.add_argument("--author", help="Expected author/nickname for ranking.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--slug", help="Output folder name.")
    parser.add_argument("--output-dir", help="Base output directory. Defaults to config output_dir or outputs/rednote-notes.")
    parser.add_argument("--cookies", help="Optional legacy Cookie-Editor JSON export path.")
    parser.add_argument("--vault", help="Obsidian vault path. Defaults to configured vault.")
    parser.add_argument("--vault-folder", default="Rednote", help="Folder inside the Obsidian vault.")
    parser.add_argument("--no-archive", action="store_true", help="Collect raw material without writing Markdown to Obsidian.")
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))
