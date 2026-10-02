#!/usr/bin/env bash
set -euo pipefail

# rednote-to-obsidian — first-time setup
# Usage: ./setup.sh

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== rednote-to-obsidian setup ==="

command -v python3 >/dev/null 2>&1 || {
  echo "Error: Python 3.10 or newer is required."
  exit 1
}

python3 - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit("Error: Python 3.10 or newer is required.")
PY

if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/python -m pip install -r requirements.txt

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Install/update the Codex skill: ./install-skill.sh --force"
echo "  2. Log in explicitly by QR code: .venv/bin/python scripts/rednote_auth.py login"
echo "  3. Configure Obsidian: .venv/bin/python scripts/rednote_config.py init --vault /path/to/ObsidianVault"
echo "  4. Verify login: .venv/bin/python scripts/rednote_scraper.py status"
echo "  5. Run tests: .venv/bin/python -m unittest discover -s tests -v"
