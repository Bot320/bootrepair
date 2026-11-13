"""Windows Update / servicing / setup state that can make the start fail or loop."""

import re
from datetime import datetime, timezone

from ..i18n import _, N_
from .. import actions as A
from ..fsutil import read_text_any, read_tail, human_size
from ..knowledge import WINRE, UNINSTALL_UPDATES

REVERT_PENDING = N_("Undo the update that is waiting to be installed:\n"
                  "`dism /image:C:\\ /cleanup-image /revertpendingactions`")
from ..parsers.regf import RegfError

SRC = "servicing"


def _mtime(p):
    try:
        return datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
    except OSError:
        return None


def analyze(ctx):
    if not ctx.ensure_windows():
        return
    ev = {}
    ctx.evidence["servicing"] = ev

    # --------------------------------------------------------------- pending.xml
    p = ctx.win_path("Windows\\WinSxS\\pending.xml")
    if p is not None:
        mt = _mtime(p)
        ev["pending_xml"] = {"time": mt.isoformat() if mt else "", "size": p.stat().st_size}
        f = ctx.add("warning", "session", _(t"A Windows Update operation is pending (WinSxS\\pending.xml)"),
                    _(t"An update was staged and will be completed during the next start ('Working on updates' / "
                      t"'Preparing Windows'). If completing it fails, Windows rolls back and restarts - often in an "
                      t"endless 'Undoing changes made to your computer' loop."),
                    [f"\\Windows\\WinSxS\\pending.xml ({human_size(p.stat().st_size)}, written {mt:%Y-%m-%d %H:%M} UTC)" if mt else "pending.xml present"],
                    [WINRE, REVERT_PENDING,
                     _(t"If dism reports an error, set the update's instruction file aside by hand:\n"
                       t"`ren C:\\Windows\\WinSxS\\pending.xml pending.xml.old`"),
                     UNINSTALL_UPDATES],
                    stopcode="update loop / 0xC000021A", source=SRC, priority=15,
                    actions=[A.revert_pending_update()])
        ctx.pending_xml = (f, mt)
        comp = ctx.load_hive("COMPONENTS")
        if comp is not None:
            try:
                vals = {n: comp.root.get(n) for n in ("PendingXmlIdentifier", "NextQueueEntryIndex",
                                                      "AdvancedInstallersNeedResolving", "ExecutionState")}
            except RegfError:
                vals = {}
            vals = {k: (v.hex() if isinstance(v, bytes) else v) for k, v in vals.items() if v is not None}
            ev["components"] = vals
            if vals:
                f.evidence.append("COMPONENTS hive: " + ", ".join(f"{k}={str(v)[:40]}" for k, v in vals.items()))

    sw = ctx.software_hive
    if sw is not None:
        try:
            cbs = sw.open("Microsoft\\Windows\\CurrentVersion\\Component Based Servicing")
            if cbs is not None:
                flags = [n for n in ("RebootPending", "PackagesPending", "SessionsPending", "RebootInProgress")
                         if cbs.subkey(n) is not None]
                ev["cbs_flags"] = flags
                if "SessionsPending" in flags:
                    sp = cbs.subkey("SessionsPending")
                    excl = sp.get("Exclusive") if sp else None
                    ev["sessions_pending_exclusive"] = excl
                if "RebootInProgress" in flags:
                    ctx.add("warning", "session", _(t"Servicing reports a reboot in progress"),
                            _(t"Component Based Servicing was in the middle of a reboot-time operation."),
                            ["Component Based Servicing\\RebootInProgress exists"], source=SRC)
        except RegfError:
            pass

    # --------------------------------------------------------------- setup / OOBE state
    h = ctx.system_hive
    if h is not None:
        try:
            st = h.open("Setup")
            if st is not None:
                vals = {n: st.get(n) for n in ("SystemSetupInProgress", "SetupType", "CmdLine", "OOBEInProgress",
                                                 "SetupPhase", "RestartSetup", "Upgrade")}
                ev["setup"] = {k: v for k, v in vals.items() if v not in (None, "")}
                child = h.get("Setup\\Status\\ChildCompletion", "setup.exe")
                in_setup = vals["SystemSetupInProgress"] == 1 or (vals["SetupType"] not in (None, 0))
                if in_setup:
                    ctx.add("critical", "logon", _(t"Windows is stuck in Setup / OOBE mode"),
                            _(t"The registry still says that Windows Setup is running. Every start launches the setup "
                              t"phase again ('Windows installation cannot proceed' / 'The computer restarted unexpectedly "
                              t"or encountered an unexpected error') instead of the normal logon."),
                            [f"HKLM\\SYSTEM\\Setup\\{k} = {v!r}" for k, v in vals.items() if v not in (None, "")]
                            + ([f"Setup\\Status\\ChildCompletion\\setup.exe = {child}"] if child is not None else []),
                            [_(t"When the error message appears, press Shift+F10. A command prompt opens."),
                             _(t"Tell Windows Setup that its last phase has finished, then restart:\n"
                               t"`reg add HKLM\\SYSTEM\\Setup\\Status\\ChildCompletion /v setup.exe /t REG_DWORD /d 3 /f\n"
                               t"shutdown /r /t 0`"),
                             _(t"If this was an aborted upgrade to a new Windows version, go back to the old one "
                               t"instead: in Automatic Repair choose Troubleshoot → Advanced options → Uninstall Updates "
                               t"→ “Uninstall latest feature update”.")],
                            stopcode="Setup/OOBE loop", source=SRC, priority=10,
                            actions=[A.setup_child_completion()] if child is not None and child != 3 else [])
        except RegfError:
            pass

    # --------------------------------------------------------------- feature upgrade leftovers
    bt = ctx.win_path("$WINDOWS.~BT")
    if bt is not None:
        rb = ctx.win_path("$WINDOWS.~BT\\Sources\\Rollback")
        ev["windows_bt"] = True
        if rb is not None:
            ctx.add("info", "session", _(t"A feature update was rolled back"),
                    _(t"$WINDOWS.~BT\\Sources\\Rollback exists: an upgrade to a newer Windows version failed and was undone."),
                    ["\\$WINDOWS.~BT\\Sources\\Rollback present"], source=SRC)
        else:
            ctx.add("info", "session", _(t"A feature update is staged or in progress ($WINDOWS.~BT)"),
                    _(t"Windows Setup files for an upgrade are on the disk."), ["\\$WINDOWS.~BT present"], source=SRC)
    errs = _setuperr(ctx)
    if errs:
        ev["setuperr"] = errs

    cbs = ctx.win_path("Windows\\Logs\\CBS\\CBS.log")
    if cbs is not None:
        try:
            tail = read_tail(cbs, 2 * 1024 * 1024).decode("utf-8", errors="replace")
            lines = [l for l in tail.splitlines() if re.search(r"\bError\b", l) and "CBS" in l]
            ev["cbs_errors"] = lines[-40:]
        except OSError:
            pass


def _setuperr(ctx):
    for rel in ("$WINDOWS.~BT\\Sources\\Panther\\setuperr.log", "Windows\\Panther\\setuperr.log",
                "$WINDOWS.~BT\\Sources\\Rollback\\setuperr.log"):
        p = ctx.win_path(rel)
        if p is None:
            continue
        try:
            txt = read_text_any(p, 1024 * 1024)
        except OSError:
            continue
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if lines:
            return [f"[{rel}]"] + lines[-25:]
    return []
