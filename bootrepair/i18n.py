"""Translations (English source strings, German catalog in locale_de.py).

    _("plain text")                      -> translated str
    _(t"Hive {name} is missing")         -> translated and filled in; the message id keeps the placeholder text
    N_("text")                           -> marks a constant for extraction; translate it with _() where it is used

A message that is not in the catalog as a whole is translated sentence by sentence, so texts that are
assembled from optional sentences still come out translated. Text in `backticks` (commands) is never changed.
"""

import os
import re
from string.templatelib import Interpolation, Template

LANGUAGES = {"en": "English", "de": "Deutsch"}
_catalog = {}
_lang = "en"


def detect():
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        v = os.environ.get(var, "")
        for part in v.split(":"):
            if part[:2] in LANGUAGES:
                return part[:2]
            if part and part not in ("C", "POSIX") and not part.startswith("C."):
                return "en"
    return "en"


def set_language(lang=None):
    """lang: 'en', 'de' or None/'auto' (from the environment). Returns the active language."""
    global _catalog, _lang
    if not lang or lang == "auto":
        lang = detect()
    _lang = lang if lang in LANGUAGES else "en"
    if lang == "pseudo":                      # testing: every translatable string becomes ⟦…⟧
        _lang, _catalog = "en", _Pseudo()
        return "pseudo"
    if _lang == "de":
        from .locale_de import MESSAGES
        _catalog = MESSAGES
    else:
        _catalog = {}
    return _lang


class _Pseudo(dict):
    def get(self, k, default=None):
        return "⟦" + k + "⟧"

    def __contains__(self, k):
        return True

    def __bool__(self):
        return True


def language():
    return _lang


def N_(s):
    return s


# ----------------------------------------------------------------------------- message ids
def _token(expr, conversion, spec):
    return "{" + expr + (f"!{conversion}" if conversion else "") + (f":{spec}" if spec else "") + "}"


def msgid_of(tmpl):
    """Template -> (msgid, {token: formatted value})"""
    parts, values = [], {}
    for item in tmpl:
        if isinstance(item, Interpolation):
            tok = _token(item.expression, item.conversion, item.format_spec)
            v = item.value
            if item.conversion == "r":
                v = repr(v)
            elif item.conversion == "s":
                v = str(v)
            elif item.conversion == "a":
                v = ascii(v)
            values[tok] = format(v, item.format_spec)
            parts.append(tok)
        else:
            parts.append(item.replace("{", "{{").replace("}", "}}"))
    return "".join(parts), values


_FILL = re.compile(r"\{\{|\}\}|\{[^{}]*\}")


def _fill(text, values, template):
    if not template:
        return text

    def sub(m):
        s = m.group(0)
        if s == "{{":
            return "{"
        if s == "}}":
            return "}"
        return values.get(s, s)
    return _FILL.sub(sub, text)


# sentence fallback: split between sentences, never inside `code` or {placeholders}
_UNITS = re.compile(r"`[^`]*`|\{\{|\}\}|\{[^{}]*\}|[^`{}]+|[{}`]")
_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"(\[{])")


def _sentences(msgid):
    out, cur = [], ""
    for u in _UNITS.findall(msgid):
        if u[0] in "`{" or not _SPLIT.search(u):
            cur += u
            continue
        pieces = _SPLIT.split(u)
        cur += pieces[0]
        for p in pieces[1:]:
            out.append(cur)
            cur = p
    if cur:
        out.append(cur)
    return out


def _lookup(msgid):
    t = _catalog.get(msgid)
    if t is not None:
        return t
    lead = len(msgid) - len(msgid.lstrip())
    trail = len(msgid) - len(msgid.rstrip())
    core = msgid.strip()
    if core != msgid and core in _catalog:
        return msgid[:lead] + _catalog[core] + (msgid[len(msgid) - trail:] if trail else "")
    sents = _sentences(core)
    if len(sents) < 2:
        return None
    out, i, hit = [], 0, False
    while i < len(sents):
        for j in range(len(sents), i, -1):
            key = " ".join(sents[i:j])
            if key in _catalog:
                out.append(_catalog[key])
                hit = True
                i = j
                break
        else:
            out.append(sents[i])
            i += 1
    if not hit:
        return None
    return msgid[:lead] + " ".join(out) + (msgid[len(msgid) - trail:] if trail else "")


def _(s):
    """Translate a str or a t-string Template."""
    if isinstance(s, Template):
        msgid, values = msgid_of(s)
        if _catalog:
            t = _lookup(msgid)
            if t is not None:
                return _fill(t, values, True)
        return _fill(msgid, values, True)
    if not isinstance(s, str) or not _catalog or not s:
        return s
    t = _lookup(s)
    return s if t is None else t
