"""Boot partition checks: EFI system partition + firmware boot entries (UEFI) or active partition (BIOS)."""

import os
import re

from ..i18n import _, N_
from .. import sysprobe
from .. import actions as A
from ..fsutil import CIRoot, inspect_file, human_size, status_word
from ..knowledge import WINRE, LINUX
from ..mounting import MountError
from ..parsers.bcd import BcdStore, device_matches, E_OSDEVICE, E_DEVICE
from ..parsers.ntfs import identify, parse_boot_sector
from ..parsers.regf import RegfError
from .context import part_label

SRC = "bootpart"


ASSIGN_S = N_("Give the EFI partition the drive letter S:. It is the small FAT32 volume in the list; replace N with "
            "its number:\n`diskpart\nlist vol\nselect vol N\nassign letter=S\nexit`")
BCDBOOT_UEFI = N_("Rebuild Windows Boot Manager, the boot configuration and the firmware boot entry:\n"
                "`bcdboot C:\\Windows /s S: /f UEFI`")


def bcdboot_fix(ctx):
    """Manual steps that rebuild the boot files and the BCD from the Windows installation."""
    if ctx.boot_mode == "bios":
        return [WINRE,
                _(t"Rebuild the boot files and the boot configuration. If the disk has a separate “System Reserved” "
                  t"partition, give it a letter in diskpart first and use that letter after /s instead of C:\n"
                  t"`bcdboot C:\\Windows /s C: /f BIOS`"),
                _(t"Rewrite the boot code:\n`bootrec /fixmbr\nbootsect /nt60 SYS /mbr`")]
    return [WINRE, ASSIGN_S, BCDBOOT_UEFI]


def _store_points_to_target(store, target):
    for o in store.osloaders():
        if device_matches(o.get(E_OSDEVICE), target) or device_matches(o.get(E_DEVICE), target):
            return True
    return False


def analyze(ctx):
    if ctx.boot_mode == "bios":
        _legacy(ctx)
    else:
        _uefi(ctx)
        _nvram(ctx)
        _secure_boot(ctx)


# ============================================================================ UEFI
def _uefi(ctx):
    esps = [p for p in ctx.all_partitions() if p["is_esp"]]
    ev = {"candidates": []}
    ctx.evidence["boot_partition"] = ev
    if ctx.esp_choice and ctx.esp_choice != "auto":
        cands = [p for p in esps if p["path"] == ctx.esp_choice or p["name"] == ctx.esp_choice.split("/")[-1]]
        if not cands:
            p = next((p for p in ctx.all_partitions() if p["path"] == ctx.esp_choice), None)
            cands = [p] if p else []
    else:
        same = [p for p in esps if p["disk"] == ctx.disk["name"]]
        cands = same or esps

    if not cands:
        ctx.add("critical", "bootmgr", _(t"There is no EFI System Partition"),
                _(t"UEFI firmware can only start Windows from a FAT32 partition of type 'EFI System'. None exists "
                  t"on any connected disk, so there is nothing for the firmware to boot."),
                ["no partition with type GUID c12a7328-f81f-11d2-ba4b-00a0c93ec93b found"],
                [WINRE,
                 _(t"Take 300 MB from the Windows volume and create an EFI partition there:\n"
                   t"`diskpart\nselect vol C\nshrink desired=300\ncreate partition efi size=300\n"
                   t"format quick fs=fat32 label=System\nassign letter=S\nexit`"),
                 BCDBOOT_UEFI],
                stopcode="firmware: no bootable device", source=SRC, priority=1)
        return

    scored = []
    for p in cands:
        item = {"partition": p["name"], "path": p["path"], "disk": p["disk"], "fstype": p["fstype"],
                "size": p["size"]}
        ev["candidates"].append(item)
        try:
            mp, how = ctx.mounts.mount_ro(p["path"], ["vfat"], "esp")
        except MountError as e:
            item["error"] = str(e)
            scored.append((-1, p, item, None, None))
            continue
        item["mount"] = how
        root = CIRoot(mp)
        bm = root.resolve("EFI\\Microsoft\\Boot\\bootmgfw.efi")
        bcdp = root.resolve("EFI\\Microsoft\\Boot\\BCD")
        store = None
        if bcdp is not None:
            try:
                store = BcdStore.from_file(bcdp)
            except (OSError, RegfError, Exception):
                store = None
        points = bool(store and _store_points_to_target(store, ctx.target))
        item.update({"bootmgfw": bm is not None, "bcd": bcdp is not None, "bcd_targets_selected": points})
        score = points * 100 + (bm is not None) * 10 + (bcdp is not None) * 5 + (p["disk"] == ctx.disk["name"]) * 2
        scored.append((score, p, item, root, mp))

    scored.sort(key=lambda t: t[0], reverse=True)
    score, p, item, root, mp = scored[0]
    ctx.boot_part = p
    ev["chosen"] = p["name"]
    item["chosen"] = True
    if root is None:
        ctx.add("critical", "bootmgr", _(t"The EFI System Partition {part_label(p)} cannot be read"),
                _(t"The ESP's FAT file system is damaged or it is not FAT at all. The firmware cannot load Windows "
                  t"Boot Manager from it."), [item.get("error", ""), f"lsblk fstype: {p['fstype'] or 'none'}"],
                [_(t"Formatting erases everything on the EFI partition. If Linux boots from the same partition, its "
                   t"boot loader has to be reinstalled afterwards."),
                 WINRE,
                 _(t"Format the EFI partition (the small volume; replace N with its number):\n"
                   t"`diskpart\nlist vol\nselect vol N\nformat quick fs=fat32 label=System\nassign letter=S\nexit`"),
                 BCDBOOT_UEFI],
                stopcode="firmware: no bootable device", source=SRC, priority=2)
        return
    ctx.boot_mount = root
    if p["disk"] != ctx.disk["name"]:
        ctx.add("info", "bootmgr", _(t"Windows boots through an EFI partition on a different disk"),
                _(t"The boot files for this Windows are on {part_label(p)} (disk {p['disk']}). If that disk is "
                  t"removed, wiped or reordered, Windows will no longer start."),
                [f"Windows: /dev/{ctx.target['name']} on {ctx.disk['name']}; ESP: /dev/{p['name']} on {p['disk']}"],
                [_(t"Nothing needs to be done as long as both disks stay connected.")], source=SRC)
    if len([c for c in scored if c[3] is not None]) > 1:
        others = [f"/dev/{c[1]['name']}: bootmgfw={'yes' if c[2].get('bootmgfw') else 'no'}, "
                  f"BCD={'yes' if c[2].get('bcd') else 'no'}, has entry for this Windows="
                  f"{'yes' if c[2].get('bcd_targets_selected') else 'no'}" for c in scored]
        ctx.add("info", "bootmgr", _(t"Several EFI partitions are present"),
                _(t"Using {part_label(p)} for the analysis (it fits this Windows best). Which one the firmware "
                  t"actually uses is decided by the firmware boot entry (see below)."), others, source=SRC)

    bm = root.resolve("EFI\\Microsoft\\Boot\\bootmgfw.efi")
    status, detail = inspect_file(bm)
    ev["bootmgfw"] = f"{status}: {detail}"
    if status == "missing":
        ctx.add("critical", "bootmgr", _(t"Windows Boot Manager (bootmgfw.efi) is missing from the EFI partition"),
                _(t"The firmware has nothing to start: \\EFI\\Microsoft\\Boot\\bootmgfw.efi does not exist on "
                  t"{part_label(p)}. Typical after a Linux installer or a tool reformatted the ESP. The PC boots "
                  t"straight to the firmware setup, another OS, or shows 'no bootable device'."),
                [f"/dev/{p['name']}: \\EFI\\Microsoft\\Boot\\ not containing bootmgfw.efi",
                 "contents of \\EFI: " + ", ".join(root.listdir("EFI"))],
                bcdboot_fix(ctx), stopcode="firmware: no bootable device", source=SRC, priority=3,
                actions=_bootfile_actions(ctx))
    elif status != "ok":
        ctx.add("critical", "bootmgr", _(t"Windows Boot Manager (bootmgfw.efi) is damaged ({status})"),
                _(t"The boot manager file exists but cannot be a valid EFI program, so the firmware refuses it."),
                [f"\\EFI\\Microsoft\\Boot\\bootmgfw.efi: {detail}"], bcdboot_fix(ctx),
                stopcode="firmware: no bootable device / Secure Boot violation", source=SRC, priority=3,
                actions=_bootfile_actions(ctx))

    bcdp = root.resolve("EFI\\Microsoft\\Boot\\BCD")
    ctx.bcd_path = bcdp
    if bcdp is None:
        ctx.add("critical", "bcd", _(t"The BCD store is missing"),
                _(t"Boot Manager starts but finds no boot configuration and shows 'The Boot Configuration Data for "
                  t"your PC is missing or contains errors'."),
                [f"/dev/{p['name']}: \\EFI\\Microsoft\\Boot\\BCD does not exist"],
                bcdboot_fix(ctx), stopcode="0xc000000f", source=SRC, priority=4)

    fb = root.resolve("EFI\\Boot\\bootx64.efi")
    if fb is not None:
        kind = _identify_efi(fb, bm)
        ev["fallback_loader"] = kind
    try:
        sv = os.statvfs(mp)
        free = sv.f_bavail * sv.f_frsize
        ev["esp_free"] = free
        if free < 2 * 1024 * 1024:
            ctx.add("warning", "bootmgr", _(t"EFI partition is almost full ({human_size(free)} free)"),
                    _(t"Windows updates have to write new boot files to the ESP; when that fails, the boot files can be "
                      t"left half-updated (and the update rolls back)."), [f"free {human_size(free)}"],
                    [_(t"Delete boot loaders of systems that are no longer installed, and old Linux kernel images, "
                       t"from the EFI partition.")], source=SRC)
    except OSError:
        pass


def _bootfile_actions(ctx):
    if ctx.win is not None and ctx.win.resolve("Windows\\Boot\\EFI\\bootmgfw.efi") is not None \
            and ctx.boot_mount is not None and ctx.boot_mount.resolve("EFI\\Microsoft\\Boot\\BCD") is not None:
        return [A.esp_restore_bootfiles()]
    return []


def _create_actions(ctx):
    p = ctx.boot_part
    if p and p.get("is_esp") and p.get("number") and ctx.boot_mount is not None \
            and ctx.boot_mount.resolve("EFI\\Microsoft\\Boot\\bootmgfw.efi") is not None:
        return [A.nvram_create(p["disk_path"], p["number"])]
    return []


def _create_steps(ctx):
    p = ctx.boot_part
    if not (p and p.get("is_esp") and p.get("number")):
        return []
    return [LINUX, _(t"Create the firmware entry for Windows Boot Manager:\n"
                     t"`sudo efibootmgr -c -d {p['disk_path']} -p {p['number']} -L \"Windows Boot Manager\" "
                     t"-l '\\EFI\\Microsoft\\Boot\\bootmgfw.efi'`")]


def _identify_efi(path, bootmgfw):
    try:
        with open(path, "rb") as f:
            data = f.read(4 * 1024 * 1024)
    except OSError:
        return "unreadable"
    if bootmgfw is not None:
        try:
            if os.path.getsize(path) == os.path.getsize(bootmgfw):
                with open(bootmgfw, "rb") as f:
                    if f.read(len(data)) == data:
                        return "copy of Windows Boot Manager"
        except OSError:
            pass
    for needle, name in ((b"s\x00h\x00i\x00m", "shim"), (b"shim", "shim"), (b"GRUB", "GRUB"),
                         (b"systemd-boot", "systemd-boot"), (b"rEFInd", "rEFInd"), (b"bootmgfw", "Windows Boot Manager"),
                         (b"B\x00o\x00o\x00t\x00 \x00M\x00a\x00n\x00a\x00g\x00e\x00r", "Windows Boot Manager"),
                         (b"Limine", "Limine")):
        if needle in data:
            return name
    return "unknown EFI program"


def _nvram(ctx):
    out = sysprobe.efibootmgr_v() if ctx.uefi_host else None
    if not out:
        return
    order = []
    entries = []
    for line in out.splitlines():
        if line.startswith("BootOrder:"):
            order = [x.strip().upper() for x in line.split(":", 1)[1].split(",") if x.strip()]
        m = re.match(r"^Boot([0-9A-Fa-f]{4})(\*?)\s+(.*?)\t(.*)$", line)
        if not m:
            continue
        num, active, desc, dp = m.groups()
        g = re.search(r"HD\(\d+,GPT,([0-9a-fA-F-]{36})", dp)
        mbr = re.search(r"HD\((\d+),MBR,(0x[0-9a-fA-F]+)", dp)
        fpath = re.search(r"(\\[^\t{]*?\.efi)", dp, re.I) or re.search(r"File\((.*?)\)", dp)
        entries.append({"num": num.upper(), "active": active == "*", "description": desc.strip(),
                        "partuuid": g.group(1).lower() if g else None,
                        "mbr": mbr.groups() if mbr else None,
                        "file": fpath.group(1) if fpath else None})
    ctx.evidence["nvram"] = {"boot_order": order, "entries": entries}
    if not entries:
        return
    parts = {p["partuuid"]: p for p in ctx.all_partitions() if p.get("partuuid")}
    win = [e for e in entries if e["file"] and "bootmgfw.efi" in e["file"].lower()]
    esp = ctx.boot_part
    if not win:
        fb_kind = ctx.evidence.get("boot_partition", {}).get("fallback_loader")
        windows_fallback = fb_kind in ("copy of Windows Boot Manager", "Windows Boot Manager")
        sev = "warning" if windows_fallback else "critical"
        ctx.add(sev, "bootmgr", _(t"No 'Windows Boot Manager' entry in the firmware (NVRAM)"),
                _(t"The firmware's boot list has no entry that starts \\EFI\\Microsoft\\Boot\\bootmgfw.efi. ")
                + (_(t"The fallback loader \\EFI\\Boot\\bootx64.efi is a copy of Windows Boot Manager, so the firmware "
                     t"may still find Windows via the disk's default entry.") if windows_fallback else
                   _(t"The fallback loader \\EFI\\Boot\\bootx64.efi is not Windows' boot manager either, so this computer "
                     t"has no path to start Windows.")),
                [f"Boot{e['num']}{'*' if e['active'] else ' '} {e['description']} -> {e['file'] or '-'}" for e in entries[:12]],
                _create_steps(ctx) + bcdboot_fix(ctx),
                stopcode="firmware boots another OS / setup", source=SRC, priority=6,
                actions=_create_actions(ctx))
        return
    good = [e for e in win if e["partuuid"] and e["partuuid"] in parts]
    if good:
        mine = [e for e in good if esp and e["partuuid"] == esp.get("partuuid")] or good
        ctx.evidence["nvram"]["windows_entry"] = (sorted(mine, key=lambda e: not e["active"]))[0]["num"]
    for e in win:
        if e["partuuid"] and e["partuuid"] not in parts:
            sev = "critical" if not good else "warning"
            ctx.add(sev, "bootmgr", _(t"Firmware entry Boot{e['num']} '{e['description']}' points to a partition that no longer exists"),
                    _(t"The firmware tries to load Windows Boot Manager from an EFI partition with this GUID, but no "
                      t"connected disk has such a partition (the ESP was re-created or the disk was replaced/cloned). "
                      t"The firmware skips the entry or shows a boot error."),
                    [f"Boot{e['num']}: HD(...,GPT,{e['partuuid']}) {e['file']}",
                     "existing ESPs: " + ", ".join(f"/dev/{p['name']}={p['partuuid']}" for p in ctx.all_partitions() if p['is_esp'])],
                    [LINUX, _(t"Delete the dead entry:\n`sudo efibootmgr -b {e['num']} -B`")]
                    + ([] if good else _create_steps(ctx)),
                    stopcode="firmware: boot entry invalid", source=SRC, priority=7,
                    actions=[A.nvram_delete(e["num"], e["description"])] + ([] if good else _create_actions(ctx)))
    if good:
        targets = {e["partuuid"] for e in good}
        if esp and esp.get("partuuid") and esp["partuuid"] not in targets:
            used = [parts[t] for t in targets]
            ctx.add("warning", "bootmgr", _(t"The firmware starts Windows Boot Manager from a different EFI partition"),
                    _(t"The analysed ESP is {part_label(esp)}, but the firmware's Windows entry uses "
                      t"{', '.join(part_label(u) for u in used)}. The BCD on that partition decides what boots."),
                    [f"Boot{e['num']} -> /dev/{parts[e['partuuid']]['name']}" for e in good],
                    [_(t"Go back, choose that EFI partition under “More options” and run the analysis again. The boot "
                       t"configuration on that partition is the one that decides what starts.")],
                    source=SRC, priority=40)
        inorder = [e for e in good if e["num"] in order]
        if not inorder:
            ctx.add("warning", "bootmgr", _(t"Windows Boot Manager is not in the firmware boot order"),
                    _(t"The entry exists but the firmware never tries it automatically."),
                    [f"BootOrder: {','.join(order)}", *(f"Boot{e['num']} {e['description']}" for e in good)],
                    [LINUX, _(t"Put Windows Boot Manager into the boot order:\n"
                              t"`sudo efibootmgr -o {','.join(order + [good[0]['num']])}`"),
                     _(t"Or open the firmware setup (usually F2 or Del right after power-on) and add “Windows Boot "
                       t"Manager” to the boot order there.")],
                    source=SRC, priority=20, actions=[A.nvram_append(good[0]["num"], order)])
        elif not any(e["active"] for e in good):
            ctx.add("warning", "bootmgr", _(t"Windows Boot Manager entry is disabled in the firmware"),
                    _(t"The firmware skips inactive entries."), [f"Boot{e['num']} is inactive" for e in good],
                    [LINUX, _(t"Enable the entry:\n`sudo efibootmgr -b {good[0]['num']} -a`")], source=SRC,
                    actions=[A.nvram_activate(good[0]["num"])])
        elif order and order[0] not in {e["num"] for e in good}:
            first = next((e for e in entries if e["num"] == order[0]), None)
            name = first["description"] if first else f"Boot{order[0]}"
            ctx.add("info", "bootmgr", _(t"The firmware starts “{name}” first, not Windows"),
                    _(t"That is normal for dual boot: Windows is started from that boot loader's menu, or from the "
                      t"firmware's boot menu (usually F12 or Esc right after power-on)."),
                    [f"BootOrder: {','.join(order)}", f"Boot{order[0]} = {name}",
                     f"Boot{good[0]['num']} = {good[0]['description']}"], source=SRC, priority=85)


def _secure_boot(ctx):
    ctx.evidence["secure_boot"] = sysprobe.secure_boot()


# ============================================================================ BIOS
def _legacy(ctx):
    ev = {}
    ctx.evidence["boot_partition"] = ev
    mbr_parts = ctx.evidence.get("disk", {}).get("mbr_partitions", [])
    active = [p for p in mbr_parts if p["active"]]
    boot = None
    if active:
        a = active[0]
        for p in ctx.disk["partitions"]:
            if p["start_bytes"] == a["start_lba"] * 512:
                boot = p
    if boot is None:
        boot = ctx.target
        ev["note"] = "no active partition - checking the Windows partition itself"
    ctx.boot_part = boot
    ev["chosen"] = boot["name"]

    try:
        with open(boot["path"], "rb") as f:
            pbr = f.read(4096)
        if identify(pbr) == "ntfs" and not parse_boot_sector(pbr)["has_bootmgr_ref"]:
            ctx.add("warning", "bootmgr", _(t"Partition boot code of the active partition does not load BOOTMGR"),
                    _(t"The volume boot record should chain to BOOTMGR. It looks like old NTLDR (XP) or foreign boot "
                      t"code, so 'NTLDR is missing' or similar errors appear."), [f"/dev/{boot['name']} boot sector has no BOOTMGR reference"],
                    [WINRE, _(t"Write the Windows boot code to the system partition and the first sector:\n"
                              t"`bootsect /nt60 SYS /mbr`")], source=SRC)
    except OSError:
        pass

    if boot is ctx.target and ctx.win is not None:
        root = ctx.win
    else:
        try:
            mp, how = ctx.mounts.mount_ro(boot["path"], ["ntfs3", "ntfs-3g", "vfat"], "sysres")
            root = CIRoot(mp)
            ev["mount"] = how
        except MountError as e:
            ctx.add("critical", "bootmgr", _(t"The active (system) partition {part_label(boot)} cannot be read"),
                    _(t"BIOS boot starts BOOTMGR from the active partition, but its file system is unreadable."),
                    [str(e)], bcdboot_fix(ctx), stopcode="BOOTMGR is missing", source=SRC, priority=3)
            return
    ctx.boot_mount = root
    bm = root.resolve("bootmgr")
    st, detail = inspect_file(bm, magic=None)
    ev["bootmgr"] = f"{st}: {detail}"
    if st != "ok":
        ctx.add("critical", "bootmgr", _(t"BOOTMGR is {status_word(st)} on the active partition"),
                _(t"The partition boot code loads \\bootmgr; without it the screen shows 'BOOTMGR is missing'."),
                [f"/dev/{boot['name']}: \\bootmgr {detail}"], bcdboot_fix(ctx),
                stopcode="BOOTMGR is missing", source=SRC, priority=3)
    bcdp = root.resolve("Boot\\BCD")
    ctx.bcd_path = bcdp
    if bcdp is None:
        ctx.add("critical", "bcd", _(t"The BCD store is missing"),
                _(t"BOOTMGR finds no \\Boot\\BCD and stops with 'The Boot Configuration Data for your PC is missing'."),
                [f"/dev/{boot['name']}: \\Boot\\BCD does not exist"], bcdboot_fix(ctx),
                stopcode="0xc000000f", source=SRC, priority=4)
