#!/usr/bin/env python3
"""Explicit, local authentication helpers for rednote-to-obsidian."""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

from xhs_cli.cookies import load_saved_cookies
from xhs_cli.qr_login import qrcode_login


class AuthError(RuntimeError):
    pass


REQUIRED_COOKIES = {"a1", "webId", "web_session"}


def _validate(cookies: dict[str, str]) -> dict[str, str]:
    cleaned = {
        str(name): str(value)
        for name, value in cookies.items()
        if name != "saved_at" and value
    }
    missing = REQUIRED_COOKIES - cleaned.keys()
    if missing:
        raise AuthError(f"Missing required cookies: {', '.join(sorted(missing))}")
    return cleaned


def load_cookie_export(path: Path) -> dict[str, str]:
    """Load the legacy Cookie-Editor JSON format."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthError(f"Cannot read cookie export: {exc}") from exc
    if not isinstance(data, list):
        raise AuthError("Cookie export must be a Cookie-Editor JSON list.")
    cookies = {
        str(item["name"]): str(item["value"])
        for item in data
        if isinstance(item, dict)
        and any(domain in str(item.get("domain", "")) for domain in ("xiaohongshu.com", "rednote.com"))
        and item.get("name")
        and item.get("value")
    }
    return _validate(cookies)


def load_cookies(explicit_file: Path | None = None) -> dict[str, str]:
    """Load only explicitly exported or explicitly QR-saved credentials.

    This intentionally does not call xhs_cli.cookies.get_cookies(), because that
    function may scan installed browser profiles without a separate prompt.
    """
    if explicit_file is not None:
        return load_cookie_export(explicit_file)
    saved = load_saved_cookies()
    if not saved:
        raise AuthError(
            "No saved Xiaohongshu session. Run: "
            ".venv/bin/python scripts/rednote_auth.py login"
        )
    return _validate(saved)


def run_login() -> int:
    """Show a terminal QR code and let xhs-cli store mode-0600 cookies.

    The upstream CLI prefers a Camoufox window. The direct HTTP flow is more
    reliable in headless terminals and does not inspect browser profiles.
    """
    qr_output = os.environ.get("REDNOTE_QR_OUTPUT")
    qr_module = importlib.import_module("xhs_cli.qr_login")
    original_display_qr = None
    if qr_output:
        import qrcode

        original_display_qr = qr_module._display_qr_in_terminal

        def display_and_save(data: str) -> bool:
            output = Path(qr_output).expanduser()
            output.parent.mkdir(parents=True, exist_ok=True)
            qr = qrcode.QRCode(border=4)
            qr.add_data(data)
            qr.make(fit=True)
            qr.make_image().save(output)
            print(f"QR image saved to: {output}", flush=True)
            return original_display_qr(data)

        qr_module._display_qr_in_terminal = display_and_save

    print("Starting terminal QR login. Scan the code with the Xiaohongshu app.", flush=True)
    try:
        qrcode_login(on_status=lambda message: print(message, flush=True), prefer_browser_assisted=False)
    finally:
        if original_display_qr is not None:
            qr_module._display_qr_in_terminal = original_display_qr
    print("Login saved locally.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the local Xiaohongshu login used by this skill.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("login", help="Log in explicitly with a QR code.")
    sub.add_parser("check", help="Check whether a saved local session exists (no network call).")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "login":
        return run_login()
    try:
        cookies = load_cookies()
    except AuthError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"saved_session": True, "required_cookies": sorted(REQUIRED_COOKIES), "cookie_count": len(cookies)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
