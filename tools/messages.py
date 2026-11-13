#!/usr/bin/env python3
"""Message catalog maintenance.

    tools/messages.py list            all message ids (numbered) found in _() / N_() calls
    tools/messages.py missing         message ids without a German translation
    tools/messages.py check           exit 1 on missing translations or placeholder mismatches
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CONV = {-1: None, 115: "s", 114: "r", 97: "a"}


def _spec(node):
    if node is None:
        return ""
    return "".join(v.value for v in node.values if isinstance(v, ast.Constant))


def msgid(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if type(node).__name__ == "TemplateStr":
        out = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                out.append(v.value.replace("{", "{{").replace("}", "}}"))
            else:
                conv = CONV.get(v.conversion)
                out.append("{" + v.str + (f"!{conv}" if conv else "") + (f":{_spec(v.format_spec)}" if v.format_spec else "") + "}")
        return "".join(out)
    return None


def extract():
    found = {}
    for p in sorted((ROOT / "bootrepair").rglob("*.py")):
        if p.name == "locale_de.py":
            continue
        tree = ast.parse(p.read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("_", "N_") and n.args:
                m = msgid(n.args[0])
                if m and m.strip():
                    found.setdefault(m, f"{p.relative_to(ROOT)}:{n.lineno}")
    return found


TOKEN = re.compile(r"\{\{|\}\}|\{[^{}]*\}")


def placeholders(s):
    return sorted(t for t in TOKEN.findall(s) if t not in ("{{", "}}"))


def needs_translation(m):
    return len(re.findall(r"[A-Za-z]{3,}", TOKEN.sub("", re.sub(r"`[^`]*`", "", m)))) >= 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    found = extract()
    from bootrepair.locale_de import MESSAGES
    if cmd == "list":
        for i, (m, loc) in enumerate(found.items()):
            print(f"#{i} {loc}\n{m!r}")
        return 0
    missing = [m for m in found if m not in MESSAGES and needs_translation(m)]
    bad = [(m, MESSAGES[m]) for m in found if m in MESSAGES and placeholders(m) != placeholders(MESSAGES[m])]
    codes = [(m, MESSAGES[m]) for m in found if m in MESSAGES
             and re.findall(r"`[^`]*`", m) != re.findall(r"`[^`]*`", MESSAGES[m])]
    unused = [m for m in MESSAGES if m not in found]
    if cmd == "missing":
        for i, m in enumerate(missing):
            print(f"#{i} {found[m]}\n{m!r}")
        print(f"{len(missing)} missing", file=sys.stderr)
        return 0
    for m, t in bad:
        print(f"PLACEHOLDERS differ:\n  {m!r}\n  {t!r}")
    for m, t in codes:
        print(f"COMMANDS differ:\n  {m!r}\n  {t!r}")
    print(f"{len(found)} messages, {len(missing)} untranslated, {len(bad)} placeholder errors, "
          f"{len(codes)} command mismatches, {len(unused)} unused")
    return 1 if (missing or bad or codes) else 0


if __name__ == "__main__":
    sys.exit(main())
