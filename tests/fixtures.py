"""Builds a fake disk + Windows installation on the local file system so the whole pipeline
can run without root, real disks or mounting."""

import os
import struct
import uuid
import zlib
from pathlib import Path

from hivebuilder import Key, build_hive, sz, esz, msz, dword, binary

DISK_GUID = "6f1c2b9e-1111-4c4c-9e9e-0123456789ab"
ESP_GUID = "0e0e0e0e-2222-4d4d-8a8a-aaaaaaaaaaaa"
WIN_GUID = "1a1a1a1a-3333-4e4e-9b9b-bbbbbbbbbbbb"
GONE_GUID = "deadbeef-4444-4f4f-8c8c-cccccccccccc"
LOADER = "{11111111-2222-3333-4444-555555555555}"
BOOTMGR = "{9dea862c-5cdd-4e70-acc1-f32b344d4795}"
ESP_TYPE = "c12a7328-f81f-11d2-ba4b-00a0c93ec93b"
BASIC_TYPE = "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7"

ESP_START = 2048 * 512
WIN_START = 4096 * 512


def device_blob(part_guid, disk_guid=DISK_GUID):
    b = bytearray(0x58)
    struct.pack_into("<I", b, 0x10, 6)
    struct.pack_into("<I", b, 0x18, 0x48)
    b[0x20:0x30] = uuid.UUID(part_guid).bytes_le
    struct.pack_into("<I", b, 0x34, 0)
    b[0x38:0x48] = uuid.UUID(disk_guid).bytes_le
    return bytes(b)


def write_gpt_disk(path, size=64 * 1024 * 1024):
    lbs = 512
    lbas = size // lbs
    with open(path, "wb") as f:
        f.truncate(size)
    entries = bytearray(128 * 128)
    for i, (t, g, first, last, name) in enumerate([
            (ESP_TYPE, ESP_GUID, ESP_START // 512, WIN_START // 512 - 1, "EFI"),
            (BASIC_TYPE, WIN_GUID, WIN_START // 512, lbas - 40, "Windows")]):
        e = uuid.UUID(t).bytes_le + uuid.UUID(g).bytes_le + struct.pack("<QQQ", first, last, 0)
        e += name.encode("utf-16-le").ljust(72, b"\0")
        entries[i * 128:(i + 1) * 128] = e
    ecrc = zlib.crc32(bytes(entries)) & 0xFFFFFFFF

    def header(cur, backup, entries_lba):
        h = bytearray(92)
        h[0:8] = b"EFI PART"
        struct.pack_into("<IIII", h, 8, 0x00010000, 92, 0, 0)
        struct.pack_into("<QQQQ", h, 24, cur, backup, 34, lbas - 34)
        h[56:72] = uuid.UUID(DISK_GUID).bytes_le
        struct.pack_into("<QIII", h, 72, entries_lba, 128, 128, ecrc)
        struct.pack_into("<I", h, 16, zlib.crc32(bytes(h)) & 0xFFFFFFFF)
        return bytes(h).ljust(lbs, b"\0")

    mbr = bytearray(512)
    mbr[446:462] = bytes([0, 0, 2, 0, 0xEE, 0xFF, 0xFF, 0xFF]) + struct.pack("<II", 1, min(lbas - 1, 0xFFFFFFFF))
    mbr[510:512] = b"\x55\xaa"
    with open(path, "r+b") as f:
        f.write(mbr)
        f.write(header(1, lbas - 1, 2))
        f.write(entries)
        f.seek((lbas - 33) * lbs)
        f.write(entries)
        f.write(header(lbas - 1, 1, lbas - 33))


def write_ntfs_partition(path, size=32 * 1024 * 1024, dirty=False):
    bps, spc = 512, 8
    bs = bytearray(512)
    bs[0:3] = b"\xeb\x52\x90"
    bs[3:11] = b"NTFS    "
    struct.pack_into("<H", bs, 0x0B, bps)
    bs[0x0D] = spc
    struct.pack_into("<Q", bs, 0x28, size // bps - 1)
    struct.pack_into("<Q", bs, 0x30, 4)
    struct.pack_into("<Q", bs, 0x38, 2)
    struct.pack_into("<b", bs, 0x40, -10)
    bs[0x1A0:0x1A0 + 14] = "BOOTMGR".encode("utf-16-le")
    bs[510:512] = b"\x55\xaa"
    rec = bytearray(1024)
    rec[0:4] = b"FILE"
    struct.pack_into("<HH", rec, 4, 0x30, 3)
    struct.pack_into("<H", rec, 0x14, 0x38)
    usn = b"\x07\x00"
    rec[0x30:0x32] = usn
    attr = bytearray(0x28)
    struct.pack_into("<II", attr, 0, 0x70, 0x28)
    attr[8] = 0
    struct.pack_into("<IH", attr, 0x10, 12, 0x18)
    attr[0x18 + 8] = 3
    attr[0x18 + 9] = 1
    struct.pack_into("<H", attr, 0x18 + 10, 1 if dirty else 0)
    rec[0x38:0x38 + 0x28] = attr
    struct.pack_into("<I", rec, 0x60, 0xFFFFFFFF)
    for i in (1, 2):
        end = i * 512 - 2
        rec[0x30 + 2 * i:0x32 + 2 * i] = rec[end:end + 2]
        rec[end:end + 2] = usn
    with open(path, "wb") as f:
        f.truncate(size)
        f.write(bs)
        f.seek(4 * 4096 + 3 * 1024)
        f.write(rec)
        f.seek(size - 512)
        f.write(bs)


def _touch(root, rel, data=b"MZ\x90\x00" + b"\x01" * 60):
    p = Path(root, *rel.split("\\"))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


def build_bcd(win_guid=WIN_GUID, esp_guid=ESP_GUID, safeboot=False):
    root = Key("{5cd9c3d1-1111-2222-3333-444444444444}")
    objs = root.add("Objects")
    bm = objs.add(BOOTMGR)
    bm.path("Description", {"Type": dword(0x10100002)})
    bm.path("Elements\\23000003", {"Element": sz(LOADER)})
    bm.path("Elements\\24000001", {"Element": msz([LOADER])})
    bm.path("Elements\\11000001", {"Element": binary(device_blob(esp_guid))})
    bm.path("Elements\\12000004", {"Element": sz("Windows Boot Manager")})
    ld = objs.add(LOADER)
    ld.path("Description", {"Type": dword(0x10200003)})
    ld.path("Elements\\12000004", {"Element": sz("Windows 11")})
    ld.path("Elements\\11000001", {"Element": binary(device_blob(win_guid))})
    ld.path("Elements\\21000001", {"Element": binary(device_blob(win_guid))})
    ld.path("Elements\\12000002", {"Element": sz("\\Windows\\system32\\winload.efi")})
    ld.path("Elements\\22000002", {"Element": sz("\\Windows")})
    if safeboot:
        ld.path("Elements\\25000080", {"Element": binary(struct.pack("<Q", 0))})
    return build_hive(root, "BCD")


SERVICES = {
    # name: (start, type, image, group, errorcontrol)
    "stornvme": (0, 1, "System32\\drivers\\stornvme.sys", "SCSI miniport", 1),
    "storahci": (3, 1, "System32\\drivers\\storahci.sys", "SCSI miniport", 3),
    "disk": (0, 1, "System32\\drivers\\disk.sys", "SCSI Class", 1),
    "partmgr": (0, 1, "System32\\drivers\\partmgr.sys", "System Bus Extender", 3),
    "volmgr": (0, 1, "System32\\drivers\\volmgr.sys", "System Bus Extender", 3),
    "Ntfs": (3, 2, None, "Boot File System", 1),
    "EventLog": (2, 0x20, "%SystemRoot%\\System32\\svchost.exe -k LocalServiceNetworkRestricted -p", "", 1),
}


def build_system(broken=False):
    root = Key("ROOT")
    root.path("Select", {"Current": dword(1), "Default": dword(1), "LastKnownGood": dword(2)})
    cs = root.path("ControlSet001")
    for name, (start, typ, image, group, ec) in SERVICES.items():
        vals = {"Start": dword(start), "Type": dword(typ), "ErrorControl": dword(ec), "Group": sz(group)}
        if image:
            vals["ImagePath"] = esz(image)
        if broken and name == "stornvme":
            vals["Start"] = dword(3)
        cs.path(f"Services\\{name}", vals)
    filters = ["partmgr"] + (["ghostflt"] if broken else [])
    cs.path("Control\\Class\\{4d36e967-e325-11ce-bfc1-08002be10318}", {"UpperFilters": msz(filters)})
    cs.path("Control\\Session Manager", {"BootExecute": msz(["autocheck autochk *"])})
    cs.path("Control\\Session Manager\\Memory Management", {"PagingFiles": msz(["?:\\pagefile.sys"])})
    cs.path("Control\\CrashControl", {"CrashDumpEnabled": dword(7), "AutoReboot": dword(1)})
    cs.path("Control\\ComputerName\\ComputerName", {"ComputerName": sz("TESTPC")})
    cs.path("Control\\Session Manager\\Power", {"HiberbootEnabled": dword(1)})
    root.path("Setup", {"SystemSetupInProgress": dword(0), "SetupType": dword(0), "CmdLine": sz("")})
    root.path("MountedDevices", {"\\DosDevices\\C:": binary(b"DMIO:ID:" + uuid.UUID(WIN_GUID).bytes_le)})
    return build_hive(root, "SYSTEM")


def build_software():
    root = Key("ROOT")
    root.path("Microsoft\\Windows NT\\CurrentVersion", {
        "ProductName": sz("Windows 10 Pro"), "CurrentBuild": sz("22631"), "UBR": dword(4317),
        "DisplayVersion": sz("23H2"), "EditionID": sz("Professional"), "InstallDate": dword(1700000000)})
    root.path("Microsoft\\Windows\\CurrentVersion\\Component Based Servicing")
    return build_hive(root, "SOFTWARE")


def build_windows_tree(root, broken=False):
    from bootrepair.knowledge import CRITICAL_FILES
    for rel, _, _ in CRITICAL_FILES:
        _touch(root, rel)
    _touch(root, "Windows\\System32\\winload.efi")
    for name, (start, typ, image, *_r) in SERVICES.items():
        if image and image.lower().endswith(".sys"):
            _touch(root, "Windows\\" + image)
    _touch(root, "Windows\\System32\\config\\SYSTEM", build_system(broken))
    _touch(root, "Windows\\System32\\config\\SOFTWARE", build_software())
    for h in ("SAM", "SECURITY", "DEFAULT"):
        _touch(root, f"Windows\\System32\\config\\{h}", build_hive(Key("ROOT", subkeys=[Key("x")]), h))
    if broken:
        Path(root, "Windows", "System32", "hal.dll").write_bytes(b"\0" * 8192)
        _touch(root, "Windows\\WinSxS\\pending.xml", b"<?xml version='1.0'?><PendingTransaction/>")
        dump = bytearray(0x2000)
        dump[0:8] = b"PAGEDU64"
        struct.pack_into("<II", dump, 8, 15, 22631)
        struct.pack_into("<I", dump, 0x38, 0x7B)
        struct.pack_into("<4Q", dump, 0x40, 0xFFFF800012345678, 0xC0000034, 0, 0)
        struct.pack_into("<I", dump, 0xF98, 4)
        struct.pack_into("<Q", dump, 0xFA8, 133700000000000000)
        _touch(root, "Windows\\Minidump\\111223-1234-01.dmp", bytes(dump))
        _touch(root, "Windows\\WinSxS\\amd64_microsoft-windows-hal_31bf3856ad364e35_10.0.22621.1_none_0\\hal.dll",
               b"MZ" + b"\x02" * 70)
        _touch(root, "Windows\\WinSxS\\amd64_microsoft-windows-hal_31bf3856ad364e35_10.0.22621.4317_none_0\\hal.dll",
               b"MZ" + b"\x03" * 70)
        srt = ("Startup Repair diagnosis and repair log\r\n---------------------------\r\n"
               "Last successful boot time: 11/10/2023 9:12:00 AM (GMT)\r\nNumber of repair attempts: 2\r\n\r\n"
               "Root cause found: \r\n---------------------------\r\n"
               "Boot critical file c:\\windows\\system32\\drivers\\ghostflt.sys is corrupt.\r\n\r\n"
               "Repair action: File repair\r\nResult: Failed. Error code =  0x2\r\n")
        _touch(root, "Windows\\System32\\LogFiles\\Srt\\SrtTrail.txt", b"\xff\xfe" + srt.encode("utf-16-le"))
    _touch(root, "hiberfil.sys", b"\0" * 4096)


def build_esp_tree(root, bcd):
    _touch(root, "EFI\\Microsoft\\Boot\\bootmgfw.efi")
    _touch(root, "EFI\\Microsoft\\Boot\\BCD", bcd)
    _touch(root, "EFI\\Boot\\bootx64.efi")


class FakeMounts:
    def __init__(self, mapping):
        self.mapping = mapping

    def mount_ro(self, dev, fstypes, label):
        from bootrepair.mounting import MountError
        if dev not in self.mapping:
            raise MountError(f"{dev}: no such fixture")
        return Path(self.mapping[dev]), "fixture directory"

    def mount_rw(self, dev, fstypes, label, extra_opts=None):
        return self.mount_ro(dev, fstypes, label)

    def bitlocker_open(self, dev, key):
        from bootrepair.mounting import MountError
        raise MountError("not supported in tests")

    def cleanup(self):
        pass


def make_system(tmp, broken=False, bcd_win_guid=WIN_GUID):
    tmp = Path(tmp)
    disk_img = tmp / "disk.img"
    win_img = tmp / "win.img"
    esp_img = tmp / "esp.img"
    write_gpt_disk(disk_img)
    write_ntfs_partition(win_img, dirty=broken)
    esp_img.write_bytes(b"\0" * 4096)
    win_dir = tmp / "win"
    esp_dir = tmp / "esp"
    build_windows_tree(win_dir, broken)
    build_esp_tree(esp_dir, build_bcd(win_guid=bcd_win_guid))
    disk = {"name": "fakedisk", "path": str(disk_img), "size": os.path.getsize(disk_img), "model": "Fake NVMe",
            "vendor": "", "serial": "", "tran": "nvme", "pttype": "gpt", "ptuuid": DISK_GUID, "removable": False,
            "logical_block_size": 512, "controller": "nvme", "partitions": []}
    common = {"disk": "fakedisk", "disk_path": str(disk_img), "ptuuid": DISK_GUID, "pttype": "gpt",
              "partflags": "", "mountpoints": [], "uuid": "", "parttypename": "", "label": ""}
    esp = dict(common, name="fakep1", path=str(esp_img), number=1, size=1 << 20, fstype="vfat",
               partuuid=ESP_GUID, parttype=ESP_TYPE, start_bytes=ESP_START, is_esp=True, is_winre=False,
               windows_score=0)
    win = dict(common, name="fakep2", path=str(win_img), number=2, size=os.path.getsize(win_img), fstype="ntfs",
               partuuid=WIN_GUID, parttype=BASIC_TYPE, start_bytes=WIN_START, is_esp=False, is_winre=False,
               windows_score=80, label="Windows")
    disk["partitions"] = [esp, win]
    mounts = FakeMounts({str(win_img): win_dir, str(esp_img): esp_dir})
    return [disk], disk, win, mounts
