"""Manual repair instructions: the step model, the recovery-prompt how-to and the exportable guide.

A finding's `fix` is a list of step strings:
  * a marker (WINRE / LINUX / WINDOWS) says where the following steps are carried out;
  * every other string is one step. Text in `backticks` is something the user types; several
    lines inside one pair of backticks are typed one after the other.
"""

import html
import re

from .fsutil import human_size
from .i18n import _, N_, language

WINRE = "@winre"
LINUX = "@linux"
WINDOWS = "@windows"
CONTEXTS = {
    WINRE: N_("In the Windows recovery command prompt"),
    LINUX: N_("In a Linux terminal"),
    WINDOWS: N_("Later, once Windows runs again (administrator command prompt)"),
}


def parse_step(step):
    """'Do this:\\n`cmd`' -> [("text", "Do this:"), ("code", ["cmd"])]

    A backtick span that starts on its own line is a command block; a span inside a sentence stays part of
    the text (renderers show it as inline code, the backticks are kept as markers)."""
    parts = []
    segs = step.split("`")
    buf = ""
    for i, seg in enumerate(segs):
        if i % 2 == 0:
            buf += seg
            continue
        block = buf.endswith("\n") or "\n" in seg or (i == len(segs) - 2 and not buf.strip())
        if block:
            t = " ".join(buf.split())
            if t:
                parts.append(("text", t))
            buf = ""
            lines = [l.strip() for l in seg.split("\n") if l.strip()]
            if lines:
                parts.append(("code", lines))
        else:
            buf += "`" + seg + "`"
    t = " ".join(buf.split())
    if t and t not in (".", ",", ";"):
        parts.append(("text", t))
    return parts


def strip_inline(text):
    return text.replace("`", "")


def sections(fix):
    """Group steps by context marker -> [(context | None, [parsed step, ...]), ...]"""
    out = []
    ctx, steps = None, []
    for s in fix or []:
        if s in CONTEXTS:
            if steps:
                out.append((ctx, steps))
            ctx, steps = s, []
        else:
            p = parse_step(s)
            if p:
                steps.append(p)
    if steps:
        out.append((ctx, steps))
    return out


def needs_winre(fix):
    return WINRE in (fix or [])


def plain_steps(fix, bullet="{n}. ", code_prefix="      "):
    """Render steps as plain text lines (terminal report, clipboard, Markdown list)."""
    lines = []
    for ctx, steps in sections(fix):
        if ctx:
            lines.append(f"{_(CONTEXTS[ctx])}:")
        for n, parts in enumerate(steps, 1):
            first = True
            for kind, val in parts:
                if kind == "text":
                    lines.append((bullet.format(n=n) if first else " " * len(bullet.format(n=n))) + strip_inline(val))
                else:
                    if first:
                        lines.append(bullet.format(n=n).rstrip())
                    lines.extend(code_prefix + c for c in val)
                first = False
    return lines


def _target_hint(report):
    if not report:
        return "", ""
    t = report.get("target") or {}
    win = ""
    if t.get("size"):
        lab = t.get("label") if t.get("label") not in (None, "", "Basic data partition") else None
        size = human_size(t["size"])
        win = (_(t"Yours is the {size} NTFS volume labelled “{lab}”.") if lab else
               _(t"Yours is the {size} NTFS volume.")) + " "
    esp = ""
    bp = report.get("boot_partition") or {}
    for c in (report.get("evidence", {}).get("boot_partition", {}) or {}).get("candidates", []):
        if c.get("partition") == bp.get("name") and c.get("size"):
            size = human_size(c["size"])
            esp = _(t"Your EFI partition is the {size} FAT32 volume.") + " "
    return win, esp


def winre_howto(report=None):
    """Steps that get the user to a recovery command prompt with the right drive letters."""
    win, esp = _target_hint(report)
    return [
        _("Start the PC and choose Windows. After two failed starts in a row Windows opens “Automatic Repair” by "
          "itself; choose “Advanced options” there. If that screen never appears, boot from a Windows installation "
          "USB stick and choose “Repair your computer”."),
        _("Choose Troubleshoot → Advanced options → Command Prompt."),
        _("Drive letters are often different in the recovery environment. List the volumes:\n`diskpart\nlist vol\nexit`"),
        _("This guide calls the Windows volume C:.") + " " + win + _("Check the letter:\n`dir C:\\Windows`\n"
          "If that reports “File Not Found”, try D:, E: and so on, and use the letter that works instead of C: in "
          "every command."),
    ] + ([esp + _("Steps that need it tell you how to give it the letter S:.")] if esp else [])


HOWTO_TITLE = N_("Getting to the Windows recovery command prompt")


# ============================================================================ HTML guide
_CSS = """
:root { color-scheme: light dark; --fg:#1d1d20; --dim:#5e5c64; --bg:#fafafb; --card:#fff; --line:#deddda;
        --code:#f0f0f2; --crit:#c01c28; --warn:#9c6e03; --accent:#1a5fb4; }
@media (prefers-color-scheme: dark) { :root { --fg:#f2f2f4; --dim:#b0aeb6; --bg:#1e1e22; --card:#2a2a2f;
        --line:#45454b; --code:#18181b; --crit:#ff7b85; --warn:#f8c751; --accent:#78aeed; } }
* { box-sizing: border-box; }
body { font: 16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; color: var(--fg); background: var(--bg);
       margin: 0; padding: 20px 16px 60px; }
main { max-width: 760px; margin: 0 auto; }
h1 { font-size: 1.5rem; margin: 0 0 4px; } h2 { font-size: 1.15rem; margin: 0 0 6px; }
.sub { color: var(--dim); margin: 0 0 20px; }
section { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px;
          margin: 14px 0; }
.tag { display: inline-block; font-size: .75rem; font-weight: 700; padding: 1px 9px; border-radius: 99px;
       border: 1px solid currentColor; margin-bottom: 6px; }
.critical { color: var(--crit); } .warning { color: var(--warn); } .how { color: var(--accent); }
.why { color: var(--dim); margin: 0 0 10px; }
.ctx { font-weight: 700; font-size: .9rem; margin: 14px 0 4px; }
ol { padding-left: 1.4rem; margin: 6px 0; } li { margin: 8px 0; }
code { background: var(--code); border-radius: 4px; padding: 0 4px; font: 14px ui-monospace, monospace; }
pre { background: var(--code); border-radius: 8px; padding: 9px 12px; margin: 6px 0; overflow-x: auto;
      font: 14px/1.45 ui-monospace, "DejaVu Sans Mono", Consolas, monospace; white-space: pre; }
details { margin-top: 10px; color: var(--dim); } details pre { font-size: 12.5px; white-space: pre-wrap; }
footer { color: var(--dim); font-size: .85rem; margin-top: 26px; }
@media print { body { background: #fff; } section { break-inside: avoid; } }
"""


def _steps_html(fix):
    out = []
    for ctx, steps in sections(fix):
        if ctx:
            out.append(f'<p class="ctx">{html.escape(_(CONTEXTS[ctx]))}</p>')
        out.append("<ol>")
        for parts in steps:
            out.append("<li>")
            for kind, val in parts:
                if kind == "text":
                    out.append("<div>" + re.sub(r"`([^`]*)`", r"<code>\\1</code>", html.escape(val)) + "</div>")
                else:
                    out.append("<pre>" + html.escape("\n".join(val)) + "</pre>")
            out.append("</li>")
        out.append("</ol>")
    return "\n".join(out)


def guide_findings(report):
    """Findings that have manual steps, most important first."""
    return [f for f in report["findings"] if f["severity"] in ("critical", "warning") and f.get("fix")]


def to_html(report):
    """Self-contained repair guide (readable on a phone or printed) for use while Linux is not running."""
    e = html.escape
    w = report.get("windows") or {}
    t = report["target"]
    v = report["verdict"]
    name = " ".join(x for x in (w.get("DisplayName"), w.get("DisplayVersion")) if x) or "Windows"
    fs = guide_findings(report)
    out = [f"<!doctype html><html lang='{e(language())}'><head><meta charset='utf-8'>",
           "<meta name='viewport' content='width=device-width, initial-scale=1'>",
           f"<title>{e(_(t'Repair guide - {name}'))}</title><style>{_CSS}</style></head><body><main>",
           f"<h1>{e(_(t'Repair guide for {name}'))}</h1>",
           f"<p class='sub'>{e(t['device'])} · "
           + e(_(t"created {report['generated'][:16].replace('T', ' ')} UTC by BootRepair {report['version']}"))
           + "</p>",
           f"<section><h2>{e(v['headline'])}</h2><p class='why'>{e(v['detail'])}</p>"
           + (f"<p>{e(_('What you see on screen:'))} <b>{e(v['stopcode'])}</b></p>" if v.get("stopcode") else "")
           + "</section>"]
    if any(needs_winre(f["fix"]) for f in fs):
        out.append(f"<section><span class='tag how'>{e(_('BEFORE YOU START'))}</span><h2>{e(_(HOWTO_TITLE))}</h2>"
                   + _steps_html(winre_howto(report)) + "</section>")
    if not fs:
        out.append(f"<section><p>{e(_('No manual repair steps are needed.'))}</p></section>")
    for n, f in enumerate(fs, 1):
        out.append(f"<section><span class='tag {f['severity']}'>{e(_('STOPS WINDOWS') if f['severity'] == 'critical' else _('SHOULD BE FIXED'))}</span>"
                   f"<h2>{n}. {e(f['title'])}</h2><p class='why'>{e(f['why'])}</p>")
        out.append(_steps_html(f["fix"]))
        if f.get("evidence"):
            out.append(f"<details><summary>{e(_('Evidence'))}</summary><pre>"
                       + e("\n".join(str(x) for x in f["evidence"])) + "</pre></details>")
        out.append("</section>")
    out.append("<footer>" + e(_("Work through the sections from top to bottom and try to start Windows after each one. "
                                "Commands are typed exactly as shown, one line at a time, each followed by Enter."))
               + "</footer>")
    out.append("</main></body></html>")
    return "\n".join(out)
