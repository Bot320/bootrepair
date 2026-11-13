"""NTFS boot sector and $Volume state, read from the raw partition."""

import struct

VOLUME_DIRTY = 0x0001


def identify(sector):
    oem = sector[3:11]
    if oem == b"-FVE-FS-":
        return "bitlocker"
    if oem == b"NTFS    ":
        return "ntfs"
    if sector[3:8] == b"MSDOS" or sector[0x52:0x57] == b"FAT32" or sector[0x36:0x39] == b"FAT":
        return "fat"
    if sector[3:11] == b"EXFAT   ":
        return "exfat"
    if not any(sector):
        return "empty"
    return "unknown"


def parse_boot_sector(sector):
    """Return dict with geometry and a list of problems (empty = valid)."""
    bps = struct.unpack_from("<H", sector, 0x0B)[0]
    spc_raw = sector[0x0D]
    spc = spc_raw if spc_raw <= 0x80 else (1 << (256 - spc_raw))
    total = struct.unpack_from("<Q", sector, 0x28)[0]
    mft = struct.unpack_from("<Q", sector, 0x30)[0]
    mftmirr = struct.unpack_from("<Q", sector, 0x38)[0]
    rec_raw = struct.unpack_from("<b", sector, 0x40)[0]
    serial = struct.unpack_from("<Q", sector, 0x48)[0]
    problems = []
    if sector[3:11] != b"NTFS    ":
        problems.append("OEM id is not 'NTFS'")
    if bps not in (512, 1024, 2048, 4096):
        problems.append(f"invalid bytes per sector {bps}")
    if spc == 0 or spc & (spc - 1):
        problems.append(f"invalid sectors per cluster {spc_raw}")
    if sector[510:512] != b"\x55\xaa":
        problems.append("missing 0x55AA end-of-sector marker")
    cluster = bps * spc if not problems else 0
    rec_size = (rec_raw * cluster) if rec_raw > 0 else (1 << -rec_raw) if rec_raw < 0 else 0
    if not problems and rec_size not in (1024, 2048, 4096):
        problems.append(f"invalid MFT record size {rec_size}")
    return {"bytes_per_sector": bps, "sectors_per_cluster": spc, "total_sectors": total,
            "mft_lcn": mft, "mftmirr_lcn": mftmirr, "record_size": rec_size, "cluster_size": cluster,
            "serial": f"{serial:016X}", "problems": problems,
            "has_bootmgr_ref": b"B\x00O\x00O\x00T\x00M\x00G\x00R" in sector or b"BOOTMGR" in sector}


def apply_fixups(rec, bps):
    rec = bytearray(rec)
    usa_off, usa_cnt = struct.unpack_from("<HH", rec, 4)
    if usa_off + 2 * usa_cnt > len(rec):
        raise ValueError("bad update sequence array")
    usn = rec[usa_off:usa_off + 2]
    for i in range(1, usa_cnt):
        end = i * bps - 2
        if end + 2 > len(rec):
            break
        if rec[end:end + 2] != usn:
            raise ValueError(f"update sequence mismatch in sector {i} (torn write)")
        rec[end:end + 2] = rec[usa_off + 2 * i:usa_off + 2 * i + 2]
    return bytes(rec)


def read_volume_state(f, bs, part_offset=0):
    """Read $MFT record 3 ($Volume). Returns dict: version, flags, dirty, error."""
    out = {}
    try:
        off = part_offset + bs["mft_lcn"] * bs["cluster_size"] + 3 * bs["record_size"]
        f.seek(off)
        rec = f.read(bs["record_size"])
        sig = rec[:4]
        if sig == b"BAAD":
            out["error"] = "$Volume MFT record is marked BAAD (corrupt)"
            out["corrupt"] = True
            return out
        if sig != b"FILE":
            out["error"] = f"$MFT record 3 has signature {sig!r} instead of FILE"
            out["corrupt"] = True
            return out
        rec = apply_fixups(rec, bs["bytes_per_sector"])
        pos = struct.unpack_from("<H", rec, 0x14)[0]
        while pos + 16 < len(rec):
            atype, alen = struct.unpack_from("<II", rec, pos)
            if atype == 0xFFFFFFFF or alen == 0:
                break
            if atype == 0x70 and rec[pos + 8] == 0:   # $VOLUME_INFORMATION, resident
                coff = struct.unpack_from("<H", rec, pos + 0x14)[0]
                c = rec[pos + coff:pos + coff + 12]
                out["version"] = f"{c[8]}.{c[9]}"
                out["flags"] = struct.unpack_from("<H", c, 10)[0]
                out["dirty"] = bool(out["flags"] & VOLUME_DIRTY)
                return out
            pos += alen
        out["error"] = "$VOLUME_INFORMATION attribute not found"
    except (OSError, ValueError, struct.error) as e:
        out["error"] = str(e)
    return out
