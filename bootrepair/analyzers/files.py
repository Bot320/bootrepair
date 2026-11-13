"""Boot-critical system files: present, non-empty, not zeroed, valid PE."""

import re

from ..i18n import _, N_
from .. import actions as A
from ..fsutil import inspect_file, status_word
from ..knowledge import CRITICAL_FILES, WINRE

SRC = "files"

STAGE_EFFECT = {
    "winload": ("winload", N_("winload loads this file before the kernel starts; without it Windows stops with "
                "'Windows failed to start ... File: <path>' (Recovery screen)."),
                "0xc000000f / 0xc0000098 / 0xc0000428"),
    "kernel": ("winload", N_("winload has to load this file together with the kernel; if it is missing or broken the "
               "start stops on the recovery screen naming the file, or the kernel crashes right after."),
               "0xc000000f / 0xc0000098 / 0x0000007B"),
    "session": ("session", N_("This program/library is needed by the critical system processes started right after "
                "the kernel; startup ends in a blue screen."),
                "0x000000EF CRITICAL_PROCESS_DIED / 0xC000021A"),
    "logon": ("logon", N_("Needed for the logon phase; Windows starts but ends in a black screen, logon loop or "
              "immediate sign-out."), "black screen / logon loop / 0xC000021A"),
}


SFC_STEP = (N_("Let Windows check and repair its own system files (takes 10-30 minutes):\n"
            "`sfc /scannow /offbootdir=C:\\ /offwindir=C:\\Windows`"))
DISM_STEP = (N_("If sfc reports that it could not repair everything, repair the component store from a Windows "
             "installation USB stick of the same version. Find the stick's drive letter with “list vol” (here D:) "
             "and check whether it contains install.wim or install.esd:\n`dir D:\\sources\\install.*`"))
DISM_CMD = (N_("Repair the component store (for install.esd write esd: instead of wim: and install.esd), then run "
            "sfc once more:\n`DISM /Image:C:\\ /Cleanup-Image /RestoreHealth /Source:wim:D:\\sources\\install.wim:1 "
            "/LimitAccess`"))

def repair_steps():
    return [WINRE, SFC_STEP, DISM_STEP, DISM_CMD]


def _version(dirname):
    m = re.search(r"_(\d+)\.(\d+)\.(\d+)\.(\d+)_", dirname)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0, 0)


def winsxs_candidate(ctx, rel):
    """Find an intact copy of a System32 file in the component store. Returns (src_rel, version) or None."""
    name = rel.split("\\")[-1].lower()
    if not rel.lower().startswith("windows\\system32\\"):
        return None
    cache = getattr(ctx, "_winsxs_dirs", None)
    if cache is None:
        cache = [d for d in ctx.win.listdir("Windows\\WinSxS") if d.lower().startswith("amd64_")]
        ctx._winsxs_dirs = cache
    best = None
    sxs = ctx.win.resolve("Windows\\WinSxS")
    if sxs is None:
        return None
    for d in cache:
        p = sxs / d
        try:
            real = next((n for n in _listing(ctx, p) if n.lower() == name), None)
        except OSError:
            continue
        if real is None:
            continue
        st, __ = inspect_file(p / real)
        if st != "ok":
            continue
        v = _version(d)
        if best is None or v > best[1]:
            best = (f"Windows\\WinSxS\\{d}\\{real}", v)
    if best is None:
        return None
    return best[0], ".".join(map(str, best[1]))


def _listing(ctx, p):
    cache = ctx.__dict__.setdefault("_sxs_listing", {})
    key = str(p)
    if key not in cache:
        import os
        cache[key] = os.listdir(p) if p.is_dir() else []
    return cache[key]


def restore_actions(ctx, rel):
    c = winsxs_candidate(ctx, rel)
    return [A.restore_system_file(rel, c[0], c[1])] if c else []


def analyze(ctx):
    if not ctx.ensure_windows():
        return
    mode = ctx.boot_mode or "uefi"
    loader = ctx.loader_path or ("\\Windows\\system32\\winload.efi" if mode == "uefi" else "\\Windows\\system32\\winload.exe")
    files = [(loader.lstrip("\\"), "winload", "OS loader (winload)")]
    files += [f for f in CRITICAL_FILES if f[0].lower() != loader.lstrip("\\").lower()]
    rows = []
    bad = []
    unreadable = []
    for rel, stage, role in files:
        p = ctx.win_path(rel)
        st, detail = inspect_file(p)
        rows.append({"file": rel, "role": role, "status": st, "detail": detail, "stage": stage})
        if st == "ok":
            continue
        if rel.lower() == loader.lstrip("\\").lower() and st == "missing" and ctx.loader_path:
            continue   # already reported by the BCD analyzer
        if st == "unreadable":
            unreadable.append((rel, detail))
        else:
            bad.append((rel, stage, role, st, detail))
    ctx.evidence["critical_files"] = rows

    if len(bad) > 4:
        stages = [STAGE_EFFECT[b[1]][0] for b in bad]
        first = min(stages, key=lambda s: ["winload", "kernel", "session", "logon"].index(s))
        ctx.add("critical", first, _(t"{len(bad)} boot-critical system files are missing or damaged"),
                _(t"Many core files are affected at once, which points to file-system corruption, a failed/aborted "
                  t"update, or files deleted by a cleanup tool or malware. Windows stops at the first one it needs."),
                [f"\\{r}: {status_word(st)} ({d})" for r, __, __, st, d in bad],
                repair_steps(), stopcode=STAGE_EFFECT[bad[0][1]][2], source=SRC, priority=8,
                actions=[a for r, *__ in bad for a in restore_actions(ctx, r)])
    else:
        for rel, stage, role, st, detail in bad:
            s, why, stop = STAGE_EFFECT[stage]
            ctx.add("critical", s, _(t"Boot-critical file {status_word(st)}: \\{rel}"),
                    _(role) + ". " + _(why), [f"\\{rel}: {detail}"], repair_steps(), stopcode=stop,
                    source=SRC, priority=8, actions=restore_actions(ctx, rel))
    if unreadable:
        ctx.add("info", "general", _(t"{len(unreadable)} system file(s) could not be read from Linux"),
                _(t"Usually these are compressed with Windows' CompactOS/WOF compression which the Linux NTFS driver "
                  t"cannot decompress, or the file is a reparse point. Not necessarily a problem - but they could not be "
                  t"verified. Read errors on a failing disk look the same, so check the disk findings."),
                [f"\\{r}: {d}" for r, d in unreadable[:10]], source=SRC)
