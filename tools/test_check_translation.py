#!/usr/bin/env python3
"""Tests for check_translation.py. Run:  python tools/test_check_translation.py
Each test copies the real articles to a temp folder, breaks one thing, and expects the checker to notice."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CHECK = HERE / "check_translation.py"


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        art = self.tmp / "content" / "articles"
        art.mkdir(parents=True)
        for name in ("feedstock.md", "feedstock.hi.md"):
            shutil.copy(REPO / "content" / "articles" / name, art / name)
        self.en, self.hi = art / "feedstock.md", art / "feedstock.hi.md"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_check(self, *extra):
        r = subprocess.run([sys.executable, str(CHECK), "--root", str(self.tmp), *extra], capture_output=True, text=True)
        return r.returncode, r.stdout

    def edit(self, path, old, new, count=1):
        t = path.read_text(encoding="utf-8")
        self.assertIn(old, t, f"test setup: {old!r} not found")
        path.write_text(t.replace(old, new, count), encoding="utf-8")

    def go_live(self):
        self.edit(self.hi, "status: draft\ndraft: true", "status: approved\ndraft: false")

    # --- the real files ---
    def test_real_draft_is_clean(self):
        code, out = self.run_check("--strict")
        self.assertEqual(code, 0, out)
        self.assertIn("ok", out)

    def test_real_translation_is_clean_when_live(self):
        self.go_live()
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    # --- things that must be caught ---
    def broken(self, old, new, expect, count=1):
        self.edit(self.hi, old, new, count)
        self.go_live()
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn(expect, out)

    def test_changed_number_in_body(self):
        self.broken("लगभग 50:1", "लगभग 40:1", "block 5: numbers differ", count=9)

    def test_changed_number_in_finding(self):
        self.broken("12 से 24 घंटे तक उनका व्यवहार देखें।\"", "12 से 48 घंटे तक उनका व्यवहार देखें।\"", "numbers in finding differ")

    def test_altered_quote(self):
        self.broken("Place the material in a container", "Put the material in a container", "quote must be identical")

    def test_altered_url(self):
        self.broken("raising-earthworms-successfully", "raising-worms", "url must be identical", count=1)

    def test_dropped_source_marker(self):
        self.broken("होता है। [2](#s2)", "होता है।", "must end with a source marker")

    def test_wrong_source_cited(self):
        self.broken("होता है। [2](#s2)", "होता है। [3](#s3)", "cites sources")

    def test_sentence_without_marker(self):
        self.broken("परखें। [5](#s5) इस", "परखें। इस", "sentence ends without a source marker")

    def test_missing_paragraph(self):
        self.broken("## अनिश्चित आहार सामग्री की जाँच", "", "structure differs")

    def test_devanagari_digits(self):
        self.broken("12 से 24 घंटे तक उनका व्यवहार देखें। [5]", "१२ से २४ घंटे तक उनका व्यवहार देखें। [5]", "Devanagari digits")

    def test_added_link(self):
        self.broken("कतरे या टुकड़े किए गए गत्ते", "[कतरे](https://example.com) या टुकड़े किए गए गत्ते", "links are not allowed", count=9)

    def test_untranslated_paragraph(self):
        self.broken("Eisenia fetida आहार सामग्री के लगभग 50:1 C:N अनुपात पर पनप सकता है, जबकि पारंपरिक कम्पोस्टिंग में यह 25:1–30:1 होता है। [2](#s2)",
                    "Eisenia fetida can thrive at feedstock C:N ratios around 50:1, compared with 25:1-30:1 for traditional composting. [2](#s2)",
                    "no Devanagari")

    def test_stale_translation(self):
        self.edit(self.en, "updated: 2026-11-10", "updated: 2026-12-01")
        self.go_live()
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("re-translate from the current English", out)

    def test_english_original_not_published(self):
        self.edit(self.en, "status: approved\ndraft: false", "status: draft\ndraft: true")
        self.go_live()
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("English original is not published", out)

    def test_missing_english_original(self):
        self.en.unlink()
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("no English original", out)

    # --- drafts warn, live blocks ---
    def test_draft_problem_warns_but_does_not_block(self):
        self.edit(self.hi, "लगभग 50:1", "लगभग 40:1")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("warn", out)
        code, out = self.run_check("--strict")
        self.assertEqual(code, 1, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
