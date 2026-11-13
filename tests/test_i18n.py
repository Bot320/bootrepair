"""Translation catalog checks: every message translated, placeholders/commands intact, `_` never shadowed."""
import ast
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools"), str(Path(__file__).parent)]

import messages  # noqa: E402
from bootrepair import i18n  # noqa: E402
from bootrepair.locale_de import MESSAGES  # noqa: E402


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.found = messages.extract()

    def test_complete(self):
        missing = [m for m in self.found if m not in MESSAGES and messages.needs_translation(m)]
        self.assertEqual(missing, [])

    def test_placeholders_and_commands(self):
        import re
        for m, loc in self.found.items():
            if m in MESSAGES:
                self.assertEqual(messages.placeholders(m), messages.placeholders(MESSAGES[m]), loc)
                self.assertEqual(re.findall(r"`[^`]*`", m), re.findall(r"`[^`]*`", MESSAGES[m]), loc)

    def test_no_underscore_shadowing(self):
        bad = []
        for p in sorted((ROOT / "bootrepair").rglob("*.py")):
            for n in ast.walk(ast.parse(p.read_text())):
                if isinstance(n, ast.Name) and n.id == "_" and isinstance(n.ctx, (ast.Store, ast.Del)) \
                        or isinstance(n, ast.arg) and n.arg == "_":
                    bad.append(f"{p.relative_to(ROOT)}:{n.lineno}")
        self.assertEqual(bad, [])


class GermanRunTest(unittest.TestCase):
    def tearDown(self):
        i18n.set_language("en")

    def test_german_report(self):
        import test_pipeline as tp
        from bootrepair import guide, report
        i18n.set_language("de")
        with tempfile.TemporaryDirectory() as t:
            r = tp.run(t, broken=True)
        md = report.to_markdown(r)
        self.assertIn("Kritisch", md)
        self.assertIn("lang='de'", guide.to_html(r))
        for f in r["findings"]:
            self.assertNotIn("⟦", f["title"])

    def test_pseudo_language_covers_report(self):
        import test_pipeline as tp
        i18n.set_language("pseudo")
        with tempfile.TemporaryDirectory() as t:
            r = tp.run(t, broken=True)
        for f in r["findings"]:
            for s in [f["title"], f["why"], *f["fix"]]:
                self.assertIn("⟦", s, s)


if __name__ == "__main__":
    unittest.main()
