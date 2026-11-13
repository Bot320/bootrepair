"""Recovery options and other additional state: WinRE, restore points, Windows.old, Fast Startup."""

import re

from ..i18n import _
from ..fsutil import read_text_any
from ..knowledge import WINDOWS, SYSTEM_RESTORE
from ..parsers.regf import RegfError

SRC = "extras"
VSS_GUID = "{3808876b-c176-4e48-b7ae-04046e6cc752}"


def analyze(ctx):
    if not ctx.ensure_windows():
        return
    ev = {}
    ctx.evidence["recovery"] = ev

    # WinRE configuration
    p = ctx.win_path("Windows\\System32\\Recovery\\ReAgent.xml")
    if p is not None:
        try:
            x = read_text_any(p, 64 * 1024)
            state = re.search(r'<InstallState\s+state="(\d+)"', x)
            loc = re.search(r'<WinreLocation\s+path="([^"]*)"', x)
            ev["winre_state"] = state.group(1) if state else ""
            ev["winre_location"] = loc.group(1) if loc else ""
            if state and state.group(1) == "0":
                ctx.add("info", "general", _(t"Windows Recovery Environment is disabled"),
                        _(t"Automatic Repair and the advanced startup options are not available from this disk; "
                          t"you will need a Windows USB stick for repairs."), ["ReAgent.xml: InstallState state=\"0\""],
                        [WINDOWS, _(t"Turn the recovery environment back on:\n`reagentc /enable`")], source=SRC)
        except OSError:
            pass

    # System restore points (VSS snapshots of this volume)
    svi = ctx.win.listdir("System Volume Information")
    snaps = [n for n in svi if VSS_GUID in n.lower()]
    ev["restore_points"] = len(snaps)
    ctx.restore_points = len(snaps)
    if snaps:
        ctx.add("info", "general", _(t"{len(snaps)} System Restore snapshot(s) exist"),
                _(t"System Restore from WinRE can return Windows to an earlier, working state (programs installed since "
                  t"then are removed, personal files stay)."),
                [f"System Volume Information: {len(snaps)} shadow-copy store file(s)"],
                [_("In Automatic Repair choose Troubleshoot → Advanced options → System Restore, then pick a restore "
                   "point from before the problem started.")],
                source=SRC, priority=70)
    elif ctx.win.resolve("System Volume Information") is not None:
        ev["restore_note"] = "no shadow copies found"

    if ctx.win.resolve("Windows.old") is not None:
        ctx.add("info", "general", _(t"A previous Windows installation (Windows.old) exists"),
                _(t"Going back to the previous version is possible (Automatic Repair → Troubleshoot → Advanced options → "
                  t"Uninstall Updates → “Uninstall latest feature update”) "
                  t"within the rollback period."), ["\\Windows.old present"], source=SRC, priority=70)

    # Fast startup
    cs = ctx.current_cs
    if cs is not None:
        try:
            pw = cs.subkey("Control").subkey("Session Manager").subkey("Power")
            hb = pw.get("HiberbootEnabled") if pw else None
            ev["fast_startup"] = hb
            if hb == 1 and ctx.hiberfile_state != "hibernated":
                ctx.add("info", "general", _(t"Fast Startup is enabled"),
                        _(t"Windows does not fully shut down; the next start resumes a saved kernel session. This hides "
                          t"some driver problems and makes dual-boot disk access risky."),
                        ["Control\\Session Manager\\Power\\HiberbootEnabled = 1"],
                        [WINDOWS, _(t"Turn Fast Startup off:\n`powercfg /h off`")], source=SRC, priority=80)
        except (RegfError, AttributeError):
            pass
