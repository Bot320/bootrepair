"""Crash dumps, Startup Repair log (SrtTrail.txt) and boot log (ntbtlog.txt)."""

import re
from collections import Counter
from datetime import datetime, timezone, timedelta

from ..i18n import _, N_
from ..fsutil import read_text_any
from ..knowledge import (BUGCHECKS, BOOT_BLOCKING_BUGCHECKS, bugcheck_text, status_text, WINRE, LINUX,
                         CHKDSK, CHKDSK_R, UNINSTALL_UPDATES, SYSTEM_RESTORE, BACKUP_FIRST)
from ..parsers.dump import parse_dump_header, DumpError
from .files import repair_steps
from .servicing import REVERT_PENDING
from .registry import _restore_steps

SRC = "crashes"


def _mtime(p):
    try:
        return datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
    except OSError:
        return None


def analyze(ctx):
    if not ctx.ensure_windows():
        return
    _dumps(ctx)
    ctx.check_cancel()
    _srttrail(ctx)
    _bootlog(ctx)


# ============================================================================ dumps
def _collect(ctx):
    files = []
    p = ctx.win_path("Windows\\MEMORY.DMP")
    if p is not None:
        files.append((p, "Windows\\MEMORY.DMP", False))
    for n in ctx.win.listdir("Windows\\Minidump"):
        if n.lower().endswith(".dmp"):
            files.append((ctx.win_path(f"Windows\\Minidump\\{n}"), f"Windows\\Minidump\\{n}", False))
    lkr = ctx.win.resolve("Windows\\LiveKernelReports")
    if lkr is not None:
        for f in sorted(lkr.rglob("*")):
            if f.suffix.lower() == ".dmp" and f.is_file():
                files.append((f, "Windows\\LiveKernelReports\\" + str(f.relative_to(lkr)).replace("/", "\\"), True))
    return files


def _dumps(ctx):
    dumps = []
    for p, rel, live in _collect(ctx)[:200]:
        try:
            with open(p, "rb") as f:
                head = f.read(8192)
            h = parse_dump_header(head)
        except (OSError, DumpError) as e:
            dumps.append({"file": rel, "error": str(e), "time": _mtime(p), "live": live})
            continue
        t = h["time"] or _mtime(p)
        dumps.append({"file": rel, "code": h["code"], "params": h["params"], "time": t, "live": live,
                      "type": h["dump_type"], "build": h["build"]})
    dumps.sort(key=lambda d: d["time"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    ctx.evidence["crashes"] = [{
        "file": d["file"], "time": d["time"].isoformat() if d["time"] else "", "live": d["live"],
        "code": bugcheck_text(d["code"]) if "code" in d else "", "error": d.get("error", ""),
        "params": [f"0x{x:X}" for x in d.get("params", [])], "type": d.get("type", "")} for d in dumps]
    ctx.crash_findings = []
    real = [d for d in dumps if not d["live"] and "code" in d]
    if not real:
        live = [d for d in dumps if d["live"] and "code" in d]
        if live:
            ctx.add("info", "general", _(t"{len(live)} live kernel report(s) (non-fatal)"),
                    _(t"Live dumps record hangs/timeouts (often graphics or USB) without crashing Windows."),
                    [f"{d['time']:%Y-%m-%d %H:%M} {bugcheck_text(d['code'])} ({d['file']})" for d in live[:6] if d["time"]],
                    source=SRC)
        return
    latest = real[0]
    by_code = Counter(d["code"] for d in real)
    for code, n in by_code.most_common():
        group = [d for d in real if d["code"] == code]
        newest = group[0]
        name, stage, meaning = BUGCHECKS.get(code, (f"0x{code:08X}", "kernel", N_("Kernel crash.")))
        window = [d for d in group if newest["time"] and d["time"] and newest["time"] - d["time"] < timedelta(days=2)]
        is_latest = newest is latest
        blocking = code in BOOT_BLOCKING_BUGCHECKS
        if is_latest and (blocking or len(window) >= 3):
            sev = "critical"
        elif blocking or n >= 3:
            sev = "warning"
        else:
            sev = "info"
        extra = _param_text(code, newest["params"])
        title = (_(t"Most recent blue screen: {bugcheck_text(code)}") if is_latest else
                 _(t"Recorded blue screen: {bugcheck_text(code)}")) + (f" ({n}x)" if n > 1 else "")
        why = _(meaning) + (" " + extra if extra else "")
        if len(window) >= 3:
            why += _(t" It happened {len(window)} times within two days - a crash loop.")
        f = ctx.add(sev, stage if stage in ("disk", "winload", "kernel", "session", "logon") else "kernel",
                    title, why,
                    [f"{d['time']:%Y-%m-%d %H:%M:%S} UTC  {bugcheck_text(code)}  params "
                     + ", ".join(f"0x{x:X}" for x in d["params"]) + f"  [{d['file']}]" for d in group[:8] if d["time"]],
                    _fix_for(ctx, code), stopcode=bugcheck_text(code), source=SRC,
                    priority=11 if is_latest else 30)
        ctx.crash_findings.append((f, newest["time"]))


def _param_text(code, params):
    if code in (0x7B, 0xED, 0x7A, 0x77) and len(params) > 1:
        st = params[1] & 0xFFFFFFFF
        if st:
            return _(t"Status: {status_text(st)}.")
    if code == 0xC000021A and len(params) > 1:
        st = params[1] & 0xFFFFFFFF
        if st:
            return _(t"Status: {status_text(st)}.")
    if code == 0xEF:
        return _("Parameter 1 is the process object that died (see the dump in WinDbg: `!analyze -v`).")
    if code == 0x74 and params:
        return _({1: N_("Registry I/O failure."), 2: N_("Failed to load/initialise a hive (corrupt hive)."),
                  3: N_("Failed to read the registry (wrong data)."), 4: N_("Bad hive.")}.get(params[0], ""))
    return ""


def _fix_for(ctx, code):
    if code in (0x7B, 0xED):
        return [_(t"Look at the disk-controller and filter-driver findings in this report first: a changed "
                  t"SATA/RAID/VMD setting in the firmware or a leftover storage filter driver is the usual cause."),
                _(t"If you changed the storage mode in the firmware setup recently, change it back."),
                WINRE, CHKDSK_R, UNINSTALL_UPDATES]
    if code in (0x74, 0x51, 0x67, 0xC0000218):
        return _restore_steps(ctx, "SYSTEM")
    if code in (0xEF, 0xF4, 0xC000021A, 0x6B, 0x6F, 0xC0000221):
        return repair_steps() + [UNINSTALL_UPDATES]
    if code in (0x7A, 0x77, 0x154, 0x124, 0x9C, 0x2E, 0x24):
        return [BACKUP_FIRST,
                LINUX, _(t"Check the disk's own health report:\n`sudo smartctl -a {ctx.disk['path']}`"),
                _(t"Test the memory: install memtest86+ and choose it in the boot menu:\n`sudo pacman -S memtest86+-efi`"),
                WINRE, CHKDSK_R]
    if code == 0xC4:
        return [_("See the “Driver Verifier is enabled” finding: turning Verifier off ends this crash loop.")]
    return [_(t"Start Windows in Safe Mode: in Automatic Repair choose Troubleshoot → Advanced options → Startup "
              t"Settings → Restart, then press 4."),
            _(t"In Safe Mode uninstall the program or driver you installed just before the crashes began."),
            _(t"If Safe Mode does not start either:"), WINRE, UNINSTALL_UPDATES]


# ============================================================================ SrtTrail
# SrtTrail.txt is written in the language of the Windows installation. Labels in English and German.
SRT_LABELS = {
    "session": ("Session details", "Sitzungsdetails"),
    "last_boot": ("Last successful boot time", "Zeitpunkt des letzten erfolgreichen Starts"),
    "attempts": ("Number of repair attempts", "Anzahl von Reparaturversuchen", "Anzahl der Reparaturversuche"),
    "root_cause": ("Root cause found", "Gefundene Fehlerursache", "Fehlerursache gefunden"),
    "repair_action": ("Repair action", "Reparaturaktion", "Reparaturvorgang"),
    "result": ("Result", "Ergebnis"),
    "no_cause": ("No root cause found", "Startup Repair cannot repair", "Keine Fehlerursache gefunden",
                 "Es wurde keine Fehlerursache gefunden", "Die Starthilfe kann"),
    "failed": ("Failed", "Fehler", "Fehlgeschlagen"),
}

# Kinds of Startup Repair root causes: (kind, stage, severity, words in English / German). First match wins.
SRT_KINDS = [
    ("serviced_binary", "winload", "critical", ("recently serviced boot binary", "kürzlich verarbeitete startbinärdatei",
                                                "startbinärdatei")),
    ("bugcheck", "kernel", "critical", ("bugcheck", "bug check", "fehlerprüfung")),
    ("boot_file", "winload", "critical", ("boot critical file", "startkritische datei")),
    ("bcd", "bcd", "critical", ("boot configuration", "bcd", "boot manager", "startkonfiguration", "start-manager")),
    ("registry", "winload", "critical", ("registry", "registrierung")),
    ("driver", "session", "critical", ("driver", "treiber")),
    ("update", "session", "critical", ("patch", "update")),
    ("disk", "disk", "critical", ("hard disk", "disk", "datenträger", "festplatte")),
    ("unspecified", "general", "warning", ("unspecified changes", "nicht angegebene änderungen",
                                           "unbekannte änderungen")),
]


def _alt(key):
    return "|".join(re.escape(x) for x in SRT_LABELS[key])


def srt_kind(cause):
    """Classify a Startup Repair root cause (any supported language) -> (kind, stage, severity)."""
    lc = cause.lower()
    for kind, stage, sev, words in SRT_KINDS:
        if any(w in lc for w in words):
            return kind, stage, sev
    if ("corrupt" in lc and "file" in lc) or ("beschädigt" in lc and "datei" in lc):
        return "boot_file", "winload", "critical"
    return "other", "general", "critical"


def parse_srttrail(txt):
    """Parse SrtTrail.txt (English or German). Windows caps the file at a few KB, so the last session is often
    cut off: the root cause is taken from the newest session that reached one."""
    info = {}
    m = re.search(rf"(?:{_alt('last_boot')}):\s*(.+)", txt)
    if m:
        info["last_successful_boot"] = m.group(1).replace("‎", "").strip()
    m = re.search(rf"(?:{_alt('attempts')}):\s*(\d+)", txt)
    if m:
        info["repair_attempts"] = int(m.group(1))
    head = rf"(?m)^[ \t]*(?:{_alt('session')})[ \t]*\r?\n-{{5,}}"
    starts = [m.start() for m in re.finditer(head, txt)]
    sessions = [txt[a:b] for a, b in zip(starts, starts[1:] + [len(txt)])] or [txt]
    info["sessions"] = len(sessions)
    cause_re = re.compile(rf"(?:{_alt('root_cause')}):[ \t]*\r?\n-{{5,}}[ \t]*\r?\n(.*?)(?:\r?\n[ \t]*\r?\n|\r?\n-{{5,}}|\r?\n(?:{_alt('repair_action')})|$)", re.S)
    action_re = re.compile(rf"(?:{_alt('repair_action')}):[ \t]*(.+?)\r?\n(?:{_alt('result')}):[ \t]*(.+?)(?:\r?\n|$)")
    chosen = None
    for sess in reversed(sessions):
        causes = []
        for cm in cause_re.finditer(sess):
            c = " ".join(cm.group(1).split())
            if c and c not in causes:
                causes.append(c)
        no_cause = any(w.lower() in sess.lower() for w in SRT_LABELS["no_cause"])
        if causes or no_cause:
            chosen = (sess, causes)
            break
    sess, causes = chosen if chosen else (sessions[-1], [])
    info["root_causes"] = causes
    info["repair_actions"] = [f"{a.strip()}: {r.strip()}" for a, r in action_re.findall(sess)]
    info["no_root_cause"] = not causes and any(w.lower() in sess.lower() for w in SRT_LABELS["no_cause"])
    return info, sess


def _srttrail(ctx):
    p = ctx.win_path("Windows\\System32\\LogFiles\\Srt\\SrtTrail.txt")
    if p is None:
        return
    try:
        txt = read_text_any(p, 2 * 1024 * 1024)
    except OSError:
        return
    mt = _mtime(p)
    info, last = parse_srttrail(txt)
    info["modified"] = mt.isoformat() if mt else ""
    causes, actions = info["root_causes"], info["repair_actions"]
    ctx.evidence["srttrail"] = {"info": info, "text": last.strip()[-12000:]}
    ctx.srt_findings = []
    if not causes:
        if info["no_root_cause"]:
            ctx.add("info", "general", _(t"Startup Repair ran but found no root cause"),
                    _(t"Windows' own Automatic Repair could not identify the problem."),
                    [f"SrtTrail.txt ({mt:%Y-%m-%d %H:%M} UTC)" if mt else "SrtTrail.txt"] + actions[:4], source=SRC)
        return
    failed_words = tuple(w.lower() for w in SRT_LABELS["failed"])
    for c in causes:
        kind, stage, sev = srt_kind(c)
        why = _(t"Windows' Automatic Repair analysed the failed start and named this as the cause.")
        if kind == "serviced_binary":
            why += _(" It means that a Windows start file that was replaced recently (by an update, an update "
                     "rollback or a repair) did not pass Windows' integrity check. This often follows an update or "
                     "rollback interrupted by a crash or power loss. Startup Repair also reports it when a "
                     "third-party driver stops the start, so check the other findings in this report as well.")
        if any(a.split(": ", 1)[-1].lower().startswith(failed_words) for a in actions):
            why += _(" It could not fix it.")
        attempts = info.get("repair_attempts")
        f = ctx.add(sev, stage, _(t"Startup Repair root cause: {c}"), why,
                    [f"SrtTrail.txt, written {mt:%Y-%m-%d %H:%M} UTC" if mt else "SrtTrail.txt",
                     *([_(t"last successful start: {info['last_successful_boot']}")] if info.get("last_successful_boot") else []),
                     *([_(t"repair attempts: {attempts}")] if attempts is not None else []),
                     *actions[:6]],
                    _srt_fix(ctx, kind, c), source=SRC, priority=7)
        f.cause_kind = kind          # language-independent; used by the verdict logic
        ctx.srt_findings.append((f, mt))


def _srt_fix(ctx, kind, cause):
    if kind == "boot_file":
        m = re.search(r"(?:file|datei) (.+?) (?:is corrupt|ist beschädigt)", cause, re.I)
        steps = repair_steps()
        if m:
            named = m.group(1)
            steps.insert(1, _(t"Startup Repair names {named}. If that belongs to an add-on driver (not "
                              t"Microsoft), look for the matching driver finding in this report: disabling the driver "
                              t"is enough."))
        return steps
    if kind == "serviced_binary":
        return [WINRE, CHKDSK] + repair_steps()[1:] + [UNINSTALL_UPDATES]
    if kind == "bcd":
        from .bootpart import bcdboot_fix
        return bcdboot_fix(ctx)
    if kind == "registry":
        return _restore_steps(ctx, "SYSTEM")
    if kind in ("update", "driver"):
        return [WINRE, REVERT_PENDING, UNINSTALL_UPDATES]
    if kind == "bugcheck":
        return _fix_for(ctx, 0)
    return [WINRE, SYSTEM_RESTORE]


# ============================================================================ ntbtlog
def _bootlog(ctx):
    p = ctx.win_path("Windows\\ntbtlog.txt")
    if p is None:
        return
    try:
        txt = read_text_any(p, 8 * 1024 * 1024)
    except OSError:
        return
    mt = _mtime(p)
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    starts = [i for i, l in enumerate(lines) if re.match(r"(?i)microsoft \(r\) windows", l)]
    sess = lines[starts[-1]:] if starts else lines
    loaded = [l for l in sess if "\\" in l and re.search(r"(?i)(BOOTLOG_LOADED|loaded driver|geladener treiber|^\S+\s+\\)", l)
              and not re.search(r"(?i)(not loaded|did not|nicht geladen|BOOTLOG_NOT_LOADED)", l)]
    not_loaded = [l for l in sess if re.search(r"(?i)(BOOTLOG_NOT_LOADED|did not load|nicht geladen)", l)]
    ctx.evidence["bootlog"] = {"modified": mt.isoformat() if mt else "", "session_header": sess[:2],
                               "loaded_count": len(loaded), "last_loaded": loaded[-5:], "not_loaded": not_loaded[:60]}
    if loaded:
        ctx.add("info", "kernel", _(t"Boot log: last driver loaded in the most recent boot attempt"),
                _(t"Windows boot logging was enabled. If Windows hung or crashed during startup, the problem is usually "
                  t"the driver loaded right after the last one listed (or this last one itself)."),
                [f"ntbtlog.txt ({mt:%Y-%m-%d %H:%M} UTC)" if mt else "ntbtlog.txt", *loaded[-5:]],
                source=SRC, priority=60)
