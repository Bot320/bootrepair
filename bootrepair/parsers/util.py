"""Small helpers shared by the binary parsers."""

import struct
import uuid
from datetime import datetime, timedelta, timezone

_EPOCH_1601 = datetime(1601, 1, 1, tzinfo=timezone.utc)


def filetime(ft):
    """Convert a Windows FILETIME (100ns ticks since 1601) to an aware datetime, or None."""
    if not ft or ft >= 0x7FFFFFFFFFFFFFFF:
        return None
    try:
        dt = _EPOCH_1601 + timedelta(microseconds=ft // 10)
    except OverflowError:
        return None
    if dt.year < 1980 or dt.year > 2200:
        return None
    return dt


def iso(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC") if dt else ""


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]


def guid_le(b, o=0):
    """GUID stored in Windows (mixed-endian) byte order -> '{xxxxxxxx-...}' lowercase."""
    return "{" + str(uuid.UUID(bytes_le=bytes(b[o:o + 16]))) + "}"


def guid_bytes(s):
    """'{guid}' or 'guid' string -> on-disk mixed-endian bytes."""
    return uuid.UUID(s.strip("{}")).bytes_le


def utf16(b):
    if len(b) % 2:
        b = b[:-1]
    s = bytes(b).decode("utf-16-le", errors="replace")
    i = s.find("\x00")
    return s if i < 0 else s[:i]
