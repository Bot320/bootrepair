"""Read-only parser for Windows registry hive files (regf format).

Used for the SYSTEM / SOFTWARE / SAM / SECURITY / DEFAULT hives and for the BCD store
(which is a registry hive too).
"""

import functools
import operator
import re
import struct

from .util import filetime, utf16

REG_NONE = 0
REG_SZ = 1
REG_EXPAND_SZ = 2
REG_BINARY = 3
REG_DWORD = 4
REG_DWORD_BIG_ENDIAN = 5
REG_LINK = 6
REG_MULTI_SZ = 7
REG_QWORD = 11

HBIN_START = 4096
BIG_DATA_SEGMENT = 16344


class RegfError(Exception):
    pass


class Hive:
    def __init__(self, data, name=""):
        self.name = name
        if len(data) < HBIN_START:
            raise RegfError(f"file is only {len(data)} bytes, too small for a registry hive")
        if data[:4] != b"regf":
            raise RegfError("missing 'regf' signature: this is not a registry hive (corrupt or overwritten)")
        self.data = data
        (self.seq1, self.seq2, ts, self.major, self.minor, self.file_type, self.file_format,
         self.root_offset, self.bins_size) = struct.unpack_from("<IIQIIIIII", data, 4)
        self.last_written = filetime(ts)
        x = functools.reduce(operator.xor, struct.unpack_from("<127I", data, 0), 0)
        if x == 0xFFFFFFFF:
            x = 0xFFFFFFFE
        elif x == 0:
            x = 1
        self.stored_checksum = struct.unpack_from("<I", data, 508)[0]
        self.checksum_ok = x == self.stored_checksum
        self.sequence_ok = self.seq1 == self.seq2

    @classmethod
    def from_file(cls, path):
        with open(path, "rb") as f:
            return cls(f.read(), name=str(path))

    # ------------------------------------------------------------------ integrity
    def check_bins(self):
        """Walk the hive bins. Returns (bin_count, [error strings])."""
        errors = []
        off = HBIN_START
        end = HBIN_START + self.bins_size
        if end > len(self.data):
            errors.append(f"hive is truncated: header declares {self.bins_size} bytes of hive bins, "
                          f"file only contains {len(self.data) - HBIN_START}")
            end = len(self.data)
        n = 0
        while off < end:
            if self.data[off:off + 4] != b"hbin":
                errors.append(f"invalid hive bin signature at file offset 0x{off:x}")
                break
            rel, size = struct.unpack_from("<II", self.data, off + 4)
            if rel != off - HBIN_START:
                errors.append(f"hive bin at 0x{off:x} records wrong offset 0x{rel:x}")
            if size < 4096 or size % 4096:
                errors.append(f"hive bin at 0x{off:x} has invalid size {size}")
                break
            off += size
            n += 1
        return n, errors

    def walk_check(self, limit=400000):
        """Visit every key and value list; returns list of (path, error)."""
        problems = []
        stack = [("", self.root_offset)]
        seen = 0
        while stack and seen < limit:
            path, off = stack.pop()
            seen += 1
            try:
                k = Key(self, off)
                kp = f"{path}\\{k.name}" if path else k.name
                for sub_off in k.subkey_offsets():
                    stack.append((kp, sub_off))
                for v in k.values():
                    __ = v.raw
            except (RegfError, struct.error, IndexError) as e:
                problems.append((path or "<root>", str(e)))
                if len(problems) > 50:
                    break
        return problems

    # ------------------------------------------------------------------ cells
    def cell(self, off):
        if off in (0, 0xFFFFFFFF):
            raise RegfError("null cell reference")
        p = HBIN_START + off
        if p + 4 > len(self.data):
            raise RegfError(f"cell offset 0x{off:x} points outside the hive")
        size = struct.unpack_from("<i", self.data, p)[0]
        if size >= 0:
            raise RegfError(f"cell 0x{off:x} is marked free but still referenced")
        size = -size
        if size < 8 or p + size > len(self.data):
            raise RegfError(f"cell 0x{off:x} has invalid size {size}")
        return self.data[p + 4:p + size]

    @property
    def root(self):
        return Key(self, self.root_offset)

    def open(self, path):
        """Open a key by backslash-separated path relative to the root (case-insensitive)."""
        k = self.root
        for part in [p for p in re.split(r"[\\/]+", path) if p]:
            k = k.subkey(part)
            if k is None:
                return None
        return k

    def get(self, path, value, default=None):
        k = self.open(path)
        if k is None:
            return default
        v = k.value(value)
        return default if v is None else v.data


class Key:
    __slots__ = ("hive", "offset", "name", "flags", "timestamp", "subkey_count",
                 "subkey_list", "value_count", "value_list", "_subindex")

    def __init__(self, hive, off):
        c = hive.cell(off)
        if c[:2] != b"nk":
            raise RegfError(f"expected key node (nk) at cell 0x{off:x}, found {bytes(c[:2])!r}")
        self.hive = hive
        self.offset = off
        self.flags, ts = struct.unpack_from("<HQ", c, 2)
        self.timestamp = filetime(ts)
        self.subkey_count = struct.unpack_from("<I", c, 20)[0]
        self.subkey_list = struct.unpack_from("<I", c, 28)[0]
        self.value_count = struct.unpack_from("<I", c, 36)[0]
        self.value_list = struct.unpack_from("<I", c, 40)[0]
        name_len = struct.unpack_from("<H", c, 72)[0]
        raw = c[76:76 + name_len]
        self.name = bytes(raw).decode("latin-1") if self.flags & 0x20 else utf16(raw)
        self._subindex = None

    def __repr__(self):
        return f"<Key {self.name}>"

    def _list_offsets(self, off, depth=0):
        if depth > 8:
            raise RegfError("subkey index nested too deeply")
        c = self.hive.cell(off)
        sig = bytes(c[:2])
        n = struct.unpack_from("<H", c, 2)[0]
        if sig in (b"lf", b"lh"):
            return [struct.unpack_from("<I", c, 4 + 8 * i)[0] for i in range(n)]
        if sig == b"li":
            return list(struct.unpack_from(f"<{n}I", c, 4))
        if sig == b"ri":
            out = []
            for sub in struct.unpack_from(f"<{n}I", c, 4):
                out.extend(self._list_offsets(sub, depth + 1))
            return out
        raise RegfError(f"invalid subkey list signature {sig!r} under key '{self.name}'")

    def subkey_offsets(self):
        if self.subkey_count == 0 or self.subkey_list in (0, 0xFFFFFFFF):
            return []
        return self._list_offsets(self.subkey_list)

    def subkeys(self):
        return [Key(self.hive, o) for o in self.subkey_offsets()]

    def subkey(self, name):
        if self._subindex is None:
            self._subindex = {}
            for o in self.subkey_offsets():
                try:
                    k = Key(self.hive, o)
                except RegfError:
                    continue
                self._subindex[k.name.lower()] = k
        return self._subindex.get(name.lower())

    def values(self):
        if self.value_count == 0 or self.value_list in (0, 0xFFFFFFFF):
            return []
        c = self.hive.cell(self.value_list)
        n = min(self.value_count, len(c) // 4)
        return [Value(self.hive, o) for o in struct.unpack_from(f"<{n}I", c, 0)]

    def value(self, name):
        name = name.lower()
        for v in self.values():
            if v.name.lower() == name:
                return v
        return None

    def get(self, name, default=None):
        v = self.value(name)
        return default if v is None else v.data


class Value:
    __slots__ = ("hive", "name", "type", "_size", "_off", "offset")

    def __init__(self, hive, off):
        c = hive.cell(off)
        if c[:2] != b"vk":
            raise RegfError(f"expected value (vk) at cell 0x{off:x}")
        self.hive = hive
        self.offset = off
        name_len, self._size, self._off, self.type, flags = struct.unpack_from("<HIIIH", c, 2)
        raw = c[20:20 + name_len]
        self.name = bytes(raw).decode("latin-1") if flags & 1 else utf16(raw)

    @property
    def raw(self):
        size = self._size
        if size & 0x80000000:
            size &= 0x7FFFFFFF
            return struct.pack("<I", self._off)[:min(size, 4)]
        if size == 0:
            return b""
        if size > BIG_DATA_SEGMENT and self.hive.minor >= 4:
            db = self.hive.cell(self._off)
            if db[:2] == b"db":
                n, seglist = struct.unpack_from("<HI", db, 2)
                segs = self.hive.cell(seglist)
                parts = [bytes(self.hive.cell(o)[:BIG_DATA_SEGMENT])
                         for o in struct.unpack_from(f"<{n}I", segs, 0)]
                return b"".join(parts)[:size]
        d = self.hive.cell(self._off)
        if len(d) < size:
            raise RegfError(f"value '{self.name}' data is truncated")
        return bytes(d[:size])

    @property
    def data(self):
        raw = self.raw
        t = self.type
        if t in (REG_SZ, REG_EXPAND_SZ, REG_LINK):
            return utf16(raw)
        if t == REG_MULTI_SZ:
            if len(raw) % 2:
                raw = raw[:-1]
            items = raw.decode("utf-16-le", errors="replace").split("\x00")
            return [s for s in items if s]
        if t == REG_DWORD:
            return int.from_bytes(raw[:4].ljust(4, b"\0"), "little")
        if t == REG_DWORD_BIG_ENDIAN:
            return int.from_bytes(raw[:4].rjust(4, b"\0"), "big")
        if t == REG_QWORD:
            return int.from_bytes(raw[:8].ljust(8, b"\0"), "little")
        return raw
