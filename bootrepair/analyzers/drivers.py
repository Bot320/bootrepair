"""SYSTEM hive: boot drivers, storage controller driver, class filters, BootExecute, Driver Verifier, drive letters."""

import re

from ..i18n import _, N_
from .. import actions as A
from ..fsutil import inspect_file, status_word
from .files import SFC_STEP
from ..knowledge import (WINRE, STORAGE_CLASSES, OTHER_FILTER_CLASSES, STORAGE_DRIVERS, SERVICE_START, ERROR_CONTROL,
                         hive_edit_steps)
from ..parsers.regf import RegfError
from ..parsers.util import guid_bytes

SRC = "drivers"


def resolve_image(ctx, image, name, stype):
    """Map a service ImagePath to a path relative to the volume root."""
    if not image:
        if stype in (1, 2, 8):
            return f"Windows\\System32\\drivers\\{name}.sys"
        return None
    s = image.strip().strip('"')
    s = re.sub(r"^\\\?\?\\", "", s)
    s = re.sub(r"(?i)^%systemroot%|^%windir%", lambda m: "\\Windows", s)
    s = re.sub(r"(?i)^\\systemroot", lambda m: "\\Windows", s)
    s = re.sub(r"(?i)^[a-z]:", "", s)
    if not s.startswith("\\"):
        s = "Windows\\" + s     # relative paths are relative to %SystemRoot%
    s = s.lstrip("\\")
    # strip arguments for services (e.g. svchost -k ...)
    m = re.match(r"(?i)(.+?\.(sys|exe|dll))(\s|$)", s)
    return m.group(1) if m else s


def _services(cs):
    out = {}
    sk = cs.subkey("Services")
    if sk is None:
        return out
    for k in sk.subkeys():
        try:
            vals = {v.name.lower(): v for v in k.values()}
            def g(n, default=None):
                v = vals.get(n.lower())
                if v is None:
                    return default
                try:
                    return v.data
                except RegfError:
                    return default
            so = None
            sok = k.subkey("StartOverride")
            if sok is not None:
                so = {v.name: v.data for v in sok.values()}
            out[k.name.lower()] = {"name": k.name, "start": g("Start"), "type": g("Type"),
                                   "image": g("ImagePath"), "group": g("Group", ""),
                                   "error_control": g("ErrorControl"), "display": g("DisplayName", ""),
                                   "start_override": so}
        except RegfError:
            continue
    return out


def analyze(ctx):
    if not ctx.ensure_windows():
        return
    cs = ctx.control_set() if ctx.current_cs is None else ctx.current_cs
    if cs is None:
        ctx.log("SYSTEM hive / control set not available - skipping driver checks")
        return
    csname = getattr(ctx, "current_cs_name", "ControlSet001")
    services = _services(cs)
    ctx.evidence["services_count"] = len(services)
    file_cache = {}

    def file_status(svc):
        rel = resolve_image(ctx, svc["image"], svc["name"], svc["type"])
        if rel is None:
            return None, "ok", ""
        if rel not in file_cache:
            file_cache[rel] = inspect_file(ctx.win_path(rel))
        st, d = file_cache[rel]
        return rel, st, d

    # ------------------------------------------------------------------ boot/system start drivers
    boot_rows = []
    missing_boot = []
    for key, s in sorted(services.items()):
        if s["start"] not in (0, 1) or not isinstance(s["type"], int) or not (s["type"] & 0x0B):
            continue
        rel, st, d = file_status(s)
        boot_rows.append({"name": s["name"], "start": SERVICE_START.get(s["start"], s["start"]),
                          "group": s["group"], "error_control": ERROR_CONTROL.get(s["error_control"], s["error_control"]),
                          "file": rel or "", "status": st})
        if st not in ("ok", "unreadable"):
            missing_boot.append((s, rel, st, d))
    ctx.evidence["boot_drivers"] = boot_rows
    ctx.check_cancel()

    # ------------------------------------------------------------------ filter drivers
    filter_problems = {}
    ck = cs.subkey("Control")
    classk = ck.subkey("Class") if ck else None
    filters_ev = []
    if classk is not None:
        for guid, cname in list(STORAGE_CLASSES.items()) + list(OTHER_FILTER_CLASSES.items()):
            cname = _(cname)
            k = classk.subkey(guid)
            if k is None:
                continue
            for vn in ("UpperFilters", "LowerFilters"):
                vals = k.get(vn)
                if not vals:
                    continue
                if isinstance(vals, str):
                    vals = [vals]
                for f in vals:
                    s = services.get(f.lower())
                    problem = None
                    if s is None:
                        problem = _("no such service (driver was uninstalled but the filter entry remained)")
                    elif s["start"] == 4:
                        problem = _("service is disabled (Start=4)")
                    else:
                        rel, st, d = file_status(s)
                        if st not in ("ok", "unreadable"):
                            problem = _(t"driver file {status_word(st)}: \\{rel}")
                    filters_ev.append({"class": cname, "value": vn, "filter": f, "problem": problem or ""})
                    if problem:
                        filter_problems.setdefault(f.lower(), []).append((guid, cname, vn, f, problem))
    ctx.evidence["class_filters"] = filters_ev

    for fname, items in filter_problems.items():
        storage = [i for i in items if i[0] in STORAGE_CLASSES]
        guid, cname, vn, f, problem = (storage or items)[0]
        if storage:
            ctx.add("critical", "kernel", _(t"Storage filter driver '{f}' is broken ({cname} {vn})"),
                    _(t"'{f}' is registered as a filter on the {cname} device stack, but {problem}. Every disk/volume "
                      t"device then fails to start, Windows loses access to its own system disk and stops with "
                      t"INACCESSIBLE_BOOT_DEVICE. Typical leftover of uninstalled antivirus, encryption or backup "
                      t"software (e.g. Acronis, Symantec, Paragon)."),
                    [f"HKLM\\SYSTEM\\{csname}\\Control\\Class\\{g}\\{v} contains '{ff}' - {pr}" for g, __, v, ff, pr in items],
                    _filter_steps(ctx, csname, guid, vn, f),
                    stopcode="0x0000007B INACCESSIBLE_BOOT_DEVICE", source=SRC, priority=10,
                    actions=[A.remove_class_filter(csname, g, v, ff, cn) for g, cn, v, ff, __ in items])
        else:
            ctx.add("warning", "logon", _(t"Filter driver '{f}' on {cname} is broken"),
                    _(t"'{f}' filters {cname} but {problem}. Windows boots, but those devices do not work "
                      t"(e.g. no keyboard/mouse at the logon screen)."),
                    [f"Class\\{g}\\{v}: '{ff}' - {pr}" for g, __, v, ff, pr in items],
                    _filter_steps(ctx, csname, guid, vn, f),
                    source=SRC, priority=30,
                    actions=[A.remove_class_filter(csname, g, v, ff, cn) for g, cn, v, ff, __ in items])

    filter_names = set(filter_problems)
    for s, rel, st, d in missing_boot:
        if s["name"].lower() in filter_names:
            continue
        ec = s["error_control"]
        boot_start = s["start"] == 0
        group = (s["group"] or "").lower()
        needed_for_disk = s["name"].lower() in {n.lower() for n in STORAGE_DRIVERS.get(ctx.disk.get("controller"), [])}
        core_group = any(x in group for x in ("boot bus", "system bus", "boot file system", "primary disk"))
        if ec in (2, 3) or (boot_start and (needed_for_disk or core_group)):
            sev = "critical"
        else:
            sev = "warning"
        stage = "kernel"
        ctx.add(sev, stage, (_(t"Boot driver “{s['name']}” is {status_word(st)}") if boot_start else
                             _(t"System driver “{s['name']}” is {status_word(st)}")),
                (_(t"The driver is configured to load at boot (group “{s['group'] or '-'}”, error control "
                   t"{ERROR_CONTROL.get(ec, ec)}), but its file \\{rel} is {status_word(st)}.") if boot_start else
                 _(t"The driver is configured to load while the kernel starts (group “{s['group'] or '-'}”, error "
                   t"control {ERROR_CONTROL.get(ec, ec)}), but its file \\{rel} is {status_word(st)}."))
                + (_(t" With error control Critical/Severe Windows aborts the start (or falls back to Last Known Good).")
                   if sev == "critical" else _(t" Windows continues without it (Event 7026), which is only harmful "
                                               t"if the device it serves is needed.")),
                [f"HKLM\\SYSTEM\\{csname}\\Services\\{s['name']}: Start={s['start']}, ImagePath={s['image'] or '(default)'}",
                 f"\\{rel}: {d}"],
                ([WINRE, SFC_STEP] if needed_for_disk or core_group else
                 [_(t"If this driver belongs to software you uninstalled, it only needs to be switched off.")]
                 + hive_edit_steps([_(t"Switch the driver off (4 = disabled):\n"
                                      t"`reg add HKLM\\OFFLINE\\{csname}\\Services\\{s['name']} /v Start /t REG_DWORD /d 4 /f`")])),
                actions=_missing_driver_actions(ctx, s, rel, csname, needed_for_disk or core_group),
                stopcode="0x0000007B / 0xc000000f" if sev == "critical" else "", source=SRC,
                priority=12 if sev == "critical" else 40)

    _storage_controller(ctx, services, csname, file_status)
    ctx.check_cancel()
    _session_manager(ctx, cs, csname)
    _verifier(ctx, cs, csname)
    _mounted_devices(ctx)
    _crash_control(ctx, cs)


def _filter_steps(ctx, csname, guid, value, flt):
    """Remove one name from an Upper/LowerFilters list: show the list, then write it back without the name."""
    cur = []
    try:
        k = ctx.current_cs.subkey("Control").subkey("Class").subkey(guid)
        cur = k.get(value) or []
        cur = [cur] if isinstance(cur, str) else cur
    except (RegfError, AttributeError):
        pass
    keep = [x for x in cur if x.lower() != flt.lower()]
    key = f"HKLM\\OFFLINE\\{csname}\\Control\\Class\\{guid}"
    if keep:
        joined = "\\0".join(keep)          # reg.exe separates REG_MULTI_SZ items with \0
        write = _(t"Write the list back without “{flt}”:\n"
                  t"`reg add {key} /v {value} /t REG_MULTI_SZ /d \"{joined}\" /f`")
    else:
        write = _(t"“{flt}” is the only entry, so delete the whole list:\n`reg delete {key} /v {value} /f`")
    return hive_edit_steps([_(t"Show the current list (it should read: {', '.join(cur) or '?'}):\n`reg query {key} /v {value}`"),
                            write])


def _missing_driver_actions(ctx, s, rel, csname, essential):
    from .files import restore_actions
    acts = restore_actions(ctx, rel) if rel else []
    if not acts and not essential and "\\driverstore\\" not in (rel or "").lower():
        acts = [A.set_service_start(csname, s["name"], 4)]
    return acts


def _storage_controller(ctx, services, csname, file_status):
    kind = ctx.disk.get("controller")
    cands = STORAGE_DRIVERS.get(kind)
    ev = {"controller": kind, "candidates": []}
    ctx.evidence["storage_driver"] = ev
    if not cands:
        return
    usable = []
    for n in cands:
        s = services.get(n.lower())
        if s is None:
            continue
        rel, st, d = file_status(s)
        override = s["start_override"] or {}
        overridden = any(v == 3 or v == 4 for v in override.values() if isinstance(v, int))
        effective_boot = s["start"] == 0 and not overridden
        ev["candidates"].append({"driver": s["name"], "start": s["start"], "start_override": override,
                                 "file": st, "effective_boot_start": effective_boot})
        if effective_boot and st in ("ok", "unreadable"):
            usable.append(s["name"])
    ev["usable"] = usable
    if kind == "usb":
        ctx.add("warning", "kernel", _(t"Windows is on a USB-attached disk"),
                _(t"Normal Windows installations cannot boot from USB (only 'Windows To Go'); the USB storage driver is not "
                  t"boot-start and Windows stops with INACCESSIBLE_BOOT_DEVICE."),
                [f"/dev/{ctx.disk['name']} transport: usb"],
                [_(t"Connect the disk internally (SATA/NVMe) to boot it.")], stopcode="0x0000007B", source=SRC, priority=20)
        return
    if usable:
        return
    primary = cands[0]
    present = [c for c in ev["candidates"]]
    why = {
        "nvme": N_("The Windows disk is an NVMe SSD, but no NVMe driver (stornvme or a vendor driver) is set to start at "
                "boot. Typical when Windows was installed on a SATA disk and then cloned to NVMe."),
        "ahci": N_("The Windows disk is attached to an AHCI SATA controller, but the AHCI driver (storahci) is not set "
                "to start at boot. Typical after switching the firmware SATA mode from RAID/IDE to AHCI, or after "
                "moving the disk to another computer."),
        "vmd": N_("The NVMe SSD sits behind Intel VMD / RST (the firmware's 'RAID On'/'VMD' mode). Windows needs the "
               "Intel RST VMD driver (iaStorVD) at boot, which is not configured. Typical when the BIOS storage mode "
               "was switched from AHCI to RAID/VMD, or Windows was installed without the RST driver."),
        "raid": N_("The disk is behind a RAID controller whose driver is not configured as boot-start."),
        "virtio": N_("The disk is a VirtIO disk but the VirtIO storage driver is not installed/boot-start."),
        "scsi": N_("The disk is behind a SAS/SCSI controller whose driver is not boot-start."),
    }.get(kind, N_("No driver for the disk's controller is configured to start at boot."))
    steps = []
    if kind in ("ahci", "nvme"):
        steps = [_("If you changed the storage mode (AHCI / RAID / VMD) in the firmware setup recently, changing it "
                   "back is the quickest fix. Otherwise switch the driver on:")] + hive_edit_steps([
            _(t"Make the {primary} driver start at boot (0 = boot start):\n"
              t"`reg add HKLM\\OFFLINE\\{csname}\\Services\\{primary} /v Start /t REG_DWORD /d 0 /f`"),
            _(t"Remove the override that keeps it switched off. “Unable to find” just means there is none:\n"
              t"`reg delete HKLM\\OFFLINE\\{csname}\\Services\\{primary}\\StartOverride /f`")])
    elif kind == "vmd":
        steps = [_(t"Easiest: open the firmware setup (usually F2 or Del) and change the storage mode from “RAID On” / "
                   t"“Intel RST” / “VMD” to “AHCI”. Windows then uses its built-in NVMe driver."),
                 WINRE,
                 _(t"Or add Intel's RST VMD driver: download it from your PC maker on another computer, unpack it to a "
                   t"USB stick (here E:) and add it:\n`dism /image:C:\\ /add-driver /driver:E:\\ /recurse`")]
    else:
        steps = [_("Change the controller mode in the firmware setup back to what it was when Windows was installed."),
                 WINRE,
                 _("Or add the controller's driver: unpack it to a USB stick (here E:) and add it:\n"
                   "`dism /image:C:\\ /add-driver /driver:E:\\ /recurse`")]
    ctx.add("critical", "kernel", _(t"No boot-start driver for the disk controller ({kind.upper()})"),
            _(why) + _(" Without it the kernel cannot see the disk it is booting from and stops with "
                       "INACCESSIBLE_BOOT_DEVICE."),
            [f"Linux sees /dev/{ctx.disk['name']} via: {kind} ({ctx.disk.get('tran') or '?'})"]
            + [f"Services\\{c['driver']}: Start={c['start']} ({SERVICE_START.get(c['start'], '?')})"
               + (f", StartOverride={c['start_override']}" if c['start_override'] else "") + f", file {c['file']}"
               for c in present]
            + ([] if present else [f"none of {', '.join(cands[:5])} is installed"]),
            steps, stopcode="0x0000007B INACCESSIBLE_BOOT_DEVICE", source=SRC, priority=9,
            actions=_controller_actions(present, cands, csname))


def _controller_actions(present, cands, csname):
    """Enable the first installed, intact candidate driver (inbox driver preferred)."""
    for c in present:
        if c["file"] in ("ok", "unreadable"):
            return [A.set_service_start(csname, c["driver"], 0, clear_override=bool(c["start_override"]))]
    return []


def _session_manager(ctx, cs, csname):
    try:
        sm = cs.subkey("Control").subkey("Session Manager")
    except (RegfError, AttributeError):
        sm = None
    if sm is None:
        return
    for vname in ("BootExecute", "SetupExecute", "PlatformExecute"):
        try:
            vals = sm.get(vname) or []
        except RegfError:
            continue
        if isinstance(vals, str):
            vals = [vals]
        vals = [v for v in vals if v.strip()]
        if not vals:
            continue
        ctx.evidence.setdefault("session_manager", {})[vname] = vals
        for entry in vals:
            tokens = entry.split()
            prog = tokens[1] if tokens and tokens[0].lower() == "autocheck" and len(tokens) > 1 else tokens[0]
            exe = prog if prog.lower().endswith(".exe") else prog + ".exe"
            exists = ctx.win_path(f"Windows\\System32\\{exe}") is not None
            is_default = entry.strip().lower() == "autocheck autochk *"
            if not exists:
                ctx.add("warning", "session", _(t"{vname} runs a program that does not exist ({exe})"),
                        _(t"Session Manager runs these native programs before Windows starts. A missing one delays boot "
                          t"and indicates a removed tool (often antivirus/cleaner leftovers)."),
                        [f"HKLM\\SYSTEM\\{csname}\\Control\\Session Manager\\{vname} = {vals}"],
                        hive_edit_steps([_(t"Reset {vname} to the Windows default:\n"
                                           t"`reg add \"HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\" /v {vname} "
                                           t"/t REG_MULTI_SZ /d \"autocheck autochk *\" /f`")]
                                        if vname == "BootExecute" else
                                        [_(t"Empty {vname}:\n`reg add \"HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\" "
                                           t"/v {vname} /t REG_MULTI_SZ /d \"\" /f`")]),
                        source=SRC, priority=35)
            elif vname == "BootExecute" and not is_default:
                if "autochk" in entry.lower() and ("/p" in entry.lower() or "/r" in entry.lower() or "\\??\\" in entry):
                    ctx.add("info", "session", _(t"A disk check (chkdsk) is scheduled for the next start"),
                            _(t"Windows will run autochk before starting. On a damaged disk this can take very long."),
                            [f"BootExecute = {vals}"], source=SRC)
                else:
                    ctx.add("info", "session", _(t"Non-standard BootExecute entry: {entry}"),
                            _(t"A program runs natively before Windows starts (often antivirus boot-time scan or "
                              t"defrag tools). If it hangs, Windows hangs with it."), [f"BootExecute = {vals}"], source=SRC)
    try:
        v = sm.value("PendingFileRenameOperations")
        raw = v.raw if v is not None else b""
    except RegfError:
        raw = b""
    pairs = pending_pairs(raw)
    if not pairs:
        return
    ctx.evidence["pending_file_renames"] = [f"{a} -> {b or '(delete)'}" for a, b in pairs[:200]]
    deletes = [a for a, b in pairs if not b]
    moves = [(a, b) for a, b in pairs if b]
    temp = [a for a in deletes if re.search(r"(?i)\\(SET[0-9A-F]+\.tmp|[^\\]+\.(tmp|old|bak|\d+))$", a)]
    sys_moves = [(a, b) for a, b in moves
                 if re.search(r"(?i)\\windows\\system32\\(drivers\\)?[^\\]+\.(sys|dll|exe)$", b)]
    ctx.pending_driver_renames = len([1 for a, b in sys_moves if "\\drivers\\" in b.lower()])
    if sys_moves:
        sev, title = "warning", _(t"{len(sys_moves)} system file(s) will be replaced at the next start")
        why = _("Session Manager will swap these Windows files very early in the next start (an installer or "
                "update that needed a restart). If one of the new files is broken or does not match the rest, "
                "startup fails right after.")
    elif len(temp) == len(pairs):
        sev, title = "info", _(t"{len(pairs)} leftover temporary file(s) will be deleted at the next start")
        why = _("Only clean-up of temporary files left by installers (SET….tmp and similar). Harmless; it has no "
                "influence on whether Windows starts.")
    else:
        sev, title = "info", _(t"{len(pairs)} file operation(s) are pending for the next start")
        why = _(t"{len(deletes)} file(s) will be deleted and {len(moves)} moved by Session Manager at the next "
                t"start (installers that needed a restart). None of them replaces a Windows system file.")
    ctx.pending_renames_finding = ctx.add(
        sev, "session", title, why,
        [f"{a} -> {b or '(delete)'}" for a, b in (sys_moves + [p for p in pairs if p not in sys_moves])[:10]],
        hive_edit_steps([_(t"Cancel the pending operations:\n"
                           t"`reg delete \"HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\" "
                           t"/v PendingFileRenameOperations /f`")]) if sys_moves else [],
        source=SRC, priority=45, actions=[A.clear_pending_renames(csname)] if sys_moves else [])


def pending_pairs(raw):
    """Decode PendingFileRenameOperations keeping empty entries (an empty target means 'delete')."""
    if not raw:
        return []
    if len(raw) % 2:
        raw = raw[:-1]
    s = raw.decode("utf-16-le", errors="replace")
    while s.endswith("\x00\x00"):
        s = s[:-1]
    if s.endswith("\x00"):
        s = s[:-1]
    items = s.split("\x00")
    pairs = []
    for i in range(0, len(items) - 1, 2):
        src, dst = items[i].strip(), items[i + 1].strip()
        if src:
            pairs.append((src, dst))
    return pairs


def _verifier(ctx, cs, csname):
    try:
        mm = cs.subkey("Control").subkey("Session Manager").subkey("Memory Management")
        vd = mm.get("VerifyDrivers") if mm else None
        lvl = mm.get("VerifyDriverLevel") if mm else None
    except (RegfError, AttributeError):
        return
    if vd:
        ctx.add("warning", "kernel", _(t"Driver Verifier is enabled"),
                _(t"Driver Verifier deliberately crashes Windows (0xC4 / 0x1C4) as soon as a verified driver misbehaves. "
                  t"Left enabled, it often produces a boot loop."),
                [f"VerifyDrivers = {vd}", f"VerifyDriverLevel = {lvl}"],
                hive_edit_steps([_(t"Switch Driver Verifier off:\n"
                                   t"`reg delete \"HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\\Memory Management\" /v VerifyDrivers /f\n"
                                   t"reg delete \"HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\\Memory Management\" /v VerifyDriverLevel /f`")]),
                stopcode="0x000000C4 DRIVER_VERIFIER_DETECTED_VIOLATION", source=SRC, priority=25,
                actions=[A.disable_verifier(csname)])


def _mounted_devices(ctx):
    h = ctx.system_hive
    if h is None:
        return
    try:
        md = h.open("MountedDevices")
        v = md.value("\\DosDevices\\C:") if md else None
        raw = v.raw if v else None
    except RegfError:
        return
    if not raw:
        return
    parts = ctx.all_partitions()
    target = ctx.target
    pointed = None
    desc = raw[:24].hex()
    if raw.startswith(b"DMIO:ID:") and len(raw) >= 24:
        g = raw[8:24]
        for p in parts:
            try:
                if p.get("partuuid") and guid_bytes(p["partuuid"]) == g:
                    pointed = p
            except ValueError:
                pass
        import uuid
        desc = f"GPT partition {{{uuid.UUID(bytes_le=bytes(g))}}}"
    elif len(raw) == 12:
        sig = int.from_bytes(raw[:4], "little")
        off = int.from_bytes(raw[4:12], "little")
        desc = f"MBR disk {sig:08x}, offset {off}"
        for p in parts:
            try:
                if p["pttype"] == "dos" and int(p["ptuuid"].split("-")[0], 16) == sig and p["start_bytes"] == off:
                    pointed = p
            except (ValueError, TypeError):
                pass
    else:
        return
    ctx.evidence["drive_letter_c"] = {"raw": desc, "partition": pointed["name"] if pointed else None}
    if pointed is not None and pointed["name"] != target["name"]:
        ctx.add("critical", "logon", _(t"Drive letter C: belongs to a different partition (/dev/{pointed['name']})"),
                _(t"Windows' MountedDevices assigns C: to another partition that is also connected - typically the "
                  t"original disk after cloning. The system boots from this partition but gets a different drive letter, "
                  t"so programs, the registry and user profiles reference the other disk: logon fails, 'Preparing "
                  t"desktop' loops or you are logged on with a temporary profile."),
                [f"HKLM\\SYSTEM\\MountedDevices\\\\DosDevices\\C: -> {desc} = /dev/{pointed['name']}",
                 f"analysed Windows: /dev/{target['name']}"],
                [_(t"Simplest: disconnect the other (old) disk and start Windows."),
                 *hive_edit_steps([_(t"Or let Windows assign the drive letters again at the next start. The volume it "
                                     t"starts from becomes C::\n`reg delete HKLM\\OFFLINE\\MountedDevices /va /f`")])],
                source=SRC, priority=20,
                actions=[A.reg_delete_values("SYSTEM", "MountedDevices", ["\\DosDevices\\C:"],
                                             _("Remove the stale C: drive-letter assignment"))])


def _crash_control(ctx, cs):
    try:
        cc = cs.subkey("Control").subkey("CrashControl")
    except (RegfError, AttributeError):
        return
    if cc is None:
        return
    info = {v: cc.get(v) for v in ("CrashDumpEnabled", "AutoReboot", "DumpFile", "MinidumpDir")}
    ctx.evidence["crash_control"] = info
    if info.get("CrashDumpEnabled") == 0:
        ctx.add("info", "general", _(t"Crash dumps are disabled"),
                _(t"Blue screens leave no dump file, so the exact crashing driver cannot be identified from dumps."),
                ["CrashControl\\CrashDumpEnabled = 0"], source=SRC)
