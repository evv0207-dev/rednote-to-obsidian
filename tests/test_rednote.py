from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rednote_auth import AuthError, load_cookie_export, load_cookies
from rednote_markdown import archive_note, render_markdown
from rednote_scraper import summarize_comments, summarize_note, summarize_search


VALID_COOKIES = {"a1": "a", "webId": "w", "web_session": "s"}


class AuthTests(unittest.TestCase):
    def test_load_saved_qr_session_without_browser_scan(self) -> None:
        with patch("rednote_auth.load_saved_cookies", return_value={**VALID_COOKIES, "saved_at": 1}):
            self.assertEqual(load_cookies(), VALID_COOKIES)

    def test_missing_saved_session_explains_login(self) -> None:
        with patch("rednote_auth.load_saved_cookies", return_value=None):
            with self.assertRaisesRegex(AuthError, "rednote_auth.py login"):
                load_cookies()

    def test_legacy_cookie_export_supports_xiaohongshu(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cookies.json"
            path.write_text(json.dumps([
                {"domain": ".xiaohongshu.com", "name": name, "value": value}
                for name, value in VALID_COOKIES.items()
            ]))
            self.assertEqual(load_cookie_export(path), VALID_COOKIES)


class NormalizerTests(unittest.TestCase):
    def test_direct_payloads_from_xhs_client(self) -> None:
        search = summarize_search({"items": [{"id": "n1", "xsec_token": "t", "note_card": {"display_title": "Title", "user": {"nickname": "A"}}}]})
        self.assertEqual(search["items"][0]["id"], "n1")
        note = summarize_note({"items": [{"id": "n1", "note_card": {"title": "Title", "image_list": []}}]})
        self.assertEqual(note["title"], "Title")
        comments = summarize_comments({"comments": [{"id": "c1", "content": "Useful"}]})
        self.assertEqual(comments["comments"][0]["content"], "Useful")


class MarkdownTests(unittest.TestCase):
    def test_archive_writes_markdown_and_copies_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note_dir = root / "raw"
            vault = root / "vault"
            note_dir.mkdir()
            vault.mkdir()
            (note_dir / "image-01.webp").write_bytes(b"image")
            (note_dir / "note.json").write_text(json.dumps({
                "id": "abc",
                "title": "Test Note",
                "author": "Author",
                "desc": "Body",
                "comments": [{"content": "Question", "user_info": {"nickname": "Reader"}}],
            }))
            markdown = archive_note(note_dir, vault)
            self.assertTrue(markdown.exists())
            self.assertTrue((markdown.parent / "image-01.webp").exists())
            text = markdown.read_text()
            self.assertIn("# Test Note", text)
            self.assertIn("![[image-01.webp]]", text)
            self.assertIn("Question", text)

    def test_render_has_traceable_source(self) -> None:
        text = render_markdown({"id": "abc", "title": "T"}, [])
        self.assertIn("https://www.xiaohongshu.com/explore/abc", text)


if __name__ == "__main__":
    unittest.main()
