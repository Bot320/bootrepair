"""End-to-end analysis against fixture images/directories (no root needed)."""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixtures import make_system, GONE_GUID  # noqa: E402
from bootrepair.analyzers import run_analysis  # noqa: E402
from bootrepair.analyzers import disk as disk_an, bootpart  # noqa: E402
from bootrepair.report import to_markdown, to_text  # noqa: E402


def run(tmp, **kw):
    disks, disk, target, mounts = make_system(tmp, **kw)
    msgs = []
    with mock.patch.object(disk_an, "_check_smart", lambda ctx, dev: None), \
            mock.patch.object(disk_an, "_check_kernel_log", lambda ctx, d: None), \
            mock.patch.object(bootpart, "_nvram", lambda ctx: None), \
            mock.patch("bootrepair.analyzers.volume.existing_mount", lambda dev: None):
        r = run_analysis(disks, disk, target, "auto", None, {"events": True}, mounts, msgs.append, lambda: False)
    json.dumps(r, default=str)   # must be serialisable
    to_markdown(r)
    to_text(r)
    return r


def titles(r, sev):
    return [f["title"] for f in r["findings"] if f["severity"] == sev]


class PipelineTests(unittest.TestCase):
    def test_healthy(self):
        with tempfile.TemporaryDirectory() as t:
            r = run(t)
        failed = [s for s in r["steps"] if s["state"] == "failed"]
        self.assertEqual(failed, [], r["findings"])
        self.assertEqual(titles(r, "critical"), [])
        self.assertIn(r["verdict"]["status"], ("ok", "warn"))
        self.assertEqual(r["windows"]["DisplayName"], "Windows 11 Pro")
        self.assertEqual(r["windows"]["Build"], "22631.4317")
        bcd = r["evidence"]["bcd"]["entries"]
        self.assertTrue(any(e["this_windows"] and e["default"] for e in bcd))

    def test_broken(self):
        with tempfile.TemporaryDirectory() as t:
            r = run(t, broken=True)
        crit = titles(r, "critical")
        joined = "\n".join(crit)
        self.assertEqual([s for s in r["steps"] if s["state"] == "failed"], [])
        self.assertIn("No boot-start driver for the disk controller (NVME)", joined)
        self.assertIn("Storage filter driver 'ghostflt'", joined)
        self.assertIn("hal.dll", joined)
        self.assertTrue(any("INACCESSIBLE_BOOT_DEVICE" in c for c in crit))
        self.assertTrue(any("Startup Repair root cause" in c for c in crit))
        self.assertEqual(r["verdict"]["status"], "fail")
        self.assertTrue(any("NTFS volume is marked dirty" in w for w in titles(r, "warning")))
        self.assertTrue(any("pending" in w.lower() for w in titles(r, "warning") + crit))
        # critical findings come first
        sevs = [f["severity"] for f in r["findings"]]
        self.assertEqual(sevs, sorted(sevs, key=["critical", "warning", "info"].index))

    def test_bcd_points_elsewhere(self):
        with tempfile.TemporaryDirectory() as t:
            r = run(t, bcd_win_guid=GONE_GUID)
        self.assertEqual(r["verdict"]["stage"], "bcd")
        self.assertIn("No BCD entry starts the Windows", r["verdict"]["headline"])
        self.assertIn("0xc000000e", r["verdict"]["stopcode"])


if __name__ == "__main__":
    unittest.main()
