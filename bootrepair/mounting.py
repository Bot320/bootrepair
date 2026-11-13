"""Strictly read-only access to partitions: read-only loop devices + ro mounts, always cleaned up."""

import os
import shutil
import subprocess
from pathlib import Path

RUN_DIR = Path("/run/bootrepair")


class MountError(Exception):
    pass


def _run(cmd, input=None, timeout=120):
    return subprocess.run(cmd, capture_output=True, text=True, input=input, timeout=timeout)


def existing_mount(dev):
    """Return the mount point if dev is already mounted, else None."""
    try:
        r = _run(["findmnt", "-n", "-r", "-o", "TARGET,OPTIONS", "--source", dev])
    except (OSError, subprocess.SubprocessError):
        return None
    for line in r.stdout.splitlines():
        parts = line.split(" ")
        if parts and parts[0]:
            target = parts[0].replace("\\x20", " ")
            opts = parts[1] if len(parts) > 1 else ""
            return target, ("ro" in opts.split(","))
    return None


class Mounts:
    """Context manager tracking every loop device, dm mapping and mount we create."""

    def __init__(self, log=print):
        self.log = log
        self.loops = []
        self.mounts = []
        self.mappers = []
        self.dirs = []
        self._n = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.cleanup()
        return False

    def attach_ro(self, dev):
        r = _run(["losetup", "--read-only", "--find", "--show", dev])
        if r.returncode != 0:
            raise MountError(f"losetup failed for {dev}: {r.stderr.strip()}")
        loop = r.stdout.strip()
        self.loops.append(loop)
        return loop

    def mount_ro(self, dev, fstypes, label):
        """Mount dev read-only (through a read-only loop device). Returns (mountpoint, description)."""
        em = existing_mount(dev)
        if em:
            return Path(em[0]), f"already mounted at {em[0]} ({'ro' if em[1] else 'rw'}), read in place"
        loop = self.attach_ro(dev)
        self._n += 1
        mp = RUN_DIR / f"{label}-{os.getpid()}-{self._n}"
        mp.mkdir(parents=True, exist_ok=True)
        self.dirs.append(mp)
        errors = []
        for fs in fstypes:
            if fs == "ntfs-3g" and not shutil.which("ntfs-3g"):
                continue
            opts = "ro"
            if fs == "vfat":
                opts = "ro,utf8,shortname=mixed"
            r = _run(["mount", "-t", fs, "-o", opts, loop, str(mp)])
            if r.returncode == 0:
                self.mounts.append(mp)
                return mp, f"mounted read-only with {fs} via {loop}"
            errors.append(f"{fs}: {(r.stderr or r.stdout).strip()}")
        raise MountError("; ".join(errors) or "no usable file-system driver")

    def mount_rw(self, dev, fstypes, label, extra_opts=None):
        """Mount dev read-write (directly, no loop). Used only by explicit repairs."""
        em = existing_mount(dev)
        if em:
            if em[1]:
                raise MountError(f"{dev} is mounted read-only at {em[0]} - unmount it first")
            return Path(em[0]), f"already mounted read-write at {em[0]}"
        self._n += 1
        mp = RUN_DIR / f"{label}-rw-{os.getpid()}-{self._n}"
        mp.mkdir(parents=True, exist_ok=True)
        self.dirs.append(mp)
        errors = []
        for fs in fstypes:
            if fs == "ntfs-3g" and not shutil.which("ntfs-3g"):
                continue
            opts = "rw" + ("," + extra_opts.get(fs) if extra_opts and extra_opts.get(fs) else "")
            if fs == "vfat":
                opts += ",utf8,shortname=mixed"
            r = _run(["mount", "-t", fs, "-o", opts, dev, str(mp)])
            if r.returncode == 0:
                self.mounts.append(mp)
                return mp, f"mounted read-write with {fs}"
            errors.append(f"{fs}: {(r.stderr or r.stdout).strip()}")
        raise MountError("; ".join(errors) or "no usable file-system driver")

    def bitlocker_open(self, dev, key):
        if not shutil.which("cryptsetup"):
            raise MountError("cryptsetup is not installed")
        loop = self.attach_ro(dev)
        name = f"bootrepair-{os.getpid()}-{Path(dev).name}"
        r = _run(["cryptsetup", "open", "--type", "bitlk", "--readonly", loop, name],
                 input=key.strip() + "\n")
        if r.returncode != 0:
            raise MountError(f"BitLocker unlock failed: {(r.stderr or r.stdout).strip()}")
        self.mappers.append(name)
        return f"/dev/mapper/{name}"

    def cleanup(self):
        for mp in reversed(self.mounts):
            r = _run(["umount", str(mp)])
            if r.returncode != 0:
                _run(["umount", "-l", str(mp)])
        self.mounts.clear()
        for name in reversed(self.mappers):
            _run(["cryptsetup", "close", name])
        self.mappers.clear()
        for loop in reversed(self.loops):
            _run(["losetup", "-d", loop])
        self.loops.clear()
        for d in reversed(self.dirs):
            try:
                d.rmdir()
            except OSError:
                pass
        self.dirs.clear()
