"""Replay an evidence bundle (bootrepair-helper collect ...) through the analysis without root.

    python3 tests/replay.py ~/bundle            -> prints the text report
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixtures import FakeMounts  # noqa: E402
from bootrepair import sysprobe  # noqa: E402
from bootrepair.analyzers import run_analysis  # noqa: E402


def load_bundle(bundle, workdir, copy=False):
    bundle = Path(bundle)
    meta = json.loads((bundle / "meta.json").read_text())
    images = {}
    for dev, size in meta["dev_sizes"].items():
        img = Path(workdir) / (Path(dev).name + ".img")
        with open(img, "wb") as f:
            f.truncate(size)
        images[dev] = str(img)
    for r in meta["regions"]:
        with open(images[r["dev"]], "r+b") as f:
            f.seek(r["offset"])
            f.write((bundle / r["file"]).read_bytes())
    disks = meta["disks"]
    for d in disks:
        d["path"] = images.get(d["path"], d["path"])
        for p in d["partitions"]:
            orig = p["path"]
            p["path"] = images.get(orig, orig)
            p["disk_path"] = d["path"]
    # working copy of the mounted trees: hard links (fast) or a real copy when repairs will write to it
    work = Path(workdir) / "fs"
    work.mkdir(exist_ok=True)
    for sub in set(meta["mounts"].values()):
        if (bundle / sub).exists():
            subprocess.run(["cp", "-a", "--reflink=auto", str(bundle / sub), str(work / sub)], check=True)
        else:
            (work / sub).mkdir()
    mapping = {images.get(dev, dev): work / sub for dev, sub in meta["mounts"].items()}
    # SAM / SECURITY are never collected (privacy): stand in valid empty hives for them
    win_dir = work / f"fs-{meta['target']}"
    from hivebuilder import Key, build_hive
    for rel in meta.get("private") or {"Windows/System32/config/SAM": 1, "Windows/System32/config/SECURITY": 1}:
        real = win_dir / rel
        if not real.exists() and real.parent.exists():
            real.write_bytes(build_hive(Key("ROOT", subkeys=[Key("x")]), Path(rel).name))
    target = next(p for d in disks for p in d["partitions"] if p["name"] == meta["target"])
    disk = next(d for d in disks if target in d["partitions"])
    return meta, disks, disk, target, FakeMounts(mapping)


def probe_patches(meta):
    probe = meta.get("probe", {})
    return [
        mock.patch.object(sysprobe, "uefi_host", lambda: probe.get("uefi_host", True)),
        mock.patch.object(sysprobe, "efibootmgr_v", lambda: probe.get("efibootmgr_v")),
        mock.patch.object(sysprobe, "smartctl_json", lambda dev: probe.get("smartctl_json")),
        mock.patch.object(sysprobe, "dmesg_text", lambda: probe.get("dmesg_text") or ""),
        mock.patch.object(sysprobe, "secure_boot", lambda: probe.get("secure_boot", "unknown")),
        mock.patch("bootrepair.analyzers.volume.existing_mount", lambda dev: None),
    ]


def analyse(meta, disks, disk, target, mounts):
    patches = probe_patches(meta)
    for p in patches:
        p.start()
    try:
        return run_analysis(disks, disk, target, meta.get("esp", "auto"), None, {"events": True}, mounts,
                            lambda m: None, lambda: False)
    finally:
        for p in patches:
            p.stop()


def run_bundle(bundle, workdir):
    meta, disks, disk, target, mounts = load_bundle(bundle, workdir)
    return analyse(meta, disks, disk, target, mounts)


def _unused(meta, disks, disk, target, mounts):
    probe = meta.get("probe", {})
    patches = [
        mock.patch.object(sysprobe, "uefi_host", lambda: probe.get("uefi_host", True)),
        mock.patch.object(sysprobe, "efibootmgr_v", lambda: probe.get("efibootmgr_v")),
        mock.patch.object(sysprobe, "smartctl_json", lambda dev: probe.get("smartctl_json")),
        mock.patch.object(sysprobe, "dmesg_text", lambda: probe.get("dmesg_text") or ""),
        mock.patch.object(sysprobe, "secure_boot", lambda: probe.get("secure_boot", "unknown")),
        mock.patch("bootrepair.analyzers.volume.existing_mount", lambda dev: None),
    ]
    for p in patches:
        p.start()
    try:
        return run_analysis(disks, disk, target, meta.get("esp", "auto"), None, {"events": True}, mounts,
                            lambda m: None, lambda: False)
    finally:
        for p in patches:
            p.stop()


if __name__ == "__main__":
    from bootrepair.report import to_text
    with tempfile.TemporaryDirectory() as t:
        r = run_bundle(sys.argv[1], t)
    print(to_text(r))
    for f in r["findings"]:
        for a in f.get("actions", []):
            print(f"  [action] {f['severity']:8} {a['title']}  ({a['kind']}, risk {a['risk']})")
