"""Evidence bundle: runs the analysis and copies everything it looked at into a directory.

The bundle can be sent to someone else for support, and it is what the test suite replays
(tests/replay.py). It is read-only for the disk like every analysis.
Password databases (SAM, SECURITY) are never copied.
"""

import json
import os
import shutil
from pathlib import Path

from . import fsutil, sysprobe
from .devices import find_partition, list_disks
from .mounting import Mounts
from .parsers.ntfs import identify, parse_boot_sector

PRIVATE = ("windows/system32/config/sam", "windows/system32/config/security")
MAX_COPY = 400 * 1024 * 1024
REGION = 1024 * 1024


class _Recorder:
    def __init__(self, out):
        self.out = out
        self.roots = {}      # mountpoint -> bundle subdir
        self.done = set()
        self.private = {}       # files deliberately not copied: rel -> size

    def __call__(self, root, path):
        dest_root = self.roots.get(str(root))
        if dest_root is None or str(path) in self.done:
            return
        self.done.add(str(path))
        rel = Path(path).relative_to(root)
        if str(rel).lower().replace("\\", "/").startswith(PRIVATE):
            try:
                self.private[str(rel)] = os.path.getsize(path)
            except OSError:
                pass
            return
        dest = dest_root / rel
        try:
            if Path(path).is_dir():
                dest.mkdir(parents=True, exist_ok=True)
                return
            dest.parent.mkdir(parents=True, exist_ok=True)
            if os.path.getsize(path) > MAX_COPY:
                with open(path, "rb") as src, open(dest, "wb") as dst:
                    dst.write(src.read(REGION))
            else:
                shutil.copy2(path, dest)
        except OSError:
            pass


def _capture(meta, out, dev, offset, length, tag):
    try:
        with open(dev, "rb") as f:
            size = f.seek(0, os.SEEK_END)
            offset = max(0, min(offset, size - 1))
            f.seek(offset)
            data = f.read(length)
    except OSError:
        return
    name = f"regions/{Path(dev).name}-{tag}-{offset}.bin"
    (out / name).write_bytes(data)
    meta["regions"].append({"dev": dev, "offset": offset, "file": name})
    meta["dev_sizes"][dev] = size


def collect(partition, outdir, esp="auto", key=None, progress=lambda m: None):
    from .analyzers import run_analysis

    out = Path(outdir)
    (out / "regions").mkdir(parents=True, exist_ok=True)
    disks = list_disks()
    disk, part = find_partition(disks, partition)
    if part is None:
        raise SystemExit(f"{partition} is not a partition")
    meta = {"target": part["name"], "esp": esp, "disks": disks, "probe": {}, "mounts": {}, "regions": [],
            "dev_sizes": {}}

    originals = {}
    for name in ("uefi_host", "efibootmgr_v", "smartctl_json", "dmesg_text", "secure_boot"):
        fn = getattr(sysprobe, name)
        originals[name] = fn

        def wrapper(*a, _fn=fn, _name=name):
            r = _fn(*a)
            meta["probe"][_name] = r
            return r
        setattr(sysprobe, name, wrapper)

    rec = _Recorder(out)
    fsutil.RECORDER = rec

    class RecMounts(Mounts):
        def mount_ro(self, dev, fstypes, label):
            mp, how = super().mount_ro(dev, fstypes, label)
            sub = f"fs-{Path(dev).name}"
            meta["mounts"][dev] = sub
            rec.roots[str(mp)] = out / sub
            return mp, how

    try:
        with RecMounts() as m:
            report = run_analysis(disks, disk, part, esp, key, {"events": True}, m, progress, lambda: False)
    finally:
        fsutil.RECORDER = None
        for k, v in originals.items():
            setattr(sysprobe, k, v)

    # raw regions: disk + every partition the analysis may read directly
    _capture(meta, out, disk["path"], 0, REGION, "head")
    _capture(meta, out, disk["path"], disk["size"] - REGION, REGION, "tail")
    parts = [part] + [p for d in disks for p in d["partitions"] if p.get("is_esp")]
    for p in parts:
        _capture(meta, out, p["path"], 0, REGION, "head")
        _capture(meta, out, p["path"], p["size"] - REGION, REGION, "tail")
    try:
        with open(part["path"], "rb") as f:
            bs = f.read(4096)
        if identify(bs) == "ntfs":
            b = parse_boot_sector(bs)
            if not b["problems"]:
                off = b["mft_lcn"] * b["cluster_size"]
                _capture(meta, out, part["path"], off, 64 * 1024, "mft")
    except OSError:
        pass

    meta["private"] = rec.private
    (out / "report.json").write_text(json.dumps(report, indent=2, default=str))
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=str))
    uid = os.environ.get("SUDO_UID") or os.environ.get("PKEXEC_UID")
    if uid:
        gid = int(os.environ.get("SUDO_GID", uid))
        for dirpath, dirnames, filenames in os.walk(out):
            for n in dirnames + filenames:
                try:
                    os.chown(os.path.join(dirpath, n), int(uid), gid)
                except OSError:
                    pass
        os.chown(out, int(uid), gid)
    return report
