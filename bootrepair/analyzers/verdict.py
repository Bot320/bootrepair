"""Correlate findings over time and compute the final verdict."""

from ..i18n import _
from ..model import STAGES, STAGE_IDS, STAGE_LABELS, SEVERITY_ORDER, sort_findings


def correlate(ctx):
    last_boot = getattr(ctx, "last_boot_time", None)
    last_log = getattr(ctx, "log_last_time", None)

    # Pending update that has never been followed by a successful start -> critical.
    if ctx.pending_xml:
        f, mt = ctx.pending_xml
        if mt and last_boot and mt > last_boot:
            f.severity = "critical"
            f.why += _(t" Windows has not recorded a successful start since this update was staged "
                       t"(last successful start: {last_boot:%Y-%m-%d %H:%M} UTC).")
            f.priority = 9

    # Registry already on a newer cumulative update than the one that last started -> half-installed update.
    lbv = getattr(ctx, "last_boot_version", None)
    ubr = str(ctx.windows_info.get("UBR", "")) if ctx.windows_info else ""
    if ctx.pending_xml and lbv and ubr and lbv[1] and lbv[1] != ubr:
        f, __ = ctx.pending_xml
        f.evidence.append(_(t"Windows last started as build {lbv[0]}.{lbv[1]}, but the registry already reports "
                            t"update level .{ubr} - the update was only partly installed"))

    # Startup Repair blames a driver update and driver files are still waiting to be swapped.
    pr = getattr(ctx, "pending_renames_finding", None)
    if pr is not None and getattr(ctx, "pending_driver_renames", 0):
        blamed = [f for f, __ in ctx.srt_findings if "driver" in getattr(f, "cause_text", "")]
        if blamed:
            pr.severity = "critical"
            pr.priority = 12
            pr.why += _(" Startup Repair names a recent driver update as the cause, and these are that update's "
                        "driver files still waiting to be swapped in at the next start.")

    # Offer the matching repairs directly on the Startup Repair finding that names the cause
    related = []
    if ctx.pending_xml:
        related += ctx.pending_xml[0].actions
    if pr is not None and getattr(ctx, "pending_driver_renames", 0):
        related += pr.actions
    for f, __ in ctx.srt_findings:
        t = getattr(f, "cause_text", "")
        if related and ("driver" in t or "update" in t or "patch" in t):
            f.actions = f.actions + [a for a in related if a not in f.actions]

    # Startup Repair blamed an update/driver change, but nothing of it is pending any more (e.g. after a repair)
    nothing_pending = ctx.pending_xml is None and not getattr(ctx, "pending_driver_renames", 0)
    for f, __ in ctx.srt_findings:
        t = getattr(f, "cause_text", "")
        if nothing_pending and f.severity == "critical" and ("driver update" in t or "patch" in t or "update" in t):
            f.severity = "warning"
            f.why += _(" No pending update or driver file operations are left on the disk now, so the change it "
                       "refers to has been undone or cleared. If Windows still fails, run Startup Repair once more.")

    # Crash dumps / Startup Repair results older than the last successful boot are history, not the cause.
    if last_boot:
        for f, t in ctx.crash_findings + ctx.srt_findings:
            if t is None:
                continue
            if t < last_boot and f.severity == "critical":
                f.severity = "warning"
                f.why += _(t" Windows started successfully afterwards, on {last_boot:%Y-%m-%d %H:%M} UTC.")
            elif t > last_boot:
                f.why += _(t" This is newer than the last successful start ({last_boot:%Y-%m-%d %H:%M} UTC).")

    if last_log:
        newer = [t for __, t in ctx.crash_findings + ctx.srt_findings if t and t > last_log]
        if newer:
            ctx.add("info", "general", _(t"Failed starts happened before the event log service could run"),
                    _(t"The System event log ends at {last_log:%Y-%m-%d %H:%M} UTC, but crash dumps / Startup Repair "
                      t"logs are newer. The failing starts therefore die early (kernel, boot drivers or Session "
                      t"Manager), before Windows can write events."),
                    [f"last event: {last_log:%Y-%m-%d %H:%M} UTC", f"newest crash/repair evidence: {max(newer):%Y-%m-%d %H:%M} UTC"],
                    source="verdict", priority=5)


def compute(ctx):
    findings = sort_findings([f.to_dict() for f in ctx.findings])
    stages = []
    first_fail = None
    for sid, label, desc in STAGES:
        fs = [f for f in findings if f["stage"] == sid]
        if any(f["severity"] == "critical" for f in fs):
            status = "fail"
            if first_fail is None:
                first_fail = sid
        elif sid in ctx.unanalyzed_stages:
            status = "unknown"
        elif any(f["severity"] == "warning" for f in fs):
            status = "warn"
        else:
            status = "ok"
        stages.append({"id": sid, "label": _(label), "description": _(desc), "status": status,
                       "critical": sum(f["severity"] == "critical" for f in fs),
                       "warning": sum(f["severity"] == "warning" for f in fs)})
    for i, f in enumerate(findings):
        f["id"] = i
    crit = [f for f in findings if f["severity"] == "critical"]
    warn = [f for f in findings if f["severity"] == "warning"]
    top = None
    inc = "; ".join(ctx.incomplete)
    if first_fail:
        top = next(f for f in crit if f["stage"] == first_fail)
        stage = _(STAGE_LABELS[first_fail])
        verdict = {"status": "fail", "stage": first_fail, "title": _("Windows does not start"),
                   "headline": _(t"Windows does not start: {top['title']}"),
                   "detail": _(t"Startup breaks at stage “{stage}”.") + " " + top["why"]}
    elif crit:
        top = crit[0]
        verdict = {"status": "fail", "stage": top["stage"], "title": _("Windows has a critical problem"),
                   "headline": _(t"Critical problem: {top['title']}"), "detail": top["why"]}
    elif ctx.incomplete:
        verdict = {"status": "incomplete", "stage": "", "title": _("Analysis incomplete"),
                   "headline": _(t"Analysis incomplete: {inc}"), "cause": inc[:1].upper() + inc[1:],
                   "detail": _("No definite boot blocker was found in the parts that could be analysed.")}
    elif warn:
        top = warn[0]
        verdict = {"status": "warn", "stage": top["stage"], "title": _("No definite boot blocker found"),
                   "headline": _("No definite boot blocker found - but there are warnings"),
                   "detail": _(t"The most important warning: {top['title']}.") + " " + top["why"]}
    else:
        ok = _("Boot partition, boot configuration, system files, registry and drivers look intact.")
        verdict = {"status": "ok", "stage": "", "title": _("No problems found"),
                   "headline": _("No problems found that would prevent Windows from starting"),
                   "cause": ok, "detail": ok}
    if top is not None:
        verdict["cause"] = top["title"]
        verdict["finding"] = top["id"]
        verdict["why"] = top["why"]
    verdict["stopcode"] = top.get("stopcode", "") if top is not None and verdict["status"] == "fail" else ""
    counts = {s: sum(f["severity"] == s for f in findings) for s in SEVERITY_ORDER}
    return findings, stages, verdict, counts
