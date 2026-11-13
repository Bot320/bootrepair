"""Privileged backend: mounts read-only, runs the analysis, prints JSON (for the GUI) or text (CLI).

Usage:  bootrepair-helper analyze /dev/nvme0n1p3 [--esp auto|/dev/X] [--key-stdin] [--no-events] [--json|--progress]
        bootrepair-helper list
"""

import argparse
import json
import os
import signal
import sys
import threading

from . import __version__
from .devices import list_disks, find_partition
from .i18n import _, set_language


class _Out:
    def __init__(self, mode):
        self.mode = mode
        self.lock = threading.Lock()

    def __call__(self, msg):
        if self.mode == "progress":
            with self.lock:
                sys.stdout.write(json.dumps(msg, default=str) + "\n")
                sys.stdout.flush()
        elif self.mode == "text" and msg.get("type") == "step" and msg.get("state") == "running":
            sys.stderr.write(f"  ... {msg['id']}\n")
            sys.stderr.flush()


def _die(out, msg, code=2):
    if out.mode == "progress":
        out({"type": "error", "msg": msg})
    else:
        sys.stderr.write(f"error: {msg}\n")
    sys.exit(code)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bootrepair-helper", description="BootRepair backend: read-only analysis and explicit, backed-up repairs")
    ap.add_argument("--version", action="version", version=__version__)
    ap.add_argument("--lang", default="auto", choices=["auto", "en", "de"],
                    help="language of the report and repair instructions (default: from the environment)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="analyse a Windows partition")
    a.add_argument("partition")
    a.add_argument("--esp", default="auto", help="EFI system partition to use (default: auto)")
    a.add_argument("--key-stdin", action="store_true", help="read a BitLocker recovery key from the first stdin line")
    a.add_argument("--no-events", action="store_true", help="skip the (slower) event log analysis")
    g = a.add_mutually_exclusive_group()
    g.add_argument("--json", action="store_true", help="print the full report as JSON")
    g.add_argument("--progress", action="store_true", help="JSON lines protocol for the GUI")
    a.add_argument("--markdown", metavar="FILE", help="also write a Markdown report to FILE")
    sub.add_parser("list", help="list disks and partitions as JSON")
    c = sub.add_parser("collect", help="analyse and save an evidence bundle (for support / testing)")
    c.add_argument("partition")
    c.add_argument("outdir")
    c.add_argument("--esp", default="auto")
    fx = sub.add_parser("fix", help="apply repair actions (JSON request on stdin)")
    fx.add_argument("--progress", action="store_true", help="JSON lines protocol for the GUI")
    ud = sub.add_parser("undo", help="undo a repair from its backup")
    ud.add_argument("backup", nargs="?", help="backup directory (default: the latest one)")
    ud.add_argument("--progress", action="store_true")
    sub.add_parser("backups", help="list repair backups as JSON")
    bn = sub.add_parser("bootnext", help="start this firmware boot entry once at the next restart")
    bn.add_argument("num", help="boot entry number, e.g. 0005")
    bn.add_argument("--progress", action="store_true")
    args = ap.parse_args(argv)
    set_language(args.lang)

    if args.cmd in ("fix", "undo", "backups"):
        return _repair_cmd(args)
    if args.cmd == "bootnext":
        return _bootnext(args)

    if args.cmd == "collect":
        if os.geteuid() != 0:
            sys.stderr.write("error: must run as root\n")
            return 2
        from .collect import collect
        from .report import to_text
        r = collect(args.partition, args.outdir, args.esp,
                    progress=lambda m: m.get("type") == "step" and m.get("state") == "running"
                    and sys.stderr.write(f"  ... {m['id']}\n"))
        print(to_text(r))
        print(f"\nEvidence bundle written to {args.outdir}")
        return 0

    if args.cmd == "list":
        print(json.dumps(list_disks(), indent=2))
        return 0

    out = _Out("progress" if args.progress else "json" if args.json else "text")
    if os.geteuid() != 0:
        _die(out, "must run as root (it needs raw read access to the disk). Use sudo or pkexec.")

    key = None
    cancel = threading.Event()
    if args.key_stdin or args.progress:
        line = sys.stdin.readline()
        key = line.strip() or None if args.key_stdin else None
    if args.progress:
        # The GUI keeps stdin open; EOF means "cancel".
        def watch():
            try:
                while sys.stdin.read(4096):
                    pass
            except (OSError, ValueError):
                pass
            cancel.set()
        threading.Thread(target=watch, daemon=True).start()

    def on_signal(signum, frame):
        cancel.set()
        raise KeyboardInterrupt
    for s in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, on_signal)

    from .analyzers import STEPS, run_analysis, Cancelled
    from .mounting import Mounts

    try:
        disks = list_disks()
    except RuntimeError as e:
        _die(out, str(e))
    disk, part = find_partition(disks, args.partition)
    if part is None:
        _die(out, f"{args.partition} is not a partition on a disk (use 'bootrepair-helper list')")

    out({"type": "steps", "steps": [{"id": s[0], "title": _(s[1])} for s in STEPS]})
    options = {"events": not args.no_events}
    mounts = Mounts()
    try:
        with mounts:
            report = run_analysis(disks, disk, part, args.esp, key, options, mounts, out, cancel.is_set)
    except (Cancelled, KeyboardInterrupt):
        mounts.cleanup()
        if out.mode == "progress":
            out({"type": "cancelled"})
        else:
            sys.stderr.write("cancelled\n")
        return 130
    except Exception as e:  # unexpected - report but never leave mounts behind
        mounts.cleanup()
        import traceback
        _die(out, f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

    if args.markdown:
        from .report import to_markdown
        with open(args.markdown, "w") as f:
            f.write(to_markdown(report))
    if out.mode == "progress":
        out({"type": "result", "report": report})
    elif out.mode == "json":
        print(json.dumps(report, indent=2, default=str))
    else:
        from .report import to_text
        print(to_text(report))
    return 0


def _bootnext(args):
    import re
    import subprocess
    out = _Out("progress" if args.progress else "text")
    if os.geteuid() != 0:
        _die(out, _("must run as root"))
    if not re.fullmatch(r"[0-9A-Fa-f]{4}", args.num):
        _die(out, _("invalid boot entry number"))
    r = subprocess.run(["efibootmgr", "-n", args.num.upper()], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        _die(out, _(t"efibootmgr failed: {(r.stderr or r.stdout).strip()}"))
    if args.progress:
        out({"type": "bootnext-result", "num": args.num.upper()})
    else:
        print(f"Boot{args.num.upper()} will be started once at the next restart.")
    return 0


def _repair_cmd(args):
    from . import fixes
    prog = getattr(args, "progress", False)
    out = _Out("progress" if prog else "text")

    def emit(msg):
        if prog:
            out(msg)
        elif msg.get("type") == "log":
            sys.stderr.write(f"  {msg['msg']}\n")
        elif msg.get("type") == "fix" and msg.get("state") in ("done", "failed"):
            sys.stderr.write(f"  {msg['state']}: {msg['id']} {msg.get('note', '')}\n")

    if os.geteuid() != 0:
        _die(out, _("must run as root"))
    try:
        if args.cmd == "backups":
            print(json.dumps(fixes.list_backups(), indent=2))
            return 0
        if args.cmd == "undo":
            b = args.backup or fixes.latest_backup()
            if b is None:
                _die(out, _("there is no repair backup to undo"))
            done = fixes.undo(b, emit)
            if prog:
                out({"type": "undo-result", "backup": str(b), "changes": done})
            else:
                print("\n".join(done) + f"\nUndone: {b}")
            return 0
        req = json.loads(sys.stdin.readline())
        res = fixes.apply(req["partition"], req.get("boot"), req["actions"], emit, state=req.get("state"))
    except Exception as e:  # noqa: BLE001
        _die(out, f"{type(e).__name__}: {e}")
    if prog:
        out({"type": "fix-result", "result": res})
    else:
        for r in res["results"]:
            print(("OK   " if r["ok"] else "FAIL ") + r["title"])
            for c in r.get("changes") or [r.get("error", "")]:
                print("       " + str(c))
        print(f"Backup (for undo): {res['backup']}")
    return 0 if all(r["ok"] for r in res["results"]) else 1


if __name__ == "__main__":
    sys.exit(main())
