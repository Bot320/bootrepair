"""Analysis pipeline."""

import traceback
from datetime import datetime, timezone

from .. import __version__
from ..i18n import _, N_
from . import disk, volume, bootpart, bcdcheck, files, registry, drivers, servicing, crashes, events, thirdparty, extras, verdict
from .context import Context, Cancelled

STEPS = [
    ("disk", N_("Disk, partition table & health"), disk.analyze),
    ("volume", N_("Windows volume (NTFS, BitLocker, hibernation)"), volume.analyze),
    ("bootpart", N_("Boot partition & firmware boot entries"), bootpart.analyze),
    ("bcd", N_("Boot configuration data (BCD)"), bcdcheck.analyze),
    ("files", N_("Boot-critical system files"), files.analyze),
    ("registry", N_("Registry hives"), registry.analyze),
    ("drivers", N_("Boot drivers, storage controller & filters"), drivers.analyze),
    ("servicing", N_("Pending updates & setup state"), servicing.analyze),
    ("crashes", N_("Crash dumps & Startup Repair logs"), crashes.analyze),
    ("events", N_("System event log"), events.analyze),
    ("thirdparty", N_("Third-party drivers & security software"), thirdparty.analyze),
    ("extras", N_("Recovery options"), extras.analyze),
]


def run_analysis(disks, disk_info, target, esp_choice, bitlocker_key, options, mounts, progress, cancelled):
    ctx = Context(disks, disk_info, target, esp_choice, bitlocker_key, options, mounts, progress, cancelled)
    steps_state = []
    for sid, title, fn in STEPS:
        ctx.check_cancel()
        progress({"type": "step", "id": sid, "state": "running"})
        note = ""
        try:
            fn(ctx)
            state = "done"
            if sid not in ("disk", "volume", "bootpart", "bcd") and not ctx.ensure_windows():
                state, note = "skipped", _("Windows volume not available")
        except Cancelled:
            raise
        except Exception as e:  # an analyzer bug must not kill the whole report
            tname = _(title)
            state = "failed"
            note = f"{type(e).__name__}: {e}"
            ctx.add("info", "general", _(t"Analysis step “{tname}” failed"),
                    _("This part of the analysis crashed; the rest of the report is still valid."),
                    traceback.format_exc().strip().splitlines()[-6:], source=sid, priority=90)
        steps_state.append({"id": sid, "title": _(title), "state": state, "note": note})
        progress({"type": "step", "id": sid, "state": state, "note": note})

    verdict.correlate(ctx)
    findings, stages, v, counts = verdict.compute(ctx)
    t = ctx.target
    report = {
        "tool": "BootRepair", "version": __version__,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": {"device": t["path"], "name": t["name"], "size": t["size"], "label": t["label"],
                   "fstype": t["fstype"], "partuuid": t["partuuid"],
                   "disk": disk_info["path"], "disk_model": disk_info["model"], "controller": disk_info["controller"]},
        "boot_partition": {"device": ctx.boot_part["path"], "name": ctx.boot_part["name"]} if ctx.boot_part else None,
        "boot_mode": ctx.boot_mode,
        "windows": ctx.windows_info,
        "verdict": v,
        "stages": stages,
        "counts": counts,
        "findings": findings,
        "evidence": ctx.evidence,
        "steps": steps_state,
        "incomplete": ctx.incomplete,
        "log": ctx.log_lines,
    }
    return report
