"""Startup Repair log (English/German), Safe Mode detection and third-party driver vendors."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bootrepair.analyzers.crashes import parse_srttrail, srt_kind  # noqa: E402
from bootrepair.analyzers.events import safe_mode_streak, skipped_drivers  # noqa: E402
from bootrepair.analyzers.thirdparty import vendor_name  # noqa: E402
from bootrepair.fsutil import pe_company  # noqa: E402

DASH = "---------------------------\r\n"
TEST_DE = "Durchgeführter Test: \r\n" + DASH + "Name: Diagnose des Start-Managers\r\nErgebnis: Erfolgreich abgeschlossen. Fehlercode =  0x0\r\nErstellungszeit = 0 ms\r\n\r\n"
SESSION_DE = ("Sitzungsdetails\r\n" + DASH + "Systemdatenträger = \\Device\\Harddisk0\r\nWindowsverzeichnis = C:\\WINDOWS\r\n"
              "AutoChk-Ausführung = 0\r\nAnzahl der Fehlerursachen = 1\r\n\r\n" + TEST_DE * 3
              + "Gefundene Fehlerursache: \r\n" + DASH + "Eine kürzlich verarbeitete Startbinärdatei ist beschädigt.\r\n\r\n"
              + TEST_DE + DASH + DASH)
SRT_DE = ("Protokoll der Starthilfediagnose und -reparatur\r\n" + DASH
          + "Zeitpunkt des letzten erfolgreichen Starts: \u200e12.\u200e11.\u200e2026 14:19:21 (GMT)\r\n"
          + "Anzahl von Reparaturversuchen: 9\r\n\r\n" + SESSION_DE * 3
          + "Sitzungsdetails\r\n" + DASH + "Systemdatenträger = \\Device\\Harddisk0\r\n" + TEST_DE + "Durchgeführter Test: \r\n---------")

SRT_EN = ("Startup Repair diagnosis and repair log\r\n" + DASH + "Last successful boot time: 11/10/2023 9:12:00 AM (GMT)\r\n"
          "Number of repair attempts: 2\r\n\r\nSession details\r\n" + DASH + "System Disk = \\Device\\Harddisk0\r\n\r\n"
          "Root cause found: \r\n" + DASH + "A patch is preventing the system from starting.\r\n"
          "Repair action: Patch uninstall\r\nResult: Failed. Error code =  0x2\r\n")


class SrtTrailTest(unittest.TestCase):
    def test_german_truncated(self):
        info, sess = parse_srttrail(SRT_DE)
        self.assertEqual(info["repair_attempts"], 9)
        self.assertEqual(info["last_successful_boot"], "12.11.2026 14:19:21 (GMT)")
        self.assertEqual(info["sessions"], 4)
        self.assertEqual(info["root_causes"], ["Eine kürzlich verarbeitete Startbinärdatei ist beschädigt."])
        self.assertEqual(srt_kind(info["root_causes"][0])[0], "serviced_binary")

    def test_english_action_after_cause(self):
        info, __ = parse_srttrail(SRT_EN)
        self.assertEqual(info["root_causes"], ["A patch is preventing the system from starting."])
        self.assertEqual(info["repair_actions"], ["Patch uninstall: Failed. Error code =  0x2"])
        self.assertEqual(srt_kind(info["root_causes"][0])[:2], ("update", "session"))

    def test_kinds(self):
        self.assertEqual(srt_kind("A recently serviced boot binary is corrupt.")[0], "serviced_binary")
        self.assertEqual(srt_kind("Boot critical file c:\\windows\\system32\\drivers\\x.sys is corrupt.")[0], "boot_file")
        self.assertEqual(srt_kind("A recent driver update installation could be preventing Windows from starting.")[0],
                         "driver")
        self.assertEqual(srt_kind("Bugcheck 7B. Parameters = 0x0")[0], "bugcheck")


def ev(minutes, provider, eid, **data):
    t = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)
    return SimpleNamespace(time=t, provider=provider, event_id=eid, data=data)


class SafeModeTest(unittest.TestCase):
    def test_streak_and_skipped(self):
        kg = "Microsoft-Windows-Kernel-General"
        starts = [ev(0, kg, 12, BootMode="0"), ev(60, kg, 12, BootMode="1"), ev(70, kg, 12, BootMode="2")]
        normal, streak = safe_mode_streak(starts)
        self.assertIs(normal, starts[0])
        self.assertEqual(streak, starts[1:])
        failed = [ev(61, "Service Control Manager", 7026, param1="\r\naswSP\r\nGemma"),
                  ev(71, "Service Control Manager", 7026, param1="\r\nEUFDDISK\r\nGemma")]
        self.assertEqual(skipped_drivers(starts[1], starts, failed), {"aswsp", "gemma"})
        self.assertEqual(skipped_drivers(starts[2], starts, failed), {"eufddisk", "gemma"})

    def test_normal_start_last(self):
        kg = "Microsoft-Windows-Kernel-General"
        self.assertEqual(safe_mode_streak([ev(0, kg, 12, BootMode="1"), ev(5, kg, 12, BootMode="0")])[1], [])


class VendorTest(unittest.TestCase):
    def test_vendor_name(self):
        self.assertEqual(vendor_name("BitDefender S.R.L. Bucharest, ROMANIA"), "BitDefender")
        self.assertEqual(vendor_name("Gen Digital Inc."), "Gen Digital")
        self.assertEqual(vendor_name("Callback Technologies, Inc. - www.callback.com"), "Callback Technologies")

    def test_pe_company(self):
        blob = (b"MZ" + b"\0" * 300 + "CompanyName".encode("utf-16-le") + b"\0\0" + b"\0\0"
                + "Contoso Ltd.".encode("utf-16-le") + b"\0\0" + "FileDescription".encode("utf-16-le"))
        with tempfile.NamedTemporaryFile(suffix=".sys") as f:
            f.write(blob)
            f.flush()
            self.assertEqual(pe_company(f.name), "Contoso Ltd.")


if __name__ == "__main__":
    unittest.main()
