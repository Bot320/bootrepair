"""Repair UI: confirmation checklist, and the result page after repairs / undo."""

from gi.repository import Adw, Gtk

from ..i18n import _, N_
from .widgets import REPAIR_ICON  # noqa: F401  (re-exported)

from . import xrow

RISK_TEXT = {"low": N_("low risk"), "medium": N_("medium risk"), "high": N_("high risk")}


def collect_actions(report):
    """[(action, finding)] in report order, de-duplicated."""
    out, seen = [], set()
    for f in report["findings"]:
        for a in f.get("actions") or []:
            if a["id"] not in seen:
                seen.add(a["id"])
                out.append((a, f))
    return out


def risk_tag(risk):
    l = Gtk.Label(label=_(RISK_TEXT.get(risk, risk)), valign=Gtk.Align.CENTER)
    l.add_css_class("tag")
    l.add_css_class(f"risk-{risk}")
    return l


def build_repair_dialog(report, on_confirm, only=None):
    """Checklist of repairs (Adw.Dialog). `only`: action ids to show (single-finding repair)."""
    items = collect_actions(report)
    if only:
        items = [(a, f) for a, f in items if a["id"] in only]
    if not items:
        return None
    dlg = Adw.Dialog(title=_(t"Repair automatically"), content_width=680, content_height=600)
    tv = Adw.ToolbarView()
    hb = Adw.HeaderBar(show_end_title_buttons=False, show_start_title_buttons=False)
    cancel = Gtk.Button(label=_(t"Cancel"))
    cancel.connect("clicked", lambda *__: dlg.close())
    hb.pack_start(cancel)
    go = Gtk.Button(css_classes=["destructive-action"])
    hb.pack_end(go)
    tv.add_top_bar(hb)

    page = Adw.PreferencesPage()
    intro = Adw.PreferencesGroup(
        description=_(t"BootRepair writes to your disk for these repairs. Every file is backed up first, and "
                      t"\"Undo last repair\" in the menu restores it byte for byte. Select what to do:"))
    page.add(intro)
    grp = Adw.PreferencesGroup()
    checks = []
    for a, f in items:
        row = xrow(Adw.ActionRow, title=a["title"], subtitle="\n".join(a["changes"]))
        row.set_subtitle_lines(0)
        cb = Gtk.CheckButton(valign=Gtk.Align.CENTER)
        cb.set_active(bool(only) or f["severity"] in ("critical", "warning"))
        row.add_prefix(cb)
        row.set_activatable_widget(cb)
        row.add_suffix(risk_tag(a["risk"]))
        row.set_tooltip_text(_(t"Fixes: {f['title']}"))
        grp.add(row)
        checks.append((cb, a))
    page.add(grp)
    note = Adw.PreferencesGroup(description=_(t"Repairs need the Windows volume to be closed cleanly. If it is "
                                              t"hibernated or marked dirty, BootRepair refuses to write to it."))
    page.add(note)
    tv.set_content(page)
    dlg.set_child(tv)

    def update(*__):
        n = sum(cb.get_active() for cb, __ in checks)
        go.set_label(_(t"Repair ({n})") if n else _(t"Repair"))
        go.set_sensitive(n > 0)
    for cb, __ in checks:
        cb.connect("toggled", update)
    update()

    def confirm(*__):
        sel = [a for cb, a in checks if cb.get_active()]
        dlg.close()
        on_confirm(sel)
    go.connect("clicked", confirm)
    return dlg


def open_repair_dialog(parent, report, on_confirm, only=None):
    dlg = build_repair_dialog(report, on_confirm, only)
    if dlg is not None:
        dlg.present(parent)


class OutcomePage(Adw.NavigationPage):
    """Shown after repairs or an undo."""

    def __init__(self, title, results, backup, on_reanalyse, on_undo=None, undo_mode=False, on_restart=None):
        super().__init__(title=title, tag="outcome")
        tv = Adw.ToolbarView()
        tv.add_top_bar(Adw.HeaderBar(show_back_button=False))
        page = Adw.PreferencesPage()
        ok = all(r.get("ok", True) if isinstance(r, dict) else True for r in results)
        head = Adw.PreferencesGroup()
        sp = Adw.StatusPage(icon_name="object-select-symbolic" if ok else "dialog-warning-symbolic",
                            title=(_(t"Undo complete") if undo_mode else _(t"Repairs applied")) if ok
                            else _(t"Some repairs failed"),
                            description=(_(t"The original files have been restored.") if undo_mode else
                                         _(t"Run the analysis again to confirm, then try starting Windows. "
                                           t"If it still fails, the new report shows what is left.")))
        sp.add_css_class("compact")
        head.add(sp)
        page.add(head)
        g = Adw.PreferencesGroup(title=_(t"What was done"))
        for r in results:
            if undo_mode:
                row = xrow(Adw.ActionRow, title=r)
                row.add_prefix(Gtk.Image(icon_name="edit-undo-symbolic"))
            else:
                row = xrow(Adw.ExpanderRow, title=r["title"],
                           subtitle=_("done") if r["ok"] else _(t"failed: {r.get('error', '')}"))
                row.add_prefix(Gtk.Image(icon_name="object-select-symbolic" if r["ok"] else "dialog-error-symbolic",
                                         css_classes=["success" if r["ok"] else "error"]))
                text = "\n".join(str(c) for c in (r.get("changes") or [r.get("error", "")]))
                l = Gtk.Label(label=text, xalign=0, wrap=True, selectable=True, margin_start=12, margin_end=12,
                              margin_top=8, margin_bottom=10, css_classes=["mono"])
                lr = Gtk.ListBoxRow(activatable=False)
                lr.set_child(l)
                row.add_row(lr)
                row.set_expanded(not r["ok"])
            g.add(row)
        page.add(g)
        if backup:
            bg = Adw.PreferencesGroup(title=_("Backup"))
            br = xrow(Adw.ActionRow, title=_(t"Original files saved in"), subtitle=backup)
            br.set_subtitle_selectable(True)
            bg.add(br)
            page.add(bg)
        btns = Gtk.Box(spacing=12, halign=Gtk.Align.CENTER, margin_top=12, margin_bottom=24)
        again = Gtk.Button(label=_(t"Analyse again"), css_classes=["suggested-action", "pill"])
        again.connect("clicked", lambda *__: on_reanalyse())
        btns.append(again)
        if on_restart and not undo_mode and ok:
            rs = Gtk.Button(label=_(t"Restart into Windows"), css_classes=["pill"])
            rs.connect("clicked", lambda *__: on_restart())
            btns.append(rs)
        if on_undo and not undo_mode:
            u = Gtk.Button(label=_(t"Undo these repairs"), css_classes=["pill"])
            u.connect("clicked", lambda *__: on_undo(backup))
            btns.append(u)
        fg = Adw.PreferencesGroup()
        fg.add(btns)
        page.add(fg)
        tv.set_content(page)
        self.set_child(tv)
