"""GTK4 / libadwaita application entry point."""

import json
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # noqa: E402

from .i18n import _, set_language, language, LANGUAGES
from . import APP_ID, APP_NAME, __version__  # noqa: E402
from . import guide  # noqa: E402
from .report import to_markdown  # noqa: E402
from .ui import state  # noqa: E402
from .ui.finding_page import FindingPage  # noqa: E402
from .ui.guide_page import GuidePage, howto_dialog  # noqa: E402
from .ui.progress_page import ProgressPage  # noqa: E402
from .ui.widgets import copy_text  # noqa: E402
from .ui.repair import OutcomePage, open_repair_dialog  # noqa: E402
from .ui.results_page import ResultsPage  # noqa: E402
from .ui.runner import analyze_process, fix_process, undo_process, bootnext_process  # noqa: E402
from .ui.select_page import SelectPage  # noqa: E402


class Window(Adw.ApplicationWindow):
    def __init__(self, app, demo_report=None):
        super().__init__(application=app, title=APP_NAME, default_width=1020, default_height=820)
        self.set_size_request(360, 480)
        self.toasts = Adw.ToastOverlay()
        self.nav = Adw.NavigationView()
        self.toasts.set_child(self.nav)
        self.set_content(self.toasts)
        self.proc = None
        self.selection = None          # (partition dict, esp, key, events) of the last analysis
        self.report = None
        self.select = SelectPage(self.start)
        self.nav.add(self.select)
        for name, cb in (("reanalyse", lambda *__: self.reanalyse()), ("guide", lambda *__: self.show_guide()),
                         ("restart-windows", lambda *__: self.restart_into_windows()),
                         ("save-html", lambda *__: self.save_report("html")),
                         ("save-md", lambda *__: self.save_report("md")),
                         ("save-json", lambda *__: self.save_report("json")),
                         ("copy-report", lambda *__: self.copy_report())):
            a = Gio.SimpleAction.new(name, None)
            a.connect("activate", cb)
            self.add_action(a)
        if demo_report is not None:
            self.show_results(demo_report)
        self.connect("close-request", self._on_close)

    def rebuild(self):
        """Re-create the pages in the newly chosen language (reports keep the language they were made in)."""
        if self.proc is not None:
            return
        self.select = SelectPage(self.start)
        if self.report is not None:
            self.nav.replace([self.select, ResultsPage(self.report, self, self.new_analysis)])
        else:
            self.nav.replace([self.select])

    def toast(self, msg):
        self.toasts.add_toast(Adw.Toast(title=msg, timeout=3))

    def busy(self):
        if self.proc is not None:
            self.toast(_(t"Please wait - BootRepair is still working"))
            return True
        return False

    # ------------------------------------------------------------------ analysis
    def start(self, part, esp, key, events):
        if self.busy():
            return
        self.selection = (part, esp, key, events)
        self.progress = ProgressPage(_(t"Analysing /dev/{part['name']}"), self.cancel)
        self.nav.push(self.progress)
        self.proc = analyze_process(part["path"], esp, key, events, self._on_analysis_msg, self._on_analysis_done)
        self.proc.start()

    def reanalyse(self):
        if self.busy():
            return
        if self.selection:
            self.nav.pop_to_page(self.select)
            self.start(*self.selection)
        else:
            self.nav.pop_to_page(self.select)

    def cancel(self):
        if self.proc:
            self.proc.cancel()
            self.progress.set_log(_("Cancelling - unmounting…"))

    def _on_analysis_msg(self, msg):
        t = msg.get("type")
        if t == "steps":
            self.progress.set_description(_(t"Partitions are mounted read-only; nothing is written."))
            self.progress.set_steps(msg["steps"])
        elif t == "step":
            self.progress.update_step(msg["id"], msg["state"], msg.get("note", ""))
        elif t == "log":
            self.progress.set_log(msg["msg"])

    def _on_analysis_done(self, final, error, cancelled):
        self.proc = None
        if final is not None:
            self.show_results(final["report"])
        elif cancelled:
            self.nav.pop_to_page(self.select)
            self.toast(_(t"Analysis cancelled"))
        else:
            self.show_error(_("The analysis could not be completed"), error or _("Unknown error"))

    def show_results(self, report):
        self.report = report
        state.remember_report(report)
        page = ResultsPage(report, self, self.new_analysis)
        self.nav.replace([self.select, page])

    def new_analysis(self):
        self.nav.pop_to_page(self.select)

    # ------------------------------------------------------------------ detail pages
    def show_finding(self, finding):
        self.nav.push(FindingPage(finding, self))

    def show_guide(self):
        if self.report is not None:
            self.nav.push(GuidePage(self.report, self))

    def show_howto(self):
        howto_dialog(self.report, self).present(self)

    # ------------------------------------------------------------------ export
    def copy_report(self):
        if self.report is not None:
            copy_text(self, to_markdown(self.report))
            self.toast(_(t"Report copied"))

    def save_report(self, kind):
        if self.report is None:
            return
        r = self.report
        ext = {"html": "html", "md": "md", "json": "json"}[kind]
        name = (f"repair-guide-{r['target']['name']}.html" if kind == "html"
                else f"bootrepair-{r['target']['name']}.{ext}")
        d = Gtk.FileDialog(title=_(t"Save repair guide") if kind == "html" else _(t"Save report"), initial_name=name)

        def done(dlg, res):
            try:
                f = dlg.save_finish(res)
            except GLib.Error:
                return
            if kind == "html":
                data = guide.to_html(r)
            elif kind == "md":
                data = to_markdown(r)
            else:
                data = json.dumps(r, indent=2, default=str)
            try:
                with open(f.get_path(), "w") as fh:
                    fh.write(data)
                self.toast(_(t"Saved {f.get_basename()}"))
            except OSError as e:
                self.toast(_(t"Could not save: {e.strerror}"))
        d.save(self, None, done)

    # ------------------------------------------------------------------ restart into Windows
    def windows_boot_entry(self, report):
        nv = (report or {}).get("evidence", {}).get("nvram") or {}
        return nv.get("windows_entry")

    def restart_into_windows(self):
        num = self.windows_boot_entry(self.report)
        if not num or self.busy():
            return
        dlg = Adw.AlertDialog(
            heading=_(t"Restart into Windows?"),
            body=_(t"The computer restarts now and starts Windows Boot Manager once. The start after that uses "
                   t"the normal boot order again. Save your work in other apps first."))
        dlg.add_response("cancel", _(t"Cancel"))
        dlg.add_response("restart", _(t"Restart"))
        dlg.set_response_appearance("restart", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_close_response("cancel")

        def go(d, resp):
            if resp != "restart":
                return

            def done(final, error, cancelled):
                self.proc = None
                if final is None:
                    if not cancelled:
                        self.show_error(_("Could not set up the restart"), error or _("Unknown error"))
                    return
                try:
                    Gio.Subprocess.new(["systemctl", "reboot"], Gio.SubprocessFlags.NONE)
                except GLib.Error as e:
                    self.toast(_(t"Windows starts at the next restart ({e.message})"))
            self.proc = bootnext_process(num, lambda m: None, done)
            self.proc.start()
        dlg.connect("response", go)
        dlg.present(self)

    # ------------------------------------------------------------------ repair
    def open_repair(self, report, only=None):
        if self.busy():
            return
        open_repair_dialog(self, report, lambda acts: self.run_repair(report, acts), only=only)

    def run_repair(self, report, actions):
        if not actions or self.busy():
            return
        target = report["target"]["device"]
        boot = (report.get("boot_partition") or {}).get("device")
        self.progress = ProgressPage(_(t"Repairing {target}"), None, title=_("Repairing…"),
                                     description=_(t"Waiting for administrator authorisation…"))
        self.progress.set_steps([{"id": a["id"], "title": a["title"]} for a in actions])
        self.nav.push(self.progress)

        def msg(m):
            if m.get("type") == "fix":
                self.progress.set_description(_(t"Backing up and applying the selected repairs…"))
                self.progress.update_step(m["id"], m["state"], m.get("note", ""))
            elif m.get("type") == "log":
                self.progress.set_log(m["msg"])

        def done(final, error, cancelled):
            self.proc = None
            if final is None:
                self.show_error(_("The repair could not be completed"), error or _("Unknown error"))
                return
            res = final["result"]
            page = OutcomePage(_("Repair finished"), res["results"], res["backup"], self.reanalyse, self.run_undo,
                               on_restart=self.restart_into_windows if self.windows_boot_entry(report) else None)
            self.nav.replace([self.select, page])
        vol = report.get("evidence", {}).get("volume", {})
        state = {"hibernated": (vol.get("hiberfil_signature") or "").lower() in ("hibr", "wake"),
                 "dirty": bool((vol.get("ntfs_state") or {}).get("dirty"))}
        self.proc = fix_process(target, boot, actions, msg, done, state)
        self.proc.start()

    def run_undo(self, backup=None):
        if self.busy():
            return
        dlg = Adw.AlertDialog(heading=_(t"Undo repair?"),
                              body=(_("Restores every file and setting changed by this repair.") if backup else
                                    _("Restores every file and setting changed by the most recent repair."))
                              + " " + _("Firmware entries that were deleted cannot be re-created."))
        dlg.add_response("cancel", _(t"Cancel"))
        dlg.add_response("undo", _(t"Undo"))
        dlg.set_response_appearance("undo", Adw.ResponseAppearance.DESTRUCTIVE)
        dlg.set_close_response("cancel")

        def go(d, resp):
            if resp != "undo":
                return
            self.progress = ProgressPage(_("Restoring the original files"), None, title=_("Undoing…"))
            self.nav.push(self.progress)

            def done(final, error, cancelled):
                self.proc = None
                if final is None:
                    self.show_error(_("Undo failed"), error or _("Unknown error"))
                    return
                page = OutcomePage(_("Undo finished"), final["changes"], final["backup"], self.reanalyse,
                                   undo_mode=True)
                self.nav.replace([self.select, page])
            self.proc = undo_process(backup, lambda m: m.get("type") == "log" and self.progress.set_log(m["msg"]),
                                     done)
            self.proc.start()
        dlg.connect("response", go)
        dlg.present(self)

    # ------------------------------------------------------------------ errors
    def show_error(self, heading, text):
        page = Adw.NavigationPage(title=_(t"Error"), tag="error")
        tv = Adw.ToolbarView()
        tv.add_top_bar(Adw.HeaderBar())
        first, __, rest = text.partition("\n\n")
        sp = Adw.StatusPage(icon_name="dialog-error-symbolic", title=heading,
                            description=GLib.markup_escape_text(first))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, halign=Gtk.Align.CENTER)
        if rest:
            exp = Gtk.Expander(label=_(t"Details"))
            l = Gtk.Label(label=rest, selectable=True, wrap=True, xalign=0)
            l.add_css_class("mono")
            exp.set_child(l)
            box.append(exp)
        back = Gtk.Button(label=_(t"Back"), css_classes=["pill"], halign=Gtk.Align.CENTER)
        back.connect("clicked", lambda *__: self.nav.pop_to_page(self.select))
        box.append(back)
        sp.set_child(box)
        tv.set_content(sp)
        page.set_child(tv)
        self.nav.replace([self.select, page])

    def _on_close(self, *__):
        if self.proc:
            self.proc.cancel()   # analysis helper unmounts on stdin EOF; repairs always run to completion
        return False


class App(Adw.Application):
    def __init__(self, demo_report=None):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.demo_report = demo_report
        pref = state.load().get("language", "auto")
        set_language(pref)
        for name, cb in (("about", self._about), ("undo", self._undo)):
            a = Gio.SimpleAction.new(name, None)
            a.connect("activate", cb)
            self.add_action(a)
        lang = Gio.SimpleAction.new_stateful("language", GLib.VariantType.new("s"), GLib.Variant("s", pref))
        lang.connect("activate", self._on_language)
        self.add_action(lang)

    def _on_language(self, action, value):
        pref = value.get_string()
        action.set_state(value)
        d = state.load()
        d["language"] = pref
        state.save(d)
        set_language(pref)
        win = self.props.active_window
        if win is not None:
            win.rebuild()

    def do_startup(self):
        Adw.Application.do_startup(self)
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        dev_icons = Path(__file__).resolve().parent.parent / "data" / "icons"
        if dev_icons.is_dir():          # running from the source tree
            theme.add_search_path(str(dev_icons))
        Gtk.Window.set_default_icon_name(APP_ID)
        css = Gtk.CssProvider()
        css.load_from_path(str(Path(__file__).parent / "ui" / "style.css"))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        win = self.props.active_window or Window(self, self.demo_report)
        win.present()

    def _undo(self, *__):
        self.props.active_window.run_undo(None)

    def _about(self, *__):
        d = Adw.AboutDialog(application_name=APP_NAME, version=__version__,
                            application_icon=APP_ID, website="https://github.com/Bot320/bootrepair",
                            comments=_(t"Diagnoses why Windows does not start and repairs it - analysis is read-only, "
                                       t"every repair is backed up and can be undone."),
                            license_type=Gtk.License.GPL_3_0)
        d.present(self.props.active_window)


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    demo = None
    if "--demo" in argv:
        i = argv.index("--demo")
        with open(argv[i + 1]) as f:
            demo = json.load(f)
        del argv[i:i + 2]
    if "--version" in argv:
        print(__version__)
        return 0
    return App(demo).run(argv[:1])


if __name__ == "__main__":
    sys.exit(main())
