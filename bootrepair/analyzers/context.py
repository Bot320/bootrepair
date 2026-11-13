"""Analysis context shared by all analyzers."""

import os
from pathlib import Path

from .. import sysprobe
from ..i18n import _
from ..fsutil import CIRoot
from ..model import Finding
from ..parsers.regf import Hive, RegfError


class Cancelled(Exception):
    pass


class Context:
    def __init__(self, disks, disk, target, esp_choice, bitlocker_key, options, mounts, progress, cancelled):
        self.disks = disks
        self.disk = disk                  # disk dict containing the target
        self.target = target              # partition dict
        self.esp_choice = esp_choice      # "auto" or /dev/...
        self.bitlocker_key = bitlocker_key
        self.options = options
        self.mounts = mounts
        self._progress = progress
        self._cancelled = cancelled
        self.findings = []
        self.evidence = {}
        self.incomplete = []              # reasons why parts could not be analysed
        self.unanalyzed_stages = set()
        self.log_lines = []

        self.uefi_host = sysprobe.uefi_host()
        self.boot_mode = None             # "uefi" | "bios"
        self.win_dev = target["path"]     # device actually holding NTFS (mapper if BitLocker)
        self.win_mount = None
        self.win = None                   # CIRoot of the Windows volume
        self.windows_dir_ok = False
        self.boot_part = None             # chosen ESP or active partition dict
        self.boot_mount = None            # CIRoot of it
        self.bcd = None
        self.bcd_path = None
        self.loader_entry = None          # the BCD osloader object for the target
        self.loader_path = None           # e.g. \Windows\system32\winload.efi
        self.hiberfile_state = None
        self.system_hive = None
        self.software_hive = None
        self.current_cs = None
        self.windows_info = {}
        self.ntfs_dirty = None
        self.crash_findings = []          # [(Finding, datetime)]
        self.srt_findings = []            # [(Finding, datetime)]
        self.pending_xml = None           # (Finding, datetime)
        self.event_summary = {}
        self.current_cs_name = "ControlSet001"

    # ----------------------------------------------------------------- helpers
    def check_cancel(self):
        if self._cancelled():
            raise Cancelled()

    def log(self, msg):
        self.log_lines.append(msg)
        self._progress({"type": "log", "msg": msg})

    def add(self, severity, stage, title, why, evidence=None, fix=None, stopcode="", source="", priority=50,
            actions=None):
        f = Finding(severity, stage, _(title), _(why), list(evidence or []), [_(s) for s in (fix or [])],
                    stopcode, source, priority, list(actions or []))
        self.findings.append(f)
        return f

    def all_partitions(self):
        return [p for d in self.disks for p in d["partitions"]]

    def part_by_name(self, name):
        for p in self.all_partitions():
            if p["name"] == name:
                return p
        return None

    def win_path(self, rel):
        return self.win.resolve(rel) if self.win else None

    def load_hive(self, name):
        """Load Windows\\System32\\config\\<name>. Returns Hive or None (errors are reported elsewhere)."""
        attr = {"SYSTEM": "system_hive", "SOFTWARE": "software_hive"}.get(name)
        if attr and getattr(self, attr) is not None:
            return getattr(self, attr)
        p = self.win_path(f"Windows\\System32\\config\\{name}")
        if p is None:
            return None
        try:
            h = Hive.from_file(p)
        except (OSError, RegfError):
            return None
        if attr:
            setattr(self, attr, h)
        return h

    def control_set(self):
        if self.current_cs is not None:
            return self.current_cs
        h = self.load_hive("SYSTEM")
        if h is None:
            return None
        cur = None
        try:
            cur = h.get("Select", "Current")
        except RegfError:
            pass
        name = f"ControlSet{cur:03d}" if isinstance(cur, int) else "ControlSet001"
        try:
            cs = h.open(name)
        except RegfError:
            cs = None
        self.current_cs = cs
        self.current_cs_name = name
        return cs

    def ensure_windows(self):
        """True if the Windows volume is mounted and contains a Windows directory."""
        return self.win is not None and self.windows_dir_ok


def part_label(p):
    if not p:
        return "?"
    bits = [f"/dev/{p['name']}"]
    if p.get("label"):
        bits.append(f"\"{p['label']}\"")
    return " ".join(bits)
