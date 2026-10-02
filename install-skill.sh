#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CODEX_ROOT="${CODEX_HOME:-${HOME}/.codex}"
TARGET="${REDNOTE_SKILL_TARGET:-${CODEX_ROOT}/skills/rednote-to-obsidian}"
FORCE=false

if [[ -z "$TARGET" || "$TARGET" == "/" || "$TARGET" == "$HOME" || "$TARGET" == "$CODEX_ROOT" ]]; then
  echo "Refusing unsafe install target: $TARGET" >&2
  exit 2
fi

if [[ "${1:-}" == "--force" ]]; then
  FORCE=true
fi

if [[ -e "$TARGET" && "$FORCE" != true ]]; then
  echo "Skill already exists: $TARGET"
  echo "Re-run with --force to replace it. Local config and login are stored elsewhere and are not deleted."
  exit 2
fi

mkdir -p "$(dirname "$TARGET")"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/rednote-to-obsidian.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/rednote-to-obsidian"
for item in SKILL.md agents references scripts requirements.txt; do
  cp -R "$SCRIPT_DIR/$item" "$STAGE/rednote-to-obsidian/"
done

if [[ -e "$TARGET" ]]; then
  rm -rf "$TARGET"
fi
mv "$STAGE/rednote-to-obsidian" "$TARGET"
python3 -m venv "$TARGET/.venv"
"$TARGET/.venv/bin/python" -m pip install -r "$TARGET/requirements.txt"
echo "Installed Codex skill: $TARGET"
echo "Next for CLI-only login: '$TARGET/.venv/bin/python' '$TARGET/scripts/rednote_auth.py' login"
