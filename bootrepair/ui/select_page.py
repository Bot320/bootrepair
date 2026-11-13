"""Start page: pick the Windows installation (and, if needed, the boot partition) to analyse."""

from gi.repository import Adw, Gio, Gtk

from ..i18n import _, N_
from . import xrow, state
from ..devices import list_disks
from ..fsutil import human_size
from .widgets import tag

STATUS_CSS = {"fail": "tag-stop", "warn": "risk-medium", "ok": "risk-low", "incomplete": "tag-esp"}
STATUS_BADGE = {"fail": N_("Does not start"), "warn": N_("Warnings"), "ok": N_("No problems found"),
                "incomplete": N_("Analysis incomplete")}


def _boot_candidate(p):
    if p["is_esp"]:
        return True
    label = (p["label"] or "").lower()
    return p["fstype"] in ("ntfs", "vfat") and p["size"] < 2 * 1024 ** 3 and not p["is_winre"] and \
        ("system" in label or "reserved" in label or "boot" in label)


def _fs(p):
    return "BitLocker" if p["fstype"] == "bitlocker" else (p["fstype"] or _("no file system")).upper()


class SelectPage(Adw.NavigationPage):
    def __init__(self, on_analyze):
        super().__init__(title="BootRepair", tag="select")
        self.on_analyze = on_analyze
        self.selected = None
        self.groups = []

        tv = Adw.ToolbarView()
        hb = Adw.HeaderBar()
        refresh = Gtk.Button(icon_name="view-refresh-symbolic", tooltip_text=_(t"Look for drives again"))
        refresh.connect("clicked", lambda *__: self.reload())
        hb.pack_start(refresh)
        m = Gio.Menu()
        lm = Gio.Menu()
        lm.append(_("Automatic"), "app.language::auto")
        lm.append("English", "app.language::en")
        lm.append("Deutsch", "app.language::de")
        m.append_submenu(_("Language"), lm)
        m.append(_(t"Undo last repair…"), "app.undo")
        m.append(_(t"About BootRepair"), "app.about")
        hb.pack_end(Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=m, tooltip_text=_(t"Menu"), primary=True))
        tv.add_top_bar(hb)

        self.page = Adw.PreferencesPage()
        tv.set_content(self.page)
        bottom = Gtk.Box(spacing=12, halign=Gtk.Align.CENTER, margin_top=10, margin_bottom=12,
                         margin_start=12, margin_end=12)
        self.summary = Gtk.Label(css_classes=["dim-label"], ellipsize=3)
        self.analyze_btn = Gtk.Button(label=_(t"Analyse"), css_classes=["suggested-action", "pill"], sensitive=False)
        self.analyze_btn.connect("clicked", self._analyze)
        bottom.append(self.summary)
        bottom.append(self.analyze_btn)
        tv.add_bottom_bar(bottom)
        self.set_child(tv)
        self.reload()

    # ------------------------------------------------------------------ build
    def _add(self, g):
        self.page.add(g)
        self.groups.append(g)

    def reload(self):
        for g in self.groups:
            self.page.remove(g)
        self.groups = []
        self.selected = None
        try:
            disks = list_disks()
        except Exception as e:  # noqa: BLE001
            self._add(Adw.PreferencesGroup(title=_(t"Could not list the drives"), description=str(e)))
            return
        st = state.load()
        known = st.get("partitions", {})
        parts = [p for d in disks for p in d["partitions"]]
        model = {d["name"]: d["model"] or d["name"] for d in disks}

        intro = Adw.PreferencesGroup(
            title=_(t"Which Windows does not start?"),
            description=_(t"BootRepair only reads your disks while it analyses them. Nothing is changed until you "
                          t"choose a repair yourself."))
        self._add(intro)

        wins = sorted([p for p in parts if p["windows_score"] >= 60 or p["partuuid"] in known],
                      key=lambda p: (p["partuuid"] not in known, -p["windows_score"], -p["size"]))
        others = [p for p in parts if p not in wins and not p["is_esp"] and p["parttype"] !=
                  "e3c9e316-0b5c-4db8-817d-f92df00215ae"]
        self.first = None
        rows = {}

        g = Adw.PreferencesGroup(title=_(t"Windows installations"))
        if not wins:
            g.set_description(_(t"No partition looks like a Windows installation. Choose one under “Other partitions”."))
        for p in wins:
            k = known.get(p["partuuid"], {})
            title = k.get("name") or (_(t"Windows partition “{p['label']}”") if p["label"] and p["label"] != "Basic data partition"
                                      else _("Windows partition"))
            sub = f"/dev/{p['name']} · {human_size(p['size'])} · {_fs(p)} · {model.get(p['disk'], p['disk'])}"
            row = self._radio_row(title, sub, p)
            if k.get("verdict"):
                row.add_suffix(tag(_(STATUS_BADGE.get(k.get("status"), k["verdict"])), STATUS_CSS.get(k.get("status"), "tag-esp")))
            g.add(row)
            rows[p["partuuid"]] = row
        self._add(g)

        if others:
            og = Adw.PreferencesGroup()
            exp = xrow(Adw.ExpanderRow, title=_(t"Other partitions"),
                       subtitle=_(t"If Windows is somewhere unexpected, or its file system is damaged"))
            for p in others:
                r = self._radio_row(f"/dev/{p['name']}" + (f" “{p['label']}”" if p["label"] else ""),
                                    f"{_fs(p)} · {human_size(p['size'])} · {p['parttypename'] or '-'}", p)
                exp.add_row(r)
            exp.set_expanded(not wins)
            og.add(exp)
            self._add(og)

        # BitLocker key, shown only when needed
        self.key_group = Adw.PreferencesGroup(
            title="BitLocker", description=_(t"This partition is encrypted. Enter its 48-digit recovery key so the "
                                             t"contents can be analysed (it is used read-only and not stored)."))
        self.key_row = Adw.PasswordEntryRow(title=_(t"Recovery key"))
        self.key_group.add(self.key_row)
        self.key_group.set_visible(False)
        self._add(self.key_group)

        # advanced
        ag = Adw.PreferencesGroup()
        adv = xrow(Adw.ExpanderRow, title=_(t"More options"), subtitle=_(t"Boot partition, event log"))
        self.esps = [p for p in parts if _boot_candidate(p)]
        names = [_("Automatic (recommended)")] + [
            f"/dev/{p['name']} · {human_size(p['size'])}" + (" · " + _("mounted") if p["mountpoints"] else "") for p in self.esps]
        self.boot_row = Adw.ComboRow(title=_(t"Boot partition"), model=Gtk.StringList.new(names))
        self.boot_row.set_subtitle(_(t"Holds Windows Boot Manager and the boot configuration"))
        adv.add_row(self.boot_row)
        self.events_row = Adw.SwitchRow(title=_(t"Read the System event log"), active=True,
                                        subtitle=_(t"Finds crashes and disk errors; adds a few seconds"))
        adv.add_row(self.events_row)
        ag.add(adv)
        self._add(ag)

        pick = rows.get(st.get("last_partuuid")) if st.get("last_partuuid") in rows else None
        target = pick or (next(iter(rows.values())) if rows else None)
        if target is not None:
            target._check.set_active(True)
        self._update()

    def _radio_row(self, title, subtitle, part):
        row = xrow(Adw.ActionRow, title=title, subtitle=subtitle)
        cb = Gtk.CheckButton(valign=Gtk.Align.CENTER)
        if self.first is None:
            self.first = cb
        else:
            cb.set_group(self.first)
        cb.connect("toggled", self._on_toggle, part)
        row.add_prefix(cb)
        row.set_activatable_widget(cb)
        row._check = cb
        return row

    # ------------------------------------------------------------------ events
    def _on_toggle(self, check, part):
        if check.get_active():
            self.selected = part
            self.key_group.set_visible(part["fstype"] == "bitlocker")
            self._update()

    def _update(self):
        p = self.selected
        self.analyze_btn.set_sensitive(p is not None)
        self.summary.set_label(f"/dev/{p['name']} · {human_size(p['size'])}" if p else _(t"Choose a partition"))

    def _analyze(self, *__):
        if not self.selected:
            return
        i = self.boot_row.get_selected()
        esp = "auto" if i in (0, Gtk.INVALID_LIST_POSITION) else self.esps[i - 1]["path"]
        key = self.key_row.get_text().strip() if self.key_group.get_visible() else ""
        self.on_analyze(self.selected, esp, key or None, self.events_row.get_active())
