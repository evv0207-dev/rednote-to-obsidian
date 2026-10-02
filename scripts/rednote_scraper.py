#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from xhs_cli.client import XhsClient
from xhs_cli.exceptions import SessionExpiredError, XhsApiError

from rednote_auth import AuthError, load_cookies


class RednoteError(RuntimeError):
    pass


class RednoteClient:
    def __init__(self, cookies: dict[str, str]):
        self.cookies = cookies
        self.client = XhsClient(cookies, request_delay=1.0)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "RednoteClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def status(self) -> dict[str, Any]:
        return self.client.get_self_info()

    def search(self, keyword: str, *, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        return self.client.search_notes(keyword, page=page, page_size=page_size)

    def read(self, note_id: str, xsec_token: str, *, source: str = "pc_search") -> dict[str, Any]:
        return self.client.get_note_detail(note_id, xsec_token=xsec_token, xsec_source=source)

    def comments(self, note_id: str, xsec_token: str, *, cursor: str = "") -> dict[str, Any]:
        return self.client.get_comments(note_id, cursor=cursor, xsec_token=xsec_token, xsec_source="pc_search")


def _payload(data: dict[str, Any]) -> dict[str, Any]:
    nested = data.get("data")
    return nested if isinstance(nested, dict) else data


def first_image(card: dict[str, Any]) -> str:
    cover = card.get("cover") or {}
    if isinstance(cover, dict):
        return str(cover.get("url_default") or cover.get("url_pre") or "")
    return ""


def summarize_search(data: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(data)
    items = payload.get("items") or []
    results = []
    for item in items:
        card = item.get("note_card") or {}
        user = card.get("user") or {}
        interact = card.get("interact_info") or {}
        results.append(
            {
                "id": item.get("id") or card.get("note_id"),
                "xsec_token": item.get("xsec_token") or card.get("xsec_token"),
                "title": card.get("display_title", ""),
                "author": user.get("nickname") or user.get("nick_name", ""),
                "liked_count": interact.get("liked_count", ""),
                "comment_count": interact.get("comment_count", ""),
                "cover": first_image(card),
            }
        )
    return {"has_more": payload.get("has_more", False), "items": results}


def summarize_note(data: dict[str, Any]) -> dict[str, Any]:
    items = _payload(data).get("items") or []
    if not items:
        return {"items": []}
    card = items[0].get("note_card") or {}
    user = card.get("user") or {}
    interact = card.get("interact_info") or {}
    return {
        "id": items[0].get("id") or card.get("note_id"),
        "title": card.get("title") or card.get("display_title", ""),
        "desc": card.get("desc", ""),
        "author": user.get("nickname") or user.get("nick_name", ""),
        "liked_count": interact.get("liked_count", ""),
        "comment_count": interact.get("comment_count", ""),
        "images": [
            info.get("url")
            for image in card.get("image_list", [])
            for info in image.get("info_list", [])
            if isinstance(info, dict) and info.get("image_scene") in {"WB_DFT", "CRD_WM_WEBP"} and info.get("url")
        ],
    }


def summarize_comments(data: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(data)
    comments = payload.get("comments") or []
    return {
        "has_more": payload.get("has_more", False),
        "cursor": payload.get("cursor", ""),
        "comments": [
            {
                "id": item.get("id"),
                "author": (item.get("user_info") or {}).get("nickname", ""),
                "content": item.get("content", ""),
                "like_count": item.get("like_count", ""),
                "sub_comment_count": item.get("sub_comment_count", ""),
            }
            for item in comments
        ],
    }


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def run(args: argparse.Namespace) -> int:
    explicit = Path(args.cookies).expanduser() if args.cookies else None
    cookies = load_cookies(explicit)
    with RednoteClient(cookies) as client:
        if args.command == "status":
            info = _payload(client.status())
            basic = info.get("basic_info", {})
            print_json({"nickname": basic.get("nickname"), "red_id": basic.get("red_id")})
        elif args.command == "search":
            data = client.search(args.keyword, page=args.page, page_size=args.limit)
            print_json(data if args.raw else summarize_search(data))
        elif args.command == "read":
            data = client.read(args.note_id, args.xsec_token)
            print_json(data if args.raw else summarize_note(data))
        elif args.command == "comments":
            data = client.comments(args.note_id, args.xsec_token, cursor=args.cursor)
            print_json(data if args.raw else summarize_comments(data))
        elif args.command == "demo":
            search = summarize_search(client.search(args.keyword, page_size=args.limit))
            if not search["items"]:
                raise RednoteError(f"No results for {args.keyword!r}")
            first = search["items"][0]
            note = summarize_note(client.read(first["id"], first["xsec_token"]))
            comments = summarize_comments(client.comments(first["id"], first["xsec_token"]))
            print_json({"query": args.keyword, "first_result": first, "note": note, "comments": comments})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read authorized Xiaohongshu content with an explicit local session.")
    parser.add_argument("--cookies", help="Optional legacy Cookie-Editor JSON export path.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")

    search = sub.add_parser("search")
    search.add_argument("keyword")
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--raw", action="store_true")

    read = sub.add_parser("read")
    read.add_argument("note_id")
    read.add_argument("xsec_token")
    read.add_argument("--raw", action="store_true")

    comments = sub.add_parser("comments")
    comments.add_argument("note_id")
    comments.add_argument("xsec_token")
    comments.add_argument("--cursor", default="")
    comments.add_argument("--raw", action="store_true")

    demo = sub.add_parser("demo")
    demo.add_argument("keyword")
    demo.add_argument("--limit", type=int, default=20)
    return parser


if __name__ == "__main__":
    try:
        raise SystemExit(run(build_parser().parse_args()))
    except (RednoteError, AuthError, SessionExpiredError, XhsApiError) as exc:
        if isinstance(exc, SessionExpiredError) or getattr(exc, "code", None) == -100:
            print("error: Login expired. Run: .venv/bin/python scripts/rednote_auth.py login", file=sys.stderr)
            raise SystemExit(1)
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
