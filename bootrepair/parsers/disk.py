"""Partition table (MBR / GPT) parser working on raw sectors."""

import struct
import zlib

from .util import guid_le

ESP_GUID = "{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}"


def parse_mbr(sector0):
    info = {"signature_ok": sector0[510:512] == b"\x55\xaa",
            "disk_signature": struct.unpack_from("<I", sector0, 440)[0],
            "bootcode_empty": not any(sector0[:440]),
            "bootcode": _identify_bootcode(sector0[:440]),
            "partitions": []}
    for i in range(4):
        e = sector0[446 + 16 * i:446 + 16 * (i + 1)]
        status, ptype = e[0], e[4]
        start, size = struct.unpack_from("<II", e, 8)
        if ptype == 0:
            continue
        info["partitions"].append({"index": i + 1, "active": status == 0x80, "status": status,
                                   "type": ptype, "start_lba": start, "sectors": size})
    info["protective"] = any(p["type"] == 0xEE for p in info["partitions"])
    return info


def _identify_bootcode(code):
    if not any(code):
        return "empty"
    if b"GRUB" in code:
        return "GRUB"
    if b"Invalid partition table" in code or b"Missing operating system" in code:
        return "Windows"
    if b"SYSLINUX" in code or b"MBR" in code[:16]:
        return "Syslinux/other"
    return "unknown"


def parse_gpt_header(buf, lba_size):
    """buf: bytes of the header sector. Returns dict (with 'valid')."""
    h = {"valid": False}
    if buf[:8] != b"EFI PART":
        h["error"] = "no 'EFI PART' signature"
        return h
    hsize = struct.unpack_from("<I", buf, 12)[0]
    if hsize < 92 or hsize > lba_size:
        h["error"] = f"invalid header size {hsize}"
        return h
    stored = struct.unpack_from("<I", buf, 16)[0]
    tmp = bytearray(buf[:hsize])
    tmp[16:20] = b"\0\0\0\0"
    h["header_crc_ok"] = (zlib.crc32(bytes(tmp)) & 0xFFFFFFFF) == stored
    (h["current_lba"], h["backup_lba"], h["first_usable"], h["last_usable"]) = struct.unpack_from("<4Q", buf, 24)
    h["disk_guid"] = guid_le(buf, 56)
    h["entries_lba"], = struct.unpack_from("<Q", buf, 72)
    h["num_entries"], h["entry_size"], h["entries_crc"] = struct.unpack_from("<III", buf, 80)
    h["valid"] = h["header_crc_ok"]
    if not h["header_crc_ok"]:
        h["error"] = "header CRC32 mismatch"
    return h


def check_gpt_entries(entries, header):
    return (zlib.crc32(entries) & 0xFFFFFFFF) == header["entries_crc"]


def parse_gpt_entries(entries, header):
    out = []
    es = header["entry_size"]
    for i in range(header["num_entries"]):
        e = entries[i * es:(i + 1) * es]
        if len(e) < 128 or not any(e[:16]):
            continue
        first, last, attrs = struct.unpack_from("<QQQ", e, 32)
        out.append({"index": i + 1, "type_guid": guid_le(e, 0), "part_guid": guid_le(e, 16),
                    "first_lba": first, "last_lba": last, "attrs": attrs,
                    "name": e[56:128].decode("utf-16-le", errors="replace").split("\x00")[0]})
    return out
