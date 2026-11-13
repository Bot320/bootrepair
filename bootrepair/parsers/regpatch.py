"""In-place registry hive editing.

Only edits that fit into the existing cell layout are supported: changing a value's data
(same size or smaller), deleting values and deleting keys. Nothing is ever appended or
reorganised, so the hive structure Windows wrote stays intact. Every change is written
to the exact byte ranges it touches.
"""

import os
import struct

from .regf import Hive, Key, RegfError, HBIN_START, REG_DWORD, REG_SZ, REG_EXPAND_SZ, REG_MULTI_SZ, REG_BINARY


class PatchError(Exception):
    pass


class HivePatcher:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.data = bytearray(f.read())
        self.hive = Hive(bytes(self.data))
        self.dirty = []
        self.changes = []

    # ------------------------------------------------------------------ low level
    def _w(self, pos, b):
        self.data[pos:pos + len(b)] = b
        self.dirty.append((pos, len(b)))

    def _reparse(self):
        self.hive = Hive(bytes(self.data))

    def _cell_pos(self, off):
        return HBIN_START + off

    def _cell_capacity(self, off):
        size = struct.unpack_from("<i", self.data, self._cell_pos(off))[0]
        if size >= 0:
            raise PatchError(f"cell 0x{off:x} is not allocated")
        return -size - 4

    def _free_cell(self, off):
        p = self._cell_pos(off)
        size = struct.unpack_from("<i", self.data, p)[0]
        if size < 0:
            self._w(p, struct.pack("<i", -size))

    def _key(self, path):
        k = self.hive.open(path)
        if k is None:
            raise PatchError(f"registry key not found: {path}")
        return k

    def _value(self, path, name):
        k = self._key(path)
        v = k.value(name)
        if v is None:
            raise PatchError(f"value not found: {path}\\{name}")
        return k, v

    # ------------------------------------------------------------------ values
    def get(self, path, name, default=None):
        k = self.hive.open(path)
        if k is None:
            return default
        v = k.value(name)
        return default if v is None else v.data

    def set_data(self, path, name, raw):
        """Replace the raw data of an existing value (must not grow beyond its cell)."""
        k, v = self._value(path, name)
        vk = self._cell_pos(v.offset) + 4
        size = v._size
        n = len(raw)
        if size & 0x80000000:                 # data stored inline in the vk cell
            if n > 4:
                raise PatchError(f"{name}: new data does not fit (inline value)")
            self._w(vk + 4, struct.pack("<I", n | 0x80000000))
            self._w(vk + 8, raw.ljust(4, b"\0"))
        else:
            if size > 16344 and self.hive.minor >= 4:
                raise PatchError(f"{name}: big-data values are not supported")
            if n > self._cell_capacity(v._off):
                raise PatchError(f"{name}: new data is larger than the existing cell")
            self._w(self._cell_pos(v._off) + 4, raw)
            self._w(vk + 4, struct.pack("<I", n))
        self.changes.append(f"{path}\\{name}: data replaced ({size & 0x7FFFFFFF} -> {n} bytes)")
        self._reparse()

    def set_dword(self, path, name, value):
        k, v = self._value(path, name)
        if v.type != REG_DWORD:
            raise PatchError(f"{path}\\{name} is not a REG_DWORD")
        old = v.data
        self.set_data(path, name, struct.pack("<I", value))
        self.changes[-1] = f"{path}\\{name}: {old} -> {value}"

    def set_string(self, path, name, text):
        k, v = self._value(path, name)
        if v.type not in (REG_SZ, REG_EXPAND_SZ):
            raise PatchError(f"{path}\\{name} is not a string")
        old = v.data
        self.set_data(path, name, (text + "\0").encode("utf-16-le"))
        self.changes[-1] = f"{path}\\{name}: '{old}' -> '{text}'"

    def set_multi_sz(self, path, name, items):
        k, v = self._value(path, name)
        if v.type != REG_MULTI_SZ:
            raise PatchError(f"{path}\\{name} is not a REG_MULTI_SZ")
        old = v.data
        self.set_data(path, name, ("\0".join(items) + "\0\0").encode("utf-16-le") if items else b"\0\0")
        self.changes[-1] = f"{path}\\{name}: {old} -> {items}"

    def set_binary(self, path, name, raw):
        k, v = self._value(path, name)
        if v.type != REG_BINARY:
            raise PatchError(f"{path}\\{name} is not REG_BINARY")
        self.set_data(path, name, raw)

    def delete_value(self, path, name):
        k, v = self._value(path, name)
        nk = self._cell_pos(k.offset) + 4
        offs = [x.offset for x in k.values()]
        idx = offs.index(v.offset)
        rest = offs[:idx] + offs[idx + 1:]
        lp = self._cell_pos(k.value_list) + 4
        self._w(lp, struct.pack(f"<{len(offs)}I", *(rest + [0])))
        self._w(nk + 36, struct.pack("<I", len(rest)))
        if not (v._size & 0x80000000) and v._size:
            self._free_cell(v._off)
        self._free_cell(v.offset)
        self.changes.append(f"{path}\\{name}: value deleted")
        self._reparse()

    # ------------------------------------------------------------------ keys
    def delete_key(self, path):
        """Delete a key and everything below it."""
        parts = [p for p in path.replace("/", "\\").split("\\") if p]
        if not parts:
            raise PatchError("cannot delete the root key")
        parent_path = "\\".join(parts[:-1])
        parent = self.hive.open(parent_path) if parent_path else self.hive.root
        if parent is None:
            raise PatchError(f"key not found: {parent_path}")
        k = parent.subkey(parts[-1])
        if k is None:
            raise PatchError(f"key not found: {path}")
        self._delete_tree(k)
        # unlink from the parent's subkey list
        lst = self.hive.cell(parent.subkey_list)
        sig = bytes(lst[:2])
        if sig not in (b"lf", b"lh", b"li"):
            raise PatchError(f"parent subkey list type {sig!r} is not supported")
        n = struct.unpack_from("<H", lst, 2)[0]
        width = 8 if sig in (b"lf", b"lh") else 4
        entries = [bytes(lst[4 + i * width:4 + (i + 1) * width]) for i in range(n)]
        keep = [e for e in entries if struct.unpack_from("<I", e, 0)[0] != k.offset]
        if len(keep) != n - 1:
            raise PatchError("key not found in its parent's subkey list")
        lp = self._cell_pos(parent.subkey_list) + 4
        self._w(lp + 2, struct.pack("<H", len(keep)) + b"".join(keep) + b"\0" * width)
        pnk = self._cell_pos(parent.offset) + 4
        self._w(pnk + 20, struct.pack("<I", parent.subkey_count - 1))
        self.changes.append(f"{path}: key deleted")
        self._reparse()

    def _delete_tree(self, k):
        for sub in k.subkeys():
            self._delete_tree(sub)
        for v in k.values():
            if not (v._size & 0x80000000) and v._size:
                self._free_cell(v._off)
            self._free_cell(v.offset)
        if k.value_count and k.value_list not in (0, 0xFFFFFFFF):
            self._free_cell(k.value_list)
        if k.subkey_count and k.subkey_list not in (0, 0xFFFFFFFF):
            lst = self.hive.cell(k.subkey_list)
            if bytes(lst[:2]) == b"ri":
                raise PatchError("indexed (ri) subkey lists are not supported")
            self._free_cell(k.subkey_list)
        self._free_cell(k.offset)

    # ------------------------------------------------------------------ commit
    def verify(self):
        h = Hive(bytes(self.data))
        n, errs = h.check_bins()
        probs = h.walk_check(limit=500000)
        if errs or probs:
            raise PatchError(f"verification failed: {errs[:2]} {probs[:2]}")

    def commit(self):
        if not self.dirty:
            return []
        self.verify()
        with open(self.path, "r+b") as f:
            for pos, n in sorted(set(self.dirty)):
                f.seek(pos)
                f.write(self.data[pos:pos + n])
            f.flush()
            os.fsync(f.fileno())
        with open(self.path, "rb") as f:
            if f.read() != bytes(self.data):
                raise PatchError("read-back after writing does not match")
        self.dirty = []
        return self.changes
