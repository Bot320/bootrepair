"""One-click repairs: applied to fixture systems and (optionally) to a copy of a real evidence bundle."""

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixtures import make_system, GONE_GUID  # noqa: E402
from test_pipeline import run  # noqa: E402
from bootrepair import fixes  # noqa: E402
from bootrepair.analyzers import run_analysis, disk as disk_an, bootpart  # noqa: E402


def analyse(disks, disk, target, mounts):
    with mock.patch.object(disk_an, "_check_smart", lambda ctx, dev: None), \
            mock.patch.object(disk_an, "_check_kernel_log", lambda ctx, d: None), \
            mock.patch.object(bootpart, "_nvram", lambda ctx: None), \
            mock.patch("bootrepair.analyzers.volume.existing_mount", lambda dev: None):
        return run_analysis(disks, disk, target, "auto", None, {"events": True}, mounts, lambda m: None,
                            lambda: False)


def all_actions(report, skip=("nvram",)):
    out, seen = [], set()
    for f in report["findings"]:
        for a in f.get("actions", []):
            if a["id"] in seen or any(n in skip for n in a["needs"]):
                continue
            seen.add(a["id"])
            out.append(a)
    return out


def crit(report):
    return sorted(f["title"] for f in report["findings"] if f["severity"] == "critical")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class FixtureRepairTests(unittest.TestCase):
    def test_fix_all_then_undo(self):
        with tempfile.TemporaryDirectory() as t:
            disks, disk, target, mounts = make_system(t, broken=True)
            before = analyse(disks, disk, target, mounts)
            acts = all_actions(before)
            kinds = {a["kind"] for a in acts}
            self.assertTrue({"set_service_start", "remove_class_filter", "revert_pending_update",
                             "restore_system_file"} <= kinds, kinds)
            system = Path(t, "win/Windows/System32/config/SYSTEM")
            hal = Path(t, "win/Windows/System32/hal.dll")
            orig = (sha(system), sha(hal))
            boot = next(p for p in disk["partitions"] if p["is_esp"])
            res = fixes.apply(target["path"], boot["path"], acts, mounts=mounts, disks=disks,
                              backup_root=Path(t, "backups"))
            self.assertTrue(all(r["ok"] for r in res["results"]), res)
            after = analyse(disks, disk, target, mounts)
            left = crit(after)
            for gone in ("No boot-start driver", "Storage filter driver", "hal.dll"):
                self.assertFalse(any(gone in c for c in left), left)
            self.assertFalse(any("pending" in f["title"].lower() and f["severity"] != "info"
                                 for f in after["findings"]), after["findings"])
            self.assertEqual(hal.read_bytes()[:3], b"MZ\x03")          # newest WinSxS version used
            # undo restores the exact original bytes
            fixes.undo(res["backup"], mounts=mounts, disks=disks)
            self.assertEqual((sha(system), sha(hal)), orig)
            self.assertEqual(crit(analyse(disks, disk, target, mounts)), crit(before))

    def test_refuses_hibernated_volume(self):
        with tempfile.TemporaryDirectory() as t:
            disks, disk, target, mounts = make_system(t, broken=True)
            acts = [a for a in all_actions(analyse(disks, disk, target, mounts)) if "win" in a["needs"]]
            with self.assertRaises(fixes.FixError):
                fixes.apply(target["path"], None, acts, mounts=mounts, disks=disks,
                            backup_root=Path(t, "backups"), state={"hibernated": True})

    def test_bcd_repoint(self):
        with tempfile.TemporaryDirectory() as t:
            disks, disk, target, mounts = make_system(t, bcd_win_guid=GONE_GUID)
            before = analyse(disks, disk, target, mounts)
            self.assertEqual(before["verdict"]["stage"], "bcd")
            acts = [a for a in all_actions(before) if a["kind"].startswith("bcd_")]
            self.assertTrue(acts)
            boot = next(p for p in disk["partitions"] if p["is_esp"])
            res = fixes.apply(target["path"], boot["path"], acts, mounts=mounts, disks=disks,
                              backup_root=Path(t, "backups"))
            self.assertTrue(all(r["ok"] for r in res["results"]), res)
            after = analyse(disks, disk, target, mounts)
            self.assertEqual(crit(after), [])
            self.assertTrue(any(e["this_windows"] and e["default"] for e in after["evidence"]["bcd"]["entries"]))


@unittest.skipUnless(os.environ.get("BOOTREPAIR_BUNDLE"), "set BOOTREPAIR_BUNDLE to a collected evidence bundle")
class RealBundleRepairTests(unittest.TestCase):
    def test_fix_and_undo_on_copy(self):
        from replay import load_bundle, analyse as ranalyse
        with tempfile.TemporaryDirectory() as t:
            meta, disks, disk, target, mounts = load_bundle(os.environ["BOOTREPAIR_BUNDLE"], t, copy=True)
            before = ranalyse(meta, disks, disk, target, mounts)
            acts = all_actions(before)
            self.assertTrue(acts)
            boot = next(p for d in disks for p in d["partitions"] if p["name"] == before["boot_partition"]["name"])
            watched = [Path(t, "fs", f"fs-{target['name']}", "Windows/System32/config/SYSTEM"),
                       Path(t, "fs", f"fs-{boot['name']}", "EFI/Microsoft/Boot/BCD")]
            orig = [sha(p) for p in watched]
            res = fixes.apply(target["path"], boot["path"], acts, mounts=mounts, disks=disks,
                              backup_root=Path(t, "backups"))
            for r in res["results"]:
                print("  ", "OK " if r["ok"] else "ERR", r["title"], r.get("changes") or r.get("error"))
            self.assertTrue(all(r["ok"] for r in res["results"]), res)
            after = ranalyse(meta, disks, disk, target, mounts)
            print("   critical after repair:", crit(after))
            self.assertFalse(any("pending" in c.lower() for c in crit(after)))
            self.assertFalse(any("broken entry" in f["title"] for f in after["findings"]))
            fixes.undo(res["backup"], mounts=mounts, disks=disks)
            self.assertEqual([sha(p) for p in watched], orig)


if __name__ == "__main__":
    unittest.main()
