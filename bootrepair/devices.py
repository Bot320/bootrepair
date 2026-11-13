"""Block device discovery via lsblk/sysfs (works without root)."""

import json
import os
import subprocess
from pathlib import Path

ESP_TYPES = {"c12a7328-f81f-11d2-ba4b-00a0c93ec93b", "0xef"}
MS_BASIC_DATA = {"ebd0a0a2-b9e5-4433-87c0-68b6b72699c7", "0x7", "0x07"}
MS_RESERVED = "e3c9e316-0b5c-4db8-817d-f92df00215ae"
WINRE_TYPE = "de94bba4-06d1-4d40-a16a-bfd50179d6ac"
MBR_HIDDEN_NTFS = {"0x17", "0x27"}

LSBLK_COLS = ("NAME,PATH,KNAME,PKNAME,TYPE,SIZE,FSTYPE,FSVER,LABEL,UUID,PARTUUID,PTUUID,PTTYPE,"
              "PARTTYPE,PARTTYPENAME,PARTLABEL,PARTFLAGS,MODEL,SERIAL,TRAN,MOUNTPOINTS,RO,RM,HOTPLUG,VENDOR")


def _sysfs_int(path):
    try:
        return int(Path(path).read_text().strip())
    except (OSError, ValueError):
        return None


def controller_kind(disk_name, tran):
    """Classify how the disk is attached, as Windows will see it: nvme | vmd | ahci | raid | usb | ..."""
    real = os.path.realpath(f"/sys/block/{disk_name}")
    tran = (tran or "").lower()
    if tran == "usb" or "/usb" in real:
        return "usb"
    if tran == "nvme" or disk_name.startswith("nvme"):
        # Intel VMD exposes NVMe drives behind a synthetic PCI domain (pci10000:...)
        if "/pci10000:" in real or "/pci1000" in real:
            return "vmd"
        return "nvme"
    if disk_name.startswith("vd"):
        return "virtio"
    if tran in ("sata", "ata"):
        # find the PCI controller driver
        p = Path(real)
        for parent in p.parents:
            drv = parent / "driver"
            if drv.exists():
                name = os.path.basename(os.path.realpath(drv))
                if name == "ahci":
                    return "ahci"
                if name in ("isci", "megaraid_sas", "mpt3sas"):
                    return "raid"
                if name not in ("sd", "scsi_disk"):
                    return "ahci" if "ahci" in name else name
        return "ahci"
    if tran in ("sas", "spi", "fc", "iscsi"):
        return "scsi"
    if disk_name.startswith("md"):
        return "raid"
    return tran or "unknown"


def list_disks():
    """Return list of disk dicts with 'partitions' list. Raises RuntimeError on failure."""
    try:
        out = subprocess.run(["lsblk", "-J", "-b", "-o", LSBLK_COLS], capture_output=True, text=True,
                             check=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError) as e:
        raise RuntimeError(f"lsblk failed: {e}")
    data = json.loads(out)
    disks = []
    for dev in data.get("blockdevices", []):
        if dev.get("type") != "disk":
            continue
        name = dev["name"]
        if name.startswith(("zram", "loop", "ram", "sr", "fd")):
            continue
        lbs = _sysfs_int(f"/sys/block/{name}/queue/logical_block_size") or 512
        disk = {
            "name": name,
            "path": dev.get("path") or f"/dev/{name}",
            "size": int(dev.get("size") or 0),
            "model": (dev.get("model") or "").strip(),
            "vendor": (dev.get("vendor") or "").strip(),
            "serial": dev.get("serial") or "",
            "tran": dev.get("tran") or "",
            "pttype": dev.get("pttype") or "",
            "ptuuid": dev.get("ptuuid") or "",
            "removable": bool(dev.get("rm")) or bool(dev.get("hotplug")),
            "logical_block_size": lbs,
            "controller": controller_kind(name, dev.get("tran")),
            "partitions": [],
        }
        for ch in dev.get("children") or []:
            if ch.get("type") not in ("part", "md"):
                continue
            pname = ch["name"]
            start = _sysfs_int(f"/sys/class/block/{pname}/start")
            partn = _sysfs_int(f"/sys/class/block/{pname}/partition")
            mps = [m for m in (ch.get("mountpoints") or []) if m]
            part = {
                "name": pname,
                "path": ch.get("path") or f"/dev/{pname}",
                "disk": name,
                "disk_path": disk["path"],
                "number": partn,
                "size": int(ch.get("size") or 0),
                "fstype": (ch.get("fstype") or "").lower(),
                "label": ch.get("label") or ch.get("partlabel") or "",
                "uuid": ch.get("uuid") or "",
                "partuuid": (ch.get("partuuid") or "").lower(),
                "ptuuid": (ch.get("ptuuid") or disk["ptuuid"] or "").lower(),
                "pttype": (ch.get("pttype") or disk["pttype"] or "").lower(),
                "parttype": (ch.get("parttype") or "").lower(),
                "parttypename": ch.get("parttypename") or "",
                "partflags": ch.get("partflags") or "",
                "mountpoints": mps,
                "start_bytes": start * 512 if start is not None else None,
            }
            part["is_esp"] = part["parttype"] in ESP_TYPES
            part["is_winre"] = part["parttype"] == WINRE_TYPE
            part["windows_score"] = windows_score(part)
            disk["partitions"].append(part)
        disks.append(disk)
    return disks


def windows_score(p):
    """Heuristic likelihood that the partition holds a Windows installation (0 = no)."""
    fs = p["fstype"]
    if p.get("is_esp") or p.get("is_winre") or p["parttype"] == MS_RESERVED:
        return 0
    if fs not in ("ntfs", "bitlocker", "") and not fs.startswith("ntfs"):
        return 0
    score = 0
    if fs == "ntfs":
        score += 40
    elif fs == "bitlocker":
        score += 35
    else:
        score += 5      # unknown filesystem might be damaged NTFS
    if p["parttype"] in MS_BASIC_DATA or p["parttype"] in MBR_HIDDEN_NTFS:
        score += 20
    gib = p["size"] / (1024 ** 3)
    if gib >= 30:
        score += 20
    elif gib >= 15:
        score += 10
    elif gib < 4:
        score -= 30
    if "windows" in p["label"].lower() or p["label"].lower() in ("os", "system", "c"):
        score += 10
    return max(score, 0)


def all_partitions(disks):
    return [p for d in disks for p in d["partitions"]]


def find_partition(disks, path_or_name):
    key = os.path.realpath(path_or_name) if path_or_name.startswith("/") else path_or_name
    for d in disks:
        for p in d["partitions"]:
            if p["path"] == path_or_name or p["path"] == key or p["name"] == path_or_name \
                    or f"/dev/{p['name']}" == key:
                return d, p
    return None, None
