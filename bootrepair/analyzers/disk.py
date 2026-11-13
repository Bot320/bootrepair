"""Disk-level checks: partition table, firmware mode, disk health."""

from ..i18n import _
from .. import sysprobe
from ..knowledge import WINRE, LINUX, BACKUP_FIRST

from ..parsers.disk import parse_mbr, parse_gpt_header, check_gpt_entries, parse_gpt_entries

SRC = "disk"


def analyze(ctx):
    disk = ctx.disk
    dev = disk["path"]
    lbs = disk["logical_block_size"]
    ev = {"device": dev, "model": disk["model"], "size": disk["size"], "logical_block_size": lbs,
          "controller": disk["controller"], "transport": disk["tran"]}
    ctx.evidence["disk"] = ev
    with open(dev, "rb") as f:
        head = f.read(lbs * 2)
        mbr = parse_mbr(head[:512])
        ev["mbr"] = {k: v for k, v in mbr.items() if k != "partitions"}
        ev["mbr_partitions"] = mbr["partitions"]

        if not mbr["signature_ok"]:
            ctx.add("critical", "disk", _(t"Partition table signature is missing (sector 0 has no 0x55AA)"),
                    _(t"The first sector of the disk does not carry a valid MBR/protective-MBR signature. "
                      t"The firmware will not consider this disk bootable."),
                    [f"{dev} sector 0 bytes 510-511 = {head[510:512].hex()} (expected 55aa)"],
                    [LINUX,
                     _(t"If Linux still lists the partitions, only the protective MBR is damaged. Rewrite it "
                       t"(x = expert menu, n = new protective MBR, w = write):\n`sudo gdisk {dev}\nx\nn\nw`"),
                     _(t"If the partitions are gone too, do not write anything to the disk. Search for the lost "
                       t"partitions and let TestDisk write the table back:\n`sudo testdisk {dev}`")],
                    stopcode="firmware: no bootable device", source=SRC, priority=1)

        if mbr["protective"]:
            ctx.boot_mode = "uefi"
            ev["scheme"] = "GPT"
            _check_gpt(ctx, f, disk, head, lbs, mbr)
        else:
            ev["scheme"] = "MBR"
            has_esp = any(p.get("is_esp") for p in disk["partitions"])
            active = [p for p in mbr["partitions"] if p["active"]]
            ctx.boot_mode = "uefi" if (has_esp and not active) else "bios"
            _check_mbr(ctx, disk, mbr)

    ev["boot_mode"] = ctx.boot_mode
    if ctx.boot_mode == "uefi" and not ctx.uefi_host:
        ctx.add("warning", "disk", _(t"Disk is GPT/UEFI but this computer is currently running in legacy BIOS mode"),
                _(t"Windows on a GPT disk can only be started by UEFI firmware. If the firmware is set to "
                  t"legacy/CSM-only boot, Windows will not be found."),
                ["/sys/firmware/efi does not exist (Linux was booted in BIOS mode)"],
                [_(t"Open the firmware setup (usually F2 or Del right after power-on) and switch the boot mode to "
                   t"UEFI. Turn “CSM” / “Legacy only” off.")], source=SRC)
    if ctx.boot_mode == "bios" and ctx.uefi_host:
        ctx.add("warning", "disk", _(t"Windows is on an MBR disk: it can only boot in legacy BIOS/CSM mode"),
                _(t"This computer is running in UEFI mode now. An MBR-installed Windows needs Compatibility "
                  t"Support Module (CSM/legacy boot) enabled. With CSM disabled (required for Secure Boot and "
                  t"standard on newer machines) the firmware will not offer this Windows at all."),
                ["partition table: MBR (no protective 0xEE entry)", "host firmware: UEFI"],
                [_(t"Easiest: open the firmware setup (usually F2 or Del right after power-on) and enable "
                   t"“CSM” / “Legacy boot”."),
                 WINRE,
                 _(t"Or convert the disk to GPT so that it boots in UEFI mode. Find the disk number first:\n"
                   t"`diskpart\nlist disk\nexit`"),
                 _(t"Convert it (replace 0 with the disk number), then switch the firmware to UEFI boot:\n"
                   t"`mbr2gpt /convert /disk:0`")], source=SRC, priority=60)

    _check_smart(ctx, dev)
    _check_kernel_log(ctx, disk)


def _check_gpt(ctx, f, disk, head, lbs, mbr):
    dev = disk["path"]
    primary = parse_gpt_header(head[lbs:2 * lbs], lbs)
    ev = ctx.evidence["disk"]
    ev["gpt_primary"] = {k: v for k, v in primary.items() if k != "entries_crc"}
    disk_lbas = disk["size"] // lbs
    backup = {"valid": False, "error": "not read"}
    try:
        f.seek((disk_lbas - 1) * lbs)
        backup = parse_gpt_header(f.read(lbs), lbs)
    except OSError as e:
        backup = {"valid": False, "error": str(e)}
    ev["gpt_backup"] = {k: v for k, v in backup.items() if k != "entries_crc"}

    entries_ok = None
    if primary.get("valid"):
        try:
            f.seek(primary["entries_lba"] * lbs)
            entries = f.read(primary["num_entries"] * primary["entry_size"])
            entries_ok = check_gpt_entries(entries, primary)
            ev["gpt_entries"] = parse_gpt_entries(entries, primary)
        except OSError as e:
            entries_ok = False
            ev["gpt_entries_error"] = str(e)

    hybrid = [p for p in mbr["partitions"] if p["type"] != 0xEE]
    if hybrid:
        ctx.add("warning", "disk", _(t"Hybrid MBR detected on a GPT disk"),
                _(t"Besides the protective 0xEE entry the MBR contains real partition entries. Some firmware then "
                  t"treats the disk as MBR (legacy) and ignores the GPT, so the EFI boot entries are not used."),
                [f"MBR entry {p['index']}: type 0x{p['type']:02x}, start LBA {p['start_lba']}" for p in hybrid],
                [LINUX, _(t"Replace the hybrid MBR with a plain protective MBR (x = expert menu, n = new protective "
                          t"MBR, w = write):\n`sudo gdisk {dev}\nx\nn\nw`")], source=SRC)

    if not primary.get("valid") and not backup.get("valid"):
        ctx.add("critical", "disk", _(t"Both GPT headers are damaged"),
                _(t"Neither the primary nor the backup GUID partition table header is valid. The firmware cannot "
                  t"find any partition on this disk, so neither the EFI partition nor Windows can be found."),
                [f"primary: {primary.get('error')}", f"backup: {backup.get('error')}"],
                [_(t"Do not write anything to this disk until the partitions are found again."),
                 LINUX, _(t"Search for the lost partitions and let TestDisk write the table back (Analyse → Quick "
                          t"Search → Write):\n`sudo testdisk {dev}`")],
                stopcode="firmware: no bootable device", source=SRC, priority=1)
    elif not primary.get("valid"):
        ctx.add("warning", "disk", _(t"Primary GPT header is damaged (backup is intact)"),
                _(t"The firmware has to fall back to the backup GPT at the end of the disk. Most UEFI firmware does this "
                  t"and repairs it, but some refuse to boot from the disk."),
                [f"primary GPT: {primary.get('error')}", "backup GPT: valid"],
                [LINUX, _(t"gdisk notices the damage and offers to use the backup table. Accept that, then write "
                          t"it with w:\n`sudo gdisk {dev}\nw`")],
                source=SRC, priority=5)
    elif not backup.get("valid"):
        ctx.add("info", "disk", _(t"Backup GPT header is missing or invalid"),
                _(t"Typical after cloning to a larger disk. Windows usually still boots, but the disk is less resilient."),
                [f"backup GPT at LBA {disk_lbas - 1}: {backup.get('error')}"],
                [LINUX, _(t"Move the backup table to the real end of the disk:\n`sudo sgdisk -e {dev}`")],
                source=SRC)
    if entries_ok is False:
        ctx.add("critical", "disk", _(t"GPT partition entry array is corrupt (CRC mismatch)"),
                _(t"The list of partitions does not match its checksum. UEFI firmware may ignore all partitions "
                  t"on this disk, so the EFI system partition and Windows cannot be found."),
                [f"entries at LBA {primary.get('entries_lba')}: CRC32 does not match header"],
                [LINUX, _(t"gdisk offers to load the backup partition table. Accept that, check the listing with p, "
                          t"then write it with w:\n`sudo gdisk {dev}\np\nw`")],
                stopcode="firmware: no bootable device", source=SRC, priority=2)


def _check_mbr(ctx, disk, mbr):
    dev = disk["path"]
    active = [p for p in mbr["partitions"] if p["active"]]
    ev = ctx.evidence["disk"]
    ev["active_partitions"] = [p["index"] for p in active]
    if ctx.boot_mode != "bios":
        return
    if mbr["bootcode_empty"]:
        ctx.add("critical", "disk", _(t"MBR contains no boot code"),
                _(t"On a legacy BIOS system the firmware executes the code in the first sector. It is empty, so "
                  t"the BIOS reports 'no bootable device' or skips this disk."),
                [f"{dev} sector 0 bytes 0-439 are all zero"],
                [WINRE, _(t"Write Windows' boot code into the first sector:\n`bootrec /fixmbr`")],
                stopcode="BIOS: no bootable device", source=SRC, priority=3)
    elif mbr["bootcode"] == "GRUB":
        ctx.add("info", "disk", _(t"MBR boot code belongs to GRUB"),
                _(t"The BIOS starts GRUB, which must chain-load Windows. If the GRUB menu has no working Windows "
                  t"entry, Windows does not start."), [f"{dev} sector 0 contains GRUB boot code"],
                [LINUX, _(t"Let GRUB find Windows and add it to its menu:\n"
                          t"`sudo os-prober\nsudo grub-mkconfig -o /boot/grub/grub.cfg`"),
                 WINRE, _(t"Or give the first sector back to Windows (this removes the GRUB menu):\n`bootrec /fixmbr`")],
                source=SRC)
    if not active:
        ctx.add("critical", "disk", _(t"No active partition on this MBR disk"),
                _(t"The Windows MBR boot code starts the partition marked 'active'. None is marked, so the BIOS "
                  t"shows 'Missing operating system' / 'No bootable device'."),
                ["MBR partition entries: " + ", ".join(f"#{p['index']} type 0x{p['type']:02x}" for p in mbr["partitions"])],
                [WINRE,
                 _(t"Mark the boot partition active. That is the small “System Reserved” partition if there is one, "
                   t"otherwise the Windows partition; use its number from “list partition”:\n"
                   t"`diskpart\nselect disk 0\nlist partition\nselect partition 1\nactive\nexit`"),
                 _(t"Rewrite the boot files. After /s put the letter of the partition you just marked active:\n"
                   t"`bootrec /fixboot\nbcdboot C:\\Windows /s C: /f BIOS`")],
                stopcode="BIOS: Missing operating system", source=SRC, priority=3)
    elif len(active) > 1:
        ctx.add("warning", "disk", _(t"More than one partition is marked active"),
                _(t"Only one partition should be active; the boot code may refuse to boot ('Invalid partition table')."),
                [f"active entries: {[p['index'] for p in active]}"],
                [WINRE, _(t"Select each partition that should not be active and clear its flag (replace 2 with its "
                          t"number):\n`diskpart\nselect disk 0\nlist partition\nselect partition 2\ninactive\nexit`")],
                source=SRC)


def _check_smart(ctx, dev):
    j = sysprobe.smartctl_json(dev)
    if j is None:
        ctx.log("smartctl not available - skipping disk health check")
        return
    health = {"passed": j.get("smart_status", {}).get("passed")}
    ctx.evidence["smart"] = health
    if health["passed"] is False:
        ctx.add("critical", "disk", _(t"The disk reports S.M.A.R.T. health status FAILED"),
                _(t"The drive itself declares that it is failing. Read errors on system files, the registry or the "
                  t"page file make Windows crash or hang during startup, and repairs will not last."),
                [f"smartctl -H {dev}: FAILED"],
                [BACKUP_FIRST, _(t"Replace the drive, then restore Windows from a backup or install it again.")],
                stopcode="often 0x0000007A / 0x000000F4 / 0x00000077", source=SRC, priority=0)
    nv = j.get("nvme_smart_health_information_log")
    if nv:
        health.update({k: nv.get(k) for k in ("critical_warning", "media_errors", "percentage_used",
                                               "available_spare", "available_spare_threshold",
                                               "num_err_log_entries", "unsafe_shutdowns")})
        cw = nv.get("critical_warning") or 0
        if cw:
            bits = []
            if cw & 0x01: bits.append("available spare below threshold")
            if cw & 0x02: bits.append("temperature out of range")
            if cw & 0x04: bits.append("NVM subsystem reliability degraded")
            if cw & 0x08: bits.append("media placed in READ-ONLY mode")
            if cw & 0x10: bits.append("volatile memory backup failed")
            ctx.add("critical", "disk", _(t"NVMe drive reports a critical warning"),
                    _(t"The SSD's controller reports a critical condition. A read-only or degraded SSD prevents "
                      t"Windows from writing the registry, logs and page file during startup, which makes boot fail "
                      t"or loop."), [f"critical_warning = 0x{cw:02x}: " + ", ".join(bits)],
                    [BACKUP_FIRST, _(t"Replace the SSD.")], source=SRC, priority=0)
        if (nv.get("media_errors") or 0) > 0:
            ctx.add("warning", "disk", _(t"NVMe drive has {nv['media_errors']} media/data-integrity errors"),
                    _(t"Unrecoverable read errors happened on the flash. If they hit system files or the registry, "
                      t"Windows fails to start."), [f"media_errors = {nv['media_errors']}"],
                    [BACKUP_FIRST,
                     LINUX, _(t"Read the whole drive once to see whether new errors appear:\n"
                              t"`sudo badblocks -sv {dev}`")], source=SRC, priority=10)
        if (nv.get("percentage_used") or 0) >= 100:
            ctx.add("warning", "disk", _(t"SSD has exceeded its rated write endurance"),
                    _(t"The drive's wear indicator is at or above 100%."), [f"percentage_used = {nv['percentage_used']}%"],
                    [_(t"Keep backups current and plan to replace the SSD.")], source=SRC)
    table = (j.get("ata_smart_attributes") or {}).get("table") or []
    attrs = {a.get("id"): (a.get("raw") or {}).get("value", 0) for a in table}
    if attrs:
        health["ata"] = {str(k): attrs.get(k) for k in (5, 187, 196, 197, 198, 199) if k in attrs}
        pending = attrs.get(197, 0) or 0
        unc = attrs.get(198, 0) or 0
        realloc = attrs.get(5, 0) or 0
        if pending or unc:
            ctx.add("warning", "disk", _(t"Disk has unreadable sectors (pending {pending}, uncorrectable {unc})"),
                    _(t"Sectors that cannot be read are waiting to be remapped. If one of them holds a boot-critical "
                      t"file or registry data, startup fails with read errors (0x7A, 0xF4, 0xC0000185)."),
                    [f"SMART 197 Current_Pending_Sector = {pending}", f"SMART 198 Offline_Uncorrectable = {unc}"],
                    [BACKUP_FIRST, _(t"Replace the disk.")], source=SRC, priority=5)
        if realloc > 50:
            ctx.add("warning", "disk", _(t"Disk has reallocated {realloc} sectors"),
                    _(t"A high and growing reallocated sector count indicates a degrading disk."),
                    [f"SMART 5 Reallocated_Sector_Ct = {realloc}"],
                    [_(t"Keep backups current and plan to replace the disk.")], source=SRC)
        if (attrs.get(199) or 0) > 0:
            ctx.add("info", "disk", _(t"Interface CRC errors recorded ({attrs[199]})"),
                    _(t"Data corruption on the SATA cable/port happened in the past. A loose or bad cable causes "
                      t"random boot failures."), [f"SMART 199 UDMA_CRC_Error_Count = {attrs[199]}"],
                    [_(t"Replace the SATA cable or use another SATA port.")], source=SRC)


def _check_kernel_log(ctx, disk):
    text = sysprobe.dmesg_text()
    name = disk["name"]
    keys = ("I/O error", "critical medium error", "Medium Error", "UNC", "timeout", "resetting controller",
            "Buffer I/O error")
    hits = [l.strip() for l in text.splitlines() if name in l and any(k in l for k in keys)]
    if hits:
        ctx.evidence["kernel_io_errors"] = hits[-30:]
        ctx.add("warning", "disk", _(t"Linux logged {len(hits)} I/O errors for this disk since it booted"),
                _(t"The disk produced read/write errors right now under Linux - a strong sign of failing hardware, "
                  t"which would also break Windows' startup."), hits[-6:],
                [BACKUP_FIRST, _(t"Reseat the drive (cable or M.2 slot)."),
                 LINUX, _(t"Start the drive's long self-test and read the result when it has finished:\n"
                          t"`sudo smartctl -t long {disk['path']}\nsudo smartctl -a {disk['path']}`")],
                source=SRC, priority=3)


