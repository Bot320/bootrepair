"""System event log analysis: crashes, failed drivers/services, disk and file-system errors, boot timeline."""

import re
from collections import defaultdict
from datetime import timedelta

from ..i18n import _
from ..knowledge import WINRE, LINUX, CHKDSK, BACKUP_FIRST
from ..knowledge import EVENTS, BOOT_OK_EVENTS, SHUTDOWN_OK_EVENTS, bugcheck_text, win32_error, STORAGE_DRIVERS
from ..parsers.evtx import Evtx, EvtxError

SRC = "events"
SCM = "Service Control Manager"
IMPORTANT_SERVICES = {"rpcss", "dcomlaunch", "lsm", "profsvc", "gpsvc", "winmgmt", "eventlog", "plugplay",
                      "power", "brokerinfrastructure", "systemeventsbroker", "coremessagingregistrar",
                      "themes", "usermanager", "samss", "cryptsvc", "netlogon", "trustedinstaller"}


def summarize(e):
    d = e.data
    k = (e.provider, e.event_id)
    if e.provider == SCM:
        if e.event_id == 7026:
            names = [x.strip() for x in re.split(r"[\r\n,]+", d.get("param1", "")) if x.strip()]
            return "Drivers that did not load: " + ", ".join(names)
        if e.event_id in (7000, 7009, 7011, 7022, 7023, 7024, 7031, 7034, 7043):
            s = f"Service '{d.get('param1', '?')}'"
            if e.event_id == 7000:
                return f"{s} failed to start: {win32_error(d.get('param2', ''))}"
            if e.event_id == 7023:
                return f"{s} terminated: {win32_error(d.get('param2', ''))}"
            return s + {7009: " timed out while starting", 7022: " hung on starting", 7024: " terminated with an error",
                        7031: " terminated unexpectedly", 7034: " terminated unexpectedly", 7011: " timed out",
                        7043: " did not shut down properly"}.get(e.event_id, "")
        if e.event_id == 7001:
            return f"Service '{d.get('param1', '?')}' could not start because '{d.get('param2', '?')}' failed: {win32_error(d.get('param3', ''))}"
    if k == ("Microsoft-Windows-Kernel-Power", 41):
        try:
            code = int(d.get("BugcheckCode", "0"))
        except ValueError:
            code = 0
        if code:
            return f"Unexpected restart after blue screen {bugcheck_text(code)}"
        if d.get("PowerButtonTimestamp", "0") not in ("0", ""):
            return "Unexpected restart - power button was held"
        return "Unexpected restart (no bug check recorded: hang, power loss or reset)"
    if e.event_id == 1001 and ("SystemErrorReporting" in e.provider or e.provider == "BugCheck"):
        return "Bug check: " + (d.get("param1") or "").split(",")[0][:160]
    vals = [str(v) for kk, v in d.items() if kk != "Binary" and v]
    return "; ".join(vals)[:240]


def _healthy(e):
    """Ntfs 98 is also logged for healthy volumes (CorruptionActionState 0)."""
    if e.event_id == 98 and "Ntfs" in e.provider:
        return e.data.get("CorruptionActionState", "0") in ("0", "")
    return False


def _drive_letter(e):
    for k in ("DriveName", "VolumeId", "DriveLetter"):
        v = e.data.get(k)
        if v and re.fullmatch(r"[A-Za-z]:", v.strip()):
            return v.strip().upper()
    return None


def _other_drive(e):
    if "Ntfs" in e.provider:
        letter = _drive_letter(e)
        return letter is not None and letter != "C:"
    if e.provider == "disk" or e.provider in ("storahci", "stornvme"):
        m = re.search(r"Harddisk(\d+)", e.data.get("param1", "") + e.data.get("param2", ""))
        return bool(m) and m.group(1) != "0"
    return False


def _drive_label(e):
    d = e.data
    vendor = (d.get("VendorId") or "").strip()
    prod = (d.get("ProductId") or "").strip()
    letter = _drive_letter(e)
    dev = re.search(r"\\Device\\Harddisk\d+", d.get("param1", ""))
    bits = [x for x in (letter, f"{vendor} {prod}".strip(), dev.group(0) if dev else "") if x]
    return " / ".join(bits) or e.provider


def analyze(ctx):
    if not ctx.ensure_windows():
        return
    if not ctx.options.get("events", True):
        ctx.log("event log analysis disabled")
        return
    p = ctx.win_path("Windows\\System32\\winevt\\Logs\\System.evtx")
    if p is None:
        ctx.add("info", "general", _(t"No System event log found"),
                _(t"\\Windows\\System32\\winevt\\Logs\\System.evtx does not exist."), source=SRC)
        return
    try:
        log = Evtx.from_file(p)
    except (OSError, EvtxError) as e:
        ctx.add("info", "general", _(t"System event log could not be read"), "", [str(e)], source=SRC)
        return

    relevant = []
    first = last = None
    total = 0
    for e in log.events():
        total += 1
        if total % 5000 == 0:
            ctx.check_cancel()
        if e.time:
            first = e.time if first is None or e.time < first else first
            last = e.time if last is None or e.time > last else last
        k = (e.provider, e.event_id)
        if k in EVENTS or k in BOOT_OK_EVENTS or k in SHUTDOWN_OK_EVENTS:
            relevant.append(e)
    relevant.sort(key=lambda e: (e.time is None, e.time))
    boots = [e for e in relevant if (e.provider, e.event_id) in BOOT_OK_EVENTS]
    shut = [e for e in relevant if (e.provider, e.event_id) in SHUTDOWN_OK_EVENTS]
    summary = {"records": total, "first": first.isoformat() if first else "", "last": last.isoformat() if last else "",
               "last_boot": boots[-1].time.isoformat() if boots and boots[-1].time else "",
               "last_clean_shutdown": shut[-1].time.isoformat() if shut and shut[-1].time else "",
               "boots_recorded": len(boots), "bad_records": log.bad_records, "dirty": log.dirty}
    ctx.event_summary = summary
    ctx.last_boot_time = boots[-1].time if boots else None
    kg = [e for e in boots if e.provider == "Microsoft-Windows-Kernel-General" and e.data.get("QfeVersion")]
    ctx.last_boot_version = (kg[-1].data.get("BuildVersion"), kg[-1].data.get("QfeVersion")) if kg else None
    ctx.log_last_time = last

    timeline = []
    for e in reversed(relevant):
        k = (e.provider, e.event_id)
        if k in BOOT_OK_EVENTS:
            sev, title = "ok", _("Windows started")
        elif k in SHUTDOWN_OK_EVENTS:
            sev, title = "ok", _("Clean shutdown / restart")
        elif _healthy(e):
            sev, title = "ok", _("Volume checked: healthy (Ntfs 98)")
        else:
            sev, title, __ = EVENTS[k]
            title = _(title)
            if _other_drive(e):
                sev, title = "info", title + _(" - other drive")
        timeline.append({"time": e.time.isoformat() if e.time else "", "provider": e.provider, "id": e.event_id,
                         "severity": sev, "title": title, "detail": summarize(e)})
        if len(timeline) >= 300:
            break
    ctx.evidence["events"] = {"summary": summary, "timeline": timeline}

    if not last:
        return
    window_start = last - timedelta(days=30)
    recent = [e for e in relevant if e.time and e.time >= window_start and (e.provider, e.event_id) in EVENTS
              and not _healthy(e)]
    other = [e for e in recent if _other_drive(e)]
    recent = [e for e in recent if not _other_drive(e)]
    if other:
        names = sorted({_drive_label(e) for e in other})
        ctx.add("info", "general", _(t"Errors on other drives ({len(other)} events) - not the Windows disk"),
                _(t"These disk / file-system errors belong to other drives (e.g. a USB disk), not to the disk Windows "
                  t"starts from, so they do not explain a startup failure. Worth checking that drive separately."),
                names[:6] + [f"{e.time:%Y-%m-%d %H:%M} {e.provider} {e.event_id}: {summarize(e)[:140]}"
                             for e in other[-4:][::-1]], source=SRC, priority=80)
    groups = defaultdict(list)
    for e in recent:
        groups[(e.provider, e.event_id)].append(e)

    storage = {n.lower() for v in STORAGE_DRIVERS.values() for n in v}
    for k, evs in groups.items():
        sev, title, why = EVENTS[k]
        title, why = _(title), _(why)
        n = len(evs)
        newest = evs[-1]
        lines = [f"{e.time:%Y-%m-%d %H:%M:%S} UTC  {summarize(e)}" for e in evs[-8:][::-1]]
        prio = 50
        if k[0] == SCM:
            if k[1] == 7026:
                names = set()
                for e in evs:
                    names.update(x.strip().lower() for x in re.split(r"[\r\n,]+", e.data.get("param1", "")) if x.strip())
                bad = names & storage
                if bad:
                    sev = "warning"
                    why += _(t" Among them storage drivers: {', '.join(sorted(bad))}.")
                    prio = 20
                else:
                    sev = "info"
                    why += _(" Usually leftovers of uninstalled software; harmless unless the device is needed.")
            else:
                names = {e.data.get("param1", "").lower() for e in evs}
                if names & IMPORTANT_SERVICES:
                    sev = "warning"
                    why += _(t" Affected core services: {', '.join(sorted(names & IMPORTANT_SERVICES))}. "
                             t"Failures here cause black screens or logon problems.")
                    prio = 30
        if k == ("Microsoft-Windows-Kernel-Power", 41):
            prio = 25
            why += _(t" This happened {n} time(s) in the last 30 days of the log.")
            if n >= 3:
                why += _(" Repeated unexpected restarts indicate a crash/boot loop or hardware/power problems.")
        stage = {"disk": "disk", "Ntfs": "kernel", "Microsoft-Windows-Ntfs": "kernel", "storahci": "disk",
                 "stornvme": "disk", "iaStorA": "disk", "iaStorAC": "disk",
                 "Microsoft-Windows-WHEA-Logger": "disk", SCM: "session",
                 "Microsoft-Windows-Kernel-Power": "kernel"}.get(k[0], "general")
        ctx.add(sev, stage, title + (_(t" - {n}x") if n > 1 else ""),
                why + _(t" Last occurrence: {newest.time:%Y-%m-%d %H:%M} UTC."),
                lines, _fix(k, ctx), source=SRC, priority=prio)


def _fix(k, ctx):
    prov, eid = k
    dev = ctx.disk["path"]
    if prov in ("disk", "storahci", "stornvme", "iaStorA", "iaStorAC"):
        return [BACKUP_FIRST,
                LINUX, _(t"Read the disk's own health report:\n`sudo smartctl -a {dev}`"),
                _(t"Reseat the drive (SATA cable or M.2 slot). For SATA, try another cable and port.")]
    if "Ntfs" in prov:
        return [WINRE, CHKDSK]
    if prov == "Microsoft-Windows-WHEA-Logger":
        return [_(t"Undo overclocking in the firmware setup, including memory profiles (XMP/EXPO)."),
                LINUX, _(t"Test the memory: install memtest86+ and choose it in the boot menu:\n"
                         t"`sudo pacman -S memtest86+-efi`"),
                _(t"If memory is fine, update the firmware (BIOS) and check temperatures and the power supply.")]
    if prov == "Microsoft-Windows-Kernel-Power":
        return [_("If the report lists blue screens, follow those findings. Without a blue screen the usual causes "
                  "are the power supply, overheating, or the power button held down during a hang.")]
    if prov == SCM:
        return [_("Usually harmless leftovers. If a named service belongs to software you no longer use, uninstall "
                  "that software once Windows runs again.")]
    return []
