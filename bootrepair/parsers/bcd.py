"""Boot Configuration Data (BCD) store parser.

The BCD store is a registry hive:  Objects\\{guid}\\Description\\Type  and
Objects\\{guid}\\Elements\\<element-type-hex>\\Element.
"""

import struct
import uuid

from .regf import Hive, RegfError, REG_SZ, REG_MULTI_SZ, REG_BINARY, REG_DWORD, REG_QWORD
from .util import guid_le

BOOTMGR = "{9dea862c-5cdd-4e70-acc1-f32b344d4795}"
FWBOOTMGR = "{a5a30fa2-3d06-4e9f-b5f4-a01df9d1fcba}"

WELL_KNOWN = {
    BOOTMGR: "{bootmgr}",
    FWBOOTMGR: "{fwbootmgr}",
    "{b2721d73-1db4-4c62-bf78-c548a880142d}": "{memdiag}",
    "{466f5a88-0af2-4f76-9038-095b170dc21c}": "{ntldr}",
    "{5189b25c-5558-4bf2-bca4-289b11bd29e2}": "{badmemory}",
    "{6efb52bf-1766-41db-a6b3-0ee5eff72bd7}": "{bootloadersettings}",
    "{4636856e-540f-4170-a130-a84776f4c654}": "{dbgsettings}",
    "{0ce4991b-e6b3-4b16-b23c-5e0d9250e5d9}": "{emssettings}",
    "{1afa9c49-16ab-4a5c-901b-212802da9460}": "{resumeloadersettings}",
    "{7ea2e1ac-2e61-4728-aaa3-896d9d0a9f0e}": "{globalsettings}",
    "{7ff607e0-4395-11db-b0de-0800200c9a66}": "{hypervisorsettings}",
    "{313e8eed-7098-4586-a9bf-309c61f8d449}": "{kerneldbgsettings}",
    "{ae5534e0-a924-466c-b836-758539a3ee3a}": "{ramdiskoptions}",
}

OBJECT_TYPES = {
    0x10100001: "Firmware Boot Manager",
    0x10100002: "Windows Boot Manager",
    0x10200003: "Windows Boot Loader",
    0x10200004: "Resume from Hibernate",
    0x10200005: "Windows Memory Tester",
    0x10300006: "Legacy OS Loader (ntldr)",
    0x10400008: "Boot Sector",
    0x101FFFFF: "Firmware application",
    0x20100000: "Inherited settings (library)",
    0x20200001: "Inherited settings (firmware bootmgr)",
    0x20200002: "Inherited settings (bootmgr)",
    0x20200003: "Inherited settings (OS loader)",
    0x20200004: "Inherited settings (resume)",
    0x20200005: "Inherited settings (memdiag)",
    0x30000000: "Device options",
}
TYPE_OSLOADER = 0x10200003
TYPE_RESUME = 0x10200004

# Element ids (see Microsoft's BcdLibraryElementTypes / BcdOSLoaderElementTypes / BcdBootMgrElementTypes)
E_DEVICE = 0x11000001
E_PATH = 0x12000002
E_DESCRIPTION = 0x12000004
E_INHERIT = 0x14000006
E_RECOVERYSEQUENCE = 0x14000008
E_RECOVERYENABLED = 0x16000009
E_DEBUG_LIB = 0x16000010
E_NOINTEGRITY = 0x16000048
E_TESTSIGNING = 0x16000049
E_OSDEVICE = 0x21000001          # osloader: osdevice ; resume: hiberfile device
E_SYSTEMROOT = 0x22000002        # osloader: systemroot ; resume: hiberfile path
E_RESUMEOBJECT = 0x23000003      # osloader: resumeobject ; bootmgr: default
E_KERNEL = 0x22000011
E_HAL = 0x22000012
E_NX = 0x25000020
E_SAFEBOOT = 0x25000080
E_SAFEBOOT_ALTSHELL = 0x26000081
E_BOOTLOG = 0x26000090
E_KERNEL_DEBUG = 0x260000A0
E_BOOTSTATUSPOLICY = 0x250000E0
E_WINPE = 0x26000022
E_DISPLAYORDER = 0x24000001
E_BOOTSEQUENCE = 0x24000002
E_DEFAULT = 0x23000003
E_TIMEOUT = 0x25000004
E_RESUME_BM = 0x23000006
E_TOOLSORDER = 0x24000010

ELEMENT_NAMES = {
    E_DEVICE: "device", E_PATH: "path", E_DESCRIPTION: "description", 0x12000005: "locale",
    E_INHERIT: "inherit", E_RECOVERYSEQUENCE: "recoverysequence", E_RECOVERYENABLED: "recoveryenabled",
    E_DEBUG_LIB: "bootdebug", E_NOINTEGRITY: "nointegritychecks", E_TESTSIGNING: "testsigning",
    E_OSDEVICE: "osdevice", E_SYSTEMROOT: "systemroot", E_RESUMEOBJECT: "resumeobject",
    E_KERNEL: "kernel", E_HAL: "hal", E_NX: "nx", E_SAFEBOOT: "safeboot",
    E_SAFEBOOT_ALTSHELL: "safebootalternateshell", E_BOOTLOG: "bootlog", E_KERNEL_DEBUG: "debug",
    E_BOOTSTATUSPOLICY: "bootstatuspolicy", E_WINPE: "winpe",
    E_DISPLAYORDER: "displayorder", E_BOOTSEQUENCE: "bootsequence", E_TIMEOUT: "timeout",
    E_RESUME_BM: "resumeobject", E_TOOLSORDER: "toolsdisplayorder",
    0x26000005: "resume", 0x26000020: "displaybootmenu", 0x16000060: "isolatedcontext",
    0x250000C2: "bootmenupolicy", 0x26000010: "detecthal", 0x26000025: "sos?",
}
SAFEBOOT_NAMES = {0: "minimal", 1: "network", 2: "dsrepair"}
BOOTSTATUS_NAMES = {0: "DisplayAllFailures", 1: "IgnoreAllFailures", 2: "IgnoreShutdownFailures",
                    3: "IgnoreBootFailures", 4: "IgnoreCheckpointFailures",
                    5: "DisplayShutdownFailures", 6: "DisplayBootFailures"}

DEVICE_KINDS = {5: "boot", 6: "partition", 8: "locate"}


def element_name(etype, obj_type=None):
    if etype == E_DEFAULT and obj_type in (0x10100002, 0x10100001):
        return "default"
    if obj_type == TYPE_RESUME:
        if etype == E_OSDEVICE:
            return "filedevice"
        if etype == E_SYSTEMROOT:
            return "filepath"
    return ELEMENT_NAMES.get(etype, f"0x{etype:08x}")


def decode_element(etype, value):
    """Decode a raw registry value of a BCD element according to its format nibble."""
    fmt = (etype >> 24) & 0xF
    data = value.data
    if fmt == 1:   # device
        return value.raw
    if fmt in (2, 3):  # string / object
        return data if isinstance(data, str) else str(data)
    if fmt == 4:   # object list
        return data if isinstance(data, list) else [data]
    if fmt == 5:   # integer
        if isinstance(data, int):
            return data
        return int.from_bytes(value.raw[:8].ljust(8, b"\0"), "little")
    if fmt == 6:   # boolean
        if isinstance(data, int):
            return bool(data)
        return any(value.raw)
    if fmt == 7:   # integer list
        raw = value.raw
        return [int.from_bytes(raw[i:i + 8], "little") for i in range(0, len(raw) - 7, 8)]
    return data


class BcdObject:
    def __init__(self, guid, otype, elements):
        self.guid = guid.lower()
        self.type = otype
        self.elements = elements   # {etype: decoded value}

    @property
    def alias(self):
        return WELL_KNOWN.get(self.guid, self.guid)

    @property
    def type_name(self):
        return OBJECT_TYPES.get(self.type, f"0x{self.type:08x}" if self.type is not None else "?")

    @property
    def description(self):
        return self.elements.get(E_DESCRIPTION, "")

    def get(self, etype, default=None):
        return self.elements.get(etype, default)


class BcdStore:
    def __init__(self, hive):
        self.hive = hive
        objs = hive.open("Objects")
        if objs is None:
            raise RegfError("BCD hive has no 'Objects' key - this is not a valid BCD store")
        self.objects = {}
        self.errors = []
        for k in objs.subkeys():
            try:
                otype = None
                d = k.subkey("Description")
                if d is not None:
                    otype = d.get("Type")
                elements = {}
                ek = k.subkey("Elements")
                if ek is not None:
                    for e in ek.subkeys():
                        try:
                            et = int(e.name, 16)
                        except ValueError:
                            continue
                        v = e.value("Element")
                        if v is not None:
                            elements[et] = decode_element(et, v)
                self.objects[k.name.lower()] = BcdObject(k.name, otype, elements)
            except (RegfError, struct.error) as ex:
                self.errors.append(f"object {k.name}: {ex}")

    @classmethod
    def from_file(cls, path):
        return cls(Hive.from_file(path))

    def get(self, guid):
        if not guid:
            return None
        return self.objects.get(guid.lower())

    @property
    def bootmgr(self):
        return self.get(BOOTMGR)

    def osloaders(self):
        return [o for o in self.objects.values() if o.type == TYPE_OSLOADER]


# ---------------------------------------------------------------- device elements

def parse_device(blob):
    """Decode the parts of a BCD device element we need.

    Layout of a partition device (0x58 bytes, verified against real Windows 11 stores):
      0x00 GUID additional options | 0x10 u32 device type (6=partition, 5=boot, 8=locate, 3=ramdisk...)
      0x18 u32 descriptor size (0x48)
      0x20 partition GUID (GPT) or u64 byte offset of the partition (MBR)
      0x34 u32 partition style (0=GPT, 1=MBR)
      0x38 disk GUID (GPT) or u32 disk signature (MBR)
    """
    info = {"kind": "unknown", "raw_len": len(blob)}
    if len(blob) < 0x14:
        info["kind"] = "empty"
        return info
    dtype = struct.unpack_from("<I", blob, 0x10)[0]
    info["type_code"] = dtype
    info["kind"] = DEVICE_KINDS.get(dtype, f"type {dtype}")
    if dtype == 6 and len(blob) >= 0x48:
        style = struct.unpack_from("<I", blob, 0x34)[0]
        if style == 0:
            info["style"] = "gpt"
            info["partition_guid"] = guid_le(blob, 0x20)
            info["disk_guid"] = guid_le(blob, 0x38)
        elif style == 1:
            info["style"] = "mbr"
            info["offset"] = struct.unpack_from("<Q", blob, 0x20)[0]
            info["signature"] = struct.unpack_from("<I", blob, 0x38)[0]
    elif len(blob) > 0x58:
        # ramdisk / vhd devices embed a nested partition device and a path
        txt = blob.decode("utf-16-le", errors="ignore")
        for frag in txt.split("\x00"):
            if "\\" in frag and len(frag) > 4 and frag.isprintable():
                info["path"] = frag
                info["kind"] = "ramdisk/file"
                break
    return info


def set_partition(blob, part):
    """Return a copy of a partition device element pointing at `part` (lsblk dict). Keeps everything else."""
    info = parse_device(blob)
    if info.get("kind") != "partition" or info.get("style") not in ("gpt", "mbr"):
        raise ValueError("not a plain partition device element")
    b = bytearray(blob)
    if (part.get("pttype") or "") == "gpt":
        struct.pack_into("<I", b, 0x34, 0)
        b[0x20:0x30] = uuid.UUID(part["partuuid"]).bytes_le
        b[0x38:0x48] = uuid.UUID(part["ptuuid"]).bytes_le
    elif (part.get("pttype") or "") == "dos":
        struct.pack_into("<I", b, 0x34, 1)
        b[0x20:0x30] = struct.pack("<Q", part["start_bytes"]) + b"\0" * 8
        b[0x38:0x48] = struct.pack("<I", int(part["ptuuid"].split("-")[0], 16)) + b"\0" * 12
    else:
        raise ValueError("unsupported partition table")
    return bytes(b)


def partition_patterns(part):
    """Byte patterns by which a BCD device element references the given partition."""
    pats = []
    pttype = (part.get("pttype") or "").lower()
    if pttype == "gpt" and part.get("partuuid"):
        try:
            pats.append(uuid.UUID(part["partuuid"]).bytes_le)
        except ValueError:
            pass
    elif pttype == "dos" and part.get("ptuuid") and part.get("start_bytes") is not None:
        try:
            sig = int(part["ptuuid"].split("-")[0], 16)
            pats.append((struct.pack("<Q", part["start_bytes"]), struct.pack("<I", sig)))
        except ValueError:
            pass
    return pats


def device_matches(blob, part):
    if not blob:
        return False
    for p in partition_patterns(part):
        if isinstance(p, tuple):
            if p[0] in blob and p[1] in blob:
                return True
        elif p in blob:
            return True
    return False


def resolve_device(blob, partitions):
    """Return (info dict, [names of matching partitions])."""
    info = parse_device(blob or b"")
    matches = [p["name"] for p in partitions if device_matches(blob, p)]
    return info, matches


def describe_device(info, matches):
    if matches:
        return "partition " + ", ".join("/dev/" + m for m in matches)
    k = info.get("kind")
    if k == "partition":
        if info.get("style") == "gpt":
            return (f"partition {info['partition_guid']} on disk {info['disk_guid']} "
                    "(NOT present on this computer)")
        if info.get("style") == "mbr":
            return (f"MBR partition at offset {info['offset']} on disk signature "
                    f"{info['signature']:08x} (NOT present on this computer)")
        return "partition (unrecognised layout)"
    if k == "boot":
        return "boot (the device Boot Manager was started from)"
    if k == "locate":
        return "locate (search all partitions)"
    if info.get("path"):
        return f"{k} {info['path']}"
    return k
