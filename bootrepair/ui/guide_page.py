"""The manual repair guide: every problem's steps in order, plus how to reach the recovery prompt."""

from gi.repository import Adw, GLib, Gtk

from ..i18n import _
from .. import guide
from .widgets import SEV_ICON, label, steps_widget, clamp_page


def howto_dialog(report, window):
    dlg = Adw.Dialog(title=_(t"Recovery command prompt"), content_width=620, content_height=560)
    tv = Adw.ToolbarView()
    tv.add_top_bar(Adw.HeaderBar())
    col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
    col.append(label(guide.HOWTO_TITLE, "title-3"))
    col.append(label(_(t"Windows has its own repair environment. All steps marked “In the Windows recovery command "
                       t"prompt” are typed there."), "dim-label"))
    col.append(steps_widget(guide.winre_howto(report), on_copied=lambda: window.toast(_("Copied"))))
    tv.set_content(clamp_page(col, 640))
    dlg.set_child(tv)
    return dlg


class GuidePage(Adw.NavigationPage):
    def __init__(self, report, window):
        super().__init__(title=_(t"Repair guide"), tag="guide")
        self.report = report
        self.window = window
        tv = Adw.ToolbarView()
        hb = Adw.HeaderBar()
        save = Gtk.Button(icon_name="document-save-symbolic",
                          tooltip_text=_(t"Save as a web page (to read on your phone while repairing)"))
        save.connect("clicked", lambda *__: window.save_report("html"))
        hb.pack_end(save)
        cp = Gtk.Button(icon_name="edit-copy-symbolic", tooltip_text=_(t"Copy the whole guide as text"))
        cp.connect("clicked", lambda *__: self._copy())
        hb.pack_end(cp)
        tv.add_top_bar(hb)

        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        fs = guide.guide_findings(report)
        intro = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        intro.append(label(_(t"Repair guide"), "title-1"))
        intro.append(label(_(t"Work through the problems from top to bottom and try to start Windows after each one. "
                             t"Linux is not running while you repair Windows, so save this guide as a web page "
                             t"(save button above) and open it on your phone."), "dim-label"))
        col.append(intro)

        if any(guide.needs_winre(f["fix"]) for f in fs):
            col.append(self._section(guide.HOWTO_TITLE, None, guide.winre_howto(report), _("Before you start")))
        if not fs:
            col.append(label(_(t"Nothing needs to be repaired by hand."), "dim-label"))
        for n, f in enumerate(fs, 1):
            col.append(self._section(f"{n}. {f['title']}", f, f["fix"],
                                     _("Stops Windows") if f["severity"] == "critical" else _("Should be fixed")))
        tv.set_content(clamp_page(col))
        self.set_child(tv)

    def _section(self, title, f, fix, kicker):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["card", "guide-card"])
        k = Gtk.Box(spacing=6)
        if f:
            k.append(Gtk.Image(icon_name=SEV_ICON[f["severity"]], css_classes=[f"sev-icon-{f['severity']}"]))
        k.append(label(kicker.upper(), "caption-heading", "dim-label", wrap=False))
        box.append(k)
        box.append(label(title, "title-4", selectable=True))
        if f and f.get("why"):
            box.append(label(f["why"], "dim-label"))
        box.append(steps_widget(fix, on_howto=None if f is None else self.window.show_howto,
                                on_copied=lambda: self.window.toast(_("Copied"))))
        if f and f.get("actions"):
            b = Gtk.Button(label=_(t"Let BootRepair do this instead…"), halign=Gtk.Align.START,
                           css_classes=["pill"], margin_top=4)
            b.connect("clicked", lambda *__: self.window.open_repair(self.report, only=[a["id"] for a in f["actions"]]))
            box.append(b)
        return box

    def _copy(self):
        lines = [_("REPAIR GUIDE"), ""]
        fs = guide.guide_findings(self.report)
        if any(guide.needs_winre(f["fix"]) for f in fs):
            lines += [guide.HOWTO_TITLE.upper(), *guide.plain_steps(guide.winre_howto(self.report)), ""]
        for n, f in enumerate(fs, 1):
            lines += [f"{n}. {f['title'].upper()}", f["why"], "", *guide.plain_steps(f["fix"]), ""]
        from .widgets import copy_text
        copy_text(self.window, "\n".join(lines))
        self.window.toast(_(t"Guide copied"))
