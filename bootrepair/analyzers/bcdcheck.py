"""BCD store analysis: does the boot configuration actually start this Windows?"""

from pathlib import Path

from ..i18n import _
from .. import actions as A
from ..parsers import bcd as B
from ..parsers.regf import RegfError
from ..knowledge import WINRE, WINDOWS
from .bootpart import bcdboot_fix, ASSIGN_S
from .context import part_label

SRC = "bcd"


def _cmd(ctx, args):
    """One bcdedit command line that addresses the analysed store explicitly."""
    store = "S:\\EFI\\Microsoft\\Boot\\BCD" if ctx.boot_mode != "bios" else "C:\\Boot\\BCD"
    return f"bcdedit /store {store} {args}"


def _bcd_steps(ctx, text, *args):
    """Manual steps that run one or more bcdedit commands in the recovery prompt."""
    cmds = "\n".join(_cmd(ctx, a) for a in args)
    pre = [WINRE] + ([ASSIGN_S] if ctx.boot_mode != "bios" else [])
    return pre + [f"{text}\n`{cmds}`"]


def _repoint_orphan(ctx, store, loaders, default, rel, parts):
    """Offer to re-point the default (or only) loader when it targets a partition that no longer exists."""
    orphans = []
    for o in loaders:
        info, m = B.resolve_device(o.get(B.E_OSDEVICE) or o.get(B.E_DEVICE), parts)
        if not m and info.get("kind") == "partition":
            orphans.append(o)
    if not orphans:
        return []
    pick = next((o for o in orphans if o.guid == default), orphans[0])
    objs = [pick.guid]
    labels = [f"'{pick.description}' {pick.alias}"]
    ro = store.get(pick.get(B.E_RESUMEOBJECT))
    if ro is not None:
        objs.append(ro.guid)
        labels.append(f"resume entry {ro.alias}")
    acts = [A.bcd_repoint(rel, objs, labels, ctx.target["name"])]
    if default and pick.guid != default:
        acts.append(A.bcd_set_default(rel, pick.guid, labels[0]))
    return acts


def analyze(ctx):
    if ctx.bcd_path is None:
        return
    try:
        store = B.BcdStore.from_file(ctx.bcd_path)
    except (OSError, RegfError, Exception) as e:
        ctx.add("critical", "bcd", _(t"The BCD store is corrupt"),
                _(t"Boot Manager cannot read its configuration and stops with 'The Boot Configuration Data for your PC "
                  t"is missing or contains errors'."), [f"{ctx.bcd_path}: {e}"], bcdboot_fix(ctx),
                stopcode="0xc000000f / 0xc0000034", source=SRC, priority=2)
        return
    ctx.bcd = store
    try:
        rel = str(Path(ctx.bcd_path).relative_to(ctx.boot_mount.root)).replace("/", "\\")
    except (ValueError, AttributeError):
        rel = "EFI\\Microsoft\\Boot\\BCD"
    hive = store.hive
    if not hive.checksum_ok:
        ctx.add("warning", "bcd", _(t"BCD store header checksum is wrong"),
                _(t"The BCD hive's base block checksum does not match. Boot Manager may reject the store."),
                [f"stored 0x{hive.stored_checksum:08x}"], bcdboot_fix(ctx), stopcode="0xc000000f", source=SRC)
    parts = ctx.all_partitions()
    target = ctx.target

    def res(blob):
        info, matches = B.resolve_device(blob, parts)
        return info, matches, B.describe_device(info, matches)

    bm = store.bootmgr
    default = None
    display = []
    if bm is None:
        ctx.add("critical", "bcd", _(t"BCD has no {{bootmgr}} object"),
                _(t"The store exists but lacks the Windows Boot Manager settings, so Boot Manager does not know which "
                  t"entries exist or which is the default."), [f"objects in store: {len(store.objects)}"],
                bcdboot_fix(ctx), stopcode="0xc000000d / 0xc000000f", source=SRC, priority=3)
    else:
        default = (bm.get(B.E_DEFAULT) or "").lower() or None
        display = [g.lower() for g in bm.get(B.E_DISPLAYORDER, [])]
        info, matches, desc = res(bm.get(B.E_DEVICE))
        if info.get("kind") == "partition" and not matches:
            ctx.add("warning", "bcd", _(t"{{bootmgr}} device points to a partition that does not exist"),
                    _(t"Boot Manager's own device (where it loads its resources from) is not present."),
                    [f"{{bootmgr}} device = {desc}"], bcdboot_fix(ctx), stopcode="0xc000000f", source=SRC)

    # ------------------------------------------------------------------ evidence table
    entries = []
    order = display + [g for g in store.objects if g not in display]
    loaders = store.osloaders()
    for guid in order:
        o = store.get(guid)
        if o is None or o.type not in (B.TYPE_OSLOADER, B.TYPE_RESUME, 0x10100002, 0x10200005):
            continue
        d_info, d_m, d_desc = res(o.get(B.E_DEVICE))
        os_info, os_m, os_desc = res(o.get(B.E_OSDEVICE))
        flags = []
        sb = o.get(B.E_SAFEBOOT)
        if sb is not None:
            flags.append(f"safeboot={B.SAFEBOOT_NAMES.get(sb, sb)}")
        for e, n in ((B.E_TESTSIGNING, "testsigning"), (B.E_NOINTEGRITY, "nointegritychecks"),
                     (B.E_WINPE, "winpe"), (B.E_BOOTLOG, "bootlog"), (B.E_KERNEL_DEBUG, "debug")):
            if o.get(e):
                flags.append(f"{n}=yes")
        entries.append({
            "id": o.alias, "guid": o.guid, "type": o.type_name, "description": o.description,
            "device": d_desc if o.get(B.E_DEVICE) is not None else "",
            "osdevice": os_desc if o.get(B.E_OSDEVICE) is not None else "",
            "path": o.get(B.E_PATH, ""), "systemroot": o.get(B.E_SYSTEMROOT, ""),
            "default": o.guid == default, "in_menu": o.guid in display,
            "this_windows": target["name"] in d_m or target["name"] in os_m,
            "flags": flags,
        })
    ctx.evidence["bcd"] = {"path": "\\" + rel, "boot_partition": ctx.boot_part["name"] if ctx.boot_part else "",
                           "default": B.WELL_KNOWN.get(default, default) if default else "", "entries": entries}

    if bm is None:
        return
    default_obj = store.get(default)
    if default and default_obj is None:
        ctx.add("critical", "bcd", _(t"The default boot entry does not exist"),
                _(t"{{bootmgr}} names a default entry that is not in the store, so there is nothing to start by default."),
                [f"default = {default}", f"existing loader entries: {', '.join(o.alias for o in loaders) or 'none'}"],
                bcdboot_fix(ctx),
                stopcode="0xc000000d", source=SRC, priority=3)
    elif not default and not display:
        ctx.add("critical", "bcd", _(t"BCD has neither a default entry nor a boot menu"),
                _(t"Boot Manager has no entry to start."), ["{bootmgr}: no 'default', empty 'displayorder'"],
                bcdboot_fix(ctx), stopcode="0xc000000d", source=SRC, priority=3)

    if not loaders:
        ctx.add("critical", "bcd", _(t"BCD contains no Windows Boot Loader entry at all"),
                _(t"The store has no entry of type 'Windows Boot Loader', so Boot Manager cannot start any Windows."),
                [f"objects: {', '.join(sorted(o.type_name for o in store.objects.values()))}"],
                bcdboot_fix(ctx), stopcode="0xc000000d / 0xc0000225", source=SRC, priority=3)
        return

    mine = []
    for o in loaders:
        dm = B.device_matches(o.get(B.E_DEVICE), target)
        om = B.device_matches(o.get(B.E_OSDEVICE), target)
        if dm or om:
            mine.append((o, dm, om))

    if not mine:
        lines = []
        for o in loaders:
            __, __, dd = res(o.get(B.E_DEVICE))
            __, __, od = res(o.get(B.E_OSDEVICE))
            lines.append(f"{o.alias} '{o.description}': device={dd}; osdevice={od}"
                         + (" [DEFAULT]" if o.guid == default else ""))
        nowhere = all("NOT present" in l for l in lines)
        ctx.add("critical", "bcd", _(t"No BCD entry starts the Windows on {part_label(target)}"),
                _(t"The boot configuration on {part_label(ctx.boot_part)} has Windows Boot Loader entries, but none "
                  t"of them points to the selected Windows partition.")
                + (_(t" They point to partitions that no longer exist (typical after cloning, re-partitioning or "
                     t"restoring an image). Boot Manager fails with “A required device isn't connected or can't be "
                     t"accessed”.") if nowhere else _(t" Boot Manager starts a different installation or fails.")),
                lines, bcdboot_fix(ctx), stopcode="0xc000000e / 0xc0000225", source=SRC, priority=2,
                actions=_repoint_orphan(ctx, store, loaders, default, rel, parts))
        return

    # prefer the default entry
    mine.sort(key=lambda t: (t[0].guid != default, t[0].guid not in display))
    o, dm, om = mine[0]
    ctx.loader_entry = o
    ctx.loader_path = o.get(B.E_PATH)
    d_info, d_m, d_desc = res(o.get(B.E_DEVICE))
    os_info, os_m, os_desc = res(o.get(B.E_OSDEVICE))

    if not dm or not om:
        bad = "device" if not dm else "osdevice"
        ctx.add("critical", "bcd", _(t"BCD entry '{o.description}' has a wrong {bad}"),
                _(t"Of the two device settings of the entry, one points to this Windows partition and the other does "
                  t"not. 'device' is where winload is loaded from, 'osdevice' is the Windows volume the kernel boots; "
                  t"both must be the Windows partition."),
                [f"{o.alias}: device = {d_desc}", f"{o.alias}: osdevice = {os_desc}"],
                _bcd_steps(ctx, _(t"Point both settings of the entry at the Windows volume:"),
                           f"/set {o.alias} device partition=C:", f"/set {o.alias} osdevice partition=C:"),
                stopcode="0xc000000e", source=SRC, priority=4,
                actions=[A.bcd_repoint(rel, [o.guid], [f"'{o.description}' {o.alias}"], target["name"])])

    if default and o.guid != default:
        dobj = store.get(default)
        ddesc = ""
        if dobj is not None:
            __, __, ddesc = res(dobj.get(B.E_OSDEVICE))
        ctx.add("warning", "bcd", _(t"This Windows is not the default boot entry"),
                (_(t"Boot Manager starts “{dobj.description if dobj else default}” by default, which lives on {ddesc}.")
                 if ddesc else _(t"Boot Manager starts “{dobj.description if dobj else default}” by default."))
                + _(t" The entry for this Windows (“{o.description}”) is only reached via the boot menu."),
                [f"default = {B.WELL_KNOWN.get(default, default)}", f"this Windows = {o.alias}"],
                _bcd_steps(ctx, _(t"Make this Windows the default entry:"), f"/default {o.alias}"),
                source=SRC, priority=30,
                actions=[A.bcd_set_default(rel, o.guid, f"'{o.description}' {o.alias}")])
    if display and o.guid not in display and o.guid != default:
        ctx.add("warning", "bcd", _(t"The entry for this Windows is not in the boot menu"),
                _(t"It is neither the default nor listed in the display order, so Boot Manager never offers it."),
                [f"displayorder = {', '.join(display)}"],
                _bcd_steps(ctx, _(t"Add the entry to the boot menu:"), f"/displayorder {o.alias} /addlast"),
                source=SRC, priority=20)

    # -------------------------------------------------------------- loader path / systemroot
    path = o.get(B.E_PATH)
    mode = ctx.boot_mode or "uefi"
    want = "winload.efi" if mode == "uefi" else "winload.exe"
    if not path:
        ctx.add("critical", "bcd", _(t"BCD entry '{o.description}' has no loader path"),
                _(t"Boot Manager does not know which file to start (expected \\Windows\\system32\\{want})."),
                [f"{o.alias}: path is not set"],
                _bcd_steps(ctx, _(t"Set the loader path:"), f"/set {o.alias} path \\Windows\\system32\\{want}"),
                stopcode="0xc000000f", source=SRC, priority=5)
    else:
        if not path.lower().endswith(want):
            ctx.add("critical", "bcd", _(t"BCD entry uses the wrong OS loader for {mode.upper()} boot"),
                    _(t"This disk boots in {mode.upper()} mode, which requires {want}, but the entry points to "
                      t"'{path}'. Boot Manager cannot run that loader."),
                    [f"{o.alias}: path = {path}"],
                    _bcd_steps(ctx, _(t"Set the loader that {mode.upper()} boot needs:"),
                               f"/set {o.alias} path \\Windows\\system32\\{want}"),
                    stopcode="0xc000000f / 0xc0000428", source=SRC, priority=5)
        if ctx.win is not None and ctx.windows_dir_ok and ctx.win.resolve(path) is None:
            ctx.add("critical", "winload", _(t"The OS loader named in the BCD does not exist: {path}"),
                    _(t"Boot Manager finds the entry but the loader file is missing on the Windows partition: "
                      t"'Windows failed to start ... File: \\Windows\\system32\\winload.efi'."),
                    [f"{o.alias}: path = {path}", f"/dev/{target['name']}: file not found"],
                    [WINRE,
                     _(t"Copy the loader back from Windows' own spare copy:\n"
                       t"`copy C:\\Windows\\System32\\Boot\\{want} C:\\Windows\\System32\\{want}`"),
                     _(t"If that copy is missing too, let Windows repair its system files:\n"
                       t"`sfc /scannow /offbootdir=C:\\ /offwindir=C:\\Windows`")],
                    stopcode="0xc000000f / 0xc0000098", source=SRC, priority=5)
    sysroot = o.get(B.E_SYSTEMROOT)
    if sysroot and ctx.win is not None and ctx.windows_dir_ok and ctx.win.resolve(sysroot) is None:
        ctx.add("critical", "bcd", _(t"BCD systemroot '{sysroot}' does not exist on this partition"),
                _(t"The loader is told to boot Windows from a directory that is not there."),
                [f"{o.alias}: systemroot = {sysroot}"],
                _bcd_steps(ctx, _(t"Set the Windows directory:"), f"/set {o.alias} systemroot \\Windows"),
                stopcode="0xc000000f", source=SRC, priority=5)

    # -------------------------------------------------------------- dangerous options
    sb = o.get(B.E_SAFEBOOT)
    if sb is not None:
        ctx.add("warning", "bcd", _(t"Windows is forced into Safe Mode ({B.SAFEBOOT_NAMES.get(sb, sb)}) on every start"),
                _(t"The “safeboot” option is set permanently, so Windows always starts in Safe Mode.")
                + (_(t" The “dsrepair” mode only works on domain controllers; on a normal PC it ends in a logon loop.")
                   if sb == 2 else ""),
                [f"{o.alias}: safeboot = {B.SAFEBOOT_NAMES.get(sb, sb)}"],
                _bcd_steps(ctx, _(t"Remove the Safe Mode setting:"), f"/deletevalue {o.alias} safeboot"),
                source=SRC, priority=15,
                actions=[A.bcd_delete_elements(rel, o.guid, [e for e in (B.E_SAFEBOOT, B.E_SAFEBOOT_ALTSHELL)
                                                             if o.get(e) is not None], o.alias)])
    if o.get(B.E_SAFEBOOT_ALTSHELL):
        ctx.add("info", "bcd", _(t"Safe Mode with Command Prompt is configured"),
                _(t"safebootalternateshell=yes starts cmd.exe instead of Explorer."), [f"{o.alias}: safebootalternateshell=yes"],
                _bcd_steps(ctx, _(t"Remove the setting:"), f"/deletevalue {o.alias} safebootalternateshell"),
                source=SRC)
    if o.get(B.E_TESTSIGNING) or o.get(B.E_NOINTEGRITY):
        sbstate = ctx.evidence.get("secure_boot", "unknown")
        ctx.add("warning", "bcd", _(t"Driver signature enforcement is weakened (testsigning / nointegritychecks)"),
                _(t"These options let unsigned drivers load. With Secure Boot enabled the firmware/Boot Manager rejects "
                  t"them and Windows reports a Secure Boot policy violation; they also indicate that an unsigned driver "
                  t"was installed. Secure Boot on this computer: {sbstate}."),
                [f"{o.alias}: testsigning={'yes' if o.get(B.E_TESTSIGNING) else 'no'}, "
                 f"nointegritychecks={'yes' if o.get(B.E_NOINTEGRITY) else 'no'}"],
                _bcd_steps(ctx, _(t"Remove the settings that are present:"),
                           *[f"/deletevalue {o.alias} {n}" for e, n in ((B.E_TESTSIGNING, "testsigning"),
                                                                        (B.E_NOINTEGRITY, "nointegritychecks"))
                             if o.get(e) is not None]),
                source=SRC, priority=40,
                actions=[A.bcd_delete_elements(rel, o.guid, [e for e in (B.E_TESTSIGNING, B.E_NOINTEGRITY)
                                                             if o.get(e) is not None], o.alias)])
    for e, n in ((B.E_KERNEL, "kernel"), (B.E_HAL, "hal")):
        v = o.get(e)
        if v:
            ok = ctx.win is None or ctx.win.resolve(f"Windows\\System32\\{v}") is not None
            ctx.add("critical" if not ok else "warning", "winload", _(t"BCD overrides the {n} file ({v})"),
                    _(t"winload loads “{v}” instead of the standard {n}.")
                    + (_(t" That file does not exist.") if not ok else ""),
                    [f"{o.alias}: {n} = {v}"],
                    _bcd_steps(ctx, _(t"Remove the override so the standard {n} is loaded:"),
                               f"/deletevalue {o.alias} {n}"),
                    stopcode="0xc000000f" if not ok else "", source=SRC, priority=6,
                    actions=[A.bcd_delete_elements(rel, o.guid, [e], o.alias)])
    if o.get(B.E_WINPE):
        ctx.add("warning", "bcd", _(t"The Windows entry is marked as WinPE"),
                _(t"winpe=yes makes winload treat the installation as a preinstallation environment."),
                [f"{o.alias}: winpe = yes"],
                _bcd_steps(ctx, _(t"Remove the setting:"), f"/deletevalue {o.alias} winpe"), source=SRC,
                actions=[A.bcd_delete_elements(rel, o.guid, [B.E_WINPE], o.alias)])
    if o.get(B.E_BOOTLOG):
        ctx.add("info", "bcd", _(t"Boot logging is enabled"),
                _(t"Windows writes C:\\Windows\\ntbtlog.txt on every boot (useful for this analysis)."),
                [f"{o.alias}: bootlog = yes"], source=SRC)
    bsp = o.get(B.E_BOOTSTATUSPOLICY)
    if bsp in (1, 3):
        ctx.add("info", "bcd", _(t"Automatic Repair after failed boots is suppressed"),
                _(t"bootstatuspolicy={B.BOOTSTATUS_NAMES.get(bsp)} hides the recovery screen, so a failing Windows "
                  t"just reboots in a loop."), [f"{o.alias}: bootstatuspolicy = {B.BOOTSTATUS_NAMES.get(bsp)}"],
                _bcd_steps(ctx, _(t"Remove the setting:"), f"/deletevalue {o.alias} bootstatuspolicy"), source=SRC,
                actions=[A.bcd_delete_elements(rel, o.guid, [B.E_BOOTSTATUSPOLICY], o.alias)])

    # -------------------------------------------------------------- resume / recovery
    ro = store.get(o.get(B.E_RESUMEOBJECT))
    if ro is not None and ctx.hiberfile_state == "hibernated":
        fd = ro.get(B.E_OSDEVICE)
        if fd is not None and not B.device_matches(fd, target):
            __, __, fdesc = res(fd)
            ctx.add("warning", "bcd", _(t"Hibernation resume entry points to another partition"),
                    _(t"Windows is hibernated, but the resume entry's hiberfile device is not this partition; resuming "
                      t"fails and Windows may discard the image or stop with an error."),
                    [f"{ro.alias}: filedevice = {fdesc}"], bcdboot_fix(ctx), source=SRC,
                    actions=[A.bcd_repoint(rel, [ro.guid], [f"resume entry {ro.alias}"], target["name"])])
    rec = o.get(B.E_RECOVERYSEQUENCE) or []
    if rec:
        robj = store.get(rec[0])
        if robj is None:
            ctx.add("info", "bcd", _(t"Windows Recovery Environment entry is missing from the BCD"),
                    _(t"Automatic Repair cannot start after failed boots."), [f"recoverysequence = {rec[0]} (not in store)"],
                    [WINDOWS, _(t"Register the recovery environment again:\n`reagentc /enable`")], source=SRC)
        else:
            __, m, desc = res(robj.get(B.E_DEVICE))
            info = B.parse_device(robj.get(B.E_DEVICE) or b"")
            if not m and (info.get("kind") == "partition" or "NOT present" in desc):
                ctx.add("info", "bcd", _(t"Windows Recovery Environment entry points to a missing partition"),
                        _(t"Automatic Repair / WinRE will not start after failed boots."),
                        [f"{robj.alias} '{robj.description}': device = {desc}"],
                        [WINDOWS, _(t"Register the recovery environment again:\n"
                                    t"`reagentc /disable\nreagentc /enable`")], source=SRC)
    elif o.get(B.E_RECOVERYENABLED) is False:
        ctx.add("info", "bcd", _(t"Automatic recovery is disabled for this entry"), "",
                [f"{o.alias}: recoveryenabled = no"], source=SRC)

    # stale entries
    keep = {(bm.get(B.E_RESUME_BM) or "").lower(), (o.get(B.E_RESUMEOBJECT) or "").lower()}
    stale = [e for e in entries if not e["this_windows"] and not e["default"] and e["guid"] not in keep
             and "NOT present" in (e["osdevice"] + e["device"])]
    if stale:
        in_menu = [e for e in stale if e["in_menu"]]
        ctx.add("warning" if in_menu else "info", "bcd",
                (_(t"The boot menu contains a broken entry ('{in_menu[0]['description']}')") if in_menu else
                 _(t"Stale boot entries point to missing partitions ({len(stale)})")),
                (_(t"The Windows Boot Manager menu offers an entry for a Windows partition that no longer exists. "
                   t"Choosing it fails with 0xc000000e; it often has the same name as the working entry, which is "
                   t"confusing.") if in_menu else
                 _(t"Old entries for Windows installations that no longer exist. Harmless unless one is the default.")),
                [f"{e['id']} '{e['description']}' ({e['type']}): {e['osdevice'] or e['device']}" for e in stale[:6]],
                _bcd_steps(ctx, _(t"Delete the dead entries:"), *[f"/delete {e['id']}" for e in stale[:8]]),
                source=SRC, priority=35,
                actions=[A.bcd_delete_objects(rel, [e["guid"] for e in stale],
                                              [f"'{e['description']}' {e['id']}" for e in stale])])
