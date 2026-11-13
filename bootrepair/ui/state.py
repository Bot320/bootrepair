"""Small per-user state: last analysed partition and what was found on each partition."""

import json
from pathlib import Path

from gi.repository import GLib


def _file():
    return Path(GLib.get_user_config_dir()) / "bootrepair" / "state.json"


def load():
    try:
        d = json.loads(_file().read_text())
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save(d):
    try:
        f = _file()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(d, indent=1))
    except OSError:
        pass


def remember_report(report):
    """Store the Windows name and the verdict per partition, shown on the start page next time."""
    uuid = report.get("target", {}).get("partuuid")
    if not uuid:
        return
    d = load()
    w = report.get("windows") or {}
    name = " ".join(x for x in (w.get("DisplayName"), w.get("DisplayVersion")) if x)
    d.setdefault("partitions", {})[uuid] = {
        "name": name, "verdict": report.get("verdict", {}).get("title", ""),
        "status": report.get("verdict", {}).get("status", ""), "when": report.get("generated", "")[:10]}
    d["last_partuuid"] = uuid
    save(d)
