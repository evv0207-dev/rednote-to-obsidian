#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import httpx

from rednote_auth import load_cookies
from rednote_scraper import RednoteClient, _payload


DEFAULT_OUT = Path("outputs/rednote-notes")


def safe_slug(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/:*?\"<>|#]+", "-", value)
    value = re.sub(r"\s+", "-", value)
    return value[:80] or "note"


def dft_images(card: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for image in card.get("image_list", []):
        url = image.get("url_default") or ""
        for info in image.get("info_list", []):
            if info.get("image_scene") == "WB_DFT" and info.get("url"):
                url = info["url"]
                break
        if url:
            urls.append(url)
    return urls


def collect(note_id: str, xsec_token: str, *, slug: str | None, output_dir: Path, cookies_file: Path | None) -> Path:
    cookies = load_cookies(cookies_file)
    with RednoteClient(cookies) as client:
        raw = client.read(note_id, xsec_token)
        comments = client.comments(note_id, xsec_token)

    items = _payload(raw).get("items") or []
    if not items:
        raise RuntimeError(f"No note data returned for {note_id}")
    card = items[0]["note_card"]
    title = card.get("title") or card.get("display_title") or note_id
    out = output_dir / safe_slug(slug or title)
    out.mkdir(parents=True, exist_ok=True)

    images = dft_images(card)
    data = {
        "id": note_id,
        "xsec_token": xsec_token,
        "title": title,
        "author": (card.get("user") or {}).get("nickname", ""),
        "desc": card.get("desc", ""),
        "interact_info": card.get("interact_info") or {},
        "tags": card.get("tag_list") or [],
        "images": images,
        "comments": _payload(comments).get("comments", []),
        "raw": raw,
    }
    (out / "note.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    with httpx.Client(timeout=30, follow_redirects=True) as http:
        for index, url in enumerate(images, start=1):
            response = http.get(url)
            response.raise_for_status()
            (out / f"image-{index:02d}.webp").write_bytes(response.content)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a Rednote note body, comments, and images.")
    parser.add_argument("--id", required=True, help="Rednote note id")
    parser.add_argument("--xsec-token", required=True, help="xsec_token from search results")
    parser.add_argument("--slug", help="Output folder name")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT), help="Base output folder")
    parser.add_argument("--cookies", help="Optional legacy Cookie-Editor JSON export path.")
    args = parser.parse_args()

    out = collect(
        args.id,
        args.xsec_token,
        slug=args.slug,
        output_dir=Path(args.output_dir).expanduser(),
        cookies_file=Path(args.cookies).expanduser() if args.cookies else None,
    )
    print(json.dumps({"output": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
