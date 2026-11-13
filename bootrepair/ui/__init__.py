def xrow(cls, title="", subtitle=None, **kw):
    """Create an Adw row whose title/subtitle are plain text (never parsed as Pango markup)."""
    r = cls(**kw)
    r.set_use_markup(False)
    r.set_title(title)
    if subtitle is not None:
        r.set_subtitle(subtitle)
    return r
