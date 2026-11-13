"""Minimal registry hive writer used to build test fixtures (SYSTEM / SOFTWARE / BCD)."""

import functools
import operator
import struct

REG_SZ, REG_EXPAND_SZ, REG_BINARY, REG_DWORD, REG_MULTI_SZ, REG_QWORD = 1, 2, 3, 4, 7, 11


def sz(s):
    return (REG_SZ, (s + "\x00").encode("utf-16-le"))


def esz(s):
    return (REG_EXPAND_SZ, (s + "\x00").encode("utf-16-le"))


def msz(items):
    return (REG_MULTI_SZ, ("\x00".join(items) + "\x00\x00").encode("utf-16-le"))


def dword(n):
    return (REG_DWORD, struct.pack("<I", n))


def binary(b):
    return (REG_BINARY, bytes(b))


class Key:
    def __init__(self, name, values=None, subkeys=None):
        self.name = name
        self.values = values or {}      # name -> (type, bytes)
        self.subkeys = subkeys or []

    def add(self, name, values=None):
        k = Key(name, values)
        self.subkeys.append(k)
        return k

    def path(self, path, values=None):
        k = self
        for part in path.split("\\"):
            nxt = next((s for s in k.subkeys if s.name.lower() == part.lower()), None)
            if nxt is None:
                nxt = k.add(part)
            k = nxt
        if values:
            k.values.update(values)
        return k


class _Writer:
    def __init__(self):
        self.buf = bytearray(b"\0" * 32)   # hbin header placeholder

    def cell(self, data):
        size = (len(data) + 4 + 7) & ~7
        off = len(self.buf)
        self.buf += struct.pack("<i", -size) + data + b"\0" * (size - 4 - len(data))
        return off

    def key(self, k, parent, root=False):
        name = k.name.encode("latin-1")
        # values first
        voffs = []
        for vn, (vt, vd) in k.values.items():
            if len(vd) <= 4:
                size, doff = len(vd) | 0x80000000, struct.unpack("<I", vd.ljust(4, b"\0"))[0]
            else:
                size, doff = len(vd), self.cell(vd)
            vname = vn.encode("latin-1")
            voffs.append(self.cell(b"vk" + struct.pack("<HIIIHH", len(vname), size, doff, vt, 1 if vname else 0, 0) + vname))
        vlist = self.cell(struct.pack(f"<{len(voffs)}I", *voffs)) if voffs else 0xFFFFFFFF
        # reserve nk cell, fill later (need subkey list)
        nk_size = 76 + len(name)
        nk_off = self.cell(b"\0" * nk_size)
        subs = [self.key(s, nk_off) for s in sorted(k.subkeys, key=lambda s: s.name.upper())]
        slist = 0xFFFFFFFF
        if subs:
            slist = self.cell(b"lh" + struct.pack("<H", len(subs)) + b"".join(struct.pack("<II", o, 0) for o in subs))
        flags = 0x20 | (0x0C if root else 0)
        nk = (b"nk" + struct.pack("<HQI", flags, 0, 0) + struct.pack("<I", parent if not root else 0)
              + struct.pack("<II", len(subs), 0) + struct.pack("<II", slist, 0xFFFFFFFF)
              + struct.pack("<II", len(voffs), vlist) + struct.pack("<II", 0xFFFFFFFF, 0xFFFFFFFF)
              + struct.pack("<IIIII", 0, 0, 0, 0, 0) + struct.pack("<HH", len(name), 0) + name)
        assert len(nk) == nk_size, (len(nk), nk_size)
        p = nk_off + 4
        self.buf[p:p + nk_size] = nk
        return nk_off


def build_hive(root, name="TEST", corrupt_checksum=False, seq=(1, 1)):
    w = _Writer()
    root_off = w.key(root, 0, root=True)
    size = (len(w.buf) + 4095) & ~4095
    free = size - len(w.buf)
    if free >= 8:
        w.buf += struct.pack("<i", free) + b"\0" * (free - 4)
    else:
        w.buf += b"\0" * free
    w.buf[0:32] = b"hbin" + struct.pack("<II", 0, size) + b"\0" * 20
    base = bytearray(4096)
    base[0:4] = b"regf"
    struct.pack_into("<IIQIIIIIII", base, 4, seq[0], seq[1], 0, 1, 5, 0, 1, root_off, size, 1)
    nm = name.encode("utf-16-le")[:64]
    base[48:48 + len(nm)] = nm
    x = functools.reduce(operator.xor, struct.unpack_from("<127I", base, 0), 0)
    if x == 0xFFFFFFFF:
        x = 0xFFFFFFFE
    elif x == 0:
        x = 1
    if corrupt_checksum:
        x ^= 0x1234
    struct.pack_into("<I", base, 508, x)
    return bytes(base) + bytes(w.buf)
