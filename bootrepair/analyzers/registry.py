"""Registry hive integrity and basic Windows information."""

from datetime import datetime, timezone

from ..i18n import _
from ..fsutil import human_size
from ..knowledge import HIVES, WINRE, SYSTEM_RESTORE
from ..parsers.regf import Hive, RegfError

SRC = "registry"


def _restore_steps(ctx, name):
    rb = ctx.win_path(f"Windows\\System32\\config\\RegBack\\{name}")
    steps = [WINRE]
    try:
        rb_size = rb.stat().st_size if rb else 0
        rb_time = datetime.fromtimestamp(rb.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d") if rb else ""
    except OSError:
        rb_size, rb_time = 0, ""
    if rb_size > 0:
        size = human_size(rb_size)
        steps += [_(t"Windows keeps an older copy of this hive (RegBack, {size}, from {rb_time}). Keep "
                    t"the damaged file under another name and put the copy in its place:\n"
                    t"`cd C:\\Windows\\System32\\config\nren {name} {name}.broken\n"
                    t"ren {name}.LOG1 {name}.LOG1.broken\nren {name}.LOG2 {name}.LOG2.broken\n"
                    t"copy RegBack\\{name} {name}`"),
                  _("Settings, drivers and updates installed after that date are lost.")]
    else:
        steps += [_(SYSTEM_RESTORE),
                  _("If there is no restore point, the remaining options are restoring a full backup or "
                    "reinstalling Windows (copy your files off first).")]
    return steps


def _regback_action(ctx, name):
    from .. import actions as A
    rb = ctx.win_path(f"Windows\\System32\\config\\RegBack\\{name}")
    try:
        if rb is None or rb.stat().st_size == 0:
            return []
        Hive.from_file(rb)
        age = datetime.fromtimestamp(rb.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d")
    except (OSError, RegfError):
        return []
    return [A.restore_hive_regback(name, f"from {age}")]


def analyze(ctx):
    if not ctx.ensure_windows():
        return
    rows = []
    for name, stage, stop in HIVES:
        row = {"hive": name}
        rows.append(row)
        p = ctx.win_path(f"Windows\\System32\\config\\{name}")
        logs = []
        for ext in ("LOG1", "LOG2", "LOG"):
            lp = ctx.win_path(f"Windows\\System32\\config\\{name}.{ext}")
            try:
                if lp is not None and lp.stat().st_size > 0:
                    logs.append(f"{name}.{ext} ({human_size(lp.stat().st_size)})")
            except OSError:
                pass
        row["logs"] = logs
        if p is None:
            row["status"] = "missing"
            ctx.add("critical", stage, _(t"Registry hive {name} is missing"),
                    _(t"\\Windows\\System32\\config\\{name} does not exist. Windows cannot start without it."),
                    [f"\\Windows\\System32\\config\\{name}: not found"], _restore_steps(ctx, name),
                    stopcode=stop, source=SRC, priority=3)
            continue
        try:
            data = p.read_bytes()
        except OSError as e:
            row["status"] = "unreadable"
            ctx.add("critical", stage, _(t"Registry hive {name} cannot be read"),
                    _(t"Reading the hive file failed - bad sectors or file-system corruption."),
                    [f"{name}: {e.strerror}"], _restore_steps(ctx, name), stopcode=stop, source=SRC, priority=3,
                    actions=_regback_action(ctx, name))
            continue
        row["size"] = len(data)
        try:
            h = Hive(data, name)
        except RegfError as e:
            row["status"] = "corrupt"
            ctx.add("critical", stage, _(t"Registry hive {name} is corrupt"),
                    _(t"The {name} hive is not a valid registry file any more. Windows stops during startup.")
                    + (_(t" Without it, winload cannot load the system configuration.") if name == "SYSTEM" else ""),
                    [f"{name}: {e}", f"size {human_size(len(data))}", "transaction logs: " + (", ".join(logs) or "none")],
                    _restore_steps(ctx, name), stopcode=stop, source=SRC, priority=3,
                    actions=_regback_action(ctx, name))
            continue
        if name == "SYSTEM":
            ctx.system_hive = h
        elif name == "SOFTWARE":
            ctx.software_hive = h
        row["last_written"] = h.last_written.isoformat() if h.last_written else ""
        row["sequence"] = f"{h.seq1}/{h.seq2}"
        nbins, errs = h.check_bins()
        ctx.check_cancel()
        probs = h.walk_check(limit=400000 if name == "SYSTEM" else 20000)
        problems = []
        if not h.checksum_ok:
            problems.append("base block checksum mismatch")
        problems += errs
        problems += [f"key {pth}: {err}" for pth, err in probs[:8]]
        row["status"] = "damaged" if problems else "ok"
        row["problems"] = problems
        if problems:
            ctx.add("critical", stage, _(t"Registry hive {name} is structurally damaged"),
                    _(t"The {name} hive has internal corruption. Windows tries to repair hives from their .LOG files; "
                      t"when that fails it stops with a registry/configuration bug check.")
                    + (_(t" Logs present: {', '.join(logs)}.") if logs else _(t" No transaction logs are available.")),
                    problems[:12], _restore_steps(ctx, name), stopcode=stop, source=SRC, priority=4,
                    actions=_regback_action(ctx, name))
        elif not h.sequence_ok:
            row["status"] = "dirty"
            if logs:
                ctx.add("info", "general", _(t"Registry hive {name} has unflushed changes in its log files"),
                        _(t"Normal after an unclean shutdown: Windows replays the .LOG files at the next start."),
                        [f"sequence numbers {h.seq1} != {h.seq2}", "logs: " + ", ".join(logs)], source=SRC)
            else:
                ctx.add("warning", stage, _(t"Registry hive {name} was not saved completely and has no logs"),
                        _(t"The hive was being written when Windows went down and the transaction logs that would "
                          t"complete it are missing - recent configuration changes may be lost or inconsistent."),
                        [f"sequence numbers {h.seq1} != {h.seq2}"], _restore_steps(ctx, name), source=SRC)

        if name == "SYSTEM" and not problems:
            cur = None
            try:
                cur = h.get("Select", "Current")
            except RegfError:
                pass
            csname = f"ControlSet{cur:03d}" if isinstance(cur, int) else None
            if csname is None or h.open(csname) is None:
                ctx.add("critical", "winload", _(t"SYSTEM hive has no valid current control set"),
                        _(t"HKLM\\SYSTEM\\Select\\Current points to a ControlSet that does not exist, so winload has no "
                          t"driver/service configuration to boot with."),
                        [f"Select\\Current = {cur}", "control sets: " + ", ".join(k.name for k in h.root.subkeys() if k.name.lower().startswith("controlset"))],
                        _restore_steps(ctx, "SYSTEM"), stopcode="0x00000074 BAD_SYSTEM_CONFIG_INFO", source=SRC, priority=3)
            else:
                ctx.current_cs = h.open(csname)
                ctx.current_cs_name = csname
                row["current_control_set"] = csname
    ctx.evidence["registry"] = rows
    _windows_info(ctx)


def _windows_info(ctx):
    info = {}
    sw = ctx.software_hive
    if sw is not None:
        try:
            k = sw.open("Microsoft\\Windows NT\\CurrentVersion")
            if k is not None:
                for v in ("ProductName", "DisplayVersion", "ReleaseId", "CurrentBuild", "CurrentBuildNumber",
                          "UBR", "EditionID", "InstallationType", "RegisteredOwner"):
                    val = k.get(v)
                    if val not in (None, ""):
                        info[v] = val
                inst = k.get("InstallDate")
                if isinstance(inst, int) and inst > 0:
                    info["InstallDate"] = datetime.fromtimestamp(inst, timezone.utc).strftime("%Y-%m-%d")
        except RegfError:
            pass
    try:
        build = int(info.get("CurrentBuild") or info.get("CurrentBuildNumber") or 0)
    except ValueError:
        build = 0
    name = info.get("ProductName", "Windows")
    if build >= 22000 and "Windows 10" in name:
        name = name.replace("Windows 10", "Windows 11")
    info["DisplayName"] = name
    info["Build"] = f"{build}.{info['UBR']}" if build and "UBR" in info else (str(build) if build else "")
    cs = ctx.current_cs
    if cs is not None:
        try:
            c = cs.subkey("Control")
            cn = c.subkey("ComputerName").subkey("ComputerName") if c and c.subkey("ComputerName") else None
            if cn is not None:
                info["ComputerName"] = cn.get("ComputerName", "")
        except (RegfError, AttributeError):
            pass
    ctx.windows_info = info
