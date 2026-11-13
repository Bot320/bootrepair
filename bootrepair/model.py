"""Shared data model for findings and the analysis report."""

from dataclasses import dataclass, field, asdict

from .i18n import N_

SEVERITIES = ("critical", "warning", "info")
SEVERITY_ORDER = {s: i for i, s in enumerate(SEVERITIES)}

# The Windows boot chain, in the order things happen at power-on.
STAGES = [
    ("disk", N_("Disk & firmware"),
     N_("The firmware reads the disk, the partition table and finds the boot partition.")),
    ("bootmgr", N_("Boot Manager"),
     N_("The firmware starts Windows Boot Manager (bootmgfw.efi on UEFI, BOOTMGR on BIOS).")),
    ("bcd", N_("Boot configuration (BCD)"),
     N_("Boot Manager reads the BCD store to find out which Windows to start and where it lives.")),
    ("winload", N_("OS loader (winload)"),
     N_("winload reads the Windows volume, the SYSTEM hive, the kernel, the HAL and all boot-start drivers.")),
    ("kernel", N_("Kernel & boot drivers"),
     N_("The kernel initialises, boot drivers start and the storage stack mounts the system volume.")),
    ("session", N_("Session Manager & services"),
     N_("smss, csrss, wininit and services.exe start; pending updates and disk checks run here.")),
    ("logon", N_("Logon"),
     N_("winlogon, LogonUI, userinit and the shell start.")),
]
STAGE_IDS = [s[0] for s in STAGES]
STAGE_LABELS = {s[0]: s[1] for s in STAGES}
STAGE_LABELS["general"] = N_("General")


@dataclass
class Finding:
    severity: str           # critical | warning | info
    stage: str              # one of STAGE_IDS or "general"
    title: str
    why: str                # plain-language explanation of the consequence
    evidence: list = field(default_factory=list)   # exact facts: paths, keys, values, events
    fix: list = field(default_factory=list)        # concrete repair steps / commands
    stopcode: str = ""      # e.g. "0x0000007B INACCESSIBLE_BOOT_DEVICE" or "0xc000000e"
    source: str = ""        # analyzer id
    priority: int = 50      # lower = more important within the same severity/stage
    actions: list = field(default_factory=list)    # one-click repairs (see actions.py)

    def to_dict(self):
        return asdict(self)


def sort_findings(findings):
    def key(f):
        stage_idx = STAGE_IDS.index(f["stage"]) if f["stage"] in STAGE_IDS else len(STAGE_IDS)
        return (SEVERITY_ORDER.get(f["severity"], 9), stage_idx, f.get("priority", 50), f["title"])
    return sorted(findings, key=key)
