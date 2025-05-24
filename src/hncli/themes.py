from rich.theme import Theme

DEFAULT_THEME = Theme({
    "info": "cyan",
    "warning": "magenta",
    "error": "bold red",
})

DARK_THEME = Theme({
    "info": "bright_cyan",
    "warning": "bright_magenta",
    "error": "bold bright_red",
})

_THEMES = {
    "default": DEFAULT_THEME,
    "dark": DARK_THEME,
}

def get_theme(name: str) -> Theme:
    """Return theme by name or default if not found."""
    return _THEMES.get(name, DEFAULT_THEME)

