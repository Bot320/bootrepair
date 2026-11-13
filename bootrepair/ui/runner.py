"""Runs the privileged helper (via pkexec) and streams its JSON-lines protocol back to the UI."""

import json
import os
from pathlib import Path

from gi.repository import Gio, GLib

from ..i18n import _

INSTALLED_HELPER = "/usr/lib/bootrepair/bootrepair-helper"
FINAL_TYPES = ("result", "fix-result", "undo-result", "bootnext-result")


def find_helper():
    root = Path(__file__).resolve().parent.parent.parent
    dev = root / "bootrepair-helper"
    if str(root) == "/usr/lib/bootrepair" or not dev.exists():
        return INSTALLED_HELPER
    return str(dev)


class HelperProcess:
    """Generic helper invocation. on_finished(final_msg | None, error | None, cancelled)."""

    def __init__(self, args, stdin_text, on_message, on_finished):
        self.args = args
        self.stdin_text = stdin_text
        self.on_message = on_message
        self.on_finished = on_finished
        self.proc = None
        self.final = None
        self.error = None
        self.cancelled = False
        self.stderr = []
        self._stdout_done = self._stderr_done = self._exited = self._finished = False

    def start(self):
        from ..i18n import language
        argv = [find_helper(), "--lang", language(), *self.args]
        if os.geteuid() != 0:
            argv = ["pkexec"] + argv
        flags = (Gio.SubprocessFlags.STDIN_PIPE | Gio.SubprocessFlags.STDOUT_PIPE |
                 Gio.SubprocessFlags.STDERR_PIPE)
        try:
            self.proc = Gio.Subprocess.new(argv, flags)
        except GLib.Error as e:
            GLib.idle_add(self._finish_error, _(t"Could not start the BootRepair helper: {e.message}"))
            return
        stdin = self.proc.get_stdin_pipe()
        stdin.write_all(self.stdin_text.encode(), None)
        stdin.flush(None)
        self.out = Gio.DataInputStream.new(self.proc.get_stdout_pipe())
        self.err = Gio.DataInputStream.new(self.proc.get_stderr_pipe())
        self.out.read_line_async(GLib.PRIORITY_DEFAULT, None, self._on_out)
        self.err.read_line_async(GLib.PRIORITY_DEFAULT, None, self._on_err)
        self.proc.wait_async(None, self._on_exit)

    def cancel(self):
        self.cancelled = True
        if self.proc is not None:
            try:
                self.proc.get_stdin_pipe().close(None)   # helper treats EOF on stdin as "cancel"
            except GLib.Error:
                pass

    def _on_out(self, stream, res):
        try:
            line, __ = stream.read_line_finish_utf8(res)
        except GLib.Error:
            line = None
        if line is None:
            self._stdout_done = True
            self._maybe_finish()
            return
        line = line.strip()
        if line:
            try:
                msg = json.loads(line)
            except ValueError:
                self.stderr.append(line)
                msg = None
            if msg is not None:
                t = msg.get("type")
                if t in FINAL_TYPES:
                    self.final = msg
                elif t == "error":
                    self.error = msg.get("msg", _("unknown error"))
                elif t == "cancelled":
                    self.cancelled = True
                self.on_message(msg)
        stream.read_line_async(GLib.PRIORITY_DEFAULT, None, self._on_out)

    def _on_err(self, stream, res):
        try:
            line, __ = stream.read_line_finish_utf8(res)
        except GLib.Error:
            line = None
        if line is None:
            self._stderr_done = True
            self._maybe_finish()
            return
        self.stderr.append(line)
        stream.read_line_async(GLib.PRIORITY_DEFAULT, None, self._on_err)

    def _on_exit(self, proc, res):
        try:
            proc.wait_finish(res)
        except GLib.Error:
            pass
        self._exited = True
        self._maybe_finish()

    def _maybe_finish(self):
        if self._finished or not (self._exited and self._stdout_done and self._stderr_done):
            return
        self._finished = True
        code = self.proc.get_exit_status() if self.proc.get_if_exited() else -1
        if self.final is not None:
            self.on_finished(self.final, None, False)
            return
        if self.cancelled:
            self.on_finished(None, None, True)
            return
        err = self.error
        if err is None:
            if code == 126:
                err = _("Authentication was cancelled. Administrator rights are needed to access the disk.")
            elif code == 127:
                cmd = "sudo " + find_helper() + " " + " ".join(self.args[:2])
                err = _(t"Not authorised, or no polkit authentication agent is running. "
                        t"Alternatively run in a terminal:  {cmd}")
            else:
                err = _(t"The helper exited with code {code}.")
        tail = "\n".join(self.stderr[-30:])
        self.on_finished(None, err + (("\n\n" + tail) if tail else ""), False)

    def _finish_error(self, msg):
        self.on_finished(None, msg, False)
        return False


def analyze_process(partition, esp, key, events, on_message, on_finished):
    args = ["analyze", partition, "--esp", esp or "auto", "--progress"]
    if key:
        args.append("--key-stdin")
    if not events:
        args.append("--no-events")
    return HelperProcess(args, (key or "") + "\n", on_message, on_finished)


def fix_process(partition, boot, actions, on_message, on_finished, state=None):
    req = json.dumps({"partition": partition, "boot": boot, "actions": actions, "state": state or {}})
    return HelperProcess(["fix", "--progress"], req + "\n", on_message, on_finished)


def undo_process(backup, on_message, on_finished):
    args = ["undo", "--progress"] + ([backup] if backup else [])
    return HelperProcess(args, "\n", on_message, on_finished)


def bootnext_process(num, on_message, on_finished):
    return HelperProcess(["bootnext", num, "--progress"], "\n", on_message, on_finished)
