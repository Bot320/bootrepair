"""Kernel crash dump header parser (MEMORY.DMP, Minidump\\*.dmp, LiveKernelReports)."""

import struct

from .util import filetime

DUMP_TYPES = {1: "full", 2: "kernel", 3: "header only", 4: "triage (minidump)", 5: "bitmap full",
              6: "bitmap kernel", 7: "automatic"}


class DumpError(Exception):
    pass


def parse_dump_header(head):
    """Parse the first 8 KiB of a kernel dump. Returns dict or raises DumpError."""
    if len(head) < 0x60:
        raise DumpError("file too small")
    sig = head[:8]
    if sig == b"PAGEDU64":
        major, minor = struct.unpack_from("<II", head, 0x08)
        code = struct.unpack_from("<I", head, 0x38)[0]
        params = list(struct.unpack_from("<4Q", head, 0x40))
        dump_type = struct.unpack_from("<I", head, 0xF98)[0] if len(head) >= 0xFA0 else None
        ts = struct.unpack_from("<Q", head, 0xFA8)[0] if len(head) >= 0xFB0 else 0
        arch = "x64"
    elif sig == b"PAGEDUMP":
        major, minor = struct.unpack_from("<II", head, 0x08)
        code = struct.unpack_from("<I", head, 0x20)[0]
        params = list(struct.unpack_from("<4I", head, 0x24))
        dump_type = struct.unpack_from("<I", head, 0xF88)[0] if len(head) >= 0xF8C else None
        ts = struct.unpack_from("<Q", head, 0xFC0)[0] if len(head) >= 0xFC8 else 0
        arch = "x86"
    elif sig[:4] == b"MDMP":
        raise DumpError("user-mode minidump (not a kernel crash)")
    else:
        raise DumpError(f"unknown dump signature {sig!r}")
    return {
        "code": code,
        "params": params,
        "build": minor,
        "arch": arch,
        "dump_type": DUMP_TYPES.get(dump_type, str(dump_type) if dump_type is not None else ""),
        "time": filetime(ts),
    }
