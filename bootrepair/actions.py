"""Builders for one-click repair actions attached to findings.

An action is a plain dict, so it can travel through JSON from the analysis to the GUI and
back to the privileged fixer:
  kind      - fixer to run (see fixes.FIXERS)
  title     - button / checklist text
  changes   - human-readable list of exactly what will be modified
  risk      - "low" | "medium" | "high"
  needs     - which volumes must be writable: "win", "boot", "nvram"
  params    - fixer arguments
"""

import hashlib
import json

from .i18n import _

HIVE_PATH = {"SYSTEM": "Windows\\System32\\config\\SYSTEM", "SOFTWARE": "Windows\\System32\\config\\SOFTWARE",
             "COMPONENTS": "Windows\\System32\\config\\COMPONENTS"}


def action(kind, title, changes, risk="low", needs=("win",), **params):
    a = {"kind": kind, "title": title, "changes": list(changes), "risk": risk, "needs": list(needs),
         "params": params}
    a["id"] = hashlib.sha1(json.dumps([kind, params], sort_keys=True, default=str).encode()).hexdigest()[:12]
    return a


def set_service_start(cs, service, start, clear_override=False, reason=""):
    ch = [_(t"HKLM\\SYSTEM\\{cs}\\Services\\{service}: Start -> {start}")]
    if clear_override:
        ch.append(_(t"HKLM\\SYSTEM\\{cs}\\Services\\{service}\\StartOverride: all values -> 0"))
    return action("set_service_start", _(t"Set '{service}' to start at boot") if start == 0 else
                  _(t"Disable driver '{service}'"), ch, "low", cs=cs, service=service, start=start,
                  clear_override=clear_override)


def remove_class_filter(cs, class_guid, value, flt, class_name):
    return action("remove_class_filter", _(t"Remove broken filter '{flt}' from {class_name}"),
                  [_(t"HKLM\\SYSTEM\\{cs}\\Control\\Class\\{class_guid}\\{value}: remove '{flt}'")], "low",
                  cs=cs, class_guid=class_guid, value=value, filter=flt)


def disable_drivers(cs, drivers, filters):
    """drivers: [(service, label)]; filters: [(class_guid, value, filter, class_name)] to remove the drivers from."""
    ch = [_(t"HKLM\\SYSTEM\\{cs}\\Services\\{name}: Start -> 4 (switched off)  [{label}]") for name, label in drivers]
    ch += [_(t"HKLM\\SYSTEM\\{cs}\\Control\\Class\\{g}\\{v}: remove '{f}' ({cn})") for g, v, f, cn in filters]
    n = len(drivers)
    return action("disable_drivers", _(t"Switch off {n} third-party startup drivers"), ch, "medium", cs=cs,
                  services=[d for d, __ in drivers],
                  filters=[{"class_guid": g, "value": v, "filter": f} for g, v, f, __ in filters])


def clear_pending_renames(cs):
    return action("clear_pending_renames", _(t"Cancel pending file replace operations"),
                  [_(t"HKLM\\SYSTEM\\{cs}\\Control\\Session Manager\\PendingFileRenameOperations(2): deleted")],
                  "medium", cs=cs)


def disable_verifier(cs):
    return action("disable_verifier", _(t"Turn off Driver Verifier"),
                  [_(t"HKLM\\SYSTEM\\{cs}\\Control\\Session Manager\\Memory Management: delete VerifyDrivers, VerifyDriverLevel")],
                  "low", cs=cs)


def revert_pending_update():
    return action("revert_pending_update", _(t"Cancel the pending Windows Update operation"),
                  [_(t"Windows\\WinSxS\\pending.xml: renamed to pending.xml.bootrepair-<time> (kept)"),
                   _(t"COMPONENTS hive: delete PendingXmlIdentifier, NextQueueEntryIndex, AdvancedInstallersNeedResolving"),
                   _(t"Windows Update installs the update again later; if it keeps failing, uninstall it from WinRE")],
                  "medium")


def restore_system_file(dst, src, version):
    return action("restore_system_file", _(t"Restore \\{dst} from the component store"),
                  [_(t"\\{dst}: replaced with \\{src} (version {version}); the old file is backed up")], "medium",
                  dst=dst, src=src)


def restore_hive_regback(hive, age):
    return action("restore_hive_regback", _(t"Restore the {hive} hive from RegBack"),
                  [_(t"Windows\\System32\\config\\{hive}: replaced by RegBack\\{hive} ({age})"),
                   _(t"{hive}.LOG1 / .LOG2: renamed so they are not replayed onto the restored hive"),
                   _(t"Settings, drivers and updates installed after that date are lost")], "high", hive=hive)


def discard_hibernation():
    return action("discard_hibernation", _(t"Discard the hibernation image"),
                  [_(t"hiberfil.sys: renamed (or removed if the volume can only be opened that way)"),
                   _(t"Unsaved work in the hibernated session is lost; Windows does a fresh start")], "medium")


def reg_set_dword(hive, path, name, value, title):
    return action("reg_set_dword", title, [_(t"HKLM\\{hive}\\{path}\\{name} -> {value}")], "medium",
                  hive=hive, path=path, name=name, value=value)


# ------------------------------------------------------------------ boot partition / BCD
def bcd_repoint(bcd_rel, objects, labels, target_name):
    return action("bcd_repoint", _(t"Point the boot entry at /dev/{target_name}"),
                  [_(t"BCD {l}: device and osdevice -> /dev/{target_name}") for l in labels], "low", needs=("boot",),
                  bcd=bcd_rel, objects=objects)


def bcd_set_default(bcd_rel, obj, label):
    return action("bcd_set_default", _(t"Make this Windows the default boot entry"),
                  [_(t"BCD {{bootmgr}} default -> {label}")], "low", needs=("boot",), bcd=bcd_rel, object=obj)


def bcd_delete_elements(bcd_rel, obj, elements, label):
    from .parsers.bcd import element_name
    names = ", ".join(element_name(e) for e in elements)
    return action("bcd_delete_elements", _(t"Remove {names} from the boot entry"),
                  [_(t"BCD {label}: delete setting {element_name(e)}") for e in elements], "low", needs=("boot",),
                  bcd=bcd_rel, object=obj, elements=[f"{e:08x}" for e in elements])


def bcd_delete_objects(bcd_rel, objects, labels):
    title = _("Remove the stale boot entry") if len(objects) == 1 else _(t"Remove {len(objects)} stale boot entries")
    return action("bcd_delete_objects", title,
                  [_(t"BCD: delete {l} and remove it from the boot menu") for l in labels], "low", needs=("boot",),
                  bcd=bcd_rel, objects=objects)


def esp_restore_bootfiles():
    return action("esp_restore_bootfiles", _(t"Restore Windows Boot Manager files on the EFI partition"),
                  [_(t"Copy \\Windows\\Boot\\EFI\\* to \\EFI\\Microsoft\\Boot\\ on the EFI partition (BCD is kept)")],
                  "low", needs=("win", "boot"))


# ------------------------------------------------------------------ firmware (NVRAM)
def nvram_create(disk, partnum):
    return action("nvram_create", _(t"Add a 'Windows Boot Manager' firmware boot entry"),
                  [_(t"efibootmgr -c -d {disk} -p {partnum} -L \"Windows Boot Manager\" -l \\EFI\\Microsoft\\Boot\\bootmgfw.efi")],
                  "low", needs=("nvram",), disk=disk, partnum=partnum)


def nvram_first(num, order):
    return action("nvram_first", _(t"Put Boot{num} (Windows Boot Manager) first in the boot order"),
                  [_(t"BootOrder: {','.join(order)} -> {','.join([num] + [o for o in order if o != num])}")], "low",
                  needs=("nvram",), num=num)


def nvram_append(num, order):
    return action("nvram_append", _(t"Add Boot{num} (Windows Boot Manager) to the boot order"),
                  [_(t"BootOrder: {','.join(order)} -> {','.join(order + [num])}")], "low", needs=("nvram",), num=num)


def nvram_activate(num):
    return action("nvram_activate", _(t"Enable firmware entry Boot{num}"), [_(t"efibootmgr -b {num} -a")], "low",
                  needs=("nvram",), num=num)


def nvram_delete(num, desc):
    return action("nvram_delete", _(t"Remove stale firmware entry Boot{num}"),
                  [_(t"efibootmgr -b {num} -B  ('{desc}')")], "low", needs=("nvram",), num=num)


def reg_delete_values(hive, path, names, title):
    return action("reg_delete_values", title, [_(t"HKLM\\{hive}\\{path}: delete {', '.join(names)}")], "medium",
                  hive=hive, path=path, names=list(names))


def setup_child_completion():
    return reg_set_dword("SYSTEM", "Setup\\Status\\ChildCompletion", "setup.exe", 3,
                         _("Mark Windows Setup as completed (setup.exe = 3)"))
