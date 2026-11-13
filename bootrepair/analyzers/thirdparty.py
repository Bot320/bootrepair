"""Third-party drivers that load at every start, and security products installed side by side."""

import re
from collections import OrderedDict

from ..i18n import _
from ..fsutil import pe_company
from .drivers import resolve_image
from .events import SAFE_MODE_HOWTO

SRC = "thirdparty"
AV_GROUPS = ("fsfilter anti-virus", "early-launch")
BUS_GROUPS = ("scsi miniport", "scsi class", "boot bus extender", "system bus extender")   # load only with hardware
BRANDS = {"gen digital": "Avast / AVG / Norton", "chengdu yiwo": "EaseUS", "avast": "Avast", "avg": "AVG"}


def vendor_name(company):
    """'BitDefender S.R.L. Bucharest, ROMANIA' -> 'BitDefender'; 'Gen Digital Inc.' -> 'Gen Digital'."""
    name = re.split(r",| S\.R\.L| Inc\b| Corporation| Corp\b| Co\.| Ltd| GmbH| - |\(", company)[0].strip()
    return name or company.strip()


def third_party_drivers(ctx, services):
    """Boot- and system-start drivers that are not part of Windows, with their vendor."""
    rows = []
    for s in services.values():
        if s["start"] not in (0, 1) or not isinstance(s["type"], int) or not (s["type"] & 0x0B):
            continue
        disp = s.get("display") or ""
        if isinstance(disp, str) and disp.startswith("@") and not re.match(r"(?i)@oem\d+\.inf", disp):
            continue        # described by a Windows inbox resource -> part of Windows
        rel = resolve_image(ctx, s["image"], s["name"], s["type"])
        path = ctx.win_path(rel) if rel else None
        if path is None:
            continue        # missing files are reported by the driver checks
        company = pe_company(path)
        if company and "microsoft" in company.lower():
            continue
        m = re.match(r"(?i)program files(?: \(x86\))?\\([^\\]+)\\", rel)
        rows.append({"name": s["name"], "group": s["group"] or "", "start": s["start"], "file": rel,
                     "company": company or "", "vendor": vendor_name(company) if company else _("unknown vendor"),
                     "product": m.group(1) if m else ""})
        ctx.check_cancel()
    return sorted(rows, key=lambda r: (r["vendor"].lower(), r["name"].lower()))


def _label(vendor, rows):
    brand = next((b for k, b in BRANDS.items() if vendor.lower().startswith(k)), "") \
        or next((r["product"] for r in rows if r["product"]), "")
    return f"{vendor} ({brand})" if brand and brand.lower() != vendor.lower() else vendor


def _by_vendor(rows):
    out = OrderedDict()
    for r in rows:
        out.setdefault(r["vendor"].lower(), (r["vendor"], []))[1].append(r)
    return out


def analyze(ctx):
    services = getattr(ctx, "services", None)
    if not services:
        return
    rows = third_party_drivers(ctx, services)
    ctx.evidence["third_party_drivers"] = rows

    av = _by_vendor([r for r in rows if r["group"].lower() in AV_GROUPS])
    if len(av) >= 2:
        names = ", ".join(_label(v, rs) for v, rs in av.values())
        ctx.add("warning", "kernel", _(t"Several antivirus programs load at the same time: {names}"),
                _("Each of them hooks into every file access with its own file-system filter and early-launch "
                  "driver. Antivirus vendors only support running alone: two real-time scanners can block each "
                  "other while Windows starts, which shows up as hangs, freezes or crashes without a clear error."),
                [f"{_label(v, rs)}: " + ", ".join(f"{r['name']} ({r['group']})" for r in rs) for v, rs in av.values()],
                [_(SAFE_MODE_HOWTO),
                 _("In Safe Mode, remove one of them with the vendor's removal tool, which also works there (Avast: "
                   "“Avast Uninstall Utility”, Bitdefender: “Bitdefender Uninstall Tool”). Keep one product, or "
                   "none: Windows then switches Microsoft Defender back on.")],
                source=SRC, priority=16)

    sm = getattr(ctx, "safe_mode_finding", None)
    if sm is None:
        return
    skipped = getattr(ctx, "safe_mode_skipped", set())
    if skipped:
        # Windows logged which start drivers Safe Mode left out: the cause of a failing normal start is among them
        suspects = [r for r in rows if r["name"].lower() in skipped]
        head = _("Third-party drivers that Safe Mode skipped, so one of them is the most likely cause:")
    else:
        suspects = [r for r in rows if not any(g in r["group"].lower() for g in BUS_GROUPS)]
        head = _("Third-party drivers that load at every normal start:")
    if suspects:
        sm.evidence.append(head)
        for v, rs in _by_vendor(suspects).values():
            sm.evidence.append(f"  {_label(v, rs)}: " + ", ".join(r["name"] for r in rs))
