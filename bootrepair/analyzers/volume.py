"""Windows volume: file system, BitLocker, dirty flag, hibernation, mounting, free space."""

import os

from ..i18n import _
from .. import actions as A
from ..fsutil import CIRoot, human_size
from ..knowledge import WINRE, LINUX, WINDOWS, CHKDSK, CHKDSK_R, BACKUP_FIRST
from ..mounting import MountError, existing_mount
from ..parsers.ntfs import identify, parse_boot_sector, read_volume_state

SRC = "volume"
LATE_STAGES = ("winload", "kernel", "session", "logon")


def _read(dev, off, n):
    with open(dev, "rb") as f:
        f.seek(off)
        return f.read(n)


def _dev_size(dev):
    with open(dev, "rb") as f:
        return f.seek(0, os.SEEK_END)


def analyze(ctx):
    dev = ctx.target["path"]
    ev = {"device": dev, "size": ctx.target["size"], "lsblk_fstype": ctx.target["fstype"]}
    ctx.evidence["volume"] = ev
    bs = _read(dev, 0, 4096)
    kind = identify(bs)
    ev["detected"] = kind

    if kind == "bitlocker":
        ev["bitlocker"] = True
        if not ctx.bitlocker_key:
            ctx.add("warning", "general", _(t"Volume is BitLocker-encrypted - Windows itself could not be analysed"),
                    _(t"Without the recovery key the contents (BCD target, registry, drivers, logs) cannot be read. "
                      t"Only disk-level and boot-partition checks were done. Note: a BitLocker volume that asks for "
                      t"the recovery key at boot is usually caused by a firmware/TPM/Secure Boot change, not damage."),
                    [f"{dev}: '-FVE-FS-' BitLocker signature"],
                    [_(t"Find the 48-digit recovery key: sign in at https://account.microsoft.com/devices/recoverykey "
                       t"with the Microsoft account used on this PC, or look for your printout."),
                     _(t"Go back, select this partition again, enter the key under “More options” and repeat the "
                       t"analysis.")], source=SRC, priority=0)
            ctx.incomplete.append(_("BitLocker volume locked"))
            ctx.unanalyzed_stages.update(LATE_STAGES)
            return
        try:
            dev = ctx.mounts.bitlocker_open(dev, ctx.bitlocker_key)
        except MountError as e:
            ctx.add("warning", "general", _(t"BitLocker unlock failed - Windows itself could not be analysed"),
                    _(t"The recovery key was not accepted (or cryptsetup cannot open this BitLocker version)."),
                    [str(e)], [_(t"Check the recovery key (48 digits in 8 groups of 6) and run the analysis again.")],
                    source=SRC, priority=0)
            ctx.incomplete.append(_("BitLocker unlock failed"))
            ctx.unanalyzed_stages.update(LATE_STAGES)
            return
        ctx.win_dev = dev
        ctx.add("info", "general", _(t"BitLocker volume unlocked read-only for analysis"),
                _(t"If Windows stops at the blue 'BitLocker recovery' screen, entering the key there lets it boot; "
                  t"the usual trigger is a BIOS update, Secure Boot / TPM change or a changed boot order."),
                [f"opened {ctx.target['path']} as {dev} (read-only)"], source=SRC)
        bs = _read(dev, 0, 4096)
        kind = identify(bs)
        ev["detected_inner"] = kind

    if kind != "ntfs":
        _no_ntfs(ctx, dev, kind, bs)
        return

    bsi = parse_boot_sector(bs)
    ev["boot_sector"] = {k: v for k, v in bsi.items()}
    if bsi["problems"]:
        _bad_boot_sector(ctx, dev, bsi["problems"])
    else:
        part_size = _dev_size(dev)
        vol_bytes = (bsi["total_sectors"] + 1) * bsi["bytes_per_sector"]
        ev["ntfs_bytes"] = vol_bytes
        ev["partition_bytes"] = part_size
        if vol_bytes > part_size:
            ctx.add("critical", "winload", _(t"NTFS file system is larger than its partition"),
                    _(t"The partition was shrunk (or moved) without shrinking the NTFS volume first. Windows' boot "
                      t"loader and NTFS refuse such a volume or hit corruption at the end of the disk area, giving "
                      t"0xc0000225 / UNMOUNTABLE_BOOT_VOLUME."),
                    [f"NTFS size {human_size(vol_bytes)} ({bsi['total_sectors']} sectors)",
                     f"partition size {human_size(part_size)}"],
                    [_(t"Grow the partition back to at least the size of the file system. Use GParted, keep the start "
                       t"of the partition where it is and only move its end."),
                     WINRE, CHKDSK],
                    stopcode="0xc0000225 / 0x000000ED UNMOUNTABLE_BOOT_VOLUME", source=SRC, priority=5)
        with open(dev, "rb") as f:
            st = read_volume_state(f, bsi)
        ev["ntfs_state"] = st
        if st.get("corrupt"):
            ctx.add("critical", "winload", _(t"NTFS metadata ($MFT) is damaged"),
                    _(t"The master file table could not be read cleanly. Boot Manager and winload cannot reliably "
                      t"read files from this volume."), [st.get("error", "")],
                    [BACKUP_FIRST, WINRE, CHKDSK_R], stopcode="0xc0000098 / 0x00000024 NTFS_FILE_SYSTEM",
                    source=SRC, priority=10)
        elif st.get("dirty"):
            ctx.ntfs_dirty = True
            ctx.add("warning", "session", _(t"NTFS volume is marked dirty"),
                    _(t"Windows did not unmount the volume cleanly (crash, power loss, forced shutdown, or a disk "
                      t"check was requested). At the next start autochk runs; on a damaged disk this can hang or "
                      t"loop ('Scanning and repairing drive C:')."),
                    [f"$Volume flags = 0x{st['flags']:04x} (VOLUME_IS_DIRTY set), NTFS {st.get('version')}"],
                    [WINRE, CHKDSK,
                     _(t"Do not use the Linux tool ntfsfix for this: it only clears the flag without repairing "
                       t"anything.")],
                    source=SRC, priority=40)
        elif st.get("error"):
            ctx.log(f"$Volume state not readable: {st['error']}")

    # ---------------------------------------------------------------- mount
    em = existing_mount(ctx.target["path"])
    try:
        mp, how = ctx.mounts.mount_ro(dev, ["ntfs3", "ntfs-3g"], "windows")
    except MountError as e:
        ctx.add("critical", "winload", _(t"The Windows volume cannot be mounted"),
                _(t"Both Linux NTFS drivers refused the volume, which means its file-system structures are badly "
                  t"damaged. Boot Manager/winload will not be able to read Windows from it either."),
                [str(e)],
                [WINRE, CHKDSK_R,
                 LINUX, _(t"If chkdsk cannot open the volume either, copy the whole partition to an image file on "
                          t"another disk before trying anything else (replace the two paths):\n"
                          t"`sudo ddrescue {ctx.target['path']} /path/to/windows.img /path/to/windows.map`"),
                 _(t"Then let TestDisk look for the file system in the partition:\n"
                   t"`sudo testdisk {ctx.target['path']}`")],
                stopcode="0xc000000e / 0x000000ED UNMOUNTABLE_BOOT_VOLUME", source=SRC, priority=4)
        ctx.incomplete.append(_("Windows volume could not be mounted"))
        ctx.unanalyzed_stages.update(LATE_STAGES)
        return
    ev["mount"] = how
    ctx.win_mount = mp
    ctx.win = CIRoot(mp)
    ctx.log(f"Windows volume: {how}")

    if ctx.win.resolve("Windows\\System32") is None:
        ctx.add("critical", "winload", _(t"No Windows installation on this partition"),
                _(t"The volume mounts fine, but there is no \\Windows\\System32 directory. Either the wrong partition "
                  t"was selected, or the Windows directory was deleted."),
                ["top-level entries: " + ", ".join(ctx.win.listdir("")[:25])],
                [_(t"Go back and select the partition that contains the Windows folder.")], source=SRC, priority=3)
        ctx.incomplete.append(_("no Windows directory found"))
        ctx.unanalyzed_stages.update(LATE_STAGES)
        return
    ctx.windows_dir_ok = True

    # ---------------------------------------------------------------- hibernation / fast startup
    hp = ctx.win.resolve("hiberfil.sys")
    if hp is not None:
        try:
            with open(hp, "rb") as f:
                sig = f.read(4)
        except OSError:
            sig = b""
        ev["hiberfil_signature"] = sig.decode("latin-1", errors="replace")
        if sig.lower() in (b"hibr", b"wake"):
            ctx.hiberfile_state = "hibernated"
            rw_mounted = em is not None and not em[1]
            sev = "warning"
            ctx.add(sev, "bootmgr", _(t"Windows is hibernated / in Fast Startup state"),
                    _(t"hiberfil.sys contains a valid hibernation image, so Boot Manager will try to resume that "
                      t"image instead of booting fresh. If the disk was changed in the meantime (by Linux, by a "
                      t"partition tool, or a different PC) the resume crashes or the volume gets corrupted.")
                    + (_(t" The volume is currently mounted read-write by Linux, which is exactly that risk.") if rw_mounted else ""),
                    [f"hiberfil.sys header = {sig!r}"]
                    + ([f"currently mounted read-write at {em[0]}"] if rw_mounted else []),
                    [_(t"Try to start Windows normally first; it may simply resume."),
                     WINRE, _(t"If resuming fails, delete the hibernation image. Unsaved work from that session is "
                              t"lost, and Windows then starts fresh:\n`del /a C:\\hiberfil.sys`"),
                     WINDOWS, _(t"Turn hibernation and Fast Startup off so this cannot happen again:\n`powercfg /h off`")],
                    source=SRC, priority=30, actions=[A.discard_hibernation()])

    # ---------------------------------------------------------------- free space
    try:
        sv = os.statvfs(mp)
        free = sv.f_bavail * sv.f_frsize
        total = sv.f_blocks * sv.f_frsize
        ev["free_bytes"] = free
        ev["total_bytes"] = total
        if free < 256 * 1024 ** 2:
            ctx.add("critical", "session", _(t"Windows volume is full ({human_size(free)} free)"),
                    _(t"Windows needs free space during startup for the registry hives, the page file, logs and "
                      t"update servicing. With the volume full, startup hangs, loops or ends in a crash."),
                    [f"free {human_size(free)} of {human_size(total)}"],
                    [WINRE, _(t"Delete the downloaded update files (Windows downloads them again when needed):\n"
                              t"`rd /s /q C:\\Windows\\SoftwareDistribution\\Download`"),
                     _(t"Delete temporary files:\n`del /s /q C:\\Windows\\Temp\\*`"),
                     _(t"If that is not enough, move large personal files (videos, downloads) to another drive. "
                       t"Aim for at least 10 GB free.")], source=SRC, priority=20)
        elif free < 2 * 1024 ** 3:
            ctx.add("warning", "session", _(t"Very little free space on the Windows volume ({human_size(free)})"),
                    _(t"Updates fail and can roll back at boot when less than a few GB are free."),
                    [f"free {human_size(free)} of {human_size(total)}"],
                    [_(t"Delete or move large personal files until at least 10 GB are free.")], source=SRC)
    except OSError:
        pass


def _no_ntfs(ctx, dev, kind, bs):
    ev = ctx.evidence["volume"]
    backup = _backup_boot_sector(dev)
    if backup:
        ev["backup_boot_sector"] = "valid NTFS"
        ctx.add("critical", "winload", _(t"NTFS boot sector is destroyed (backup copy is intact)"),
                _(t"The first sector of the Windows volume no longer identifies it as NTFS, so nothing - neither "
                  t"Boot Manager nor Windows - can open the volume. The backup boot sector at the end of the "
                  t"partition is still valid, so this is repairable."),
                [f"{dev} sector 0: {kind}, OEM id {bs[3:11]!r}", "backup boot sector: valid NTFS"],
                _backup_bs_steps(dev, True),
                stopcode="0xc000000e / 0x000000ED UNMOUNTABLE_BOOT_VOLUME", source=SRC, priority=2)
    elif kind == "empty":
        ctx.add("critical", "winload", _(t"The selected partition is empty (no file system)"),
                _(t"The start of the partition is all zeros - the partition was wiped, re-created or overwritten."),
                [f"{dev} first 4 KiB are zero"],
                [_(t"Go back and check that you selected the right partition."),
                 LINUX, _(t"If Windows really was here, stop writing to this disk and search for the lost file "
                          t"system:\n`sudo testdisk {dev}`")],
                source=SRC, priority=2)
    else:
        ctx.add("critical", "winload", _(t"The selected partition does not contain NTFS (found: {kind})"),
                _(t"Windows can only be installed on NTFS. Either the wrong partition was selected or the volume "
                  t"was reformatted."), [f"{dev}: detected {kind}, lsblk fstype '{ctx.target['fstype']}'"],
                [_(t"Go back and select the partition that contains Windows.")], source=SRC, priority=2)
    ctx.incomplete.append(_("no readable NTFS volume"))
    ctx.unanalyzed_stages.update(LATE_STAGES)


def _bad_boot_sector(ctx, dev, problems):
    backup = _backup_boot_sector(dev)
    ctx.add("critical", "winload", _(t"NTFS boot sector is damaged"),
            _(t"The volume's boot sector has invalid geometry, so the volume cannot be opened by Boot Manager or "
              t"Windows.") + (_(t" The backup boot sector is still valid.") if backup else ""),
            problems + (["backup boot sector: valid"] if backup else ["backup boot sector: not valid"]),
            _backup_bs_steps(dev, backup),
            stopcode="0x000000ED UNMOUNTABLE_BOOT_VOLUME", source=SRC, priority=2)


def _backup_bs_steps(dev, has_backup):
    return [LINUX,
            _(t"Open the partition in TestDisk:\n`sudo testdisk {dev}`"),
            (_(t"Choose Advanced → Boot → “Backup BS”. That copies the intact backup boot sector over the damaged one.")
             if has_backup else
             _(t"Choose Advanced → Boot → “Rebuild BS”, let it search, and write the result if the file listing "
               t"(“List”) shows your files.")),
            WINRE, CHKDSK]


def _backup_boot_sector(dev):
    try:
        size = _dev_size(dev)
        for bps in (512, 4096):
            sec = _read(dev, size - bps, bps if bps == 512 else 4096)
            if identify(sec) == "ntfs" and not parse_boot_sector(sec)["problems"]:
                return True
    except OSError:
        pass
    return False
