#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path.home() / ".rednote-to-obsidian" / "config.json"


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(config: dict[str, Any], path: Path = DEFAULT_CONFIG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_cookie_path(explicit: str | None = None, *, required: bool = True) -> Path | None:
    if explicit:
        return Path(explicit).expanduser()
    config = load_config()
    value = config.get("cookie_file")
    if value:
        return Path(str(value)).expanduser()
    env_value = __import__("os").environ.get("REDNOTE_COOKIE_FILE")
    if env_value:
        return Path(env_value).expanduser()
    if required:
        raise SystemExit(
            "No legacy cookie file configured. Use QR login: "
            ".venv/bin/python scripts/rednote_auth.py login"
        )
    return None


def resolve_vault_path(explicit: str | None = None) -> Path | None:
    if explicit:
        return Path(explicit).expanduser()
    config = load_config()
    value = config.get("obsidian_vault")
    if value:
        return Path(str(value)).expanduser()
    return None


def run_init(args: argparse.Namespace) -> int:
    config = load_config()
    if args.cookie_file:
        cookie = Path(args.cookie_file).expanduser()
        if not cookie.exists():
            raise SystemExit(f"Cookie file does not exist: {cookie}")
        config["cookie_file"] = str(cookie)
    if args.vault:
        vault = Path(args.vault).expanduser()
        if not vault.exists():
            raise SystemExit(f"Obsidian vault does not exist: {vault}")
        config["obsidian_vault"] = str(vault)
    if args.output_dir:
        config["output_dir"] = str(Path(args.output_dir).expanduser())
    save_config(config)
    print(json.dumps({"config": str(DEFAULT_CONFIG), "values": config}, ensure_ascii=False, indent=2))
    return 0


def run_check(_args: argparse.Namespace) -> int:
    config = load_config()
    cookie = resolve_cookie_path(None, required=False)
    vault = resolve_vault_path(None)
    result = {
        "config": str(DEFAULT_CONFIG),
        "legacy_cookie_file": str(cookie) if cookie else None,
        "legacy_cookie_exists": cookie.exists() if cookie else False,
        "obsidian_vault": str(vault) if vault else None,
        "vault_exists": vault.exists() if vault else False,
        "output_dir": config.get("output_dir", "outputs/rednote-notes"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Configure rednote-to-obsidian local settings.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--cookie-file", help="Optional legacy Cookie-Editor JSON export.")
    init.add_argument("--vault", help="Obsidian vault path.")
    init.add_argument("--output-dir", help="Folder for raw Rednote collections.")
    sub.add_parser("check")
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    if args.command == "init":
        raise SystemExit(run_init(args))
    if args.command == "check":
        raise SystemExit(run_check(args))
