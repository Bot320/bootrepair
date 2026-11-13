import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bootrepair import guide  # noqa: E402
from test_pipeline import run  # noqa: E402


class GuideTests(unittest.TestCase):
    def test_parse_step(self):
        self.assertEqual(guide.parse_step("Load it:\n`reg load X\nreg unload X`"),
                         [("text", "Load it:"), ("code", ["reg load X", "reg unload X"])])
        self.assertEqual(guide.parse_step("Leave (`exit`) and go on."),
                         [("text", "Leave (`exit`) and go on.")])

    def test_sections_and_plain(self):
        fix = ["Read this first.", guide.WINRE, "Run:\n`chkdsk C: /f`", guide.WINDOWS, "Then (`powercfg /h off`)."]
        secs = guide.sections(fix)
        self.assertEqual([c for c, _ in secs], [None, guide.WINRE, guide.WINDOWS])
        text = "\n".join(guide.plain_steps(fix))
        self.assertIn("chkdsk C: /f", text)
        self.assertNotIn("`", text)

    def test_reports_are_well_formed(self):
        """Every generated instruction has balanced backticks and renders to HTML."""
        from fixtures import GONE_GUID
        for kw in ({"broken": True}, {}, {"bcd_win_guid": GONE_GUID}):
            with tempfile.TemporaryDirectory() as t:
                r = run(t, **kw)
            for f in r["findings"]:
                for s in f["fix"]:
                    if s not in guide.CONTEXTS:
                        self.assertEqual(s.count("`") % 2, 0, (f["title"], s))
                        self.assertNotIn(" -> ", s, f["title"])
            html = guide.to_html(r)
            self.assertIn("<html", html)
            self.assertIn(r["verdict"]["headline"].split(":")[0], html)
            if any(guide.needs_winre(f["fix"]) for f in guide.guide_findings(r)):
                self.assertIn(guide.HOWTO_TITLE, html)


if __name__ == "__main__":
    unittest.main()
