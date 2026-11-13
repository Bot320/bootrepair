"""Privileged repair engine: applies selected actions with full backups, and can undo them.

Every file is copied into a backup directory before it is touched, renames are recorded, and
firmware (NVRAM) changes store their inverse commands. `undo()` replays the manifest backwards.
"""

import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from .devices import list_disks, find_partition
from .i18n import _
from .fsutil import CIRoot
from .mounting import Mounts, MountError
from .parsers import bcd as B
from .parsers.regf import Hive
from .parsers.regpatch import HivePatcher, PatchError
from .parsers.ntfs import identify

BACKUP_ROOT = Path("/var/lib/bootrepair/backups")


class FixError(Exception):
    pass


class FixContext:
    def __init__(self, disks, target, boot, mounts, backup_dir, log):
        self.disks = disks
        self.target = target
        self.boot = boot
        self.mounts = mounts
        self.backup_dir = backup_dir
        self.log = log
        self.roots = {}          # role -> CIRoot
        self.entries = []        # undo manifest
        self._backed_up = set()
        self.stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    def root(self, role):
        r = self.roots.get(role)
        if r is None:
            raise FixError((_("the Windows partition is not mounted writable") if role == "win" else
                            _("the boot partition is not mounted writable")))
        return r

    def resolve(self, role, rel, must=True):
        p = self.root(role).resolve(rel)
        if p is None and must:
            raise FixError(_(t"\\{rel} not found"))
        return p

    def rel_of(self, role, path):
        return str(Path(path).relative_to(self.root(role).root))

    # ---------------------------------------------------------------- backups
    def backup(self, role, path):
        path = Path(path)
        rel = self.rel_of(role, path)
        if (role, rel) in self._backed_up:      # keep the ORIGINAL, not an intermediate state
            return
        self._backed_up.add((role, rel))
        if path.exists():
            dest = self.backup_dir / "files" / role / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            self.entries.append({"op": "file", "role": role, "rel": rel, "backup": str(dest)})
        else:
            self.entries.append({"op": "created", "role": role, "rel": rel})

    def rename(self, role, path, new_name):
        path = Path(path)
        new = path.with_name(new_name)
        os.rename(path, new)
        self.entries.append({"op": "rename", "role": role, "from": self.rel_of(role, path),
                             "to": self.rel_of(role, new)})
        return new

    def patch_hive(self, role, rel):
        p = self.resolve(role, rel)
        h = Hive.from_file(p)
        if not h.sequence_ok:
            raise FixError(_(t"\\{rel} has unsaved transaction-log data (sequence {h.seq1}/{h.seq2}); "
                             t"editing it from Linux could lose that data. Let Windows/WinRE start once, "
                             t"or use the manual steps."))
        self.backup(role, p)
        return HivePatcher(p)


def _cs(params):
    cs = params.get("cs") or "ControlSet001"
    if not re.fullmatch(r"ControlSet\d{3}", cs):
        raise FixError(_(t"invalid control set name"))
    return cs


# ============================================================================ fixers
def fx_set_service_start(c, p):
    cs = _cs(p)
    hp = c.patch_hive("win", "Windows\\System32\\config\\SYSTEM")
    key = f"{cs}\\Services\\{p['service']}"
    hp.set_dword(key, "Start", int(p["start"]))
    if p.get("clear_override"):
        k = hp.hive.open(key + "\\StartOverride")
        if k is not None:
            for v in k.values():
                if v.type == 4 and v.data != 0:
                    hp.set_dword(key + "\\StartOverride", v.name, 0)
    return hp.commit()


def fx_remove_class_filter(c, p):
    cs = _cs(p)
    hp = c.patch_hive("win", "Windows\\System32\\config\\SYSTEM")
    key = f"{cs}\\Control\\Class\\{p['class_guid']}"
    cur = hp.get(key, p["value"]) or []
    if isinstance(cur, str):
        cur = [cur]
    new = [x for x in cur if x.lower() != p["filter"].lower()]
    if len(new) == len(cur):
        return [_(t"'{p['filter']}' is no longer in {p['value']} - nothing to do")]
    hp.set_multi_sz(key, p["value"], new)
    return hp.commit()


def fx_clear_pending_renames(c, p):
    cs = _cs(p)
    hp = c.patch_hive("win", "Windows\\System32\\config\\SYSTEM")
    key = f"{cs}\\Control\\Session Manager"
    done = False
    for name in ("PendingFileRenameOperations", "PendingFileRenameOperations2"):
        if hp.get(key, name) is not None:
            hp.delete_value(key, name)
            done = True
    return hp.commit() if done else [_(t"no pending operations left")]


def fx_disable_verifier(c, p):
    cs = _cs(p)
    hp = c.patch_hive("win", "Windows\\System32\\config\\SYSTEM")
    key = f"{cs}\\Control\\Session Manager\\Memory Management"
    for name in ("VerifyDrivers", "VerifyDriverLevel"):
        if hp.get(key, name) is not None:
            hp.delete_value(key, name)
    return hp.commit()


def fx_reg_set_dword(c, p):
    rel = {"SYSTEM": "Windows\\System32\\config\\SYSTEM", "SOFTWARE": "Windows\\System32\\config\\SOFTWARE"}[p["hive"]]
    hp = c.patch_hive("win", rel)
    hp.set_dword(p["path"], p["name"], int(p["value"]))
    return hp.commit()


def fx_reg_delete_values(c, p):
    rel = {"SYSTEM": "Windows\\System32\\config\\SYSTEM", "SOFTWARE": "Windows\\System32\\config\\SOFTWARE"}[p["hive"]]
    hp = c.patch_hive("win", rel)
    for name in p["names"]:
        if hp.get(p["path"], name) is not None:
            hp.delete_value(p["path"], name)
    return hp.commit() or [_(t"values already gone")]


def fx_revert_pending_update(c, p):
    out = []
    pend = c.resolve("win", "Windows\\WinSxS\\pending.xml", must=False)
    if pend is not None:
        c.rename("win", pend, f"pending.xml.bootrepair-{c.stamp}")
        out.append(_(t"\\Windows\\WinSxS\\pending.xml renamed to pending.xml.bootrepair-{c.stamp}"))
    comp = c.resolve("win", "Windows\\System32\\config\\COMPONENTS", must=False)
    if comp is not None:
        hp = c.patch_hive("win", "Windows\\System32\\config\\COMPONENTS")
        for name in ("PendingXmlIdentifier", "NextQueueEntryIndex", "AdvancedInstallersNeedResolving"):
            if hp.get("", name) is not None:
                hp.delete_value("", name)
        out += hp.commit()
    return out or [_(t"nothing pending any more")]


def fx_restore_system_file(c, p):
    src = c.resolve("win", p["src"])
    with open(src, "rb") as f:
        if f.read(2) != b"MZ":
            raise FixError(_(t"source \\{p['src']} is not a valid program file"))
    dst_rel = p["dst"]
    dst = c.resolve("win", dst_rel, must=False)
    if dst is None:
        parent = c.resolve("win", str(Path(dst_rel.replace("\\", "/")).parent).replace("/", "\\"))
        dst = parent / Path(dst_rel.replace("\\", "/")).name
    c.backup("win", dst)
    shutil.copyfile(src, dst)
    os.sync()
    return [_(t"\\{dst_rel} restored from \\{p['src']} ({os.path.getsize(dst)} bytes)")]


def fx_restore_hive_regback(c, p):
    hive = p["hive"]
    if hive not in ("SYSTEM", "SOFTWARE", "DEFAULT", "SAM", "SECURITY"):
        raise FixError(_(t"invalid hive"))
    rb = c.resolve("win", f"Windows\\System32\\config\\RegBack\\{hive}")
    if rb.stat().st_size == 0:
        raise FixError(_(t"RegBack copy is empty"))
    Hive.from_file(rb)   # must parse
    cur = c.resolve("win", f"Windows\\System32\\config\\{hive}", must=False)
    cfg = c.resolve("win", "Windows\\System32\\config")
    out = []
    if cur is not None:
        c.backup("win", cur)
    for ext in ("LOG", "LOG1", "LOG2"):
        lp = c.resolve("win", f"Windows\\System32\\config\\{hive}.{ext}", must=False)
        if lp is not None:
            c.rename("win", lp, f"{lp.name}.bootrepair-{c.stamp}")
            out.append(_(t"{lp.name} renamed"))
    dst = cur or (cfg / hive)
    if cur is None:
        c.entries.append({"op": "created", "role": "win", "rel": c.rel_of("win", dst)})
    shutil.copyfile(rb, dst)
    os.sync()
    return out + [_(t"{hive} restored from RegBack")]


def fx_discard_hibernation(c, p):
    hp = c.resolve("win", "hiberfil.sys", must=False)
    if hp is None:
        return [_(t"hiberfil.sys is already gone")]
    c.rename("win", hp, f"hiberfil.sys.bootrepair-{c.stamp}")
    return [_(t"hiberfil.sys renamed - Windows will do a fresh start")]


# ---------------------------------------------------------------- BCD
def _bcd(c, p):
    rel = p.get("bcd") or "EFI\\Microsoft\\Boot\\BCD"
    return c.patch_hive("boot", rel)


def _elem_path(obj, etype):
    return f"Objects\\{obj}\\Elements\\{etype:08x}"


def fx_bcd_repoint(c, p):
    hp = _bcd(c, p)
    store = B.BcdStore(hp.hive)
    done = []
    for g in p["objects"]:
        o = store.get(g)
        if o is None:
            raise FixError(_(t"BCD object {g} no longer exists"))
        for et in (B.E_DEVICE, B.E_OSDEVICE):
            blob = o.get(et)
            if blob is None:
                continue
            new = B.set_partition(blob, c.target)
            if new != blob:
                key = _real_key(hp, _elem_path(o.guid, et))
                hp.set_binary(key, "Element", new)
                done.append(g)
    out = hp.commit()
    store = B.BcdStore(Hive.from_file(c.resolve("boot", p.get("bcd") or "EFI\\Microsoft\\Boot\\BCD")))
    for g in p["objects"]:
        o = store.get(g)
        if not B.device_matches(o.get(B.E_OSDEVICE) or o.get(B.E_DEVICE), c.target):
            raise FixError(_(t"verification failed: entry does not point at the target after the change"))
    return out or [_(t"entries already point at this partition")]


def _real_key(hp, path):
    """Element key names are case-sensitive hex in practice; find the actual spelling."""
    k = hp.hive.open(path)
    if k is None:
        raise FixError(_(t"BCD key {path} not found"))
    return path


def fx_bcd_set_default(c, p):
    hp = _bcd(c, p)
    key = _elem_path(B.BOOTMGR, B.E_DEFAULT)
    cur = hp.get(key, "Element")
    if cur is None:
        raise FixError(_(t"{{bootmgr}} has no default setting to change"))
    new = p["object"]
    if len(new) != len(cur):
        raise FixError(_(t"unexpected identifier format"))
    store = B.BcdStore(hp.hive)
    real = store.get(new)
    if real is None:
        raise FixError(_(t"target entry not found"))
    hp.set_string(key, "Element", real.guid if cur.islower() else real.guid.upper())
    return hp.commit()


def fx_bcd_delete_elements(c, p):
    hp = _bcd(c, p)
    for e in p["elements"]:
        if not re.fullmatch(r"[0-9a-fA-F]{8}", e):
            raise FixError(_(t"invalid element id"))
        path = f"Objects\\{p['object']}\\Elements\\{e}"
        if hp.hive.open(path) is not None:
            hp.delete_key(path)
    return hp.commit()


def fx_bcd_delete_objects(c, p):
    hp = _bcd(c, p)
    store = B.BcdStore(hp.hive)
    targets = {g.lower() for g in p["objects"]}
    bm = store.bootmgr
    if bm is not None:
        for et in (B.E_DISPLAYORDER, B.E_TOOLSORDER, B.E_BOOTSEQUENCE):
            lst = bm.get(et)
            if lst:
                key = _elem_path(B.BOOTMGR, et)
                new = [g for g in lst if g.lower() not in targets]
                if len(new) != len(lst):
                    hp.set_multi_sz(key, "Element", new)
        if (bm.get(B.E_DEFAULT) or "").lower() in targets:
            raise FixError(_(t"refusing to delete the default entry"))
    for g in p["objects"]:
        o = B.BcdStore(hp.hive).get(g)
        if o is not None:
            hp.delete_key(f"Objects\\{_actual_name(hp, g)}")
    return hp.commit()


def _actual_name(hp, guid):
    objs = hp.hive.open("Objects")
    for k in objs.subkeys():
        if k.name.lower() == guid.lower():
            return k.name
    raise FixError(_(t"object {guid} not found"))


def fx_esp_restore_bootfiles(c, p):
    src = c.resolve("win", "Windows\\Boot\\EFI")
    esp = c.root("boot").root
    dest = esp / "EFI" / "Microsoft" / "Boot"
    dest.mkdir(parents=True, exist_ok=True)
    out = []
    for f in sorted(src.rglob("*")):
        if f.is_dir() or f.name.upper().startswith("BCD"):
            continue
        rel = f.relative_to(src)
        d = dest / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        c.backup("boot", d)
        shutil.copyfile(f, d)
        out.append(_(t"\\EFI\\Microsoft\\Boot\\{str(rel).replace('/', chr(92))}"))
    os.sync()
    return [_(t"copied {len(out)} files")] + out[:10]


# ---------------------------------------------------------------- firmware
def _efibootmgr(*args):
    r = subprocess.run(["efibootmgr", *args], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise FixError(_(t"efibootmgr {' '.join(args)}: {(r.stderr or r.stdout).strip()}"))
    return r.stdout


def _bootorder(text):
    m = re.search(r"^BootOrder:\s*(\S+)", text, re.M)
    return m.group(1) if m else ""


def _num(n):
    if not re.fullmatch(r"[0-9A-Fa-f]{4}", str(n)):
        raise FixError(_(t"invalid boot entry number"))
    return str(n).upper()


def fx_nvram_create(c, p):
    if not re.fullmatch(r"/dev/[\w/-]+", p["disk"]) or not str(p["partnum"]).isdigit():
        raise FixError(_(t"invalid disk/partition"))
    before = _efibootmgr()
    nums_before = set(re.findall(r"^Boot([0-9A-F]{4})", before, re.M))
    after = _efibootmgr("-c", "-d", p["disk"], "-p", str(p["partnum"]), "-L", "Windows Boot Manager",
                        "-l", "\\EFI\\Microsoft\\Boot\\bootmgfw.efi")
    new = set(re.findall(r"^Boot([0-9A-F]{4})", after, re.M)) - nums_before
    undo = [["-b", n, "-B"] for n in new] + ([["-o", _bootorder(before)]] if _bootorder(before) else [])
    c.entries.append({"op": "nvram", "undo": undo})
    return [_(t"created Boot{n}") for n in new]


def fx_nvram_first(c, p):
    num = _num(p["num"])
    before = _efibootmgr()
    order = [x for x in _bootorder(before).split(",") if x]
    new = [num] + [x for x in order if x != num]
    _efibootmgr("-o", ",".join(new))
    c.entries.append({"op": "nvram", "undo": [["-o", ",".join(order)]] if order else []})
    return [_(t"BootOrder: {','.join(order)} -> {','.join(new)}")]


def fx_nvram_append(c, p):
    num = _num(p["num"])
    before = _efibootmgr()
    order = [x for x in _bootorder(before).split(",") if x]
    new = [x for x in order if x != num] + [num]
    _efibootmgr("-o", ",".join(new))
    c.entries.append({"op": "nvram", "undo": [["-o", ",".join(order)]] if order else []})
    return [_(t"BootOrder: {','.join(order)} -> {','.join(new)}")]


def fx_nvram_activate(c, p):
    num = _num(p["num"])
    _efibootmgr("-b", num, "-a")
    c.entries.append({"op": "nvram", "undo": [["-b", num, "-A"]]})
    return [_(t"Boot{num} activated")]


def fx_nvram_delete(c, p):
    num = _num(p["num"])
    before = _efibootmgr("-v")
    line = next((l for l in before.splitlines() if l.startswith(f"Boot{num}")), "")
    _efibootmgr("-b", num, "-B")
    c.entries.append({"op": "nvram", "undo": [], "note": f"deleted entry was: {line}"})
    return [_(t"Boot{num} removed")]


FIXERS = {
    "set_service_start": fx_set_service_start,
    "remove_class_filter": fx_remove_class_filter,
    "clear_pending_renames": fx_clear_pending_renames,
    "disable_verifier": fx_disable_verifier,
    "reg_set_dword": fx_reg_set_dword,
    "reg_delete_values": fx_reg_delete_values,
    "revert_pending_update": fx_revert_pending_update,
    "restore_system_file": fx_restore_system_file,
    "restore_hive_regback": fx_restore_hive_regback,
    "discard_hibernation": fx_discard_hibernation,
    "bcd_repoint": fx_bcd_repoint,
    "bcd_set_default": fx_bcd_set_default,
    "bcd_delete_elements": fx_bcd_delete_elements,
    "bcd_delete_objects": fx_bcd_delete_objects,
    "esp_restore_bootfiles": fx_esp_restore_bootfiles,
    "nvram_create": fx_nvram_create,
    "nvram_first": fx_nvram_first,
    "nvram_append": fx_nvram_append,
    "nvram_activate": fx_nvram_activate,
    "nvram_delete": fx_nvram_delete,
}


# ============================================================================ driver
def _mount_role(c, role, part, mounts, extra=None):
    if role == "win":
        with open(part["path"], "rb") as f:
            kind = identify(f.read(512))
        if kind == "bitlocker":
            raise FixError(_(t"repairs on BitLocker-encrypted volumes are not supported yet - use the manual steps"))
        # ntfs3 only: it refuses dirty volumes. ntfs-3g would reset the NTFS journal on an unclean volume,
        # so it is used solely to discard a hibernation image (its remove_hiberfile option).
        fstypes = ["ntfs-3g"] if extra else ["ntfs3"]
        mp, how = mounts.mount_rw(part["path"], fstypes, "windows", extra)
    else:
        fs = ["vfat"] if part.get("fstype") in ("vfat", "") or part.get("is_esp") else ["ntfs3", "ntfs-3g", "vfat"]
        mp, how = mounts.mount_rw(part["path"], fs, "boot")
    c.roots[role] = CIRoot(mp)
    c.log(f"{role}: {how}")


def apply(partition, boot, actions, progress=lambda m: None, mounts=None, disks=None, backup_root=None,
          state=None):
    """Apply actions. Returns result dict. `mounts`/`disks` can be injected for tests."""
    disks = disks if disks is not None else list_disks()
    __, target = find_partition(disks, partition)
    if target is None:
        raise FixError(_(t"{partition} not found"))
    bpart = None
    if boot:
        __, bpart = find_partition(disks, boot)
    state = state or {}
    discard = any(a["kind"] == "discard_hibernation" for a in actions)
    if state.get("hibernated") and not discard and any("win" in a.get("needs", ["win"]) for a in actions):
        raise FixError(_(t"Windows is hibernated (Fast Startup). Writing to it now would be lost or corrupt the volume "
                         t"when Windows resumes. Include 'Discard the hibernation image' or boot Windows and shut it "
                         t"down fully first."))
    unknown = [a["kind"] for a in actions if a["kind"] not in FIXERS]
    if unknown:
        raise FixError(_(t"unknown repair actions: {unknown}"))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bdir = Path(backup_root or BACKUP_ROOT) / f"{stamp}-{target['name']}"
    bdir.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(bdir.parent, 0o700)    # backups contain registry hives
    except OSError:
        pass
    log_lines = []

    def log(msg):
        log_lines.append(msg)
        progress({"type": "log", "msg": msg})

    mounts = mounts if mounts is not None else Mounts()
    c = FixContext(disks, target, bpart, mounts, bdir, log)
    results = []
    manifest = {"created": stamp, "target": {"path": target["path"], "partuuid": target.get("partuuid")},
                "boot": {"path": bpart["path"], "partuuid": bpart.get("partuuid")} if bpart else None,
                "actions": actions, "entries": c.entries}
    try:
        needs = {n for a in actions for n in a.get("needs", ["win"])}
        extra = {"ntfs-3g": "remove_hiberfile"} if any(a["kind"] == "discard_hibernation" for a in actions) else None
        if "win" in needs:
            try:
                _mount_role(c, "win", target, mounts, extra)
            except MountError as e:
                raise FixError(_(t"cannot open the Windows volume for writing: {e}. If it is marked dirty, run "
                                 t"'chkdsk C: /f' from WinRE first (BootRepair will not write to an unclean NTFS)."))
        if "boot" in needs:
            if bpart is None:
                raise FixError(_(t"no boot partition given"))
            _mount_role(c, "boot", bpart, mounts)
        for a in actions:
            progress({"type": "fix", "id": a["id"], "state": "running"})
            try:
                changes = FIXERS[a["kind"]](c, a.get("params", {}))
                results.append({"id": a["id"], "title": a["title"], "ok": True, "changes": changes})
                progress({"type": "fix", "id": a["id"], "state": "done"})
            except (FixError, PatchError, OSError, ValueError, KeyError) as e:
                results.append({"id": a["id"], "title": a["title"], "ok": False, "error": str(e)})
                progress({"type": "fix", "id": a["id"], "state": "failed", "note": str(e)})
            (bdir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
        os.sync()
    finally:
        mounts.cleanup()
        (bdir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    return {"backup": str(bdir), "results": results, "log": log_lines}


def latest_backup(root=None):
    root = Path(root or BACKUP_ROOT)
    dirs = sorted([d for d in root.glob("*") if (d / "manifest.json").exists()]) if root.exists() else []
    return dirs[-1] if dirs else None


def list_backups(root=None):
    root = Path(root or BACKUP_ROOT)
    out = []
    for d in sorted(root.glob("*")) if root.exists() else []:
        try:
            m = json.loads((d / "manifest.json").read_text())
        except (OSError, ValueError):
            continue
        out.append({"dir": str(d), "created": m.get("created"), "target": m.get("target", {}).get("path"),
                    "actions": [a.get("title") for a in m.get("actions", [])], "undone": (d / "UNDONE").exists()})
    return out


def undo(backup_dir, progress=lambda m: None, mounts=None, disks=None):
    bdir = Path(backup_dir)
    m = json.loads((bdir / "manifest.json").read_text())
    disks = disks if disks is not None else list_disks()
    target = _find_by_uuid(disks, m["target"])
    boot = _find_by_uuid(disks, m["boot"]) if m.get("boot") else None
    mounts = mounts if mounts is not None else Mounts()
    c = FixContext(disks, target, boot, mounts, bdir, lambda s: progress({"type": "log", "msg": s}))
    out = []
    try:
        roles = {e.get("role") for e in m["entries"] if e.get("role")}
        if "win" in roles:
            _mount_role(c, "win", target, mounts)
        if "boot" in roles:
            _mount_role(c, "boot", boot, mounts)
        for e in reversed(m["entries"]):
            op = e["op"]
            if op == "file":
                dst = c.root(e["role"]).root / e["rel"]
                shutil.copy2(e["backup"], dst)
                out.append(_(t"restored {e['rel']}"))
            elif op == "created":
                p = c.root(e["role"]).root / e["rel"]
                if p.exists():
                    p.unlink()
                out.append(_(t"removed {e['rel']}"))
            elif op == "rename":
                root = c.root(e["role"]).root
                os.rename(root / e["to"], root / e["from"])
                out.append(_(t"renamed {e['to']} back to {e['from']}"))
            elif op == "nvram":
                for args in e.get("undo", []):
                    _efibootmgr(*args)
                out.append(_(t"firmware entry change reverted") if e.get("undo") else
                           _(t"cannot recreate a deleted firmware entry ({e.get('note', '')})"))
        os.sync()
        (bdir / "UNDONE").write_text(time.ctime())
    finally:
        mounts.cleanup()
    return out


def _find_by_uuid(disks, info):
    for d in disks:
        for p in d["partitions"]:
            if info.get("partuuid") and p.get("partuuid") == info["partuuid"]:
                return p
    __, p = find_partition(disks, info["path"])
    if p is None:
        raise FixError(_(t"partition {info['path']} not found"))
    return p
