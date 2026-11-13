"""Render a report dict as Markdown or plain terminal text."""

from . import guide
from .fsutil import human_size
from .i18n import _, N_
from .model import STAGE_LABELS

ICON = {"critical": "✖", "warning": "▲", "info": "ℹ"}
STAGE_ICON = {"ok": "✔", "warn": "▲", "fail": "✖", "unknown": "?"}
SEV_HEADINGS = (("critical", N_("Critical - prevents Windows from starting")),
                ("warning", N_("Warnings - may be involved")),
                ("info", N_("Additional information")))
STATUS_WORD = {"ok": N_("ok"), "warn": N_("warning"), "fail": N_("fails"), "unknown": N_("not analysed")}


def _stage(f):
    return _(STAGE_LABELS.get(f["stage"], f["stage"]))


def to_markdown(r):
    out = []
    t = r["target"]
    w = r.get("windows") or {}
    out.append("# " + _("BootRepair report") + "\n")
    gen, ver = r["generated"], r["version"]
    out.append("*" + _(t"Generated {gen} - version {ver}") + "*\n")
    out.append("| | |\n|---|---|")
    out.append(f"| {_('Windows partition')} | `{t['device']}` {t.get('label') or ''} ({human_size(t['size'])}) |")
    out.append(f"| {_('Disk')} | `{t['disk']}` {t.get('disk_model') or ''} ({t.get('controller')}) |")
    if r.get("boot_partition"):
        out.append(f"| {_('Boot partition')} | `{r['boot_partition']['device']}` ({(r.get('boot_mode') or '').upper()}) |")
    if w:
        out.append(f"| Windows | {w.get('DisplayName', '')} {w.get('DisplayVersion', '')} build {w.get('Build', '')} "
                   f"{('(' + w['ComputerName'] + ')') if w.get('ComputerName') else ''} |")
    out.append("")
    v = r["verdict"]
    out.append(f"## {_('Verdict')}\n\n**{v['headline']}**\n\n{v['detail']}\n")
    if v.get("stopcode"):
        out.append(f"{_('What you see on screen:')} `{v['stopcode']}`\n")
    if any(guide.needs_winre(f["fix"]) for f in r["findings"] if f["severity"] != "info"):
        out.append(f"## {_(guide.HOWTO_TITLE)}\n\n```\n" + "\n".join(guide.plain_steps(guide.winre_howto(r)))
                   + "\n```\n")
    out.append(f"## {_('Boot chain')}\n")
    for s in r["stages"]:
        out.append(f"- {STAGE_ICON[s['status']]} **{s['label']}** - {_(STATUS_WORD[s['status']])}")
    out.append("")
    for sev, title in SEV_HEADINGS:
        fs = [f for f in r["findings"] if f["severity"] == sev]
        if not fs:
            continue
        out.append(f"## {_(title)} ({len(fs)})\n")
        for f in fs:
            out.append(f"### {ICON[sev]} {f['title']}\n")
            out.append(f"*{_('Stage')}: {_stage(f)}*"
                       + (f" - {_('stop code')} `{f['stopcode']}`" if f.get("stopcode") else "") + "\n")
            if f["why"]:
                out.append(f"{f['why']}\n")
            if f["evidence"]:
                out.append(_("Evidence") + ":\n\n```\n" + "\n".join(str(e) for e in f["evidence"]) + "\n```\n")
            if f["fix"]:
                out.append(_("How to fix by hand") + ":\n\n```\n" + "\n".join(guide.plain_steps(f["fix"])) + "\n```\n")
    ev = r.get("evidence", {})
    if ev.get("bcd", {}).get("entries"):
        out.append(f"## {_('Boot configuration (BCD)')}\n")
        for e in ev["bcd"]["entries"]:
            out.append(f"- `{e['id']}` {e['type']} '{e['description']}'"
                       + (f" **[{_('default')}]**" if e["default"] else "") + (f" **[{_('this Windows')}]**" if e["this_windows"] else ""))
            for k in ("device", "osdevice", "path", "systemroot"):
                if e.get(k):
                    out.append(f"  - {k}: {e[k]}")
            if e["flags"]:
                out.append(f"  - flags: {', '.join(e['flags'])}")
        out.append("")
    if ev.get("crashes"):
        out.append(f"## {_('Crash dumps')}\n")
        for c in ev["crashes"][:30]:
            out.append(f"- {c['time']} {c['code'] or c['error']} `{c['file']}`" + (" (live)" if c["live"] else ""))
        out.append("")
    if ev.get("events", {}).get("timeline"):
        out.append(f"## {_('Boot-relevant events (newest first)')}\n")
        for e in ev["events"]["timeline"][:80]:
            out.append(f"- {e['time'][:19]} [{e['severity']}] {e['provider']} {e['id']}: {e['title']} - {e['detail']}")
        out.append("")
    return "\n".join(out)


def to_text(r):
    lines = []
    v = r["verdict"]
    t = r["target"]
    w = r.get("windows") or {}
    lines.append("=" * 78)
    lines.append(f" BootRepair - {t['device']} ({t['disk']})")
    if w:
        lines.append(f" {w.get('DisplayName', '')} {w.get('DisplayVersion', '')} build {w.get('Build', '')}")
    lines.append("=" * 78)
    lines.append(f"\n>>> {v['headline']}")
    lines.append(f"    {v['detail']}")
    if v.get("stopcode"):
        lines.append(f"    {_('What you see on screen:')} {v['stopcode']}")
    lines.append("\n" + _("Boot chain") + ": "
                 + "  ->  ".join(f"{STAGE_ICON[s['status']]} {s['label']}" for s in r["stages"]))
    for sev, title in SEV_HEADINGS:
        fs = [f for f in r["findings"] if f["severity"] == sev]
        if not fs:
            continue
        lines.append(f"\n---------------- {_(title).upper()} ({len(fs)}) ----------------")
        for f in fs:
            lines.append(f"\n{ICON[sev]} {f['title']}  [{_stage(f)}]"
                         + (f"  ({f['stopcode']})" if f.get("stopcode") else ""))
            if f["why"]:
                lines.append("   " + f["why"])
            for e in f["evidence"][:12]:
                lines.append(f"     · {e}")
            if f["fix"] and sev != "info":
                lines.append("   " + _("How to fix by hand") + ":")
                lines.extend("     " + l for l in guide.plain_steps(f["fix"]))
    if any(guide.needs_winre(f["fix"]) for f in r["findings"] if f["severity"] != "info"):
        lines.append(f"\n---------------- {_(guide.HOWTO_TITLE).upper()} ----------------")
        lines.extend("   " + l for l in guide.plain_steps(guide.winre_howto(r)))
    return "\n".join(lines)
