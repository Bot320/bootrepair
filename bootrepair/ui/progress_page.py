"""Live progress of an analysis or a repair run."""

from gi.repository import Adw, Gtk

from ..i18n import _
from . import xrow


class ProgressPage(Adw.NavigationPage):
    def __init__(self, heading, on_cancel=None, title=None, description=None):
        title = title or _("Analysing…")
        description = description or _("Waiting for administrator authorisation…")
        super().__init__(title=title, tag="progress", can_pop=False)
        self.rows = {}
        tv = Adw.ToolbarView()
        hb = Adw.HeaderBar(show_back_button=False)
        if on_cancel:
            self.cancel_btn = Gtk.Button(label=_(t"Cancel"))
            self.cancel_btn.connect("clicked", lambda *__: (self.cancel_btn.set_sensitive(False), on_cancel()))
            hb.pack_start(self.cancel_btn)
        tv.add_top_bar(hb)

        page = Adw.PreferencesPage()
        self.head = Adw.PreferencesGroup(title=heading, description=description)
        page.add(self.head)
        self.steps_group = Adw.PreferencesGroup()
        page.add(self.steps_group)
        self.log = Gtk.Label(xalign=0, wrap=True, css_classes=["dim-label", "caption"], margin_top=6)
        foot = Adw.PreferencesGroup()
        foot.add(self.log)
        page.add(foot)
        tv.set_content(page)
        self.set_child(tv)

    def set_description(self, text):
        self.head.set_description(text)

    def set_steps(self, steps):
        for s in steps:
            row = xrow(Adw.ActionRow, title=s["title"])
            stack = Gtk.Stack()
            stack.add_named(Gtk.Image(icon_name="content-loading-symbolic", css_classes=["dim-label"]), "pending")
            stack.add_named(Adw.Spinner(), "running")
            stack.add_named(Gtk.Image(icon_name="object-select-symbolic", css_classes=["success"]), "done")
            stack.add_named(Gtk.Image(icon_name="action-unavailable-symbolic", css_classes=["dim-label"]), "skipped")
            stack.add_named(Gtk.Image(icon_name="dialog-warning-symbolic", css_classes=["warning"]), "failed")
            stack.set_visible_child_name("pending")
            row.add_prefix(stack)
            self.steps_group.add(row)
            self.rows[s["id"]] = (row, stack)

    def update_step(self, sid, state, note=""):
        if sid not in self.rows:
            return
        row, stack = self.rows[sid]
        stack.set_visible_child_name(state if state in ("running", "done", "skipped", "failed") else "pending")
        if note:
            row.set_subtitle(note)

    def set_log(self, msg):
        self.log.set_label(msg)
