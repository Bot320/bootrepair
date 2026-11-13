"""Read-only parser for Windows XML Event Log (.evtx) files.

Decodes the binary XML of each record far enough to extract the System section
(provider, event id, level, time) and the EventData / UserData values.
"""

import struct
import uuid

from .util import filetime

CHUNK_SIZE = 0x10000
FILE_HEADER = 0x1000


class EvtxError(Exception):
    pass


class Elem:
    __slots__ = ("name", "attrs", "children")

    def __init__(self, name):
        self.name = name
        self.attrs = {}      # name -> list of parts (str | Sub | list[Elem])
        self.children = []   # parts: Elem | str | Sub

    def __repr__(self):
        return f"<{self.name} {self.attrs} {self.children}>"


class Sub:
    __slots__ = ("index", "optional")

    def __init__(self, index, optional):
        self.index = index
        self.optional = optional


class Node:
    """Instantiated element: plain data."""
    __slots__ = ("name", "attrs", "children")

    def __init__(self, name):
        self.name = name
        self.attrs = {}
        self.children = []   # Node | str

    def find(self, name):
        for c in self.children:
            if isinstance(c, Node) and c.name == name:
                return c
        return None

    def findall(self, name):
        return [c for c in self.children if isinstance(c, Node) and c.name == name]

    def text(self):
        out = []
        for c in self.children:
            out.append(c if isinstance(c, str) else c.text())
        return "".join(out)


def _sid(b):
    if len(b) < 8:
        return b.hex()
    rev, n = b[0], b[1]
    auth = int.from_bytes(b[2:8], "big")
    subs = struct.unpack_from(f"<{n}I", b, 8) if len(b) >= 8 + 4 * n else ()
    return "S-%d-%d" % (rev, auth) + "".join(f"-{s}" for s in subs)


def _systemtime(b):
    if len(b) < 16:
        return b.hex()
    y, mo, _dow, d, h, mi, s, ms = struct.unpack_from("<8H", b, 0)
    return f"{y:04d}-{mo:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}.{ms:03d}Z"


class Chunk:
    def __init__(self, evtx, offset):
        self.evtx = evtx
        self.offset = offset
        self.data = evtx.data[offset:offset + CHUNK_SIZE]
        if self.data[:8] != b"ElfChnk\x00":
            raise EvtxError("bad chunk signature")
        self.templates = {}
        self.names = {}

    # ---------------------------------------------------------------- primitives
    def name_at(self, off):
        n = self.names.get(off)
        if n is None:
            d = self.data
            ln = struct.unpack_from("<H", d, off + 6)[0]
            n = d[off + 8:off + 8 + 2 * ln].decode("utf-16-le", errors="replace")
            self.names[off] = n
        return n

    def _name_ref(self, pos):
        """Read a name offset at pos; skip an inline definition. Returns (name, new_pos)."""
        off = struct.unpack_from("<I", self.data, pos)[0]
        pos += 4
        name = self.name_at(off)
        if off == pos:
            ln = struct.unpack_from("<H", self.data, pos + 6)[0]
            pos += 8 + 2 * ln + 2
        return name, pos

    def _valid_name_off(self, off, pos):
        if off > pos or off < 0x200 or off + 8 > len(self.data):
            return False
        ln = struct.unpack_from("<H", self.data, off + 6)[0]
        return 0 < ln < 256 and off + 8 + 2 * ln + 2 <= len(self.data)

    # ---------------------------------------------------------------- binxml
    def parse(self, pos, end, in_template):
        """Parse binary XML between pos and end. Returns (list of top-level parts, pos)."""
        d = self.data
        root = Elem(None)
        stack = [root]
        attr_target = None     # list collecting the current attribute value
        in_start_tag = False
        while pos < end:
            tok = d[pos]
            base = tok & 0x0F
            if tok == 0x00:                      # EOF
                pos += 1
                break
            if tok == 0x0F:                      # fragment header
                pos += 4
            elif base == 0x01:                   # open start element
                p = pos + 1
                # Normally: u16 dependency id, u32 data size, u32 name offset,
                # [inline name], [u32 attribute list size if 0x41].
                name_off = struct.unpack_from("<I", d, p + 6)[0]
                if self._valid_name_off(name_off, p + 10):
                    p += 6
                else:                            # variant without the dependency id
                    p += 4
                name_off = struct.unpack_from("<I", d, p)[0]
                p += 4
                name = self.name_at(name_off)
                if name_off == p:
                    ln = struct.unpack_from("<H", d, p + 6)[0]
                    p += 8 + 2 * ln + 2
                if tok & 0x40:
                    p += 4
                el = Elem(name)
                stack[-1].children.append(el)
                stack.append(el)
                in_start_tag = True
                attr_target = None
                pos = p
            elif tok == 0x02:                    # close start element
                in_start_tag = False
                attr_target = None
                pos += 1
            elif tok in (0x03, 0x04):            # close empty / end element
                if len(stack) > 1:
                    stack.pop()
                in_start_tag = False
                attr_target = None
                pos += 1
            elif base == 0x06:                   # attribute
                name, pos = self._name_ref(pos + 1)
                attr_target = []
                stack[-1].attrs[name] = attr_target
            elif base == 0x05:                   # value text
                vtype = d[pos + 1]
                if vtype != 0x01:
                    raise EvtxError(f"unsupported inline value type {vtype}")
                ln = struct.unpack_from("<H", d, pos + 2)[0]
                s = d[pos + 4:pos + 4 + 2 * ln].decode("utf-16-le", errors="replace")
                pos += 4 + 2 * ln
                (attr_target if attr_target is not None else stack[-1].children).append(s)
            elif base == 0x07:                   # CDATA
                ln = struct.unpack_from("<H", d, pos + 1)[0]
                s = d[pos + 3:pos + 3 + 2 * ln].decode("utf-16-le", errors="replace")
                pos += 3 + 2 * ln
                stack[-1].children.append(s)
            elif base == 0x08:                   # char ref
                c = struct.unpack_from("<H", d, pos + 1)[0]
                pos += 3
                (attr_target if attr_target is not None else stack[-1].children).append(chr(c))
            elif base == 0x09:                   # entity ref
                name, pos = self._name_ref(pos + 1)
                s = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}.get(name, f"&{name};")
                (attr_target if attr_target is not None else stack[-1].children).append(s)
            elif tok == 0x0A:                    # PI target
                __, pos = self._name_ref(pos + 1)
            elif tok == 0x0B:                    # PI data
                ln = struct.unpack_from("<H", d, pos + 1)[0]
                pos += 3 + 2 * ln
            elif tok == 0x0C:                    # template instance
                nodes, pos = self.template_instance(pos)
                stack[-1].children.append(nodes)
            elif tok in (0x0D, 0x0E):            # substitution
                idx = struct.unpack_from("<H", d, pos + 1)[0]
                pos += 4
                sub = Sub(idx, tok == 0x0E)
                (attr_target if attr_target is not None else stack[-1].children).append(sub)
            else:
                raise EvtxError(f"unknown binxml token 0x{tok:02x} at chunk offset 0x{pos:x}")
        return root.children, pos

    def template_instance(self, pos):
        d = self.data
        tmpl_off = struct.unpack_from("<I", d, pos + 6)[0]
        pos += 10
        if tmpl_off >= pos:
            data_len = struct.unpack_from("<I", d, tmpl_off + 20)[0]
            tmpl = self.template_at(tmpl_off)
            pos = tmpl_off + 24 + data_len
        else:
            tmpl = self.template_at(tmpl_off)
        n = struct.unpack_from("<I", d, pos)[0]
        pos += 4
        if n > 4096:
            raise EvtxError("implausible substitution count")
        descs = [struct.unpack_from("<HB", d, pos + 4 * i) for i in range(n)]
        pos += 4 * n
        values = []
        for size, vtype in descs:
            values.append(self.decode_value(pos, size, vtype))
            pos += size
        return instantiate(tmpl, values), pos

    def template_at(self, off):
        t = self.templates.get(off)
        if t is None:
            data_len = struct.unpack_from("<I", self.data, off + 20)[0]
            t, __ = self.parse(off + 24, off + 24 + data_len, True)
            self.templates[off] = t
        return t

    def decode_value(self, pos, size, vtype):
        b = self.data[pos:pos + size]
        if vtype == 0x00:
            return None
        if vtype == 0x01:
            return b.decode("utf-16-le", errors="replace").rstrip("\x00")
        if vtype == 0x02:
            return b.decode("latin-1").rstrip("\x00")
        if vtype in (0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A):
            signed = vtype in (0x03, 0x05, 0x07, 0x09)
            return str(int.from_bytes(b, "little", signed=signed))
        if vtype == 0x0B and size == 4:
            return str(struct.unpack("<f", b)[0])
        if vtype == 0x0C and size == 8:
            return str(struct.unpack("<d", b)[0])
        if vtype == 0x0D:
            return "true" if int.from_bytes(b, "little") else "false"
        if vtype == 0x0E:
            return b.hex()
        if vtype == 0x0F and size == 16:
            return "{" + str(uuid.UUID(bytes_le=bytes(b))).upper() + "}"
        if vtype == 0x10:
            return "0x" + format(int.from_bytes(b, "little"), "x")
        if vtype == 0x11 and size == 8:
            dt = filetime(int.from_bytes(b, "little"))
            return dt.isoformat() if dt else ""
        if vtype == 0x12:
            return _systemtime(b)
        if vtype == 0x13:
            return _sid(b)
        if vtype == 0x14:
            return "0x%08x" % int.from_bytes(b, "little")
        if vtype == 0x15:
            return "0x%016x" % int.from_bytes(b, "little")
        if vtype == 0x21:
            nodes, __ = self.parse(pos, pos + size, False)
            return nodes
        if vtype == 0x81:
            return ", ".join(s for s in b.decode("utf-16-le", errors="replace").split("\x00") if s)
        return b.hex()


def instantiate(parts, values):
    out = []
    for p in parts:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, Sub):
            v = values[p.index] if p.index < len(values) else None
            if v is None:
                continue
            if isinstance(v, list):
                out.extend(_flatten(v))
            else:
                out.append(v)
        elif isinstance(p, Elem):
            # optional substitution elements whose only content is a null value are dropped
            n = Node(p.name)
            for an, aparts in p.attrs.items():
                vals = instantiate(aparts, values)
                n.attrs[an] = "".join(x if isinstance(x, str) else x.text() for x in vals)
            n.children = instantiate(p.children, values)
            out.append(n)
        elif isinstance(p, list):
            out.extend(_flatten(p))
    return out


def _flatten(parts):
    out = []
    for p in parts:
        if isinstance(p, list):
            out.extend(_flatten(p))
        else:
            out.append(p)
    return out


class Event:
    __slots__ = ("record_id", "time", "provider", "event_id", "level", "data", "computer")

    def __repr__(self):
        return f"<Event {self.time} {self.provider} {self.event_id} {self.data}>"

    def to_dict(self):
        return {"record_id": self.record_id, "time": self.time.isoformat() if self.time else "",
                "provider": self.provider, "event_id": self.event_id, "level": self.level,
                "data": self.data}


def _event_from_nodes(nodes, rid, rtime):
    ev = None
    for n in nodes:
        if isinstance(n, Node) and n.name == "Event":
            ev = n
            break
    if ev is None:
        return None
    e = Event()
    e.record_id = rid
    e.time = rtime
    e.provider = ""
    e.event_id = None
    e.level = None
    e.computer = ""
    e.data = {}
    sysn = ev.find("System")
    if sysn is not None:
        p = sysn.find("Provider")
        if p is not None:
            e.provider = p.attrs.get("Name") or p.attrs.get("EventSourceName") or ""
        i = sysn.find("EventID")
        if i is not None:
            try:
                e.event_id = int(i.text().strip())
            except ValueError:
                pass
        lv = sysn.find("Level")
        if lv is not None:
            try:
                e.level = int(lv.text().strip())
            except ValueError:
                pass
        c = sysn.find("Computer")
        if c is not None:
            e.computer = c.text()
    ed = ev.find("EventData")
    if ed is not None:
        for i, dn in enumerate(ed.findall("Data")):
            key = dn.attrs.get("Name") or f"param{i + 1}"
            e.data[key] = dn.text()
        b = ed.find("Binary")
        if b is not None and b.text():
            e.data["Binary"] = b.text()
    ud = ev.find("UserData")
    if ud is not None:
        def walk(n, prefix=""):
            leaf = True
            for c in n.children:
                if isinstance(c, Node):
                    leaf = False
                    walk(c, c.name)
            if leaf and prefix:
                e.data[prefix] = n.text()
        for c in ud.children:
            if isinstance(c, Node):
                walk(c, c.name)
    return e


class Evtx:
    def __init__(self, data):
        if data[:8] != b"ElfFile\x00":
            raise EvtxError("not an EVTX file (missing 'ElfFile' signature)")
        self.data = data
        self.flags = struct.unpack_from("<I", data, 120)[0]
        self.dirty = bool(self.flags & 1)
        self.full = bool(self.flags & 2)
        self.bad_chunks = 0
        self.bad_records = 0

    @classmethod
    def from_file(cls, path):
        with open(path, "rb") as f:
            return cls(f.read())

    def chunks(self):
        for off in range(FILE_HEADER, len(self.data) - CHUNK_SIZE + 1, CHUNK_SIZE):
            if self.data[off:off + 8] != b"ElfChnk\x00":
                if any(self.data[off:off + 512]):
                    self.bad_chunks += 1
                continue
            try:
                yield Chunk(self, off)
            except EvtxError:
                self.bad_chunks += 1

    def events(self, wanted=None):
        """Yield Event objects. `wanted(provider, event_id)` can filter early."""
        for ch in self.chunks():
            d = ch.data
            free = struct.unpack_from("<I", d, 48)[0]
            end = min(free, CHUNK_SIZE) if free >= 0x200 else CHUNK_SIZE
            pos = 0x200
            while pos + 24 <= end:
                if d[pos:pos + 4] != b"\x2a\x2a\x00\x00":
                    break
                size = struct.unpack_from("<I", d, pos + 4)[0]
                if size < 28 or pos + size > CHUNK_SIZE:
                    break
                rid, ts = struct.unpack_from("<QQ", d, pos + 8)
                try:
                    nodes, __ = ch.parse(pos + 24, pos + size - 4, False)
                    ev = _event_from_nodes(_flatten(nodes), rid, filetime(ts))
                    if ev is not None and (wanted is None or wanted(ev.provider, ev.event_id)):
                        yield ev
                except (EvtxError, struct.error, IndexError, KeyError, UnicodeDecodeError):
                    self.bad_records += 1
                pos += size
