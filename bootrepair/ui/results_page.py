"""Results: a short verdict, where startup stops, the problems (each opens a detail page), and the raw evidence."""

from gi.repository import Adw, Gio, Gtk

from ..i18n import _, N_
from . import xrow
from .. import guide
from ..fsutil import human_size
from .repair import collect_actions
from .widgets import (SEV_ICON, REPAIR_ICON, STATUS_ICON, label, chain_strip, nav_row)

VERDICT_ICON = {"fail": "dialog-error-symbolic", "warn": "dialog-warning-symbolic", "ok": "object-select-symbolic",
                "incomplete": "dialog-question-symbolic"}


class ResultsPage(Adw.NavigationPage):
    def __init__(self, report, window, on_new):
        super().__init__(title=_("Diagnosis"), tag="results")
        self.report = report
        self.window = window
        tv = Adw.ToolbarView()
        hb = Adw.HeaderBar(show_back_button=False)
        new = Gtk.Button(icon_name="go-previous-symbolic", tooltip_text=_(t"Choose another partition"))
        new.connect("clicked", lambda *__: on_new())
        hb.pack_start(new)
        stack = Adw.ViewStack()
        hb.set_title_widget(Adw.ViewSwitcher(stack=stack, policy=Adw.ViewSwitcherPolicy.WIDE))

        menu = Gio.Menu()
        sec = Gio.Menu()
        sec.append(_(t"Analyse again"), "win.reanalyse")
        sec.append(_(t"Repair guide"), "win.guide")
        if window.windows_boot_entry(report):
            sec.append(_(t"Restart into Windows…"), "win.restart-windows")
        menu.append_section(None, sec)
        sec = Gio.Menu()
        sec.append(_(t"Save repair guide as web page…"), "win.save-html")
        sec.append(_(t"Save report as Markdown…"), "win.save-md")
        sec.append(_(t"Save report as JSON…"), "win.save-json")
        sec.append(_(t"Copy report"), "win.copy-report")
        menu.append_section(None, sec)
        sec = Gio.Menu()
        sec.append(_(t"Undo last repair…"), "app.undo")
        sec.append(_(t"About BootRepair"), "app.about")
        menu.append_section(None, sec)
        hb.pack_end(Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu, tooltip_text=_(t"Menu"),
                                   primary=True))
        tv.add_top_bar(hb)

        stack.add_titled_with_icon(self._diagnosis(), "diagnosis", _("Diagnosis"), "system-search-symbolic")
        stack.add_titled_with_icon(self._evidence(), "evidence", _("Evidence"), "view-list-symbolic")
        tv.add_bottom_bar(Adw.ViewSwitcherBar(stack=stack))
        tv.set_content(stack)
        self.set_child(tv)

    # ================================================================== diagnosis
    def _diagnosis(self):
        r = self.report
        v = r["verdict"]
        page = Adw.PreferencesPage()
        findings = r["findings"]
        by_id = {f.get("id"): f for f in findings}

        # ------------------------------------------------------------ verdict
        g = Adw.PreferencesGroup()
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["verdict-card", f"verdict-{v['status']}"])
        top = Gtk.Box(spacing=14)
        icon = Gtk.Image(icon_name=VERDICT_ICON.get(v["status"], "dialog-question-symbolic"), pixel_size=40,
                         valign=Gtk.Align.START, css_classes=["verdict-icon"])
        top.append(icon)
        txt = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, hexpand=True)
        txt.append(label(v.get("title") or v["headline"], "title-2"))
        if v.get("cause"):
            txt.append(label(v["cause"], "heading", selectable=True))
        if v.get("stopcode"):
            txt.append(label(_(t"On screen: {v['stopcode']}"), "caption", "dim-label", selectable=True))
        top.append(txt)
        card.append(top)

        btns = Gtk.Box(spacing=8, margin_top=4)
        acts = collect_actions(r)
        important = [a for a, f in acts if f["severity"] in ("critical", "warning")]
        if acts:
            b = Gtk.Button(css_classes=["suggested-action", "pill"])
            bc = Gtk.Box(spacing=8)
            bc.append(Gtk.Image(icon_name=REPAIR_ICON))
            n = len(important) or len(acts)
            bc.append(Gtk.Label(label=_(t"Repair automatically ({n})") if n > 1 else _(t"Repair automatically")))
            b.set_child(bc)
            b.connect("clicked", lambda *__: self.window.open_repair(r))
            btns.append(b)
        if guide.guide_findings(r):
            b = Gtk.Button(label=_(t"Repair guide"), css_classes=["pill"])
            b.connect("clicked", lambda *__: self.window.show_guide())
            btns.append(b)
        if v.get("finding") is not None and v["finding"] in by_id:
            b = Gtk.Button(label=_(t"Details"), css_classes=["pill", "flat"])
            b.connect("clicked", lambda *__: self.window.show_finding(by_id[v["finding"]]))
            btns.append(b)
        if btns.get_first_child() is not None:
            card.append(btns)
        g.add(card)
        page.add(g)

        # ------------------------------------------------------------ boot chain
        chain = Adw.PreferencesGroup(title=_(t"Where startup stops"))
        chain.add(chain_strip(r["stages"]))
        page.add(chain)

        # ------------------------------------------------------------ problems
        problems = [f for f in findings if f["severity"] in ("critical", "warning")]
        notes = [f for f in findings if f["severity"] == "info"]
        if problems:
            pg = Adw.PreferencesGroup(title=_("Problems"),
                                      description=_(t"In the order they should be fixed. Open one for the explanation, "
                                                    t"the evidence and the repair."))
            for f in problems:
                pg.add(self._row(f))
            page.add(pg)
        if notes:
            ng = Adw.PreferencesGroup()
            exp = xrow(Adw.ExpanderRow, title=_(t"{len(notes)} notes") if len(notes) != 1 else _("1 note"),
                       subtitle=_(t"Background information - nothing here stops Windows"))
            exp.add_prefix(Gtk.Image(icon_name=SEV_ICON["info"], css_classes=["sev-icon-info"]))
            for f in notes:
                exp.add_row(self._row(f, icon=False))
            ng.add(exp)
            page.add(ng)

        # ------------------------------------------------------------ installation
        page.add(self._installation())
        return page

    def _row(self, f, icon=True):
        sub = f["why"].split(". ")[0].rstrip(".") + "." if f.get("why") else ""
        suffix = None
        if f.get("actions"):
            suffix = Gtk.Image(icon_name=REPAIR_ICON, tooltip_text=_(t"BootRepair can fix this"), css_classes=["accent"])
        return nav_row(f["title"], sub, SEV_ICON[f["severity"]] if icon else None, f"sev-icon-{f['severity']}",
                       lambda f=f: self.window.show_finding(f), suffix)

    def _installation(self):
        r = self.report
        t = r["target"]
        w = r.get("windows") or {}
        g = Adw.PreferencesGroup()
        name = " ".join(x for x in (w.get("DisplayName"), w.get("DisplayVersion")) if x) or "Windows"
        exp = xrow(Adw.ExpanderRow, title=name,
                   subtitle=f"{t['device']} · {human_size(t['size'])}" + (" · " + _(t"build {w['Build']}") if w.get("Build") else ""))
        exp.add_prefix(Gtk.Image(icon_name="computer-symbolic"))
        facts = []
        if w.get("ComputerName"):
            facts.append((_("Computer name"), w["ComputerName"]))
        if w.get("InstallDate"):
            facts.append((_("Installed"), w["InstallDate"]))
        facts.append((_("Disk"), f"{t['disk']} · {t.get('disk_model') or '?'} · {t.get('controller') or '?'}"))
        if r.get("boot_partition"):
            facts.append((_("Boot partition"), f"{r['boot_partition']['device']} · {(r.get('boot_mode') or '?').upper()}"))
        es = r.get("evidence", {}).get("events", {}).get("summary", {})
        if es.get("last_boot"):
            facts.append((_("Last successful start"), es["last_boot"][:16].replace("T", " ") + " UTC"))
        sb = r.get("evidence", {}).get("secure_boot")
        if sb and sb != "unknown":
            facts.append((_("Secure Boot (this PC)"), _({"enabled": N_("enabled"), "disabled": N_("disabled")}.get(sb, sb))))
        for k, val in facts:
            row = xrow(Adw.ActionRow, title=k, subtitle=val)
            row.add_css_class("property")
            row.set_subtitle_selectable(True)
            exp.add_row(row)
        g.add(exp)
        return g

    # ================================================================== evidence
    def _evidence(self):
        r = self.report
        ev = r.get("evidence", {})
        page = Adw.PreferencesPage()

        bcd = ev.get("bcd")
        if bcd:
            g = Adw.PreferencesGroup(title=_(t"Boot configuration (BCD)"),
                                     description=_(t"{bcd.get('path', '')} on /dev/{bcd.get('boot_partition', '')}"))
            for e in bcd.get("entries", []):
                tags = []
                if e["default"]:
                    tags.append(_("default"))
                if e["this_windows"]:
                    tags.append(_("this Windows"))
                if "NOT present" in (e["osdevice"] + e["device"]):
                    tags.append(_("partition missing"))
                row = xrow(Adw.ExpanderRow, title=f"{e['description'] or e['type']}" + (f"  [{', '.join(tags)}]" if tags else ""),
                                      subtitle=f"{e['id']} · {e['type']}")
                row.set_use_markup(False)
                lines = [f"{k}: {e[k]}" for k in ("device", "osdevice", "path", "systemroot") if e.get(k)]
                if e["flags"]:
                    lines.append("flags: " + ", ".join(e["flags"]))
                self._text_row(row, "\n".join(lines) or _("(no device/path settings)"))
                g.add(row)
            page.add(g)

        nv = ev.get("nvram")
        if nv and nv.get("entries"):
            g = Adw.PreferencesGroup(title=_(t"Firmware boot entries (this computer)"),
                                     description="BootOrder: " + ",".join(nv.get("boot_order", [])))
            for e in nv["entries"]:
                row = xrow(Adw.ActionRow, title=f"Boot{e['num']} {e['description']}" + ("" if e["active"] else "  " + _("(inactive)")),
                                    subtitle=f"{e.get('file') or '-'}" + (" · " + _(t"partition {e['partuuid']}") if e.get("partuuid") else ""))
                row.set_use_markup(False)
                g.add(row)
            page.add(g)

        crashes = ev.get("crashes")
        if crashes:
            g = Adw.PreferencesGroup(title=_(t"Crash dumps ({len(crashes)})"), description=_(t"Newest first"))
            for c in crashes[:60]:
                row = xrow(Adw.ActionRow, title=(c["code"] or c["error"]) + (_(t"  (live report)") if c["live"] else ""),
                                    subtitle=f"{c['time'][:19].replace('T', ' ')} · {c['file']}"
                                             + (f" · params {', '.join(c['params'])}" if c.get("params") else ""))
                row.set_use_markup(False)
                row.set_subtitle_selectable(True)
                g.add(row)
            page.add(g)

        srt = ev.get("srttrail")
        if srt:
            g = Adw.PreferencesGroup(title=_(t"Startup Repair log (SrtTrail.txt)"))
            row = xrow(Adw.ExpanderRow, title=_(t"Latest Startup Repair session"),
                                  subtitle=_(t"{srt['info'].get('repair_attempts', '?')} repair attempt(s)"))
            self._text_row(row, srt["text"])
            g.add(row)
            page.add(g)

        evs = ev.get("events")
        if evs:
            s = evs["summary"]
            last_start = s["last_boot"][:16].replace("T", " ") or _("not recorded")
            last_shutdown = s["last_clean_shutdown"][:16].replace("T", " ") or _("not recorded")
            g = Adw.PreferencesGroup(
                title=_(t"System event log"),
                description=_(t"{s['records']} records from {s['first'][:10]} to {s['last'][:10]} · "
                              t"last start {last_start} · last clean shutdown {last_shutdown}"))
            tl = evs["timeline"][:150]
            holder = xrow(Adw.ExpanderRow, title=_(t"Boot-relevant events ({len(evs['timeline'])})"),
                          subtitle=_(t"Newest first"))
            g.add(holder)
            for e in tl:
                row = xrow(Adw.ActionRow, title=e["detail"] or e["title"],
                                    subtitle=f"{e['time'][:19].replace('T', ' ')} · {e['provider']} {e['id']} · {e['title']}")
                row.set_use_markup(False)
                row.set_title_lines(3)
                icon = {"ok": "object-select-symbolic", "critical": "dialog-error-symbolic",
                        "warning": "dialog-warning-symbolic"}.get(e["severity"], "dialog-information-symbolic")
                im = Gtk.Image(icon_name=icon)
                im.add_css_class({"ok": "success", "critical": "error", "warning": "warning"}.get(e["severity"], "dim-label"))
                row.add_prefix(im)
                holder.add_row(row)
            page.add(g)

        misc = Adw.PreferencesGroup(title=_(t"Details"))
        for key, title in (("boot_drivers", _("Boot- and system-start drivers")), ("class_filters", _("Device class filters")),
                           ("critical_files", _("Boot-critical files")), ("registry", _("Registry hives")),
                           ("storage_driver", _("Storage controller driver")), ("bootlog", _("Boot log (ntbtlog.txt)")),
                           ("servicing", _("Servicing / setup state")), ("disk", _("Disk & partition table")),
                           ("volume", _("Windows volume")), ("boot_partition", _("Boot partition")), ("smart", _("Disk health (SMART)")),
                           ("recovery", _("Recovery options")), ("pending_file_renames", _("Pending file operations")),
                           ("session_manager", _("Session Manager start programs"))):
            if ev.get(key):
                row = xrow(Adw.ExpanderRow, title=title)
                row.set_use_markup(False)
                self._text_row(row, _fmt(ev[key]))
                misc.add(row)
        if r.get("log"):
            row = xrow(Adw.ExpanderRow, title=_(t"Analysis log"))
            row.set_use_markup(False)
            self._text_row(row, "\n".join(r["log"]))
            misc.add(row)
        page.add(misc)
        return page

    def _text_row(self, exp, text):
        l = label(text, "mono", selectable=True)
        l.set_margin_start(12)
        l.set_margin_end(12)
        l.set_margin_top(8)
        l.set_margin_bottom(10)
        lr = Gtk.ListBoxRow(activatable=False, selectable=False)
        lr.set_child(l)
        exp.add_row(lr)


def _fmt(obj, indent=0):
    pad = "  " * indent
    if isinstance(obj, dict):
        out = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append(f"{pad}{k}:")
                out.append(_fmt(v, indent + 1))
            else:
                out.append(f"{pad}{k}: {v}")
        return "\n".join(out)
    if isinstance(obj, list):
        out = []
        for v in obj:
            if isinstance(v, dict):
                out.append(pad + "- " + ", ".join(f"{k}={vv}" for k, vv in v.items()))
            else:
                out.append(f"{pad}- {v}")
        return "\n".join(out)
    return pad + str(obj)
