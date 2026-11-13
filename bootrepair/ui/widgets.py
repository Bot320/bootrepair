"""Small reusable widgets: labels, tags, copyable command blocks, instruction steps, the boot-chain strip."""

import re

from gi.repository import Adw, Gdk, GLib, Gtk, Pango

from ..i18n import _, N_
from .. import guide

SEV_ICON = {"critical": "dialog-error-symbolic", "warning": "dialog-warning-symbolic",
            "info": "dialog-information-symbolic"}
SEV_WORD = {"critical": N_("Stops Windows"), "warning": N_("Should be fixed"), "info": N_("Note")}
STAGE_SHORT = {"disk": N_("Disk"), "bootmgr": N_("Boot manager"), "bcd": N_("Boot config"),
               "winload": N_("Loader"), "kernel": N_("Kernel"), "session": N_("Services"), "logon": N_("Logon")}
STATUS_ICON = {"ok": "object-select-symbolic", "warn": "dialog-warning-symbolic", "fail": "dialog-error-symbolic",
               "unknown": "dialog-question-symbolic"}
CONTEXT_ICON = {guide.WINRE: "utilities-terminal-symbolic", guide.LINUX: "utilities-terminal-symbolic",
                guide.WINDOWS: "computer-symbolic"}
REPAIR_ICON = "applications-engineering-symbolic"


def label(text, *css, wrap=True, selectable=False, xalign=0.0, markup=False):
    l = Gtk.Label(xalign=xalign, wrap=wrap, selectable=selectable)
    if markup:
        l.set_markup(text)
    else:
        l.set_text(text)
    l.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    if selectable:
        l.set_focusable(False)      # selectable by mouse, but never auto-focused (would highlight everything)
    for c in css:
        l.add_css_class(c)
    return l


def inline_markup(text):
    """Plain text with `inline code` -> Pango markup."""
    esc = GLib.markup_escape_text(text)
    return re.sub(r"`([^`]*)`", r"<tt>\1</tt>", esc)


def copy_text(widget, text):
    widget.get_clipboard().set_content(Gdk.ContentProvider.new_for_value(text))


def tag(text, css):
    l = Gtk.Label(label=text, valign=Gtk.Align.CENTER)
    l.add_css_class("tag")
    l.add_css_class(css)
    return l


def heading(text):
    return label(text, "heading", wrap=False)


def code_block(lines, on_copied=None):
    """Monospace block with a copy button."""
    text = "\n".join(lines)
    box = Gtk.Box(spacing=6, css_classes=["code-block"])
    l = Gtk.Label(label=text, xalign=0, selectable=True, hexpand=True, wrap=True,
                  wrap_mode=Pango.WrapMode.CHAR, css_classes=["mono"], focusable=False)
    box.append(l)
    b = Gtk.Button(icon_name="edit-copy-symbolic", valign=Gtk.Align.START, tooltip_text=_(t"Copy"),
                   css_classes=["flat", "circular"])

    def copy(btn):
        copy_text(btn, text)
        if on_copied:
            on_copied()
    b.connect("clicked", copy)
    box.append(b)
    return box


def steps_widget(fix, on_howto=None, on_copied=None):
    """Numbered instructions grouped by where they are carried out."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    for ctx, steps in guide.sections(fix):
        if ctx:
            hdr = Gtk.Box(spacing=8, margin_top=4)
            hdr.append(Gtk.Image(icon_name=CONTEXT_ICON[ctx], css_classes=["dim-label"]))
            hdr.append(label(_(guide.CONTEXTS[ctx]), "heading", wrap=True))
            if ctx == guide.WINRE and on_howto:
                link = Gtk.Button(label=_(t"How do I get there?"), css_classes=["flat", "link-button"],
                                  halign=Gtk.Align.END, hexpand=True, valign=Gtk.Align.CENTER)
                link.connect("clicked", lambda *__: on_howto())
                hdr.append(link)
            outer.append(hdr)
        for n, parts in enumerate(steps, 1):
            row = Gtk.Box(spacing=12)
            num = Gtk.Label(label=str(n), valign=Gtk.Align.START, css_classes=["step-num"])
            row.append(num)
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, hexpand=True)
            for kind, val in parts:
                if kind == "text":
                    col.append(label(inline_markup(val), markup=True, selectable=True))
                else:
                    col.append(code_block(val, on_copied))
            row.append(col)
            outer.append(row)
    return outer


def chain_strip(stages):
    """Seven compact boot stages in one row; the first failing one stands out."""
    box = Gtk.Box(homogeneous=True, spacing=4, css_classes=["chain"])
    for s in stages:
        seg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["chain-seg", f"chain-{s['status']}"])
        bar = Gtk.Box(css_classes=["chain-bar"])
        seg.append(bar)
        lab = Gtk.Box(spacing=4, halign=Gtk.Align.CENTER)
        if s["status"] != "ok":
            lab.append(Gtk.Image(icon_name=STATUS_ICON[s["status"]], pixel_size=12))
        lab.append(label(_(STAGE_SHORT.get(s["id"], s["label"])), "caption", wrap=True, xalign=0.5))
        seg.append(lab)
        tip = f"{s['label']}\n{s['description']}"
        if s["critical"] or s["warning"]:
            tip += "\n\n" + _(t"{s['critical']} critical, {s['warning']} warning(s)")
        if s["status"] == "unknown":
            tip += "\n\n" + _("Not analysed (the Windows volume was not accessible).")
        seg.set_tooltip_text(tip)
        box.append(seg)
    return box


def nav_row(title, subtitle, icon=None, icon_css=None, on_activate=None, suffix=None):
    from . import xrow
    row = xrow(Adw.ActionRow, title=title, subtitle=subtitle)
    row.set_title_lines(2)
    row.set_subtitle_lines(2)
    if icon:
        im = Gtk.Image(icon_name=icon)
        if icon_css:
            im.add_css_class(icon_css)
        row.add_prefix(im)
    if suffix is not None:
        row.add_suffix(suffix)
    if on_activate:
        row.add_suffix(Gtk.Image(icon_name="go-next-symbolic"))
        row.set_activatable(True)
        row.connect("activated", lambda *__: on_activate())
    return row


def clamp_page(child, maximum=760):
    """Scrollable, centred content column (for pages that are not PreferencesPages)."""
    sw = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, vexpand=True)
    clamp = Adw.Clamp(maximum_size=maximum, tightening_threshold=600, margin_top=18, margin_bottom=30,
                      margin_start=16, margin_end=16)
    clamp.set_child(child)
    sw.set_child(clamp)
    return sw
