"""Detail page for one finding: what is wrong, one-click repair, manual repair, evidence."""

from gi.repository import Adw, Gtk

from ..i18n import _
from ..model import STAGE_LABELS
from .widgets import (SEV_ICON, SEV_WORD, REPAIR_ICON, label, tag, steps_widget, code_block, clamp_page,
                      inline_markup)
from .repair import risk_tag


class FindingPage(Adw.NavigationPage):
    def __init__(self, finding, window):
        f = finding
        super().__init__(title=_(SEV_WORD[f["severity"]]))
        self.window = window
        tv = Adw.ToolbarView()
        tv.add_top_bar(Adw.HeaderBar())
        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)

        # ------------------------------------------------------------- header
        head = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        top = Gtk.Box(spacing=8)
        top.append(Gtk.Image(icon_name=SEV_ICON[f["severity"]], css_classes=[f"sev-icon-{f['severity']}"]))
        top.append(label(_(SEV_WORD[f["severity"]]), "caption-heading", f"sev-text-{f['severity']}", wrap=False))
        top.append(label("·  " + _(STAGE_LABELS.get(f["stage"], f["stage"])), "caption", "dim-label", wrap=False))
        head.append(top)
        head.append(label(f["title"], "title-2", selectable=True))
        if f.get("stopcode"):
            row = Gtk.Box(spacing=8)
            row.append(label(_("On screen:"), "dim-label", wrap=False))
            row.append(tag(f["stopcode"], "tag-stop"))
            head.append(row)
        if f.get("why"):
            head.append(label(f["why"], selectable=True))
        col.append(head)

        # ------------------------------------------------------------- one-click repair
        if f.get("actions"):
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["card", "repair-card"])
            h = Gtk.Box(spacing=8)
            h.append(Gtk.Image(icon_name=REPAIR_ICON))
            h.append(label(_(t"BootRepair can fix this"), "heading"))
            card.append(h)
            for a in f["actions"]:
                r = Gtk.Box(spacing=10)
                t = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, hexpand=True)
                t.append(label(a["title"]))
                t.append(label("\n".join(a["changes"]), "caption", "dim-label", selectable=True))
                r.append(t)
                r.append(risk_tag(a["risk"]))
                card.append(r)
            btn = Gtk.Button(label=_("Repair…"), halign=Gtk.Align.START, css_classes=["suggested-action", "pill"])
            btn.connect("clicked", lambda *__: window.open_repair(window.report, only=[a["id"] for a in f["actions"]]))
            card.append(btn)
            card.append(label(_(t"Every changed file is backed up first and can be restored with “Undo last repair”."),
                              "caption", "dim-label"))
            col.append(card)

        # ------------------------------------------------------------- manual repair
        if f.get("fix"):
            sec = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            sec.append(label(_(t"Repair it yourself") if f.get("actions") else _(t"How to fix"), "title-4"))
            sec.append(steps_widget(f["fix"], on_howto=window.show_howto,
                                    on_copied=lambda: window.toast(_("Copied"))))
            col.append(sec)

        # ------------------------------------------------------------- evidence
        if f.get("evidence"):
            exp = Gtk.Expander(label=_("Evidence"), css_classes=["evidence-expander"])
            exp.set_child(code_block([str(e) for e in f["evidence"]], lambda: window.toast(_("Copied"))))
            exp.get_child().set_margin_top(8)
            col.append(exp)

        tv.set_content(clamp_page(col))
        self.set_child(tv)
