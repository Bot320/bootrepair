"""Case-insensitive path resolution on mounted Windows volumes and file sanity checks."""

import os
import re
from pathlib import Path

from .i18n import _, N_


RECORDER = None   # set by the evidence collector: called with (root, path) for every resolved path


class CIRoot:
    """Resolve Windows-style (case-insensitive, backslash) paths below a mount point."""

    def __init__(self, root):
        self.root = Path(root)
        self._dirs = {}

    def _listing(self, d):
        key = str(d)
        ent = self._dirs.get(key)
        if ent is None:
            try:
                ent = {n.lower(): n for n in os.listdir(d)}
            except OSError:
                ent = {}
            self._dirs[key] = ent
        return ent

    def resolve(self, winpath):
        parts = [p for p in re.split(r"[\\/]+", winpath) if p]
        cur = self.root
        for p in parts:
            real = self._listing(cur).get(p.lower())
            if real is None:
                return None
            cur = cur / real
        if RECORDER is not None:
            RECORDER(self.root, cur)
        return cur

    def exists(self, winpath):
        return self.resolve(winpath) is not None

    def listdir(self, winpath):
        p = self.resolve(winpath)
        if p is None or not p.is_dir():
            return []
        return sorted(self._listing(p).values(), key=str.lower)


def inspect_file(path, magic=b"MZ"):
    """Return (status, detail). status: ok | missing | empty | zeroed | invalid | unreadable"""
    if path is None:
        return "missing", _("file does not exist")
    try:
        st = path.stat()
    except OSError as e:
        return "unreadable", _(t"cannot stat: {e.strerror}")
    if path.is_dir():
        return "invalid", _("is a directory")
    if st.st_size == 0:
        return "empty", _("file is 0 bytes")
    try:
        with open(path, "rb") as f:
            head = f.read(4096)
    except OSError as e:
        return "unreadable", _(t"read error: {e.strerror} (file may be damaged, or WOF/LZX-compressed and unsupported by the Linux NTFS driver)")
    if not head.strip(b"\0"):
        return "zeroed", _(t"first {len(head)} bytes are all zero (content lost, typical after a crash or power loss during an update)")
    if magic and not head.startswith(magic):
        return "invalid", _(t"does not start with {magic!r} (found {head[:4]!r}) - the file content is not valid")
    return "ok", _(t"{st.st_size} bytes")


STATUS_WORDS = {"missing": N_("missing"), "empty": N_("empty"), "zeroed": N_("zeroed"),
                "invalid": N_("invalid"), "unreadable": N_("unreadable"), "corrupt": N_("corrupt")}


def status_word(st):
    """Translated adjective for an inspect_file() status code."""
    return _(STATUS_WORDS[st]) if st in STATUS_WORDS else st


def human_size(n):
    n = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024 or unit == "TiB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024


def read_text_any(path, limit=4 * 1024 * 1024):
    """Read a Windows text log (UTF-16 with/without BOM, UTF-8, or ANSI)."""
    with open(path, "rb") as f:
        b = f.read(limit)
    if b.startswith(b"\xff\xfe"):
        return b[2:].decode("utf-16-le", errors="replace")
    if b.startswith(b"\xef\xbb\xbf"):
        return b[3:].decode("utf-8", errors="replace")
    if len(b) > 4 and b[1] == 0 and b[3] == 0:
        return b.decode("utf-16-le", errors="replace")
    return b.decode("utf-8", errors="replace")


def read_tail(path, size):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        n = f.tell()
        f.seek(max(0, n - size))
        return f.read()
