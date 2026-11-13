"""Everything the analysis asks the *running* Linux system (not the Windows disk).

Kept in one place so an evidence bundle can record the answers and tests can replay them.
"""

import json
import os
import shutil
import subprocess

SECUREBOOT_VAR = "/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c"


def _run(cmd, timeout=60):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return None


def uefi_host():
    return os.path.isdir("/sys/firmware/efi")


def efibootmgr_v():
    """Text of `efibootmgr -v`, or None if unavailable."""
    if not uefi_host() or not shutil.which("efibootmgr"):
        return None
    return _run(["efibootmgr", "-v"], 20)


def smartctl_json(dev):
    """Parsed `smartctl -j -H -A -i dev`, or None."""
    if not shutil.which("smartctl"):
        return None
    out = _run(["smartctl", "-j", "-H", "-A", "-i", dev])
    try:
        return json.loads(out or "")
    except ValueError:
        return None


def dmesg_text():
    return _run(["dmesg"], 20) or ""


def secure_boot():
    try:
        with open(SECUREBOOT_VAR, "rb") as f:
            b = f.read()
        return "enabled" if len(b) >= 5 and b[4] == 1 else "disabled"
    except OSError:
        return "unknown"
