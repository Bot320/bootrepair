import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hivebuilder import Key, build_hive, sz, msz, dword, binary  # noqa: E402
from fixtures import build_bcd, device_blob, WIN_GUID, GONE_GUID, LOADER, DISK_GUID  # noqa: E402
from bootrepair.parsers.regf import Hive, RegfError  # noqa: E402
from bootrepair.parsers import bcd as B  # noqa: E402
from bootrepair.parsers.dump import parse_dump_header  # noqa: E402
from bootrepair.parsers.disk import parse_mbr, parse_gpt_header  # noqa: E402


class RegfTests(unittest.TestCase):
    def test_roundtrip(self):
        root = Key("ROOT")
        root.path("A\\B", {"s": sz("hello"), "n": dword(42), "m": msz(["x", "y"]), "b": binary(b"\x01\x02\x03\x04\x05")})
        h = Hive(build_hive(root))
        self.assertTrue(h.checksum_ok)
        self.assertTrue(h.sequence_ok)
        self.assertEqual(h.check_bins()[1], [])
        self.assertEqual(h.walk_check(), [])
        k = h.open("a\\b")
        self.assertEqual(k.get("s"), "hello")
        self.assertEqual(k.get("N"), 42)
        self.assertEqual(k.get("m"), ["x", "y"])
        self.assertEqual(k.get("b"), b"\x01\x02\x03\x04\x05")
        self.assertIsNone(h.open("A\\C"))

    def test_bad_checksum_and_signature(self):
        h = Hive(build_hive(Key("R"), corrupt_checksum=True))
        self.assertFalse(h.checksum_ok)
        with self.assertRaises(RegfError):
            Hive(b"\0" * 8192)

    def test_dirty(self):
        h = Hive(build_hive(Key("R"), seq=(5, 4)))
        self.assertFalse(h.sequence_ok)


class BcdTests(unittest.TestCase):
    parts = [{"name": "win", "pttype": "gpt", "partuuid": WIN_GUID, "ptuuid": DISK_GUID, "start_bytes": 0},
             {"name": "other", "pttype": "gpt", "partuuid": "99999999-9999-4999-8999-999999999999",
              "ptuuid": DISK_GUID, "start_bytes": 0}]

    def test_parse_and_match(self):
        st = B.BcdStore(Hive(build_bcd()))
        self.assertIsNotNone(st.bootmgr)
        self.assertEqual(st.bootmgr.get(B.E_DEFAULT).lower(), LOADER)
        ld = st.get(LOADER)
        self.assertEqual(ld.type, B.TYPE_OSLOADER)
        self.assertEqual(ld.description, "Windows 11")
        info, m = B.resolve_device(ld.get(B.E_OSDEVICE), self.parts)
        self.assertEqual(m, ["win"])
        self.assertEqual(info["kind"], "partition")
        self.assertEqual(info["partition_guid"], "{" + WIN_GUID + "}")

    def test_missing_partition(self):
        st = B.BcdStore(Hive(build_bcd(win_guid=GONE_GUID)))
        info, m = B.resolve_device(st.get(LOADER).get(B.E_OSDEVICE), self.parts)
        self.assertEqual(m, [])
        self.assertIn("NOT present", B.describe_device(info, m))

    def test_mbr_match(self):
        b = bytearray(0x58)
        struct.pack_into("<I", b, 0x10, 6)
        struct.pack_into("<Q", b, 0x20, 1048576)
        struct.pack_into("<I", b, 0x34, 1)
        struct.pack_into("<I", b, 0x38, 0xD36F268A)
        p = {"name": "sda1", "pttype": "dos", "ptuuid": "d36f268a", "partuuid": "d36f268a-01", "start_bytes": 1048576}
        self.assertTrue(B.device_matches(bytes(b), p))
        p2 = dict(p, start_bytes=2048 * 512 * 2)
        self.assertFalse(B.device_matches(bytes(b), p2))


class DumpTests(unittest.TestCase):
    def test_header(self):
        d = bytearray(0x2000)
        d[0:8] = b"PAGEDU64"
        struct.pack_into("<I", d, 0x38, 0x7B)
        struct.pack_into("<4Q", d, 0x40, 1, 0xC0000034, 3, 4)
        struct.pack_into("<Q", d, 0xFA8, 133700000000000000)
        h = parse_dump_header(bytes(d))
        self.assertEqual(h["code"], 0x7B)
        self.assertEqual(h["params"][1], 0xC0000034)
        self.assertEqual(h["time"].year, 2024)


class DiskTests(unittest.TestCase):
    def test_gpt_image(self):
        import tempfile
        from fixtures import write_gpt_disk
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "d.img")
            write_gpt_disk(p)
            with open(p, "rb") as f:
                head = f.read(1024)
            m = parse_mbr(head[:512])
            self.assertTrue(m["protective"])
            h = parse_gpt_header(head[512:1024], 512)
            self.assertTrue(h["valid"], h)


class EvtxTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("BOOTREPAIR_SAMPLE_EVTX"), "set BOOTREPAIR_SAMPLE_EVTX to a System.evtx sample")
    def test_sample(self):
        from bootrepair.parsers.evtx import Evtx
        log = Evtx.from_file(os.environ["BOOTREPAIR_SAMPLE_EVTX"])
        evs = list(log.events())
        self.assertGreater(len(evs), 10)
        self.assertEqual(log.bad_records, 0)
        self.assertTrue(all(e.provider for e in evs[:50]))


if __name__ == "__main__":
    unittest.main()
